from pydantic import BaseModel
from typing import Any, Optional, List
from app.interfaces.schemas.event import AgentSSEEvent
from app.domain.models.session import SessionStatus


class ChatRequest(BaseModel):
    """Chat request schema"""
    timestamp: Optional[int] = None
    message: Optional[str] = None
    attachments: Optional[List[dict]] = None
    event_id: Optional[str] = None


class CreateSessionRequest(BaseModel):
    """Create session request schema"""
    model_name: Optional[str] = None
    provider_id: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    project_color: Optional[str] = None


class UpdateSessionProjectRequest(BaseModel):
    """Update session project metadata"""
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    project_color: Optional[str] = None


class ShellViewRequest(BaseModel):
    """Shell view request schema"""
    session_id: str


class CreateSessionResponse(BaseModel):
    """Create session response schema"""
    session_id: str
    provider_id: Optional[str] = None
    provider_label: Optional[str] = None
    model_name: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    project_color: Optional[str] = None
    browser_cdp_url: Optional[str] = None
    browser_cookie_profile: Optional[str] = None
    browser_extension_paths: List[str] = []
    browser_cookies: List[dict[str, Any]] = []


class GetSessionResponse(BaseModel):
    """Get session response schema"""
    session_id: str
    title: Optional[str] = None
    status: SessionStatus
    events: List[AgentSSEEvent] = []
    is_shared: bool = False
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    project_color: Optional[str] = None
    provider_id: Optional[str] = None
    provider_label: Optional[str] = None
    model_name: Optional[str] = None
    browser_engine: Optional[str] = None
    browser_cdp_url: Optional[str] = None
    browser_cookie_profile: Optional[str] = None
    browser_extension_paths: List[str] = []
    browser_cookies: List[dict[str, Any]] = []


class ListSessionItem(BaseModel):
    """List session item schema"""
    session_id: str
    title: Optional[str] = None
    latest_message: Optional[str] = None
    latest_message_at: Optional[int] = None
    status: SessionStatus
    unread_message_count: int
    is_shared: bool = False
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    project_color: Optional[str] = None
    provider_id: Optional[str] = None
    provider_label: Optional[str] = None
    model_name: Optional[str] = None
    browser_engine: Optional[str] = None
    browser_cdp_url: Optional[str] = None
    browser_cookie_profile: Optional[str] = None
    browser_extension_paths: List[str] = []
    browser_cookies: List[dict[str, Any]] = []


class ListSessionResponse(BaseModel):
    """List session response schema"""
    sessions: List[ListSessionItem]


class ConsoleRecord(BaseModel):
    """Console record schema"""
    ps1: str
    command: str
    output: str


class ShellViewResponse(BaseModel):
    """Shell view response schema"""
    output: str
    session_id: str
    console: Optional[List[ConsoleRecord]] = None


class ShareSessionResponse(BaseModel):
    """Share session response schema"""
    session_id: str
    is_shared: bool


class SharedSessionResponse(BaseModel):
    """Shared session response schema (for public access)"""
    session_id: str
    title: Optional[str] = None
    status: SessionStatus
    events: List[AgentSSEEvent] = []
    is_shared: bool
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    project_color: Optional[str] = None
    provider_id: Optional[str] = None
    provider_label: Optional[str] = None
    model_name: Optional[str] = None
    browser_engine: Optional[str] = None
    browser_cdp_url: Optional[str] = None
    browser_cookie_profile: Optional[str] = None
    browser_extension_paths: List[str] = []
    browser_cookies: List[dict[str, Any]] = []
