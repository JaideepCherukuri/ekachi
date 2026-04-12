from pydantic import BaseModel


class UpdatePrivacySettingsRequest(BaseModel):
    help_improve: bool = False


class PrivacySettingsResponse(BaseModel):
    help_improve: bool = False

    @staticmethod
    def from_user(user) -> "PrivacySettingsResponse":
        return PrivacySettingsResponse(help_improve=user.help_improve)
