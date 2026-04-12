from datetime import UTC, datetime
from typing import List, Optional

from app.application.errors.exceptions import BadRequestError, NotFoundError
from app.domain.models.capability import ProjectMemoryNote, Skill, WorkerLane, WorkerProfile, WorkerRole
from app.domain.models.project import Project
from app.domain.repositories.capability_repository import CapabilityRepository
from app.domain.repositories.project_repository import ProjectRepository


class CapabilityService:
    def __init__(
        self,
        capability_repository: CapabilityRepository,
        project_repository: ProjectRepository,
    ):
        self._capability_repository = capability_repository
        self._project_repository = project_repository

    async def list_skills(self, user_id: str, project_id: str | None) -> List[Skill]:
        user_skills = await self._capability_repository.find_skills_by_user_id(user_id, project_id)
        return [
            *sorted(user_skills, key=lambda skill: skill.updated_at, reverse=True),
            *self._example_skills(user_id, project_id),
        ]

    async def list_workers(self, user_id: str, project_id: str | None) -> List[WorkerProfile]:
        return await self._capability_repository.find_workers_by_user_id(user_id, project_id)

    async def create_skill(
        self,
        user_id: str,
        project_id: str | None,
        name: str,
        description: Optional[str],
        instructions: str,
        enabled: bool,
    ) -> Skill:
        project = await self._resolve_project(user_id, project_id)
        trimmed_name = name.strip()
        trimmed_instructions = instructions.strip()
        if not trimmed_name or not trimmed_instructions:
            raise BadRequestError("Skill name and instructions are required")
        skill = Skill(
            user_id=user_id,
            project_id=project.id if project else None,
            name=trimmed_name,
            description=description.strip() if description else None,
            instructions=trimmed_instructions,
            enabled=enabled,
        )
        await self._capability_repository.save_skill(skill)
        return skill

    async def update_skill(
        self,
        skill_id: str,
        user_id: str,
        project_id: str | None | object,
        name: Optional[str],
        description: Optional[str],
        instructions: Optional[str],
        enabled: Optional[bool],
    ) -> Skill:
        skill = await self._capability_repository.find_skill_by_id_and_user_id(skill_id, user_id)
        if not skill:
            raise NotFoundError("Skill not found")
        if project_id is not _UNSET:
            project = await self._resolve_project(user_id, project_id if isinstance(project_id, str) else None)
            skill.project_id = project.id if project else None
        if name is not None:
            trimmed_name = name.strip()
            if not trimmed_name:
                raise BadRequestError("Skill name is required")
            skill.name = trimmed_name
        if description is not None:
            skill.description = description.strip() or None
        if instructions is not None:
            trimmed_instructions = instructions.strip()
            if not trimmed_instructions:
                raise BadRequestError("Skill instructions are required")
            skill.instructions = trimmed_instructions
        if enabled is not None:
            skill.enabled = enabled
        skill.updated_at = datetime.now(UTC)
        await self._capability_repository.save_skill(skill)
        return skill

    async def delete_skill(self, skill_id: str, user_id: str) -> None:
        skill = await self._capability_repository.find_skill_by_id_and_user_id(skill_id, user_id)
        if not skill:
            raise NotFoundError("Skill not found")
        await self._capability_repository.delete_skill(skill_id)

    async def create_worker(
        self,
        user_id: str,
        project_id: str | None,
        name: str,
        description: Optional[str],
        role: WorkerRole,
        lane: WorkerLane,
        instructions: str,
        tool_names: list[str],
        enabled: bool,
    ) -> WorkerProfile:
        project = await self._resolve_project(user_id, project_id)
        trimmed_name = name.strip()
        trimmed_instructions = instructions.strip()
        normalized_tools = self._normalize_tool_names(tool_names)
        if not trimmed_name or not trimmed_instructions:
            raise BadRequestError("Worker name and instructions are required")
        worker = WorkerProfile(
            user_id=user_id,
            project_id=project.id if project else None,
            name=trimmed_name,
            description=description.strip() if description else None,
            role=role,
            lane=lane,
            instructions=trimmed_instructions,
            tool_names=normalized_tools,
            enabled=enabled,
        )
        await self._capability_repository.save_worker(worker)
        return worker

    async def update_worker(
        self,
        worker_id: str,
        user_id: str,
        project_id: str | None | object,
        name: Optional[str],
        description: Optional[str],
        role: Optional[WorkerRole],
        lane: Optional[WorkerLane],
        instructions: Optional[str],
        tool_names: Optional[list[str]],
        enabled: Optional[bool],
    ) -> WorkerProfile:
        worker = await self._capability_repository.find_worker_by_id_and_user_id(worker_id, user_id)
        if not worker:
            raise NotFoundError("Worker not found")
        if project_id is not _UNSET:
            project = await self._resolve_project(user_id, project_id if isinstance(project_id, str) else None)
            worker.project_id = project.id if project else None
        if name is not None:
            trimmed_name = name.strip()
            if not trimmed_name:
                raise BadRequestError("Worker name is required")
            worker.name = trimmed_name
        if description is not None:
            worker.description = description.strip() or None
        if role is not None:
            worker.role = role
        if lane is not None:
            worker.lane = lane
        if instructions is not None:
            trimmed_instructions = instructions.strip()
            if not trimmed_instructions:
                raise BadRequestError("Worker instructions are required")
            worker.instructions = trimmed_instructions
        if tool_names is not None:
            worker.tool_names = self._normalize_tool_names(tool_names)
        if enabled is not None:
            worker.enabled = enabled
        worker.updated_at = datetime.now(UTC)
        await self._capability_repository.save_worker(worker)
        return worker

    async def delete_worker(self, worker_id: str, user_id: str) -> None:
        worker = await self._capability_repository.find_worker_by_id_and_user_id(worker_id, user_id)
        if not worker:
            raise NotFoundError("Worker not found")
        await self._capability_repository.delete_worker(worker_id)

    async def get_memory(self, user_id: str, project_id: str | None) -> Optional[ProjectMemoryNote]:
        return await self._capability_repository.get_memory(user_id, project_id)

    async def update_memory(self, user_id: str, project_id: str | None, content: str) -> ProjectMemoryNote:
        project = await self._resolve_project(user_id, project_id)
        memory = await self._capability_repository.get_memory(user_id, project.id if project else None)
        if memory:
            memory.content = content
            memory.updated_at = datetime.now(UTC)
        else:
            memory = ProjectMemoryNote(
                user_id=user_id,
                project_id=project.id if project else None,
                content=content,
            )
        await self._capability_repository.save_memory(memory)
        return memory

    async def build_runtime_context(self, user_id: str, project_id: str | None) -> str:
        memory = await self._capability_repository.get_memory(user_id, project_id)
        skills = await self._capability_repository.find_skills_by_user_id(user_id, project_id)
        workers = await self._capability_repository.find_workers_by_user_id(user_id, project_id)
        enabled_skills = [skill for skill in skills if skill.enabled]
        enabled_workers = [worker for worker in workers if worker.enabled]

        sections: list[str] = []
        if memory and memory.content.strip():
            sections.append(f"Project memory:\n{memory.content.strip()}")
        if enabled_workers:
            worker_lines = [
                f"- {worker.name} [{worker.role} / {worker.lane}] tools={', '.join(worker.tool_names) or 'none'}: {worker.instructions.strip()}"
                for worker in enabled_workers
            ]
            sections.append("Enabled workers:\n" + "\n".join(worker_lines))
        if enabled_skills:
            skill_lines = [
                f"- {skill.name}: {skill.instructions.strip()}"
                for skill in enabled_skills
            ]
            sections.append("Enabled skills:\n" + "\n".join(skill_lines))
        return "\n\n".join(sections)

    async def clear_project_references(self, user_id: str, project_id: str) -> None:
        await self._capability_repository.clear_project_for_user_capabilities(user_id, project_id)

    async def _resolve_project(self, user_id: str, project_id: str | None) -> Optional[Project]:
        if not project_id:
            return None
        project = await self._project_repository.find_by_id_and_user_id(project_id, user_id)
        if not project:
            raise NotFoundError("Project not found")
        return project

    def _normalize_tool_names(self, tool_names: list[str]) -> list[str]:
        normalized: list[str] = []
        for tool_name in tool_names:
            trimmed = tool_name.strip()
            if trimmed and trimmed not in normalized:
                normalized.append(trimmed)
        return normalized

    def _example_skills(self, user_id: str, project_id: str | None) -> List[Skill]:
        now = datetime.now(UTC)
        examples = [
            {
                "template_key": "evidence-bundle",
                "name": "Evidence Bundle",
                "description": "Research template for producing source-backed findings with explicit confidence and open questions.",
                "instructions": (
                    "When investigating, prefer primary sources, separate verified facts from inference, "
                    "and end with a short list of unresolved questions."
                ),
            },
            {
                "template_key": "implementation-review",
                "name": "Implementation Review",
                "description": "Engineering template for reviewing diffs, catching regressions, and naming missing tests.",
                "instructions": (
                    "Review code changes for behavioral regressions, unsafe assumptions, and missing verification. "
                    "Present findings first, ordered by severity."
                ),
            },
            {
                "template_key": "launch-operator",
                "name": "Launch Operator",
                "description": "Operations template for release checklists, incident hygiene, and deployment accountability.",
                "instructions": (
                    "Before rollout, verify deploy prerequisites, config drift, and rollback steps. "
                    "Summarize operational risk in plain language."
                ),
            },
            {
                "template_key": "browser-hand-off",
                "name": "Browser Hand-off",
                "description": "Browser workflow template for authenticated web tasks that need careful session handling.",
                "instructions": (
                    "When operating in the browser, preserve authenticated state, avoid destructive clicks until intent is confirmed, "
                    "and keep a concise action log for the next worker."
                ),
            },
        ]
        return [
            Skill(
                id=f"example-{item['template_key']}",
                user_id=user_id,
                project_id=project_id,
                name=item["name"],
                description=item["description"],
                instructions=item["instructions"],
                source="example",
                template_key=item["template_key"],
                enabled=False,
                created_at=now,
                updated_at=now,
            )
            for item in examples
        ]


class _Unset:
    pass


_UNSET = _Unset()
