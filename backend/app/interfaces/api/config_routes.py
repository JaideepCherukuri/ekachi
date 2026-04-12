from pathlib import Path

from fastapi import APIRouter

from app.core.config import get_settings
from app.interfaces.schemas.base import APIResponse
from app.interfaces.schemas.config import ClientConfigResponse, ControlPlaneConfigResponse

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/frontend", response_model=APIResponse[ClientConfigResponse])
async def get_frontend_config() -> APIResponse[ClientConfigResponse]:
    """Get frontend runtime config."""
    settings = get_settings()

    return APIResponse.success(
        ClientConfigResponse(
            auth_provider=settings.auth_provider,
            show_github_button=settings.show_github_button,
            github_repository_url=settings.github_repository_url,
            google_analytics_id=settings.google_analytics_id,
            claw_enabled=settings.claw_enabled,
            default_model_name=settings.model_name,
            available_models=settings.available_models or [settings.model_name],
        )
    )


@router.get("/control-plane", response_model=APIResponse[ControlPlaneConfigResponse])
async def get_control_plane_config() -> APIResponse[ControlPlaneConfigResponse]:
    """Get non-secret runtime capability metadata for the frontend settings control plane."""
    settings = get_settings()
    mcp_configured = Path(settings.mcp_config_path).exists()

    return APIResponse.success(
        ControlPlaneConfigResponse(
            auth_provider=settings.auth_provider,
            model_provider=settings.model_provider,
            default_model_name=settings.model_name,
            available_models=settings.available_models or [settings.model_name],
            browser_engine=settings.browser_engine,
            search_provider=settings.search_provider,
            supported_search_providers=["google", "bing", "bing_web", "baidu", "baidu_web", "tavily"],
            supported_browser_engines=["browser_use", "playwright"],
            show_github_button=settings.show_github_button,
            github_repository_url=settings.github_repository_url,
            google_analytics_enabled=bool(settings.google_analytics_id),
            claw_enabled=settings.claw_enabled,
            email_enabled=bool(settings.email_host and settings.email_port and settings.email_from),
            mcp_configured=mcp_configured,
        )
    )
