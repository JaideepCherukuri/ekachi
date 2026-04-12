from datetime import datetime
from typing import Optional, Protocol, List

from app.domain.models.trigger import Trigger, TriggerRun


class TriggerRepository(Protocol):
    async def save_trigger(self, trigger: Trigger) -> None:
        ...

    async def find_trigger_by_id(self, trigger_id: str) -> Optional[Trigger]:
        ...

    async def find_trigger_by_id_and_user_id(self, trigger_id: str, user_id: str) -> Optional[Trigger]:
        ...

    async def find_trigger_by_webhook(self, trigger_id: str, webhook_secret: str) -> Optional[Trigger]:
        ...

    async def find_triggers_by_user_id(self, user_id: str, project_id: str | None = None) -> List[Trigger]:
        ...

    async def find_due_schedule_triggers(self, now: datetime, limit: int = 25) -> List[Trigger]:
        ...

    async def delete_trigger(self, trigger_id: str) -> None:
        ...

    async def clear_project_for_user_triggers(self, user_id: str, project_id: str) -> None:
        ...

    async def save_run(self, run: TriggerRun) -> None:
        ...

    async def find_run_by_id(self, run_id: str) -> Optional[TriggerRun]:
        ...

    async def find_runs_by_user_id(
        self,
        user_id: str,
        project_id: str | None = None,
        trigger_id: str | None = None,
        limit: int = 50,
    ) -> List[TriggerRun]:
        ...

    async def clear_project_for_user_runs(self, user_id: str, project_id: str) -> None:
        ...
