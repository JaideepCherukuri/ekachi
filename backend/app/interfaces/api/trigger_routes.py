from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, Query

from app.application.services.trigger_service import TriggerService, _UNSET
from app.domain.models.user import User
from app.domain.models.trigger import TriggerType
from app.interfaces.dependencies import get_current_user, get_trigger_service
from app.interfaces.schemas.base import APIResponse
from app.interfaces.schemas.trigger import (
    CreateTriggerRequest,
    ExecuteTriggerRequest,
    ListTriggerRunsResponse,
    ListTriggersResponse,
    TriggerResponse,
    TriggerRunResponse,
    UpdateTriggerRequest,
)


router = APIRouter(prefix="/triggers", tags=["triggers"])


def _to_trigger_response(trigger) -> TriggerResponse:
    return TriggerResponse(
        trigger_id=trigger.id,
        project_id=trigger.project_id,
        name=trigger.name,
        prompt=trigger.prompt,
        trigger_type=trigger.trigger_type,
        status=trigger.status,
        webhook_secret=trigger.webhook_secret,
        schedule_cron=trigger.schedule_cron,
        schedule_timezone=trigger.schedule_timezone,
        next_run_at=trigger.next_run_at,
        last_run_at=trigger.last_run_at,
        last_run_status=trigger.last_run_status,
        execution_count=trigger.execution_count,
        success_count=trigger.success_count,
        failure_count=trigger.failure_count,
        cancelled_count=trigger.cancelled_count,
        created_at=trigger.created_at,
        updated_at=trigger.updated_at,
    )


def _to_run_response(run) -> TriggerRunResponse:
    return TriggerRunResponse(
        run_id=run.id,
        trigger_id=run.trigger_id,
        project_id=run.project_id,
        session_id=run.session_id,
        trigger_type=run.trigger_type,
        status=run.status,
        source=run.source,
        input_payload=run.input_payload,
        output_summary=run.output_summary,
        error_message=run.error_message,
        duration_seconds=run.duration_seconds,
        attempt_number=run.attempt_number,
        started_at=run.started_at,
        completed_at=run.completed_at,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


@router.get("", response_model=APIResponse[ListTriggersResponse])
async def list_triggers(
    project_id: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    trigger_service: TriggerService = Depends(get_trigger_service),
) -> APIResponse[ListTriggersResponse]:
    triggers = await trigger_service.list_triggers(current_user.id, project_id)
    return APIResponse.success(ListTriggersResponse(triggers=[_to_trigger_response(trigger) for trigger in triggers]))


@router.get("/runs", response_model=APIResponse[ListTriggerRunsResponse])
async def list_runs(
    project_id: Optional[str] = Query(default=None),
    trigger_id: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    trigger_service: TriggerService = Depends(get_trigger_service),
) -> APIResponse[ListTriggerRunsResponse]:
    runs = await trigger_service.list_runs(current_user.id, project_id, trigger_id, limit)
    return APIResponse.success(ListTriggerRunsResponse(runs=[_to_run_response(run) for run in runs]))


@router.get("/runs/{run_id}", response_model=APIResponse[TriggerRunResponse])
async def get_run(
    run_id: str,
    current_user: User = Depends(get_current_user),
    trigger_service: TriggerService = Depends(get_trigger_service),
) -> APIResponse[TriggerRunResponse]:
    run = await trigger_service.get_run(run_id, current_user.id)
    return APIResponse.success(_to_run_response(run))


@router.post("", response_model=APIResponse[TriggerResponse])
async def create_trigger(
    request: CreateTriggerRequest,
    current_user: User = Depends(get_current_user),
    trigger_service: TriggerService = Depends(get_trigger_service),
) -> APIResponse[TriggerResponse]:
    trigger = await trigger_service.create_trigger(
        user_id=current_user.id,
        project_id=request.project_id,
        name=request.name,
        prompt=request.prompt,
        trigger_type=request.trigger_type,
        status=request.status,
        schedule_cron=request.schedule_cron,
        schedule_timezone=request.schedule_timezone,
    )
    return APIResponse.success(_to_trigger_response(trigger))


@router.patch("/{trigger_id}", response_model=APIResponse[TriggerResponse])
async def update_trigger(
    trigger_id: str,
    request: UpdateTriggerRequest,
    current_user: User = Depends(get_current_user),
    trigger_service: TriggerService = Depends(get_trigger_service),
) -> APIResponse[TriggerResponse]:
    trigger = await trigger_service.update_trigger(
        trigger_id=trigger_id,
        user_id=current_user.id,
        project_id=request.project_id if "project_id" in request.model_fields_set else _UNSET,
        name=request.name,
        prompt=request.prompt,
        status=request.status,
        schedule_cron=request.schedule_cron,
        schedule_timezone=request.schedule_timezone,
    )
    return APIResponse.success(_to_trigger_response(trigger))


@router.delete("/{trigger_id}", response_model=APIResponse[None])
async def delete_trigger(
    trigger_id: str,
    current_user: User = Depends(get_current_user),
    trigger_service: TriggerService = Depends(get_trigger_service),
) -> APIResponse[None]:
    await trigger_service.delete_trigger(trigger_id, current_user.id)
    return APIResponse.success()


@router.post("/{trigger_id}/execute", response_model=APIResponse[TriggerRunResponse])
async def execute_trigger(
    trigger_id: str,
    request: ExecuteTriggerRequest | None = Body(default=None),
    current_user: User = Depends(get_current_user),
    trigger_service: TriggerService = Depends(get_trigger_service),
) -> APIResponse[TriggerRunResponse]:
    run = await trigger_service.execute_trigger(
        trigger_id=trigger_id,
        user_id=current_user.id,
        source=TriggerType.MANUAL,
        input_payload=request.input_payload if request else None,
    )
    return APIResponse.success(_to_run_response(run))


@router.post("/webhook/{trigger_id}/{webhook_secret}", response_model=APIResponse[TriggerRunResponse])
async def execute_webhook_trigger(
    trigger_id: str,
    webhook_secret: str,
    payload: Optional[dict[str, Any]] = Body(default=None),
    trigger_service: TriggerService = Depends(get_trigger_service),
) -> APIResponse[TriggerRunResponse]:
    run = await trigger_service.execute_webhook_trigger(trigger_id, webhook_secret, payload)
    return APIResponse.success(_to_run_response(run))


@router.post("/runs/{run_id}/retry", response_model=APIResponse[TriggerRunResponse])
async def retry_run(
    run_id: str,
    current_user: User = Depends(get_current_user),
    trigger_service: TriggerService = Depends(get_trigger_service),
) -> APIResponse[TriggerRunResponse]:
    run = await trigger_service.retry_run(run_id, current_user.id)
    return APIResponse.success(_to_run_response(run))


@router.post("/runs/{run_id}/cancel", response_model=APIResponse[TriggerRunResponse])
async def cancel_run(
    run_id: str,
    current_user: User = Depends(get_current_user),
    trigger_service: TriggerService = Depends(get_trigger_service),
) -> APIResponse[TriggerRunResponse]:
    run = await trigger_service.cancel_run(run_id, current_user.id)
    return APIResponse.success(_to_run_response(run))
