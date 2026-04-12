from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.application.services.capability_service import CapabilityService, _UNSET
from app.domain.models.user import User
from app.interfaces.dependencies import get_capability_service, get_current_user
from app.interfaces.schemas.base import APIResponse
from app.interfaces.schemas.capability import (
    CreateSkillRequest,
    CreateWorkerRequest,
    ListSkillsResponse,
    ListWorkersResponse,
    MemoryResponse,
    SkillResponse,
    UpdateMemoryRequest,
    UpdateSkillRequest,
    UpdateWorkerRequest,
    WorkerResponse,
)


router = APIRouter(prefix="/capabilities", tags=["capabilities"])


def _to_skill_response(skill) -> SkillResponse:
    return SkillResponse(
        skill_id=skill.id,
        project_id=skill.project_id,
        name=skill.name,
        description=skill.description,
        instructions=skill.instructions,
        source=skill.source,
        is_example=skill.source == "example",
        template_key=skill.template_key,
        enabled=skill.enabled,
        created_at=skill.created_at,
        updated_at=skill.updated_at,
    )


def _to_memory_response(memory, project_id: str | None) -> MemoryResponse:
    if not memory:
        return MemoryResponse(project_id=project_id, content="")
    return MemoryResponse(
        memory_id=memory.id,
        project_id=memory.project_id,
        content=memory.content,
        created_at=memory.created_at,
        updated_at=memory.updated_at,
    )


def _to_worker_response(worker) -> WorkerResponse:
    return WorkerResponse(
        worker_id=worker.id,
        project_id=worker.project_id,
        name=worker.name,
        description=worker.description,
        role=worker.role,
        lane=worker.lane,
        instructions=worker.instructions,
        tool_names=worker.tool_names,
        enabled=worker.enabled,
        created_at=worker.created_at,
        updated_at=worker.updated_at,
    )


@router.get("/skills", response_model=APIResponse[ListSkillsResponse])
async def list_skills(
    project_id: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    capability_service: CapabilityService = Depends(get_capability_service),
) -> APIResponse[ListSkillsResponse]:
    skills = await capability_service.list_skills(current_user.id, project_id)
    return APIResponse.success(ListSkillsResponse(skills=[_to_skill_response(skill) for skill in skills]))


@router.post("/skills", response_model=APIResponse[SkillResponse])
async def create_skill(
    request: CreateSkillRequest,
    current_user: User = Depends(get_current_user),
    capability_service: CapabilityService = Depends(get_capability_service),
) -> APIResponse[SkillResponse]:
    skill = await capability_service.create_skill(
        user_id=current_user.id,
        project_id=request.project_id,
        name=request.name,
        description=request.description,
        instructions=request.instructions,
        enabled=request.enabled,
    )
    return APIResponse.success(_to_skill_response(skill))


@router.patch("/skills/{skill_id}", response_model=APIResponse[SkillResponse])
async def update_skill(
    skill_id: str,
    request: UpdateSkillRequest,
    current_user: User = Depends(get_current_user),
    capability_service: CapabilityService = Depends(get_capability_service),
) -> APIResponse[SkillResponse]:
    skill = await capability_service.update_skill(
        skill_id=skill_id,
        user_id=current_user.id,
        project_id=request.project_id if "project_id" in request.model_fields_set else _UNSET,
        name=request.name,
        description=request.description,
        instructions=request.instructions,
        enabled=request.enabled,
    )
    return APIResponse.success(_to_skill_response(skill))


@router.delete("/skills/{skill_id}", response_model=APIResponse[None])
async def delete_skill(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    capability_service: CapabilityService = Depends(get_capability_service),
) -> APIResponse[None]:
    await capability_service.delete_skill(skill_id, current_user.id)
    return APIResponse.success()


@router.get("/memory", response_model=APIResponse[MemoryResponse])
async def get_memory(
    project_id: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    capability_service: CapabilityService = Depends(get_capability_service),
) -> APIResponse[MemoryResponse]:
    memory = await capability_service.get_memory(current_user.id, project_id)
    return APIResponse.success(_to_memory_response(memory, project_id))


@router.put("/memory", response_model=APIResponse[MemoryResponse])
async def update_memory(
    request: UpdateMemoryRequest,
    current_user: User = Depends(get_current_user),
    capability_service: CapabilityService = Depends(get_capability_service),
) -> APIResponse[MemoryResponse]:
    memory = await capability_service.update_memory(current_user.id, request.project_id, request.content)
    return APIResponse.success(_to_memory_response(memory, request.project_id))


@router.get("/workers", response_model=APIResponse[ListWorkersResponse])
async def list_workers(
    project_id: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    capability_service: CapabilityService = Depends(get_capability_service),
) -> APIResponse[ListWorkersResponse]:
    workers = await capability_service.list_workers(current_user.id, project_id)
    return APIResponse.success(ListWorkersResponse(workers=[_to_worker_response(worker) for worker in workers]))


@router.post("/workers", response_model=APIResponse[WorkerResponse])
async def create_worker(
    request: CreateWorkerRequest,
    current_user: User = Depends(get_current_user),
    capability_service: CapabilityService = Depends(get_capability_service),
) -> APIResponse[WorkerResponse]:
    worker = await capability_service.create_worker(
        user_id=current_user.id,
        project_id=request.project_id,
        name=request.name,
        description=request.description,
        role=request.role,
        lane=request.lane,
        instructions=request.instructions,
        tool_names=request.tool_names,
        enabled=request.enabled,
    )
    return APIResponse.success(_to_worker_response(worker))


@router.patch("/workers/{worker_id}", response_model=APIResponse[WorkerResponse])
async def update_worker(
    worker_id: str,
    request: UpdateWorkerRequest,
    current_user: User = Depends(get_current_user),
    capability_service: CapabilityService = Depends(get_capability_service),
) -> APIResponse[WorkerResponse]:
    worker = await capability_service.update_worker(
        worker_id=worker_id,
        user_id=current_user.id,
        project_id=request.project_id if "project_id" in request.model_fields_set else _UNSET,
        name=request.name,
        description=request.description,
        role=request.role,
        lane=request.lane,
        instructions=request.instructions,
        tool_names=request.tool_names,
        enabled=request.enabled,
    )
    return APIResponse.success(_to_worker_response(worker))


@router.delete("/workers/{worker_id}", response_model=APIResponse[None])
async def delete_worker(
    worker_id: str,
    current_user: User = Depends(get_current_user),
    capability_service: CapabilityService = Depends(get_capability_service),
) -> APIResponse[None]:
    await capability_service.delete_worker(worker_id, current_user.id)
    return APIResponse.success()
