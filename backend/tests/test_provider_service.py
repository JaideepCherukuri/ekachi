from datetime import UTC, datetime

import pytest

from app.application.errors.exceptions import BadRequestError, NotFoundError
from app.application.services.provider_service import ProviderService
from app.application.services.secret_cipher import SecretCipher
from app.domain.models.provider import Provider, SYSTEM_PROVIDER_ID


class InMemoryProviderRepository:
    def __init__(self):
        self.providers: dict[str, Provider] = {}

    async def save(self, provider: Provider) -> None:
        self.providers[provider.id] = provider.model_copy(deep=True)

    async def find_by_id(self, provider_id: str):
        provider = self.providers.get(provider_id)
        return provider.model_copy(deep=True) if provider else None

    async def find_by_id_and_user_id(self, provider_id: str, user_id: str):
        provider = self.providers.get(provider_id)
        if not provider or provider.user_id != user_id:
            return None
        return provider.model_copy(deep=True)

    async def find_by_user_id(self, user_id: str):
        return [provider.model_copy(deep=True) for provider in self.providers.values() if provider.user_id == user_id]

    async def delete(self, provider_id: str) -> None:
        self.providers.pop(provider_id, None)


@pytest.mark.asyncio
async def test_create_provider_encrypts_api_key():
    repository = InMemoryProviderRepository()
    service = ProviderService(repository, SecretCipher("jwt-secret"))

    created = await service.create_provider(
        user_id="user-1",
        label="Primary OpenAI",
        model_provider="openai",
        api_base="https://api.openai.com/v1",
        api_key="sk-secret",
        available_models=["gpt-5.4", "gpt-5.4-mini"],
        default_model_name="gpt-5.4",
        enabled=True,
    )

    stored = next(iter(repository.providers.values()))
    assert stored.encrypted_api_key
    assert stored.encrypted_api_key != "sk-secret"
    assert created.api_key == "sk-secret"
    assert created.default_model_name == "gpt-5.4"


@pytest.mark.asyncio
async def test_resolve_runtime_config_rejects_model_not_exposed_by_provider():
    repository = InMemoryProviderRepository()
    service = ProviderService(repository, SecretCipher("jwt-secret"))
    created = await service.create_provider(
        user_id="user-1",
        label="Anthropic Team",
        model_provider="anthropic",
        api_base=None,
        api_key="anthropic-key",
        available_models=["claude-sonnet-4-5"],
        default_model_name="claude-sonnet-4-5",
        enabled=True,
    )

    with pytest.raises(BadRequestError):
        await service.resolve_runtime_config(
            user_id="user-1",
            provider_id=created.provider_id,
            model_name="gpt-5.4",
        )


@pytest.mark.asyncio
async def test_resolve_runtime_config_rejects_disabled_custom_provider():
    repository = InMemoryProviderRepository()
    service = ProviderService(repository, SecretCipher("jwt-secret"))
    created = await service.create_provider(
        user_id="user-1",
        label="Disabled Provider",
        model_provider="openai",
        api_base="https://example.com/v1",
        api_key="sk-secret",
        available_models=["gpt-5.4"],
        default_model_name="gpt-5.4",
        enabled=False,
    )

    with pytest.raises(BadRequestError):
        await service.resolve_runtime_config(user_id="user-1", provider_id=created.provider_id)


@pytest.mark.asyncio
async def test_delete_provider_removes_it():
    repository = InMemoryProviderRepository()
    service = ProviderService(repository, SecretCipher("jwt-secret"))
    created = await service.create_provider(
        user_id="user-1",
        label="Disposable",
        model_provider="openai",
        api_base="https://api.openai.com/v1",
        api_key="sk-secret",
        available_models=["gpt-5.4"],
        default_model_name="gpt-5.4",
        enabled=True,
    )

    await service.delete_provider(user_id="user-1", provider_id=created.provider_id)

    with pytest.raises(NotFoundError):
        await service.get_provider("user-1", created.provider_id)


def test_system_provider_id_constant():
    assert SYSTEM_PROVIDER_ID == "system"
