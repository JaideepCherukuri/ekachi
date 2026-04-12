import asyncio

import pytest

from app.application.services.trigger_service import TriggerService
from app.domain.models.project import Project
from app.domain.models.trigger import Trigger, TriggerRun, TriggerRunStatus, TriggerStatus, TriggerType


class InMemoryTriggerRepository:
    def __init__(self):
        self.triggers: dict[str, Trigger] = {}
        self.runs: dict[str, TriggerRun] = {}

    async def save_trigger(self, trigger: Trigger) -> None:
        self.triggers[trigger.id] = trigger.model_copy(deep=True)

    async def find_trigger_by_id(self, trigger_id: str):
        trigger = self.triggers.get(trigger_id)
        return trigger.model_copy(deep=True) if trigger else None

    async def find_trigger_by_id_and_user_id(self, trigger_id: str, user_id: str):
        trigger = self.triggers.get(trigger_id)
        if not trigger or trigger.user_id != user_id:
            return None
        return trigger.model_copy(deep=True)

    async def find_trigger_by_webhook(self, trigger_id: str, webhook_secret: str):
        trigger = self.triggers.get(trigger_id)
        if not trigger or trigger.webhook_secret != webhook_secret:
            return None
        return trigger.model_copy(deep=True)

    async def find_triggers_by_user_id(self, user_id: str, project_id: str | None = None):
        return [
            trigger.model_copy(deep=True)
            for trigger in self.triggers.values()
            if trigger.user_id == user_id and trigger.project_id == project_id
        ]

    async def find_due_schedule_triggers(self, now, limit: int = 25):
        return []

    async def delete_trigger(self, trigger_id: str) -> None:
        self.triggers.pop(trigger_id, None)

    async def clear_project_for_user_triggers(self, user_id: str, project_id: str) -> None:
        return None

    async def save_run(self, run: TriggerRun) -> None:
        self.runs[run.id] = run.model_copy(deep=True)

    async def find_run_by_id(self, run_id: str):
        run = self.runs.get(run_id)
        return run.model_copy(deep=True) if run else None

    async def find_runs_by_user_id(self, user_id: str, project_id: str | None = None, trigger_id: str | None = None, limit: int = 50):
        runs = [
            run.model_copy(deep=True)
            for run in self.runs.values()
            if run.user_id == user_id and run.project_id == project_id and (trigger_id is None or run.trigger_id == trigger_id)
        ]
        return runs[:limit]

    async def clear_project_for_user_runs(self, user_id: str, project_id: str) -> None:
        return None


class NoopProjectRepository:
    async def find_by_id_and_user_id(self, project_id: str, user_id: str):
        return None


class FakeSession:
    def __init__(self, session_id: str):
        self.id = session_id


class FakeAgentService:
    def __init__(self):
        self.session_counter = 0
        self.block_execution = False
        self.started_event = asyncio.Event()
        self.release_event = asyncio.Event()
        self.stopped_sessions: list[str] = []

    async def create_session(self, **kwargs):
        self.session_counter += 1
        return FakeSession(f"session-{self.session_counter}")

    async def chat(self, **kwargs):
        self.started_event.set()
        if self.block_execution:
            await self.release_event.wait()
        if False:
            yield None

    async def stop_session(self, session_id: str, user_id: str):
        self.stopped_sessions.append(session_id)


@pytest.mark.asyncio
async def test_retry_run_increments_attempt_number():
    trigger_repository = InMemoryTriggerRepository()
    agent_service = FakeAgentService()
    service = TriggerService(
        trigger_repository=trigger_repository,
        project_repository=NoopProjectRepository(),
        agent_service=agent_service,
    )

    trigger = await service.create_trigger(
        user_id="user-1",
        project_id=None,
        name="Manual Trigger",
        prompt="Do the thing",
        trigger_type=TriggerType.MANUAL,
        status=TriggerStatus.ACTIVE,
        schedule_cron=None,
        schedule_timezone="UTC",
    )

    first_run = await service.execute_trigger(trigger.id, "user-1", TriggerType.MANUAL, {"source": "first"})
    await asyncio.sleep(0)
    retried_run = await service.retry_run(first_run.id, "user-1")
    await asyncio.sleep(0)

    assert retried_run.attempt_number == 2
    assert retried_run.input_payload == {"source": "first"}


@pytest.mark.asyncio
async def test_cancel_run_marks_execution_cancelled_and_updates_counts():
    trigger_repository = InMemoryTriggerRepository()
    agent_service = FakeAgentService()
    agent_service.block_execution = True
    service = TriggerService(
        trigger_repository=trigger_repository,
        project_repository=NoopProjectRepository(),
        agent_service=agent_service,
    )

    trigger = await service.create_trigger(
        user_id="user-1",
        project_id=None,
        name="Blocking Trigger",
        prompt="Wait for cancellation",
        trigger_type=TriggerType.MANUAL,
        status=TriggerStatus.ACTIVE,
        schedule_cron=None,
        schedule_timezone="UTC",
    )

    run = await service.execute_trigger(trigger.id, "user-1", TriggerType.MANUAL, {"source": "cancel"})
    await asyncio.wait_for(agent_service.started_event.wait(), timeout=2)
    cancelled_run = await service.cancel_run(run.id, "user-1")
    updated_trigger = await trigger_repository.find_trigger_by_id_and_user_id(trigger.id, "user-1")

    assert cancelled_run.status == TriggerRunStatus.CANCELLED
    assert cancelled_run.duration_seconds is not None
    assert run.session_id in agent_service.stopped_sessions
    assert updated_trigger is not None
    assert updated_trigger.execution_count == 1
    assert updated_trigger.cancelled_count == 1


@pytest.mark.asyncio
async def test_failed_run_updates_trigger_failure_counts():
    trigger_repository = InMemoryTriggerRepository()

    class FailingAgentService(FakeAgentService):
        async def chat(self, **kwargs):
            raise RuntimeError("forced failure")
            if False:
                yield None

    service = TriggerService(
        trigger_repository=trigger_repository,
        project_repository=NoopProjectRepository(),
        agent_service=FailingAgentService(),
    )

    trigger = await service.create_trigger(
        user_id="user-1",
        project_id=None,
        name="Failing Trigger",
        prompt="Break",
        trigger_type=TriggerType.MANUAL,
        status=TriggerStatus.ACTIVE,
        schedule_cron=None,
        schedule_timezone="UTC",
    )

    run = await service.execute_trigger(trigger.id, "user-1", TriggerType.MANUAL)
    await asyncio.sleep(0)
    saved_run = await trigger_repository.find_run_by_id(run.id)
    updated_trigger = await trigger_repository.find_trigger_by_id_and_user_id(trigger.id, "user-1")

    assert saved_run is not None
    assert saved_run.status == TriggerRunStatus.FAILED
    assert saved_run.error_message == "forced failure"
    assert updated_trigger is not None
    assert updated_trigger.execution_count == 1
    assert updated_trigger.failure_count == 1
