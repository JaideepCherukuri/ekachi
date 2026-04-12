from fastapi import APIRouter, Depends

from app.application.services.project_service import ProjectService
from app.domain.models.user import User
from app.interfaces.dependencies import get_current_user, get_project_service
from app.interfaces.schemas.base import APIResponse
from app.interfaces.schemas.project import (
    BrowserPoolEntryResponse,
    CreateProjectRequest,
    ListProjectsResponse,
    ProjectResponse,
    UpdateProjectRequest,
)


router = APIRouter(prefix="/projects", tags=["projects"])


def _to_response(project) -> ProjectResponse:
    return ProjectResponse(
        project_id=project.id,
        name=project.name,
        color=project.color,
        default_provider_id=project.default_provider_id,
        default_model_name=project.default_model_name,
        preferred_search_provider=project.preferred_search_provider,
        preferred_browser_engine=project.preferred_browser_engine,
        browser_cdp_url=project.browser_cdp_url,
        browser_pool=[
            BrowserPoolEntryResponse(
                browser_id=browser.id,
                label=browser.label,
                cdp_url=browser.cdp_url,
                source=browser.source,
                created_at=browser.created_at,
                updated_at=browser.updated_at,
            )
            for browser in project.browser_pool
        ],
        browser_cookie_profile=project.browser_cookie_profile,
        browser_extension_paths=project.browser_extension_paths,
        browser_cookies=project.browser_cookies,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("", response_model=APIResponse[ListProjectsResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> APIResponse[ListProjectsResponse]:
    projects = await project_service.list_projects(current_user.id)
    return APIResponse.success(ListProjectsResponse(projects=[_to_response(project) for project in projects]))


@router.post("", response_model=APIResponse[ProjectResponse])
async def create_project(
    request: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> APIResponse[ProjectResponse]:
    project = await project_service.create_project(
        current_user.id,
        request.name,
        request.color,
        request.default_provider_id,
        request.default_model_name,
        request.preferred_search_provider,
        request.preferred_browser_engine,
        request.browser_cdp_url,
        [item.model_dump() for item in request.browser_pool],
        request.browser_cookie_profile,
        request.browser_extension_paths,
        request.browser_cookies,
    )
    return APIResponse.success(_to_response(project))


@router.patch("/{project_id}", response_model=APIResponse[ProjectResponse])
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> APIResponse[ProjectResponse]:
    project = await project_service.update_project(
        project_id=project_id,
        user_id=current_user.id,
        name=request.name,
        color=request.color,
        default_provider_id=request.default_provider_id,
        default_model_name=request.default_model_name,
        preferred_search_provider=request.preferred_search_provider,
        preferred_browser_engine=request.preferred_browser_engine,
        browser_cdp_url=request.browser_cdp_url,
        browser_pool=[item.model_dump() for item in request.browser_pool] if request.browser_pool is not None else None,
        browser_cookie_profile=request.browser_cookie_profile,
        browser_extension_paths=request.browser_extension_paths,
        browser_cookies=request.browser_cookies,
    )
    return APIResponse.success(_to_response(project))


@router.delete("/{project_id}", response_model=APIResponse[None])
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
) -> APIResponse[None]:
    await project_service.delete_project(project_id, current_user.id)
    return APIResponse.success()
