import pytest

from app.application.errors.exceptions import BadRequestError
from app.application.services.capability_service import CapabilityService
from app.domain.models.capability import ProjectMemoryNote, Skill, WorkerProfile
from app.domain.models.project import Project


class InMemoryCapabilityRepository:
    def __init__(self):
        self.skills: dict[str, Skill] = {}
        self.workers: dict[str, WorkerProfile] = {}
        self.memories: dict[tuple[str, str | None], ProjectMemoryNote] = {}

    async def save_skill(self, skill: Skill) -> None:
        self.skills[skill.id] = skill.model_copy(deep=True)

    async def find_skill_by_id_and_user_id(self, skill_id: str, user_id: str):
        skill = self.skills.get(skill_id)
        if not skill or skill.user_id != user_id:
            return None
        return skill.model_copy(deep=True)

    async def find_skills_by_user_id(self, user_id: str, project_id: str | None = None):
        return [
            skill.model_copy(deep=True)
            for skill in self.skills.values()
            if skill.user_id == user_id and skill.project_id == project_id
        ]

    async def delete_skill(self, skill_id: str) -> None:
        self.skills.pop(skill_id, None)

    async def get_memory(self, user_id: str, project_id: str | None = None):
        memory = self.memories.get((user_id, project_id))
        return memory.model_copy(deep=True) if memory else None

    async def save_memory(self, memory: ProjectMemoryNote) -> None:
        self.memories[(memory.user_id, memory.project_id)] = memory.model_copy(deep=True)

    async def save_worker(self, worker: WorkerProfile) -> None:
        self.workers[worker.id] = worker.model_copy(deep=True)

    async def find_worker_by_id_and_user_id(self, worker_id: str, user_id: str):
        worker = self.workers.get(worker_id)
        if not worker or worker.user_id != user_id:
            return None
        return worker.model_copy(deep=True)

    async def find_workers_by_user_id(self, user_id: str, project_id: str | None = None):
        return [
            worker.model_copy(deep=True)
            for worker in self.workers.values()
            if worker.user_id == user_id and worker.project_id == project_id
        ]

    async def delete_worker(self, worker_id: str) -> None:
        self.workers.pop(worker_id, None)

    async def clear_project_for_user_capabilities(self, user_id: str, project_id: str) -> None:
        return None


class InMemoryProjectRepository:
    def __init__(self):
        self.projects: dict[str, Project] = {}

    async def save(self, project: Project) -> None:
        self.projects[project.id] = project.model_copy(deep=True)

    async def find_by_id_and_user_id(self, project_id: str, user_id: str):
        project = self.projects.get(project_id)
        if not project or project.user_id != user_id:
            return None
        return project.model_copy(deep=True)


@pytest.mark.asyncio
async def test_create_worker_normalizes_tools_and_project_scope():
    capability_repository = InMemoryCapabilityRepository()
    project_repository = InMemoryProjectRepository()
    project = Project(user_id="user-1", name="Research", color="#111111")
    await project_repository.save(project)
    service = CapabilityService(capability_repository, project_repository)

    worker = await service.create_worker(
        user_id="user-1",
        project_id=project.id,
        name=" Research Worker ",
        description=" Evidence owner ",
        role="research",
        lane="research",
        instructions=" Prefer primary sources ",
        tool_names=["search", "browser", "search"],
        enabled=True,
    )

    assert worker.project_id == project.id
    assert worker.name == "Research Worker"
    assert worker.description == "Evidence owner"
    assert worker.tool_names == ["search", "browser"]


@pytest.mark.asyncio
async def test_build_runtime_context_includes_enabled_workers_memory_and_skills():
    capability_repository = InMemoryCapabilityRepository()
    project_repository = InMemoryProjectRepository()
    service = CapabilityService(capability_repository, project_repository)

    await capability_repository.save_memory(ProjectMemoryNote(user_id="user-1", project_id=None, content="Mission context"))
    await capability_repository.save_worker(
        WorkerProfile(
            user_id="user-1",
            project_id=None,
            name="Browser Specialist",
            role="browser",
            lane="execution",
            instructions="Own browsing tasks",
            tool_names=["browser"],
            enabled=True,
        )
    )
    await capability_repository.save_skill(
        Skill(
            user_id="user-1",
            project_id=None,
            name="Concise Style",
            instructions="Prefer concise output",
            enabled=True,
        )
    )

    runtime_context = await service.build_runtime_context("user-1", None)

    assert "Project memory" in runtime_context
    assert "Enabled workers" in runtime_context
    assert "Browser Specialist [browser / execution]" in runtime_context
    assert "Enabled skills" in runtime_context


@pytest.mark.asyncio
async def test_list_skills_includes_example_library_entries():
    capability_repository = InMemoryCapabilityRepository()
    project_repository = InMemoryProjectRepository()
    service = CapabilityService(capability_repository, project_repository)

    await capability_repository.save_skill(
        Skill(
            user_id="user-1",
            project_id=None,
            name="Team Style",
            instructions="Prefer concise language",
            enabled=True,
        )
    )

    skills = await service.list_skills("user-1", None)

    assert any(skill.source == "user" and skill.name == "Team Style" for skill in skills)
    assert any(skill.source == "example" and skill.template_key == "evidence-bundle" for skill in skills)


@pytest.mark.asyncio
async def test_create_worker_rejects_blank_name_or_instructions():
    capability_repository = InMemoryCapabilityRepository()
    project_repository = InMemoryProjectRepository()
    service = CapabilityService(capability_repository, project_repository)

    with pytest.raises(BadRequestError):
        await service.create_worker(
            user_id="user-1",
            project_id=None,
            name="",
            description=None,
            role="custom",
            lane="execution",
            instructions="   ",
            tool_names=[],
            enabled=True,
        )
