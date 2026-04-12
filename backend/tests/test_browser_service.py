import pytest

from app.application.errors.exceptions import BadRequestError, NotFoundError
from app.application.services.browser_service import BrowserService
from app.domain.models.project import BrowserPoolEntry, Project


class InMemoryProjectRepository:
    def __init__(self):
        self.projects: dict[str, Project] = {}

    async def save(self, project: Project) -> None:
        self.projects[project.id] = project.model_copy(deep=True)

    async def find_by_id_and_user_id(self, project_id: str, user_id: str):
        project = self.projects.get(project_id)
        if not project or project.user_id != user_id:
            return None
        return project.model_copy(deep=True)


class StubBrowserService(BrowserService):
    async def _resolve_browser_connection(self, cdp_url: str):
        if "unhealthy" in cdp_url:
            raise BadRequestError("Browser unavailable")
        return ({"Browser": "Chrome/123"}, "ws://example.test/devtools")

    def _cdp_session(self, ws_url: str):  # type: ignore[override]
        return _StubCDPSession()


class _StubCDPClient:
    async def send(self, method: str, params=None):
        if method == "Target.getTargets":
            return {"targetInfos": [{"type": "page"}]}
        if method == "Storage.getCookies":
            return {"cookies": [{"name": "sid", "value": "1", "domain": "example.com", "path": "/"}]}
        return {}


class _StubCDPSession:
    async def __aenter__(self):
        return _StubCDPClient()

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_browser_pool_add_activate_and_remove_flow():
    repository = InMemoryProjectRepository()
    project = Project(user_id="user-1", name="Browser Ops", color="#111111")
    await repository.save(project)
    service = StubBrowserService(repository)

    pool = await service.add_browser_pool_entry(
        "user-1",
        project.id,
        label="Primary Browser",
        cdp_url="http://127.0.0.1:9222",
        source="manual",
        set_active=True,
    )

    assert pool["active_browser_id"] is not None
    assert pool["browsers"][0]["healthy"] is True

    second_pool = await service.add_browser_pool_entry(
        "user-1",
        project.id,
        label="Standby Browser",
        cdp_url="http://127.0.0.1:9333",
        source="manual",
        set_active=False,
    )
    second_id = next(browser["browser_id"] for browser in second_pool["browsers"] if browser["label"] == "Standby Browser")

    activated = await service.activate_browser_pool_entry("user-1", project.id, second_id)
    assert next(browser for browser in activated["browsers"] if browser["browser_id"] == second_id)["active"] is True

    removed = await service.remove_browser_pool_entry("user-1", project.id, second_id)
    assert all(browser["browser_id"] != second_id for browser in removed["browsers"])


@pytest.mark.asyncio
async def test_browser_pool_reports_unhealthy_entries_without_failing_inventory():
    repository = InMemoryProjectRepository()
    project = Project(
        user_id="user-1",
        name="Browser Ops",
        color="#111111",
        browser_pool=[BrowserPoolEntry(label="Broken", cdp_url="http://unhealthy.test:9222")],
    )
    await repository.save(project)
    service = StubBrowserService(repository)

    pool = await service.list_browser_pool("user-1", project.id)

    assert pool["browsers"][0]["healthy"] is False
    assert "Browser unavailable" in (pool["browsers"][0]["error"] or "")


@pytest.mark.asyncio
async def test_browser_pool_rejects_invalid_urls():
    repository = InMemoryProjectRepository()
    project = Project(user_id="user-1", name="Browser Ops", color="#111111")
    await repository.save(project)
    service = StubBrowserService(repository)

    with pytest.raises(BadRequestError):
        await service.add_browser_pool_entry(
            "user-1",
            project.id,
            label="Broken",
            cdp_url="localhost:9222",
            source="manual",
            set_active=False,
        )


@pytest.mark.asyncio
async def test_browser_pool_missing_entry_raises_not_found():
    repository = InMemoryProjectRepository()
    project = Project(user_id="user-1", name="Browser Ops", color="#111111")
    await repository.save(project)
    service = StubBrowserService(repository)

    with pytest.raises(NotFoundError):
        await service.activate_browser_pool_entry("user-1", project.id, "missing")
