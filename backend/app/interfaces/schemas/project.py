from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class BrowserPoolEntryResponse(BaseModel):
    browser_id: str
    label: str
    cdp_url: str
    source: str
    created_at: datetime
    updated_at: datetime


class BrowserPoolEntryRequest(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    cdp_url: str = Field(min_length=1, max_length=2048)
    source: str = "manual"


class ProjectResponse(BaseModel):
    project_id: str
    name: str
    color: str
    default_provider_id: Optional[str] = None
    default_model_name: Optional[str] = None
    preferred_search_provider: Optional[str] = None
    preferred_browser_engine: Optional[str] = None
    browser_cdp_url: Optional[str] = None
    browser_pool: List[BrowserPoolEntryResponse] = Field(default_factory=list)
    browser_cookie_profile: Optional[str] = None
    browser_extension_paths: List[str] = Field(default_factory=list)
    browser_cookies: List[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ListProjectsResponse(BaseModel):
    projects: List[ProjectResponse]


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    color: str = Field(min_length=4, max_length=32)
    default_provider_id: Optional[str] = None
    default_model_name: Optional[str] = None
    preferred_search_provider: Optional[str] = None
    preferred_browser_engine: Optional[str] = None
    browser_cdp_url: Optional[str] = Field(default=None, max_length=2048)
    browser_pool: List[BrowserPoolEntryRequest] = Field(default_factory=list)
    browser_cookie_profile: Optional[str] = Field(default=None, max_length=20000)
    browser_extension_paths: List[str] = Field(default_factory=list)
    browser_cookies: List[dict[str, Any]] = Field(default_factory=list)


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    color: Optional[str] = Field(default=None, min_length=4, max_length=32)
    default_provider_id: Optional[str] = None
    default_model_name: Optional[str] = None
    preferred_search_provider: Optional[str] = None
    preferred_browser_engine: Optional[str] = None
    browser_cdp_url: Optional[str] = Field(default=None, max_length=2048)
    browser_pool: Optional[List[BrowserPoolEntryRequest]] = None
    browser_cookie_profile: Optional[str] = Field(default=None, max_length=20000)
    browser_extension_paths: Optional[List[str]] = None
    browser_cookies: Optional[List[dict[str, Any]]] = None
