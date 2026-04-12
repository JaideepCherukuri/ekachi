from typing import Optional, Protocol, List

from app.domain.models.project import Project


class ProjectRepository(Protocol):
    async def save(self, project: Project) -> None:
        ...

    async def find_by_id(self, project_id: str) -> Optional[Project]:
        ...

    async def find_by_id_and_user_id(self, project_id: str, user_id: str) -> Optional[Project]:
        ...

    async def find_by_user_id(self, user_id: str) -> List[Project]:
        ...

    async def delete(self, project_id: str) -> None:
        ...
