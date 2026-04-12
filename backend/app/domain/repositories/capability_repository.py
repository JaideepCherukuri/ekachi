from typing import Optional, Protocol, List

from app.domain.models.capability import ProjectMemoryNote, Skill, WorkerProfile


class CapabilityRepository(Protocol):
    async def save_skill(self, skill: Skill) -> None:
        ...

    async def find_skill_by_id_and_user_id(self, skill_id: str, user_id: str) -> Optional[Skill]:
        ...

    async def find_skills_by_user_id(self, user_id: str, project_id: str | None = None) -> List[Skill]:
        ...

    async def delete_skill(self, skill_id: str) -> None:
        ...

    async def get_memory(self, user_id: str, project_id: str | None = None) -> Optional[ProjectMemoryNote]:
        ...

    async def save_memory(self, memory: ProjectMemoryNote) -> None:
        ...

    async def save_worker(self, worker: WorkerProfile) -> None:
        ...

    async def find_worker_by_id_and_user_id(self, worker_id: str, user_id: str) -> Optional[WorkerProfile]:
        ...

    async def find_workers_by_user_id(self, user_id: str, project_id: str | None = None) -> List[WorkerProfile]:
        ...

    async def delete_worker(self, worker_id: str) -> None:
        ...

    async def clear_project_for_user_capabilities(self, user_id: str, project_id: str) -> None:
        ...
