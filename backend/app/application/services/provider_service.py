import asyncio
import logging
import re
from datetime import UTC, datetime
from typing import List, Optional

from langchain.messages import HumanMessage

from app.application.errors.exceptions import BadRequestError, NotFoundError, ValidationError
from app.application.services.secret_cipher import SecretCipher
from app.core.config import get_settings
from app.domain.models.provider import Provider, ProviderRuntimeConfig, SYSTEM_PROVIDER_ID
from app.domain.repositories.provider_repository import ProviderRepository
from app.domain.services.model_factory import SUPPORTED_MODEL_PROVIDERS, build_chat_model


logger = logging.getLogger(__name__)


class ProviderService:
    def __init__(self, provider_repository: ProviderRepository, secret_cipher: SecretCipher):
        self._provider_repository = provider_repository
        self._secret_cipher = secret_cipher

    def encrypt_api_key(self, api_key: str) -> str:
        return self._secret_cipher.encrypt(api_key)

    def _validate_model_provider(self, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in SUPPORTED_MODEL_PROVIDERS:
            raise ValidationError(f"Unsupported model provider: {value}")
        return normalized

    def _validate_label(self, value: str) -> str:
        label = value.strip()
        if not label:
            raise ValidationError("Provider label is required")
        if len(label) > 80:
            raise ValidationError("Provider label must be 80 characters or fewer")
        return label

    def _normalize_api_base(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            return None
        if not re.match(r"^https?://|^http?://", trimmed):
            if trimmed.startswith("localhost:") or trimmed.startswith("127.0.0.1:"):
                return f"http://{trimmed}"
        return trimmed

    def _normalize_available_models(self, available_models: List[str]) -> List[str]:
        models: List[str] = []
        seen: set[str] = set()
        for model in available_models:
            trimmed = model.strip()
            if not trimmed or trimmed in seen:
                continue
            seen.add(trimmed)
            models.append(trimmed)
        if not models:
            raise ValidationError("At least one model must be configured")
        return models

    def _normalize_default_model_name(self, default_model_name: Optional[str], available_models: List[str]) -> str:
        trimmed = default_model_name.strip() if default_model_name else ""
        if not trimmed:
            return available_models[0]
        if trimmed not in available_models:
            raise ValidationError("Default model must be one of the configured available models")
        return trimmed

    def get_system_provider(self) -> ProviderRuntimeConfig:
        settings = get_settings()
        available_models = settings.available_models or [settings.model_name]
        return ProviderRuntimeConfig(
            provider_id=SYSTEM_PROVIDER_ID,
            label="System Runtime",
            model_provider=settings.model_provider,
            api_base=settings.api_base,
            api_key=settings.api_key,
            available_models=available_models,
            default_model_name=settings.model_name,
            enabled=True,
            is_system=True,
            created_at=None,
            updated_at=None,
        )

    def _runtime_from_provider(self, provider: Provider) -> ProviderRuntimeConfig:
        return ProviderRuntimeConfig(
            provider_id=provider.id,
            label=provider.label,
            model_provider=provider.model_provider,
            api_base=provider.api_base,
            api_key=self._secret_cipher.decrypt(provider.encrypted_api_key) if provider.encrypted_api_key else None,
            available_models=list(provider.available_models),
            default_model_name=provider.default_model_name or provider.available_models[0],
            enabled=provider.enabled,
            is_system=False,
            created_at=provider.created_at,
            updated_at=provider.updated_at,
        )

    async def list_providers(self, user_id: str) -> List[ProviderRuntimeConfig]:
        custom_providers = await self._provider_repository.find_by_user_id(user_id)
        ordered = sorted(custom_providers, key=lambda item: item.updated_at, reverse=True)
        return [self.get_system_provider(), *[self._runtime_from_provider(provider) for provider in ordered]]

    async def get_provider(self, user_id: str, provider_id: str) -> ProviderRuntimeConfig:
        if provider_id == SYSTEM_PROVIDER_ID:
            return self.get_system_provider()
        provider = await self._provider_repository.find_by_id_and_user_id(provider_id, user_id)
        if not provider:
            raise NotFoundError("Provider not found")
        return self._runtime_from_provider(provider)

    async def resolve_runtime_config(
        self,
        *,
        user_id: str,
        provider_id: Optional[str] = None,
        model_name: Optional[str] = None,
        allow_disabled: bool = False,
    ) -> ProviderRuntimeConfig:
        runtime = await self.get_provider(user_id, provider_id or SYSTEM_PROVIDER_ID)
        if not allow_disabled and not runtime.enabled:
            raise BadRequestError("Provider is disabled")

        selected_model = model_name.strip() if model_name else ""
        if selected_model and selected_model not in runtime.available_models:
            raise BadRequestError(f"Unsupported model for provider {runtime.label}: {selected_model}")
        runtime.default_model_name = selected_model or runtime.default_model_name
        return runtime

    async def create_provider(
        self,
        *,
        user_id: str,
        label: str,
        model_provider: str,
        api_base: Optional[str],
        api_key: Optional[str],
        available_models: List[str],
        default_model_name: Optional[str],
        enabled: bool,
    ) -> ProviderRuntimeConfig:
        normalized_models = self._normalize_available_models(available_models)
        provider = Provider(
            user_id=user_id,
            label=self._validate_label(label),
            model_provider=self._validate_model_provider(model_provider),
            api_base=self._normalize_api_base(api_base),
            encrypted_api_key=self._secret_cipher.encrypt(api_key.strip()) if api_key and api_key.strip() else None,
            available_models=normalized_models,
            default_model_name=self._normalize_default_model_name(default_model_name, normalized_models),
            enabled=enabled,
        )
        await self._provider_repository.save(provider)
        return self._runtime_from_provider(provider)

    async def update_provider(
        self,
        *,
        user_id: str,
        provider_id: str,
        label: Optional[str] = None,
        model_provider: Optional[str] = None,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        clear_api_key: bool = False,
        available_models: Optional[List[str]] = None,
        default_model_name: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> ProviderRuntimeConfig:
        provider = await self._provider_repository.find_by_id_and_user_id(provider_id, user_id)
        if not provider:
            raise NotFoundError("Provider not found")

        if label is not None:
            provider.label = self._validate_label(label)
        if model_provider is not None:
            provider.model_provider = self._validate_model_provider(model_provider)
        if api_base is not None:
            provider.api_base = self._normalize_api_base(api_base)
        if clear_api_key:
            provider.encrypted_api_key = None
        elif api_key is not None:
            trimmed_api_key = api_key.strip()
            provider.encrypted_api_key = self._secret_cipher.encrypt(trimmed_api_key) if trimmed_api_key else None
        if available_models is not None:
            provider.available_models = self._normalize_available_models(available_models)
        if default_model_name is not None or available_models is not None:
            provider.default_model_name = self._normalize_default_model_name(default_model_name or provider.default_model_name, provider.available_models)
        if enabled is not None:
            provider.enabled = enabled
        provider.updated_at = datetime.now(UTC)

        await self._provider_repository.save(provider)
        return self._runtime_from_provider(provider)

    async def delete_provider(self, *, user_id: str, provider_id: str) -> None:
        provider = await self._provider_repository.find_by_id_and_user_id(provider_id, user_id)
        if not provider:
            raise NotFoundError("Provider not found")
        await self._provider_repository.delete(provider_id)

    async def test_provider(
        self,
        *,
        user_id: str,
        provider_id: str,
        model_name: Optional[str] = None,
    ) -> ProviderRuntimeConfig:
        runtime = await self.resolve_runtime_config(user_id=user_id, provider_id=provider_id, model_name=model_name)
        model = build_chat_model(
            model_name=runtime.default_model_name,
            model_provider=runtime.model_provider,
            temperature=0,
            max_tokens=32,
            api_base=runtime.api_base,
            api_key=runtime.api_key,
            default_headers=get_settings().extra_headers,
        )
        await asyncio.wait_for(
            model.ainvoke([HumanMessage(content="Reply with OK only.")]),
            timeout=30,
        )
        return runtime
