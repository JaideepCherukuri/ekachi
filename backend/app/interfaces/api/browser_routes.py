from fastapi import APIRouter, Depends

from app.application.services.browser_service import BrowserService
from app.domain.models.user import User
from app.interfaces.dependencies import get_browser_service, get_current_user
from app.interfaces.schemas.base import APIResponse
from app.interfaces.schemas.browser import (
    AddBrowserPoolEntryRequest,
    BrowserConnectionResponse,
    BrowserCookieInventoryResponse,
    BrowserCookieMutationResponse,
    BrowserPoolResponse,
)


router = APIRouter(prefix="/browser", tags=["browser"])


@router.get("/projects/{project_id}/connection", response_model=APIResponse[BrowserConnectionResponse])
async def test_browser_connection(
    project_id: str,
    current_user: User = Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service),
) -> APIResponse[BrowserConnectionResponse]:
    result = await browser_service.test_connection(current_user.id, project_id)
    return APIResponse.success(BrowserConnectionResponse(**result))


@router.get("/projects/{project_id}/pool", response_model=APIResponse[BrowserPoolResponse])
async def list_browser_pool(
    project_id: str,
    current_user: User = Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service),
) -> APIResponse[BrowserPoolResponse]:
    result = await browser_service.list_browser_pool(current_user.id, project_id)
    return APIResponse.success(BrowserPoolResponse(**result))


@router.post("/projects/{project_id}/pool", response_model=APIResponse[BrowserPoolResponse])
async def add_browser_pool_entry(
    project_id: str,
    request: AddBrowserPoolEntryRequest,
    current_user: User = Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service),
) -> APIResponse[BrowserPoolResponse]:
    result = await browser_service.add_browser_pool_entry(
        current_user.id,
        project_id,
        label=request.label,
        cdp_url=request.cdp_url,
        source=request.source,
        set_active=request.set_active,
    )
    return APIResponse.success(BrowserPoolResponse(**result))


@router.post("/projects/{project_id}/pool/{browser_id}/activate", response_model=APIResponse[BrowserPoolResponse])
async def activate_browser_pool_entry(
    project_id: str,
    browser_id: str,
    current_user: User = Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service),
) -> APIResponse[BrowserPoolResponse]:
    result = await browser_service.activate_browser_pool_entry(current_user.id, project_id, browser_id)
    return APIResponse.success(BrowserPoolResponse(**result))


@router.delete("/projects/{project_id}/pool/{browser_id}", response_model=APIResponse[BrowserPoolResponse])
async def delete_browser_pool_entry(
    project_id: str,
    browser_id: str,
    current_user: User = Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service),
) -> APIResponse[BrowserPoolResponse]:
    result = await browser_service.remove_browser_pool_entry(current_user.id, project_id, browser_id)
    return APIResponse.success(BrowserPoolResponse(**result))


@router.get("/projects/{project_id}/cookies/live", response_model=APIResponse[BrowserCookieInventoryResponse])
async def list_live_browser_cookies(
    project_id: str,
    current_user: User = Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service),
) -> APIResponse[BrowserCookieInventoryResponse]:
    result = await browser_service.list_live_cookie_inventory(current_user.id, project_id)
    return APIResponse.success(BrowserCookieInventoryResponse(**result))


@router.get("/projects/{project_id}/cookies/project", response_model=APIResponse[BrowserCookieInventoryResponse])
async def list_project_browser_cookies(
    project_id: str,
    current_user: User = Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service),
) -> APIResponse[BrowserCookieInventoryResponse]:
    result = await browser_service.list_project_cookie_inventory(current_user.id, project_id)
    return APIResponse.success(BrowserCookieInventoryResponse(**result))


@router.post("/projects/{project_id}/cookies/capture", response_model=APIResponse[BrowserCookieMutationResponse])
async def capture_live_browser_cookies(
    project_id: str,
    current_user: User = Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service),
) -> APIResponse[BrowserCookieMutationResponse]:
    result = await browser_service.capture_live_cookies(current_user.id, project_id)
    return APIResponse.success(BrowserCookieMutationResponse(**result))


@router.post("/projects/{project_id}/cookies/apply", response_model=APIResponse[BrowserCookieMutationResponse])
async def apply_project_browser_cookies(
    project_id: str,
    current_user: User = Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service),
) -> APIResponse[BrowserCookieMutationResponse]:
    result = await browser_service.apply_project_cookies(current_user.id, project_id)
    return APIResponse.success(BrowserCookieMutationResponse(**result))


@router.delete("/projects/{project_id}/cookies/project", response_model=APIResponse[BrowserCookieMutationResponse])
async def clear_all_project_browser_cookies(
    project_id: str,
    current_user: User = Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service),
) -> APIResponse[BrowserCookieMutationResponse]:
    result = await browser_service.clear_project_cookies(current_user.id, project_id)
    return APIResponse.success(BrowserCookieMutationResponse(**result))


@router.delete("/projects/{project_id}/cookies/project/{domain:path}", response_model=APIResponse[BrowserCookieMutationResponse])
async def clear_project_browser_cookies_for_domain(
    project_id: str,
    domain: str,
    current_user: User = Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service),
) -> APIResponse[BrowserCookieMutationResponse]:
    result = await browser_service.clear_project_cookies(current_user.id, project_id, domain)
    return APIResponse.success(BrowserCookieMutationResponse(**result))


@router.delete("/projects/{project_id}/cookies/live", response_model=APIResponse[BrowserCookieMutationResponse])
async def clear_all_live_browser_cookies(
    project_id: str,
    current_user: User = Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service),
) -> APIResponse[BrowserCookieMutationResponse]:
    result = await browser_service.clear_live_cookies(current_user.id, project_id)
    return APIResponse.success(BrowserCookieMutationResponse(**result))


@router.delete("/projects/{project_id}/cookies/live/{domain:path}", response_model=APIResponse[BrowserCookieMutationResponse])
async def clear_live_browser_cookies_for_domain(
    project_id: str,
    domain: str,
    current_user: User = Depends(get_current_user),
    browser_service: BrowserService = Depends(get_browser_service),
) -> APIResponse[BrowserCookieMutationResponse]:
    result = await browser_service.clear_live_cookies(current_user.id, project_id, domain)
    return APIResponse.success(BrowserCookieMutationResponse(**result))
