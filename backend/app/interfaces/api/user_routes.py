from fastapi import APIRouter, Depends

from app.application.services.auth_service import AuthService
from app.domain.models.user import User
from app.interfaces.dependencies import get_auth_service, get_current_user
from app.interfaces.schemas.base import APIResponse
from app.interfaces.schemas.user import PrivacySettingsResponse, UpdatePrivacySettingsRequest

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/privacy", response_model=APIResponse[PrivacySettingsResponse])
async def get_privacy_settings(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> APIResponse[PrivacySettingsResponse]:
    user = await auth_service.get_privacy_settings(current_user)
    return APIResponse.success(PrivacySettingsResponse.from_user(user))


@router.put("/privacy", response_model=APIResponse[PrivacySettingsResponse])
async def update_privacy_settings(
    request: UpdatePrivacySettingsRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> APIResponse[PrivacySettingsResponse]:
    user = await auth_service.update_privacy_settings(current_user, request.help_improve)
    return APIResponse.success(PrivacySettingsResponse.from_user(user))
