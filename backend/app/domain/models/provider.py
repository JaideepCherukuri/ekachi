from datetime import UTC, datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field, field_validator, model_validator


SYSTEM_PROVIDER_ID = "system"


class Provider(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    user_id: str
    label: str
    model_provider: str
    api_base: Optional[str] = None
    encrypted_api_key: Optional[str] = None
    available_models: List[str] = Field(default_factory=list)
    default_model_name: Optional[str] = None
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("label", "model_provider")
    @classmethod
    def _strip_required_text(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Provider fields may not be empty")
        return trimmed

    @field_validator("api_base")
    @classmethod
    def _normalize_api_base(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @field_validator("available_models")
    @classmethod
    def _normalize_available_models(cls, value: List[str]) -> List[str]:
        models: List[str] = []
        seen: set[str] = set()
        for item in value:
            trimmed = item.strip()
            if not trimmed or trimmed in seen:
                continue
            seen.add(trimmed)
            models.append(trimmed)
        if not models:
            raise ValueError("At least one model must be configured")
        return models

    @field_validator("default_model_name")
    @classmethod
    def _normalize_default_model_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @model_validator(mode="after")
    def _validate_default_model(self) -> "Provider":
        if self.default_model_name and self.default_model_name not in self.available_models:
            raise ValueError("Default model must be one of the configured available models")
        return self


class ProviderRuntimeConfig(BaseModel):
    provider_id: str
    label: str
    model_provider: str
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    available_models: List[str] = Field(default_factory=list)
    default_model_name: str
    enabled: bool = True
    is_system: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
