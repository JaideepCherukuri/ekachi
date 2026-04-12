from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProviderResponse(BaseModel):
    provider_id: str
    label: str
    model_provider: str
    api_base: Optional[str] = None
    available_models: List[str]
    default_model_name: str
    enabled: bool
    is_system: bool
    has_api_key: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ListProvidersResponse(BaseModel):
    providers: List[ProviderResponse]


class CreateProviderRequest(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    model_provider: str = Field(min_length=1, max_length=32)
    api_base: Optional[str] = Field(default=None, max_length=2048)
    api_key: Optional[str] = Field(default=None, max_length=4096)
    available_models: List[str] = Field(default_factory=list)
    default_model_name: Optional[str] = Field(default=None, max_length=256)
    enabled: bool = True


class UpdateProviderRequest(BaseModel):
    label: Optional[str] = Field(default=None, min_length=1, max_length=80)
    model_provider: Optional[str] = Field(default=None, min_length=1, max_length=32)
    api_base: Optional[str] = Field(default=None, max_length=2048)
    api_key: Optional[str] = Field(default=None, max_length=4096)
    clear_api_key: bool = False
    available_models: Optional[List[str]] = None
    default_model_name: Optional[str] = Field(default=None, max_length=256)
    enabled: Optional[bool] = None


class TestProviderRequest(BaseModel):
    model_name: Optional[str] = Field(default=None, max_length=256)


class TestProviderResponse(BaseModel):
    provider_id: str
    model_name: str
    ok: bool = True
