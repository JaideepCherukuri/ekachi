from datetime import datetime
from typing import List, Optional

from app.domain.models.trigger import Trigger, TriggerRun, TriggerStatus, TriggerType
from app.domain.repositories.trigger_repository import TriggerRepository
from app.infrastructure.models.documents import TriggerDocument, TriggerRunDocument


class MongoTriggerRepository(TriggerRepository):
    async def save_trigger(self, trigger: Trigger) -> None:
        mongo_trigger = await TriggerDocument.find_one(TriggerDocument.trigger_id == trigger.id)
        if not mongo_trigger:
            mongo_trigger = TriggerDocument.from_domain(trigger)
            await mongo_trigger.save()
            return

        mongo_trigger.update_from_domain(trigger)
        await mongo_trigger.save()

    async def find_trigger_by_id(self, trigger_id: str) -> Optional[Trigger]:
        mongo_trigger = await TriggerDocument.find_one(TriggerDocument.trigger_id == trigger_id)
        return mongo_trigger.to_domain() if mongo_trigger else None

    async def find_trigger_by_id_and_user_id(self, trigger_id: str, user_id: str) -> Optional[Trigger]:
        mongo_trigger = await TriggerDocument.find_one(
            TriggerDocument.trigger_id == trigger_id,
            TriggerDocument.user_id == user_id,
        )
        return mongo_trigger.to_domain() if mongo_trigger else None

    async def find_trigger_by_webhook(self, trigger_id: str, webhook_secret: str) -> Optional[Trigger]:
        mongo_trigger = await TriggerDocument.find_one(
            TriggerDocument.trigger_id == trigger_id,
            TriggerDocument.webhook_secret == webhook_secret,
            TriggerDocument.trigger_type == TriggerType.WEBHOOK,
            TriggerDocument.status == TriggerStatus.ACTIVE,
        )
        return mongo_trigger.to_domain() if mongo_trigger else None

    async def find_triggers_by_user_id(self, user_id: str, project_id: str | None = None) -> List[Trigger]:
        filters = [TriggerDocument.user_id == user_id]
        if project_id is None:
            filters.append(TriggerDocument.project_id == None)  # noqa: E711
        else:
            filters.append(TriggerDocument.project_id == project_id)

        mongo_triggers = await TriggerDocument.find(*filters).sort("-updated_at").to_list()
        return [mongo_trigger.to_domain() for mongo_trigger in mongo_triggers]

    async def find_due_schedule_triggers(self, now: datetime, limit: int = 25) -> List[Trigger]:
        mongo_triggers = await TriggerDocument.find(
            TriggerDocument.trigger_type == TriggerType.SCHEDULE,
            TriggerDocument.status == TriggerStatus.ACTIVE,
            TriggerDocument.next_run_at <= now,
        ).sort("next_run_at").limit(limit).to_list()
        return [mongo_trigger.to_domain() for mongo_trigger in mongo_triggers]

    async def delete_trigger(self, trigger_id: str) -> None:
        mongo_trigger = await TriggerDocument.find_one(TriggerDocument.trigger_id == trigger_id)
        if mongo_trigger:
            await mongo_trigger.delete()
        await TriggerRunDocument.find(TriggerRunDocument.trigger_id == trigger_id).delete()

    async def clear_project_for_user_triggers(self, user_id: str, project_id: str) -> None:
        collection = TriggerDocument.get_pymongo_collection()
        await collection.update_many(
            {"user_id": user_id, "project_id": project_id},
            {"$set": {"project_id": None}},
        )

    async def save_run(self, run: TriggerRun) -> None:
        mongo_run = await TriggerRunDocument.find_one(TriggerRunDocument.trigger_run_id == run.id)
        if not mongo_run:
            mongo_run = TriggerRunDocument.from_domain(run)
            await mongo_run.save()
            return

        mongo_run.update_from_domain(run)
        await mongo_run.save()

    async def find_run_by_id(self, run_id: str) -> Optional[TriggerRun]:
        mongo_run = await TriggerRunDocument.find_one(TriggerRunDocument.trigger_run_id == run_id)
        return mongo_run.to_domain() if mongo_run else None

    async def find_runs_by_user_id(
        self,
        user_id: str,
        project_id: str | None = None,
        trigger_id: str | None = None,
        limit: int = 50,
    ) -> List[TriggerRun]:
        filters = [TriggerRunDocument.user_id == user_id]
        if project_id is None:
            filters.append(TriggerRunDocument.project_id == None)  # noqa: E711
        else:
            filters.append(TriggerRunDocument.project_id == project_id)
        if trigger_id:
            filters.append(TriggerRunDocument.trigger_id == trigger_id)

        mongo_runs = await TriggerRunDocument.find(*filters).sort("-started_at").limit(limit).to_list()
        return [mongo_run.to_domain() for mongo_run in mongo_runs]

    async def clear_project_for_user_runs(self, user_id: str, project_id: str) -> None:
        collection = TriggerRunDocument.get_pymongo_collection()
        await collection.update_many(
            {"user_id": user_id, "project_id": project_id},
            {"$set": {"project_id": None}},
        )
