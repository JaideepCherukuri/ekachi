from datetime import datetime
from typing import Any, Optional, List

from pydantic import BaseModel, Field

from app.domain.models.trigger import TriggerRunStatus, TriggerStatus, TriggerType


class TriggerResponse(BaseModel):
    trigger_id: str
    project_id: Optional[str] = None
    name: str
    prompt: str
    trigger_type: TriggerType
    status: TriggerStatus
    webhook_secret: Optional[str] = None
    schedule_cron: Optional[str] = None
    schedule_timezone: str
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    last_run_status: Optional[TriggerRunStatus] = None
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    cancelled_count: int = 0
    created_at: datetime
    updated_at: datetime


class ListTriggersResponse(BaseModel):
    triggers: List[TriggerResponse]


class TriggerRunResponse(BaseModel):
    run_id: str
    trigger_id: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    trigger_type: TriggerType
    status: TriggerRunStatus
    source: TriggerType
    input_payload: Optional[dict[str, Any]] = None
    output_summary: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    attempt_number: int = 1
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ListTriggerRunsResponse(BaseModel):
    runs: List[TriggerRunResponse]


class CreateTriggerRequest(BaseModel):
    project_id: Optional[str] = None
    name: str = Field(min_length=1, max_length=120)
    prompt: str = Field(min_length=1, max_length=12000)
    trigger_type: TriggerType
    status: TriggerStatus = TriggerStatus.ACTIVE
    schedule_cron: Optional[str] = None
    schedule_timezone: str = "UTC"


class UpdateTriggerRequest(BaseModel):
    project_id: Optional[str] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    prompt: Optional[str] = Field(default=None, min_length=1, max_length=12000)
    status: Optional[TriggerStatus] = None
    schedule_cron: Optional[str] = None
    schedule_timezone: Optional[str] = None


class ExecuteTriggerRequest(BaseModel):
    input_payload: Optional[dict[str, Any]] = None
