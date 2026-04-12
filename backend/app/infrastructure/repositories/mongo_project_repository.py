from typing import List, Optional

from app.domain.models.project import Project
from app.domain.repositories.project_repository import ProjectRepository
from app.infrastructure.models.documents import ProjectDocument


class MongoProjectRepository(ProjectRepository):
    async def save(self, project: Project) -> None:
        mongo_project = await ProjectDocument.find_one(ProjectDocument.project_id == project.id)

        if not mongo_project:
            mongo_project = ProjectDocument.from_domain(project)
            await mongo_project.save()
            return

        mongo_project.update_from_domain(project)
        await mongo_project.save()

    async def find_by_id(self, project_id: str) -> Optional[Project]:
        mongo_project = await ProjectDocument.find_one(ProjectDocument.project_id == project_id)
        return mongo_project.to_domain() if mongo_project else None

    async def find_by_id_and_user_id(self, project_id: str, user_id: str) -> Optional[Project]:
        mongo_project = await ProjectDocument.find_one(
            ProjectDocument.project_id == project_id,
            ProjectDocument.user_id == user_id,
        )
        return mongo_project.to_domain() if mongo_project else None

    async def find_by_user_id(self, user_id: str) -> List[Project]:
        mongo_projects = await ProjectDocument.find(
            ProjectDocument.user_id == user_id
        ).sort("-updated_at").to_list()
        return [mongo_project.to_domain() for mongo_project in mongo_projects]

    async def delete(self, project_id: str) -> None:
        mongo_project = await ProjectDocument.find_one(ProjectDocument.project_id == project_id)
        if mongo_project:
            await mongo_project.delete()
