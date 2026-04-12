from typing import List

from pydantic import BaseModel


class BrowserPoolEntryResponse(BaseModel):
    browser_id: str
    label: str
    cdp_url: str
    source: str
    active: bool = False
    healthy: bool = False
    browser: str | None = None
    page_count: int = 0
    total_cookie_count: int = 0
    error: str | None = None


class BrowserPoolResponse(BaseModel):
    active_browser_id: str | None = None
    browsers: List[BrowserPoolEntryResponse]


class AddBrowserPoolEntryRequest(BaseModel):
    label: str
    cdp_url: str
    source: str = "manual"
    set_active: bool = False


class BrowserConnectionResponse(BaseModel):
    cdp_url: str
    ws_url: str
    browser: str | None = None
    user_agent: str | None = None
    protocol_version: str | None = None
    context_count: int = 0
    page_count: int = 0
    total_cookie_count: int = 0


class BrowserCookieDomainResponse(BaseModel):
    domain: str
    root_domain: str
    cookie_count: int
    http_only_count: int
    secure_count: int


class BrowserCookieInventoryResponse(BaseModel):
    source: str
    total_cookie_count: int
    domains: List[BrowserCookieDomainResponse]


class BrowserCookieMutationResponse(BaseModel):
    removed_count: int = 0
    captured_count: int = 0
    applied_count: int = 0
    inventory: BrowserCookieInventoryResponse
