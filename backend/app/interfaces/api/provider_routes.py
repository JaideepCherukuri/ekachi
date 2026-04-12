from fastapi import APIRouter, Depends

from app.application.services.provider_service import ProviderService
from app.domain.models.provider import SYSTEM_PROVIDER_ID
from app.domain.models.user import User
from app.interfaces.dependencies import get_current_user, get_provider_service
from app.interfaces.schemas.base import APIResponse
from app.interfaces.schemas.provider import (
    CreateProviderRequest,
    ListProvidersResponse,
    ProviderResponse,
    TestProviderRequest,
    TestProviderResponse,
    UpdateProviderRequest,
)


router = APIRouter(prefix="/providers", tags=["providers"])


def _to_response(runtime) -> ProviderResponse:
    return ProviderResponse(
        provider_id=runtime.provider_id,
        label=runtime.label,
        model_provider=runtime.model_provider,
        api_base=runtime.api_base,
        available_models=runtime.available_models,
        default_model_name=runtime.default_model_name,
        enabled=runtime.enabled,
        is_system=runtime.is_system,
        has_api_key=bool(runtime.api_key),
        created_at=runtime.created_at,
        updated_at=runtime.updated_at,
    )


@router.get("", response_model=APIResponse[ListProvidersResponse])
async def list_providers(
    current_user: User = Depends(get_current_user),
    provider_service: ProviderService = Depends(get_provider_service),
) -> APIResponse[ListProvidersResponse]:
    providers = await provider_service.list_providers(current_user.id)
    return APIResponse.success(ListProvidersResponse(providers=[_to_response(provider) for provider in providers]))


@router.post("", response_model=APIResponse[ProviderResponse])
async def create_provider(
    request: CreateProviderRequest,
    current_user: User = Depends(get_current_user),
    provider_service: ProviderService = Depends(get_provider_service),
) -> APIResponse[ProviderResponse]:
    provider = await provider_service.create_provider(
        user_id=current_user.id,
        label=request.label,
        model_provider=request.model_provider,
        api_base=request.api_base,
        api_key=request.api_key,
        available_models=request.available_models,
        default_model_name=request.default_model_name,
        enabled=request.enabled,
    )
    return APIResponse.success(_to_response(provider))


@router.patch("/{provider_id}", response_model=APIResponse[ProviderResponse])
async def update_provider(
    provider_id: str,
    request: UpdateProviderRequest,
    current_user: User = Depends(get_current_user),
    provider_service: ProviderService = Depends(get_provider_service),
) -> APIResponse[ProviderResponse]:
    provider = await provider_service.update_provider(
        user_id=current_user.id,
        provider_id=provider_id,
        label=request.label,
        model_provider=request.model_provider,
        api_base=request.api_base,
        api_key=request.api_key,
        clear_api_key=request.clear_api_key,
        available_models=request.available_models,
        default_model_name=request.default_model_name,
        enabled=request.enabled,
    )
    return APIResponse.success(_to_response(provider))


@router.delete("/{provider_id}", response_model=APIResponse[None])
async def delete_provider(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    provider_service: ProviderService = Depends(get_provider_service),
) -> APIResponse[None]:
    await provider_service.delete_provider(user_id=current_user.id, provider_id=provider_id)
    return APIResponse.success()


@router.post("/{provider_id}/test", response_model=APIResponse[TestProviderResponse])
async def test_provider(
    provider_id: str,
    request: TestProviderRequest,
    current_user: User = Depends(get_current_user),
    provider_service: ProviderService = Depends(get_provider_service),
) -> APIResponse[TestProviderResponse]:
    runtime = await provider_service.test_provider(
        user_id=current_user.id,
        provider_id=provider_id,
        model_name=request.model_name,
    )
    return APIResponse.success(
        TestProviderResponse(
            provider_id=runtime.provider_id,
            model_name=runtime.default_model_name,
            ok=True,
        )
    )
