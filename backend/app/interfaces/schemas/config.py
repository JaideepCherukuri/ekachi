from pydantic import BaseModel


class ClientConfigResponse(BaseModel):
    """Client runtime configuration response schema"""
    auth_provider: str
    show_github_button: bool
    github_repository_url: str
    google_analytics_id: str | None = None
    claw_enabled: bool
    default_model_name: str
    available_models: list[str]


class ControlPlaneConfigResponse(BaseModel):
    """Non-secret runtime capability metadata for the settings control plane."""
    auth_provider: str
    model_provider: str
    default_model_name: str
    available_models: list[str]
    browser_engine: str
    search_provider: str | None = None
    supported_search_providers: list[str]
    supported_browser_engines: list[str]
    show_github_button: bool
    github_repository_url: str
    google_analytics_enabled: bool
    claw_enabled: bool
    email_enabled: bool
    mcp_configured: bool
