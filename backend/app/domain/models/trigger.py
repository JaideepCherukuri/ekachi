from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
import uuid

from pydantic import BaseModel, Field


class TriggerType(str, Enum):
    MANUAL = "manual"
    WEBHOOK = "webhook"
    SCHEDULE = "schedule"


class TriggerStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"


class TriggerRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Trigger(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    user_id: str
    project_id: Optional[str] = None
    name: str
    prompt: str
    trigger_type: TriggerType
    status: TriggerStatus = TriggerStatus.ACTIVE
    webhook_secret: Optional[str] = None
    schedule_cron: Optional[str] = None
    schedule_timezone: str = "UTC"
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    last_run_status: Optional[TriggerRunStatus] = None
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    cancelled_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TriggerRun(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    trigger_id: str
    user_id: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    trigger_type: TriggerType
    status: TriggerRunStatus = TriggerRunStatus.PENDING
    source: TriggerType
    input_payload: Optional[dict[str, Any]] = None
    output_summary: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    attempt_number: int = 1
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
