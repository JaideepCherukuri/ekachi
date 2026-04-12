from datetime import UTC, datetime
from typing import Any, List, Literal, Optional
import uuid

from pydantic import BaseModel, Field


BrowserPoolSource = Literal["manual", "managed"]


class BrowserPoolEntry(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    label: str
    cdp_url: str
    source: BrowserPoolSource = "manual"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Project(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    user_id: str
    name: str
    color: str
    default_provider_id: Optional[str] = None
    default_model_name: Optional[str] = None
    preferred_search_provider: Optional[str] = None
    preferred_browser_engine: Optional[str] = None
    browser_cdp_url: Optional[str] = None
    browser_pool: List[BrowserPoolEntry] = Field(default_factory=list)
    browser_cookie_profile: Optional[str] = None
    browser_extension_paths: List[str] = Field(default_factory=list)
    browser_cookies: List[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
