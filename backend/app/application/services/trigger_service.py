import asyncio
from datetime import UTC, datetime, timedelta
import json
import logging
import secrets
from typing import Any, Optional, List

from app.application.errors.exceptions import BadRequestError, NotFoundError
from app.application.services.agent_service import AgentService
from app.domain.models.project import Project
from app.domain.models.trigger import Trigger, TriggerRun, TriggerRunStatus, TriggerStatus, TriggerType
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.trigger_repository import TriggerRepository


logger = logging.getLogger(__name__)

SCHEDULER_POLL_INTERVAL_SECONDS = 30


class TriggerService:
    def __init__(
        self,
        trigger_repository: TriggerRepository,
        project_repository: ProjectRepository,
        agent_service: AgentService,
    ):
        self._trigger_repository = trigger_repository
        self._project_repository = project_repository
        self._agent_service = agent_service
        self._scheduler_task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()
        self._run_tasks: dict[str, asyncio.Task[None]] = {}

    async def start(self) -> None:
        if self._scheduler_task and not self._scheduler_task.done():
            return
        self._stop_event.clear()
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())

    async def shutdown(self) -> None:
        self._stop_event.set()
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
            self._scheduler_task = None

    async def list_triggers(self, user_id: str, project_id: str | None) -> List[Trigger]:
        return await self._trigger_repository.find_triggers_by_user_id(user_id, project_id)

    async def list_runs(
        self,
        user_id: str,
        project_id: str | None,
        trigger_id: str | None = None,
        limit: int = 50,
    ) -> List[TriggerRun]:
        return await self._trigger_repository.find_runs_by_user_id(user_id, project_id, trigger_id, limit)

    async def get_run(self, run_id: str, user_id: str) -> TriggerRun:
        run = await self._trigger_repository.find_run_by_id(run_id)
        if not run or run.user_id != user_id:
            raise NotFoundError("Trigger run not found")
        return run

    async def create_trigger(
        self,
        user_id: str,
        project_id: str | None,
        name: str,
        prompt: str,
        trigger_type: TriggerType,
        status: TriggerStatus,
        schedule_cron: str | None,
        schedule_timezone: str,
    ) -> Trigger:
        project = await self._resolve_project(user_id, project_id)
        trigger = Trigger(
            user_id=user_id,
            project_id=project.id if project else None,
            name=name.strip(),
            prompt=prompt.strip(),
            trigger_type=trigger_type,
            status=status,
            webhook_secret=secrets.token_urlsafe(24) if trigger_type == TriggerType.WEBHOOK else None,
            schedule_cron=schedule_cron.strip() if schedule_cron else None,
            schedule_timezone=schedule_timezone or "UTC",
        )
        self._validate_trigger(trigger)
        if trigger.trigger_type == TriggerType.SCHEDULE and trigger.status == TriggerStatus.ACTIVE:
            trigger.next_run_at = self._calculate_next_run_at(trigger)
        await self._trigger_repository.save_trigger(trigger)
        return trigger

    async def update_trigger(
        self,
        trigger_id: str,
        user_id: str,
        project_id: str | None | object,
        name: Optional[str],
        prompt: Optional[str],
        status: Optional[TriggerStatus],
        schedule_cron: Optional[str],
        schedule_timezone: Optional[str],
    ) -> Trigger:
        trigger = await self._trigger_repository.find_trigger_by_id_and_user_id(trigger_id, user_id)
        if not trigger:
            raise NotFoundError("Trigger not found")

        if project_id is not _UNSET:
            project = await self._resolve_project(user_id, project_id if isinstance(project_id, str) else None)
            trigger.project_id = project.id if project else None
        if name is not None:
            trigger.name = name.strip()
        if prompt is not None:
            trigger.prompt = prompt.strip()
        if status is not None:
            trigger.status = status
        if schedule_cron is not None:
            trigger.schedule_cron = schedule_cron.strip() or None
        if schedule_timezone is not None:
            trigger.schedule_timezone = schedule_timezone
        trigger.updated_at = datetime.now(UTC)
        self._validate_trigger(trigger)
        if trigger.trigger_type == TriggerType.SCHEDULE and trigger.status == TriggerStatus.ACTIVE:
            trigger.next_run_at = self._calculate_next_run_at(trigger)
        elif trigger.trigger_type != TriggerType.SCHEDULE:
            trigger.next_run_at = None
        await self._trigger_repository.save_trigger(trigger)
        return trigger

    async def delete_trigger(self, trigger_id: str, user_id: str) -> None:
        trigger = await self._trigger_repository.find_trigger_by_id_and_user_id(trigger_id, user_id)
        if not trigger:
            raise NotFoundError("Trigger not found")
        await self._trigger_repository.delete_trigger(trigger_id)

    async def execute_trigger(
        self,
        trigger_id: str,
        user_id: str,
        source: TriggerType,
        input_payload: Optional[dict[str, Any]] = None,
    ) -> TriggerRun:
        trigger = await self._trigger_repository.find_trigger_by_id_and_user_id(trigger_id, user_id)
        if not trigger:
            raise NotFoundError("Trigger not found")
        return await self._dispatch_trigger(trigger, source=source, input_payload=input_payload)

    async def execute_webhook_trigger(
        self,
        trigger_id: str,
        webhook_secret: str,
        input_payload: Optional[dict[str, Any]] = None,
    ) -> TriggerRun:
        trigger = await self._trigger_repository.find_trigger_by_webhook(trigger_id, webhook_secret)
        if not trigger:
            raise NotFoundError("Trigger not found")
        return await self._dispatch_trigger(trigger, source=TriggerType.WEBHOOK, input_payload=input_payload)

    async def retry_run(self, run_id: str, user_id: str) -> TriggerRun:
        run = await self.get_run(run_id, user_id)
        trigger = await self._trigger_repository.find_trigger_by_id_and_user_id(run.trigger_id, user_id)
        if not trigger:
            raise NotFoundError("Trigger not found")
        return await self._dispatch_trigger(
            trigger,
            source=TriggerType.MANUAL,
            input_payload=run.input_payload,
            attempt_number=run.attempt_number + 1,
        )

    async def cancel_run(self, run_id: str, user_id: str) -> TriggerRun:
        run = await self.get_run(run_id, user_id)
        if run.status != TriggerRunStatus.RUNNING:
            raise BadRequestError("Only running trigger executions can be cancelled")

        if run.session_id:
            try:
                await self._agent_service.stop_session(run.session_id, user_id)
            except Exception:
                logger.exception("Failed to stop session for cancelled trigger run", extra={"run_id": run.id})

        task = self._run_tasks.get(run.id)
        if task:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
            refreshed = await self._trigger_repository.find_run_by_id(run.id)
            if refreshed:
                return refreshed

        trigger = await self._trigger_repository.find_trigger_by_id_and_user_id(run.trigger_id, user_id)
        now = datetime.now(UTC)
        run.status = TriggerRunStatus.CANCELLED
        run.completed_at = now
        run.updated_at = now
        run.duration_seconds = max((now - run.started_at).total_seconds(), 0.0)
        await self._trigger_repository.save_run(run)
        if trigger:
            trigger.execution_count += 1
            trigger.cancelled_count += 1
            trigger.last_run_at = now
            trigger.last_run_status = TriggerRunStatus.CANCELLED
            trigger.updated_at = now
            await self._trigger_repository.save_trigger(trigger)
        return run

    async def clear_project_references(self, user_id: str, project_id: str) -> None:
        await self._trigger_repository.clear_project_for_user_triggers(user_id, project_id)
        await self._trigger_repository.clear_project_for_user_runs(user_id, project_id)

    async def _dispatch_trigger(
        self,
        trigger: Trigger,
        source: TriggerType,
        input_payload: Optional[dict[str, Any]] = None,
        attempt_number: int = 1,
    ) -> TriggerRun:
        if trigger.status != TriggerStatus.ACTIVE and source != TriggerType.MANUAL:
            raise BadRequestError("Trigger is not active")

        project = await self._resolve_project(trigger.user_id, trigger.project_id)
        session = await self._agent_service.create_session(
            user_id=trigger.user_id,
            project_id=project.id if project else None,
            project_name=project.name if project else None,
            project_color=project.color if project else None,
        )

        now = datetime.now(UTC)
        run = TriggerRun(
            trigger_id=trigger.id,
            user_id=trigger.user_id,
            project_id=trigger.project_id,
            session_id=session.id,
            trigger_type=trigger.trigger_type,
            status=TriggerRunStatus.RUNNING,
            source=source,
            input_payload=input_payload,
            attempt_number=attempt_number,
            started_at=now,
            created_at=now,
            updated_at=now,
        )
        await self._trigger_repository.save_run(run)

        trigger.last_run_at = now
        trigger.last_run_status = TriggerRunStatus.RUNNING
        trigger.updated_at = now
        if trigger.trigger_type == TriggerType.SCHEDULE:
          trigger.next_run_at = self._calculate_next_run_at(trigger, base_time=now)
        await self._trigger_repository.save_trigger(trigger)

        task = asyncio.create_task(self._execute_trigger_run(trigger, run))
        self._run_tasks[run.id] = task
        return run

    async def _execute_trigger_run(self, trigger: Trigger, run: TriggerRun) -> None:
        try:
            message = self._build_trigger_message(trigger, run.input_payload)
            async for _ in self._agent_service.chat(
                session_id=run.session_id or "",
                user_id=trigger.user_id,
                message=message,
                timestamp=datetime.now(UTC),
            ):
                pass
            run.status = TriggerRunStatus.COMPLETED
            run.output_summary = "Trigger execution completed"
            run.completed_at = datetime.now(UTC)
            run.updated_at = run.completed_at
            run.duration_seconds = max((run.completed_at - run.started_at).total_seconds(), 0.0)
            trigger.last_run_status = TriggerRunStatus.COMPLETED
            if trigger.trigger_type == TriggerType.SCHEDULE and trigger.status == TriggerStatus.ACTIVE:
                trigger.next_run_at = self._calculate_next_run_at(trigger, base_time=run.completed_at)
        except asyncio.CancelledError:
            run.status = TriggerRunStatus.CANCELLED
            run.completed_at = datetime.now(UTC)
            run.updated_at = run.completed_at
            run.duration_seconds = max((run.completed_at - run.started_at).total_seconds(), 0.0)
            trigger.last_run_status = TriggerRunStatus.CANCELLED
            raise
        except Exception as error:
            logger.exception("Trigger execution failed", extra={"trigger_id": trigger.id, "run_id": run.id})
            run.status = TriggerRunStatus.FAILED
            run.error_message = str(error)
            run.completed_at = datetime.now(UTC)
            run.updated_at = run.completed_at
            run.duration_seconds = max((run.completed_at - run.started_at).total_seconds(), 0.0)
            trigger.last_run_status = TriggerRunStatus.FAILED
        finally:
            terminal_time = run.completed_at or datetime.now(UTC)
            trigger.last_run_at = terminal_time
            trigger.updated_at = terminal_time
            if run.status == TriggerRunStatus.COMPLETED:
                trigger.execution_count += 1
                trigger.success_count += 1
            elif run.status == TriggerRunStatus.FAILED:
                trigger.execution_count += 1
                trigger.failure_count += 1
            elif run.status == TriggerRunStatus.CANCELLED:
                trigger.execution_count += 1
                trigger.cancelled_count += 1
            await self._trigger_repository.save_run(run)
            await self._trigger_repository.save_trigger(trigger)
            self._run_tasks.pop(run.id, None)

    async def _scheduler_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                now = datetime.now(UTC)
                due_triggers = await self._trigger_repository.find_due_schedule_triggers(now)
                for trigger in due_triggers:
                    try:
                        await self._dispatch_trigger(trigger, TriggerType.SCHEDULE, {"scheduled_at": now.isoformat()})
                    except Exception:
                        logger.exception("Failed to dispatch scheduled trigger", extra={"trigger_id": trigger.id})
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Trigger scheduler poll failed")

            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=SCHEDULER_POLL_INTERVAL_SECONDS)
            except asyncio.TimeoutError:
                continue

    async def _resolve_project(self, user_id: str, project_id: str | None) -> Optional[Project]:
        if not project_id:
            return None
        project = await self._project_repository.find_by_id_and_user_id(project_id, user_id)
        if not project:
            raise NotFoundError("Project not found")
        return project

    def _validate_trigger(self, trigger: Trigger) -> None:
        if not trigger.name.strip():
            raise BadRequestError("Trigger name is required")
        if not trigger.prompt.strip():
            raise BadRequestError("Trigger prompt is required")
        if trigger.trigger_type == TriggerType.SCHEDULE:
            if not trigger.schedule_cron:
                raise BadRequestError("Scheduled triggers require a cron expression")
            self._calculate_next_run_at(trigger)
        else:
            trigger.schedule_cron = None
            trigger.schedule_timezone = "UTC"

    def _calculate_next_run_at(self, trigger: Trigger, base_time: Optional[datetime] = None) -> datetime:
        if not trigger.schedule_cron:
            raise BadRequestError("Scheduled triggers require a cron expression")

        base = (base_time or datetime.now(UTC)).replace(second=0, microsecond=0)
        fields = trigger.schedule_cron.split()
        if len(fields) != 5:
            raise BadRequestError("Cron expression must have 5 fields")

        minute_field, hour_field, day_field, month_field, weekday_field = fields

        for offset in range(1, 366 * 24 * 60):
            candidate = base + timedelta(minutes=offset)
            if (
                self._matches_field(candidate.minute, minute_field, 0, 59)
                and self._matches_field(candidate.hour, hour_field, 0, 23)
                and self._matches_field(candidate.day, day_field, 1, 31)
                and self._matches_field(candidate.month, month_field, 1, 12)
                and self._matches_field(candidate.weekday(), self._normalize_weekday_field(weekday_field), 0, 6)
            ):
                return candidate
        raise BadRequestError("Unable to calculate next run time from cron expression")

    def _normalize_weekday_field(self, field: str) -> str:
        return field.replace("7", "0")

    def _matches_field(self, value: int, field: str, minimum: int, maximum: int) -> bool:
        if field == "*":
            return True

        for part in field.split(","):
            if "/" in part:
                raw_base, raw_step = part.split("/", 1)
                step = int(raw_step)
                if raw_base == "*":
                    if (value - minimum) % step == 0:
                        return True
                    continue
                if "-" in raw_base:
                    start, end = [int(item) for item in raw_base.split("-", 1)]
                else:
                    start, end = int(raw_base), maximum
                if start <= value <= end and (value - start) % step == 0:
                    return True
                continue

            if "-" in part:
                start, end = [int(item) for item in part.split("-", 1)]
                if start <= value <= end:
                    return True
                continue

            if int(part) == value:
                return True

        return False

    def _build_trigger_message(self, trigger: Trigger, input_payload: Optional[dict[str, Any]]) -> str:
        if not input_payload:
            return trigger.prompt
        payload_json = json.dumps(input_payload, indent=2, sort_keys=True)
        return f"{trigger.prompt}\n\nTrigger context:\n```json\n{payload_json}\n```"


class _Unset:
    pass


_UNSET = _Unset()
