from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.domain.models.capability import SkillSource, WorkerLane, WorkerRole


class SkillResponse(BaseModel):
    skill_id: str
    project_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    instructions: str
    source: SkillSource = "user"
    is_example: bool = False
    template_key: Optional[str] = None
    enabled: bool
    created_at: datetime
    updated_at: datetime


class ListSkillsResponse(BaseModel):
    skills: List[SkillResponse]


class CreateSkillRequest(BaseModel):
    project_id: Optional[str] = None
    name: str = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=240)
    instructions: str = Field(min_length=1, max_length=12000)
    enabled: bool = True


class UpdateSkillRequest(BaseModel):
    project_id: Optional[str] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=240)
    instructions: Optional[str] = Field(default=None, min_length=1, max_length=12000)
    enabled: Optional[bool] = None


class MemoryResponse(BaseModel):
    memory_id: Optional[str] = None
    project_id: Optional[str] = None
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UpdateMemoryRequest(BaseModel):
    project_id: Optional[str] = None
    content: str = Field(default="", max_length=20000)


class WorkerResponse(BaseModel):
    worker_id: str
    project_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    role: WorkerRole
    lane: WorkerLane
    instructions: str
    tool_names: List[str]
    enabled: bool
    created_at: datetime
    updated_at: datetime


class ListWorkersResponse(BaseModel):
    workers: List[WorkerResponse]


class CreateWorkerRequest(BaseModel):
    project_id: Optional[str] = None
    name: str = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=240)
    role: WorkerRole = "custom"
    lane: WorkerLane = "execution"
    instructions: str = Field(min_length=1, max_length=12000)
    tool_names: List[str] = Field(default_factory=list, max_length=24)
    enabled: bool = True


class UpdateWorkerRequest(BaseModel):
    project_id: Optional[str] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=240)
    role: Optional[WorkerRole] = None
    lane: Optional[WorkerLane] = None
    instructions: Optional[str] = Field(default=None, min_length=1, max_length=12000)
    tool_names: Optional[List[str]] = Field(default=None, max_length=24)
    enabled: Optional[bool] = None
