from datetime import UTC, datetime
from typing import Literal, Optional
import uuid

from pydantic import BaseModel, Field


SkillSource = Literal["user", "example"]


class Skill(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    user_id: str
    project_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    instructions: str
    source: SkillSource = "user"
    template_key: Optional[str] = None
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProjectMemoryNote(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    user_id: str
    project_id: Optional[str] = None
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


WorkerRole = Literal["coordinator", "research", "developer", "browser", "document", "automation", "custom"]
WorkerLane = Literal["intake", "research", "execution", "delivery"]


class WorkerProfile(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    user_id: str
    project_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    role: WorkerRole = "custom"
    lane: WorkerLane = "execution"
    instructions: str
    tool_names: list[str] = Field(default_factory=list)
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
