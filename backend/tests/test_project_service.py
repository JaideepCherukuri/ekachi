import pytest

from app.application.errors.exceptions import BadRequestError
from app.application.services.project_service import ProjectService
from app.application.services.provider_service import ProviderService
from app.application.services.secret_cipher import SecretCipher
from app.domain.models.project import Project
from app.domain.models.provider import Provider


class InMemoryProjectRepository:
    def __init__(self):
        self.projects: dict[str, Project] = {}

    async def save(self, project: Project) -> None:
        self.projects[project.id] = project.model_copy(deep=True)

    async def find_by_user_id(self, user_id: str):
        return [project.model_copy(deep=True) for project in self.projects.values() if project.user_id == user_id]

    async def find_by_id_and_user_id(self, project_id: str, user_id: str):
        project = self.projects.get(project_id)
        if not project or project.user_id != user_id:
            return None
        return project.model_copy(deep=True)

    async def delete(self, project_id: str) -> None:
        self.projects.pop(project_id, None)


class NoopSessionRepository:
    async def update_project_for_user_sessions(self, **kwargs) -> None:
        return None

    async def clear_project_for_user_sessions(self, user_id: str, project_id: str) -> None:
        return None


class NoopTriggerRepository:
    async def clear_project_for_user_triggers(self, user_id: str, project_id: str) -> None:
        return None

    async def clear_project_for_user_runs(self, user_id: str, project_id: str) -> None:
        return None


class NoopCapabilityRepository:
    async def clear_project_for_user_capabilities(self, user_id: str, project_id: str) -> None:
        return None


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
async def test_create_project_accepts_custom_provider_backed_default_model():
    provider_repository = InMemoryProviderRepository()
    provider_service = ProviderService(provider_repository, SecretCipher("jwt-secret"))
    provider = await provider_service.create_provider(
        user_id="user-1",
        label="Anthropic",
        model_provider="anthropic",
        api_base=None,
        api_key="anthropic-key",
        available_models=["claude-sonnet-4-5"],
        default_model_name="claude-sonnet-4-5",
        enabled=True,
    )
    service = ProjectService(
        project_repository=InMemoryProjectRepository(),
        session_repository=NoopSessionRepository(),
        trigger_repository=NoopTriggerRepository(),
        capability_repository=NoopCapabilityRepository(),
        provider_service=provider_service,
    )

    project = await service.create_project(
        user_id="user-1",
        name="Research",
        color="#000000",
        default_provider_id=provider.provider_id,
        default_model_name="claude-sonnet-4-5",
    )

    assert project.default_provider_id == provider.provider_id
    assert project.default_model_name == "claude-sonnet-4-5"


@pytest.mark.asyncio
async def test_create_project_rejects_disabled_provider():
    provider_repository = InMemoryProviderRepository()
    provider_service = ProviderService(provider_repository, SecretCipher("jwt-secret"))
    provider = await provider_service.create_provider(
        user_id="user-1",
        label="Disabled",
        model_provider="openai",
        api_base="https://api.openai.com/v1",
        api_key="sk-secret",
        available_models=["gpt-5.4"],
        default_model_name="gpt-5.4",
        enabled=False,
    )
    service = ProjectService(
        project_repository=InMemoryProjectRepository(),
        session_repository=NoopSessionRepository(),
        trigger_repository=NoopTriggerRepository(),
        capability_repository=NoopCapabilityRepository(),
        provider_service=provider_service,
    )

    with pytest.raises(BadRequestError):
        await service.create_project(
            user_id="user-1",
            name="Blocked",
            color="#111111",
            default_provider_id=provider.provider_id,
            default_model_name="gpt-5.4",
        )
