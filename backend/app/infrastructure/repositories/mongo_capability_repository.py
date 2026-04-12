from typing import List, Optional

from app.domain.models.capability import ProjectMemoryNote, Skill, WorkerProfile
from app.domain.repositories.capability_repository import CapabilityRepository
from app.infrastructure.models.documents import MemoryNoteDocument, SkillDocument, WorkerDocument


class MongoCapabilityRepository(CapabilityRepository):
    async def save_skill(self, skill: Skill) -> None:
        mongo_skill = await SkillDocument.find_one(SkillDocument.skill_id == skill.id)
        if not mongo_skill:
            mongo_skill = SkillDocument.from_domain(skill)
            await mongo_skill.save()
            return
        mongo_skill.update_from_domain(skill)
        await mongo_skill.save()

    async def find_skill_by_id_and_user_id(self, skill_id: str, user_id: str) -> Optional[Skill]:
        mongo_skill = await SkillDocument.find_one(
            SkillDocument.skill_id == skill_id,
            SkillDocument.user_id == user_id,
        )
        return mongo_skill.to_domain() if mongo_skill else None

    async def find_skills_by_user_id(self, user_id: str, project_id: str | None = None) -> List[Skill]:
        filters = [SkillDocument.user_id == user_id]
        if project_id is None:
            filters.append(SkillDocument.project_id == None)  # noqa: E711
        else:
            filters.append(SkillDocument.project_id == project_id)
        mongo_skills = await SkillDocument.find(*filters).sort("-updated_at").to_list()
        return [mongo_skill.to_domain() for mongo_skill in mongo_skills]

    async def delete_skill(self, skill_id: str) -> None:
        mongo_skill = await SkillDocument.find_one(SkillDocument.skill_id == skill_id)
        if mongo_skill:
            await mongo_skill.delete()

    async def get_memory(self, user_id: str, project_id: str | None = None) -> Optional[ProjectMemoryNote]:
        filters = [MemoryNoteDocument.user_id == user_id]
        if project_id is None:
            filters.append(MemoryNoteDocument.project_id == None)  # noqa: E711
        else:
            filters.append(MemoryNoteDocument.project_id == project_id)
        mongo_memory = await MemoryNoteDocument.find_one(*filters)
        return mongo_memory.to_domain() if mongo_memory else None

    async def save_memory(self, memory: ProjectMemoryNote) -> None:
        mongo_memory = await MemoryNoteDocument.find_one(MemoryNoteDocument.memory_note_id == memory.id)
        if not mongo_memory:
            mongo_memory = MemoryNoteDocument.from_domain(memory)
            await mongo_memory.save()
            return
        mongo_memory.update_from_domain(memory)
        await mongo_memory.save()

    async def save_worker(self, worker: WorkerProfile) -> None:
        mongo_worker = await WorkerDocument.find_one(WorkerDocument.worker_id == worker.id)
        if not mongo_worker:
            mongo_worker = WorkerDocument.from_domain(worker)
            await mongo_worker.save()
            return
        mongo_worker.update_from_domain(worker)
        await mongo_worker.save()

    async def find_worker_by_id_and_user_id(self, worker_id: str, user_id: str) -> Optional[WorkerProfile]:
        mongo_worker = await WorkerDocument.find_one(
            WorkerDocument.worker_id == worker_id,
            WorkerDocument.user_id == user_id,
        )
        return mongo_worker.to_domain() if mongo_worker else None

    async def find_workers_by_user_id(self, user_id: str, project_id: str | None = None) -> List[WorkerProfile]:
        filters = [WorkerDocument.user_id == user_id]
        if project_id is None:
            filters.append(WorkerDocument.project_id == None)  # noqa: E711
        else:
            filters.append(WorkerDocument.project_id == project_id)
        mongo_workers = await WorkerDocument.find(*filters).sort("lane", "-updated_at").to_list()
        return [mongo_worker.to_domain() for mongo_worker in mongo_workers]

    async def delete_worker(self, worker_id: str) -> None:
        mongo_worker = await WorkerDocument.find_one(WorkerDocument.worker_id == worker_id)
        if mongo_worker:
            await mongo_worker.delete()

    async def clear_project_for_user_capabilities(self, user_id: str, project_id: str) -> None:
        await SkillDocument.get_pymongo_collection().update_many(
            {"user_id": user_id, "project_id": project_id},
            {"$set": {"project_id": None}},
        )
        await WorkerDocument.get_pymongo_collection().update_many(
            {"user_id": user_id, "project_id": project_id},
            {"$set": {"project_id": None}},
        )
        await MemoryNoteDocument.get_pymongo_collection().update_many(
            {"user_id": user_id, "project_id": project_id},
            {"$set": {"project_id": None}},
        )
