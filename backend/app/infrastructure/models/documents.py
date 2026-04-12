from typing import Any, Dict, Optional, List, Type, TypeVar, Generic, get_args, Self
from datetime import datetime, timezone, UTC
from beanie import Document
from pydantic import BaseModel, Field
from app.domain.models.agent import Agent
from app.domain.models.memory import Memory
from app.domain.models.event import AgentEvent
from app.domain.models.session import Session, SessionStatus
from app.domain.models.file import FileInfo
from app.domain.models.user import User, UserRole
from app.domain.models.claw import Claw, ClawStatus, ClawMessage
from app.domain.models.project import BrowserPoolEntry, Project
from app.domain.models.provider import Provider
from app.domain.models.capability import Skill, ProjectMemoryNote, WorkerProfile, WorkerRole, WorkerLane, SkillSource
from app.domain.models.trigger import Trigger, TriggerRun, TriggerStatus, TriggerType, TriggerRunStatus
from pymongo import IndexModel, ASCENDING, DESCENDING

T = TypeVar('T', bound=BaseModel)

class BaseDocument(Document, Generic[T]):
    def __init_subclass__(cls, id_field="id", domain_model_class: Type[T] = None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._ID_FIELD = id_field
        cls._DOMAIN_MODEL_CLASS = domain_model_class
    
    def update_from_domain(self, domain_obj: T) -> None:
        """Update the document from domain model"""
        data = domain_obj.model_dump(exclude={'id', 'created_at'})
        data[self._ID_FIELD] = domain_obj.id
        if hasattr(self, 'updated_at'):
            data['updated_at'] = datetime.now(UTC)
        
        for field, value in data.items():
            setattr(self, field, value)
    
    def to_domain(self) -> T:
        """Convert MongoDB document to domain model"""
        # Convert to dict and map agent_id to id field
        data = self.model_dump(exclude={'id'})
        data['id'] = data.pop(self._ID_FIELD)
        return self._DOMAIN_MODEL_CLASS.model_validate(data)
    
    @classmethod
    def from_domain(cls, domain_obj: T) -> Self:
        """Create a new MongoDB agent from domain"""
        # Convert to dict and map id to agent_id field
        data = domain_obj.model_dump()
        data[cls._ID_FIELD] = data.pop('id')
        return cls.model_validate(data)

class UserDocument(BaseDocument[User], id_field="user_id", domain_model_class=User):
    """MongoDB document for User"""
    user_id: str
    fullname: str
    email: str  # Now required field for login
    password_hash: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    help_improve: bool = False
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)
    last_login_at: Optional[datetime] = None

    class Settings:
        name = "users"
        indexes = [
            "user_id",
            "fullname",  # Keep fullname index but not unique
            IndexModel([("email", ASCENDING)], unique=True),  # Email as unique index
        ]

class AgentDocument(BaseDocument[Agent], id_field="agent_id", domain_model_class=Agent):
    """MongoDB document for Agent"""
    agent_id: str
    model_name: str
    provider_id: str
    provider_label: str
    model_provider: str
    api_base: Optional[str] = None
    encrypted_api_key: Optional[str] = None
    temperature: float
    max_tokens: int
    memories: Dict[str, Memory] = {}
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "agents"
        indexes = [
            "agent_id",
        ]


class SessionDocument(BaseDocument[Session], id_field="session_id", domain_model_class=Session):
    """MongoDB model for Session"""
    session_id: str
    user_id: str  # User ID that owns this session
    sandbox_id: Optional[str] = None
    agent_id: str
    task_id: Optional[str] = None
    title: Optional[str] = None
    unread_message_count: int = 0
    latest_message: Optional[str] = None
    latest_message_at: Optional[datetime] = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)
    events: List[AgentEvent]
    status: SessionStatus
    files: List[FileInfo] = []
    is_shared: Optional[bool] = False
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    project_color: Optional[str] = None
    provider_id: Optional[str] = None
    provider_label: Optional[str] = None
    model_name: Optional[str] = None
    search_provider: Optional[str] = None
    browser_engine: Optional[str] = None
    browser_cdp_url: Optional[str] = None
    browser_cookie_profile: Optional[str] = None
    browser_extension_paths: List[str] = []
    browser_cookies: List[dict[str, Any]] = []
    class Settings:
        name = "sessions"
        indexes = [
            "session_id",
            "user_id",
            IndexModel(
                [("user_id", ASCENDING), ("latest_message_at", DESCENDING)],
                name="user_id_latest_message_at",
            ),
        ]


class ProjectDocument(BaseDocument[Project], id_field="project_id", domain_model_class=Project):
    """MongoDB document for Project"""
    project_id: str
    user_id: str
    name: str
    color: str
    default_provider_id: Optional[str] = None
    default_model_name: Optional[str] = None
    preferred_search_provider: Optional[str] = None
    preferred_browser_engine: Optional[str] = None
    browser_cdp_url: Optional[str] = None
    browser_pool: List[BrowserPoolEntry] = []
    browser_cookie_profile: Optional[str] = None
    browser_extension_paths: List[str] = []
    browser_cookies: List[dict[str, Any]] = []
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "projects"
        indexes = [
            "project_id",
            IndexModel([("user_id", ASCENDING), ("updated_at", DESCENDING)], name="user_id_updated_at"),
        ]


class ProviderDocument(BaseDocument[Provider], id_field="provider_id", domain_model_class=Provider):
    provider_id: str
    user_id: str
    label: str
    model_provider: str
    api_base: Optional[str] = None
    encrypted_api_key: Optional[str] = None
    available_models: List[str] = []
    default_model_name: Optional[str] = None
    enabled: bool = True
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "providers"
        indexes = [
            "provider_id",
            IndexModel([("user_id", ASCENDING), ("updated_at", DESCENDING)], name="user_id_provider_updated_at"),
        ]


class TriggerDocument(BaseDocument[Trigger], id_field="trigger_id", domain_model_class=Trigger):
    trigger_id: str
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
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "triggers"
        indexes = [
            "trigger_id",
            IndexModel([("user_id", ASCENDING), ("project_id", ASCENDING), ("updated_at", DESCENDING)], name="user_project_updated_at"),
            IndexModel([("trigger_type", ASCENDING), ("status", ASCENDING), ("next_run_at", ASCENDING)], name="schedule_poll"),
            IndexModel([("trigger_id", ASCENDING), ("webhook_secret", ASCENDING)], name="webhook_lookup"),
        ]


class TriggerRunDocument(BaseDocument[TriggerRun], id_field="trigger_run_id", domain_model_class=TriggerRun):
    trigger_run_id: str
    trigger_id: str
    user_id: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    trigger_type: TriggerType
    status: TriggerRunStatus = TriggerRunStatus.PENDING
    source: TriggerType
    input_payload: Optional[dict] = None
    output_summary: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    attempt_number: int = 1
    started_at: datetime = datetime.now(timezone.utc)
    completed_at: Optional[datetime] = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "trigger_runs"
        indexes = [
            "trigger_run_id",
            IndexModel([("user_id", ASCENDING), ("project_id", ASCENDING), ("started_at", DESCENDING)], name="user_project_started_at"),
            IndexModel([("trigger_id", ASCENDING), ("started_at", DESCENDING)], name="trigger_started_at"),
        ]


class SkillDocument(BaseDocument[Skill], id_field="skill_id", domain_model_class=Skill):
    skill_id: str
    user_id: str
    project_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    instructions: str
    source: SkillSource = "user"
    template_key: Optional[str] = None
    enabled: bool = True
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "skills"
        indexes = [
            "skill_id",
            IndexModel([("user_id", ASCENDING), ("project_id", ASCENDING), ("updated_at", DESCENDING)], name="user_project_skill_updated_at"),
        ]


class MemoryNoteDocument(BaseDocument[ProjectMemoryNote], id_field="memory_note_id", domain_model_class=ProjectMemoryNote):
    memory_note_id: str
    user_id: str
    project_id: Optional[str] = None
    content: str
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "memory_notes"
        indexes = [
            "memory_note_id",
            IndexModel([("user_id", ASCENDING), ("project_id", ASCENDING)], name="user_project_memory"),
        ]


class WorkerDocument(BaseDocument[WorkerProfile], id_field="worker_id", domain_model_class=WorkerProfile):
    worker_id: str
    user_id: str
    project_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    role: WorkerRole = "custom"
    lane: WorkerLane = "execution"
    instructions: str
    tool_names: List[str] = []
    enabled: bool = True
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "workers"
        indexes = [
            "worker_id",
            IndexModel([("user_id", ASCENDING), ("project_id", ASCENDING), ("lane", ASCENDING), ("updated_at", DESCENDING)], name="user_project_worker_lane_updated_at"),
        ]


class ClawDocument(BaseDocument[Claw], id_field="claw_id", domain_model_class=Claw):
    """MongoDB document for Claw instance"""
    claw_id: str
    user_id: str
    container_name: Optional[str] = None
    container_ip: Optional[str] = None
    api_key: str
    status: ClawStatus = ClawStatus.CREATING
    error_message: Optional[str] = None
    expires_at: Optional[datetime] = None
    messages: List[ClawMessage] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "claws"
        indexes = [
            "claw_id",
            IndexModel([("user_id", ASCENDING)], unique=True),  # One claw per user
        ]
