from datetime import UTC, datetime
import logging
from typing import List, Optional
from urllib.parse import urlparse

from app.application.errors.exceptions import BadRequestError
from app.application.services.provider_service import ProviderService
from app.domain.models.project import BrowserPoolEntry, Project
from app.domain.models.provider import SYSTEM_PROVIDER_ID
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.session_repository import SessionRepository
from app.domain.repositories.trigger_repository import TriggerRepository
from app.domain.repositories.capability_repository import CapabilityRepository


logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        session_repository: SessionRepository,
        trigger_repository: TriggerRepository,
        capability_repository: CapabilityRepository,
        provider_service: ProviderService,
    ):
        self._project_repository = project_repository
        self._session_repository = session_repository
        self._trigger_repository = trigger_repository
        self._capability_repository = capability_repository
        self._provider_service = provider_service

    async def list_projects(self, user_id: str) -> List[Project]:
        return await self._project_repository.find_by_user_id(user_id)

    async def get_project(self, project_id: str, user_id: str) -> Optional[Project]:
        return await self._project_repository.find_by_id_and_user_id(project_id, user_id)

    async def create_project(
        self,
        user_id: str,
        name: str,
        color: str,
        default_provider_id: Optional[str] = None,
        default_model_name: Optional[str] = None,
        preferred_search_provider: Optional[str] = None,
        preferred_browser_engine: Optional[str] = None,
        browser_cdp_url: Optional[str] = None,
        browser_pool: Optional[List[dict]] = None,
        browser_cookie_profile: Optional[str] = None,
        browser_extension_paths: Optional[List[str]] = None,
        browser_cookies: Optional[List[dict]] = None,
    ) -> Project:
        trimmed_name = name.strip()
        if not trimmed_name:
            raise BadRequestError("Project name is required")
        await self._validate_runtime_preferences(
            user_id=user_id,
            default_provider_id=default_provider_id,
            default_model_name=default_model_name,
            preferred_search_provider=preferred_search_provider,
            preferred_browser_engine=preferred_browser_engine,
            browser_cdp_url=browser_cdp_url,
            browser_pool=browser_pool,
            browser_extension_paths=browser_extension_paths,
        )
        project = Project(
            user_id=user_id,
            name=trimmed_name,
            color=color,
            default_provider_id=default_provider_id or None,
            default_model_name=default_model_name,
            preferred_search_provider=preferred_search_provider,
            preferred_browser_engine=preferred_browser_engine,
            browser_cdp_url=self._normalize_browser_cdp_url(browser_cdp_url),
            browser_pool=self._normalize_browser_pool(browser_pool, self._normalize_browser_cdp_url(browser_cdp_url)),
            browser_cookie_profile=self._normalize_browser_cookie_profile(browser_cookie_profile),
            browser_extension_paths=self._normalize_browser_extension_paths(browser_extension_paths),
            browser_cookies=self._normalize_browser_cookies(browser_cookies),
        )
        await self._project_repository.save(project)
        return project

    async def update_project(
        self,
        project_id: str,
        user_id: str,
        name: Optional[str] = None,
        color: Optional[str] = None,
        default_provider_id: Optional[str] = None,
        default_model_name: Optional[str] = None,
        preferred_search_provider: Optional[str] = None,
        preferred_browser_engine: Optional[str] = None,
        browser_cdp_url: Optional[str] = None,
        browser_pool: Optional[List[dict]] = None,
        browser_cookie_profile: Optional[str] = None,
        browser_extension_paths: Optional[List[str]] = None,
        browser_cookies: Optional[List[dict]] = None,
    ) -> Project:
        project = await self._project_repository.find_by_id_and_user_id(project_id, user_id)
        if not project:
            raise RuntimeError("Project not found")

        if name is not None:
            trimmed_name = name.strip()
            if not trimmed_name:
                raise BadRequestError("Project name is required")
            project.name = trimmed_name
        if color is not None:
            project.color = color
        await self._validate_runtime_preferences(
            user_id=user_id,
            default_provider_id=default_provider_id,
            default_model_name=default_model_name,
            preferred_search_provider=preferred_search_provider,
            preferred_browser_engine=preferred_browser_engine,
            browser_cdp_url=browser_cdp_url,
            browser_pool=browser_pool,
            browser_extension_paths=browser_extension_paths,
        )
        if default_provider_id is not None:
            project.default_provider_id = default_provider_id or None
        if default_model_name is not None:
            project.default_model_name = default_model_name or None
        if preferred_search_provider is not None:
            project.preferred_search_provider = preferred_search_provider or None
        if preferred_browser_engine is not None:
            project.preferred_browser_engine = preferred_browser_engine or None
        if browser_cdp_url is not None:
            project.browser_cdp_url = self._normalize_browser_cdp_url(browser_cdp_url)
        if browser_pool is not None:
            project.browser_pool = self._normalize_browser_pool(browser_pool, project.browser_cdp_url)
        if browser_cookie_profile is not None:
            project.browser_cookie_profile = self._normalize_browser_cookie_profile(browser_cookie_profile)
        if browser_extension_paths is not None:
            project.browser_extension_paths = self._normalize_browser_extension_paths(browser_extension_paths)
        if browser_cookies is not None:
            project.browser_cookies = self._normalize_browser_cookies(browser_cookies)
        project.updated_at = datetime.now(UTC)

        await self._project_repository.save(project)
        await self._session_repository.update_project_for_user_sessions(
            user_id=user_id,
            project_id=project.id,
            project_name=project.name,
            project_color=project.color,
        )
        return project

    async def delete_project(self, project_id: str, user_id: str) -> None:
        project = await self._project_repository.find_by_id_and_user_id(project_id, user_id)
        if not project:
            raise RuntimeError("Project not found")

        await self._project_repository.delete(project_id)
        await self._session_repository.clear_project_for_user_sessions(user_id, project_id)
        await self._trigger_repository.clear_project_for_user_triggers(user_id, project_id)
        await self._trigger_repository.clear_project_for_user_runs(user_id, project_id)
        await self._capability_repository.clear_project_for_user_capabilities(user_id, project_id)

    async def _validate_runtime_preferences(
        self,
        user_id: str,
        default_provider_id: Optional[str],
        default_model_name: Optional[str],
        preferred_search_provider: Optional[str],
        preferred_browser_engine: Optional[str],
        browser_cdp_url: Optional[str] = None,
        browser_pool: Optional[List[dict]] = None,
        browser_extension_paths: Optional[List[str]] = None,
    ) -> None:
        if default_provider_id is not None or default_model_name:
            runtime = await self._provider_service.resolve_runtime_config(
                user_id=user_id,
                provider_id=default_provider_id or SYSTEM_PROVIDER_ID,
                model_name=default_model_name or None,
                allow_disabled=True,
            )
            if runtime.provider_id != SYSTEM_PROVIDER_ID and not runtime.enabled:
                raise BadRequestError("Project default provider must be enabled")
        if preferred_search_provider:
            supported_search_providers = {"google", "bing", "bing_web", "baidu", "baidu_web", "tavily"}
            if preferred_search_provider not in supported_search_providers:
                raise BadRequestError(f"Unsupported search provider: {preferred_search_provider}")
        if preferred_browser_engine:
            supported_browser_engines = {"browser_use", "playwright"}
            if preferred_browser_engine not in supported_browser_engines:
                raise BadRequestError(f"Unsupported browser engine: {preferred_browser_engine}")
        if browser_cdp_url:
            parsed = urlparse(browser_cdp_url.strip())
            if parsed.scheme not in {"http", "https", "ws", "wss"} or not parsed.netloc:
                raise BadRequestError("Browser CDP URL must be a valid http(s) or ws(s) URL")
        if browser_pool is not None:
            normalized_pool = self._normalize_browser_pool(browser_pool, self._normalize_browser_cdp_url(browser_cdp_url))
            for browser in normalized_pool:
                parsed = urlparse(browser.cdp_url.strip())
                if parsed.scheme not in {"http", "https", "ws", "wss"} or not parsed.netloc:
                    raise BadRequestError("Browser pool entries must use valid http(s) or ws(s) URLs")
            if len(normalized_pool) > 20:
                raise BadRequestError("At most 20 browser endpoints may be configured in the browser pool")
        if browser_extension_paths is not None:
            normalized = self._normalize_browser_extension_paths(browser_extension_paths)
            if len(normalized) > 20:
                raise BadRequestError("At most 20 browser extension paths may be configured")

    @staticmethod
    def _normalize_browser_cdp_url(browser_cdp_url: Optional[str]) -> Optional[str]:
        if browser_cdp_url is None:
            return None
        trimmed = browser_cdp_url.strip()
        return trimmed or None

    @staticmethod
    def _normalize_browser_cookie_profile(browser_cookie_profile: Optional[str]) -> Optional[str]:
        if browser_cookie_profile is None:
            return None
        trimmed = browser_cookie_profile.strip()
        return trimmed or None

    @staticmethod
    def _normalize_browser_extension_paths(browser_extension_paths: Optional[List[str]]) -> List[str]:
        if not browser_extension_paths:
            return []
        return [path.strip() for path in browser_extension_paths if path and path.strip()]

    @staticmethod
    def _normalize_browser_pool(
        browser_pool: Optional[List[dict]],
        active_cdp_url: Optional[str],
    ) -> List[BrowserPoolEntry]:
        if not browser_pool:
            if active_cdp_url:
                return [
                    BrowserPoolEntry(
                        label="Primary browser",
                        cdp_url=active_cdp_url,
                    )
                ]
            return []

        normalized: list[BrowserPoolEntry] = []
        seen_urls: set[str] = set()
        for item in browser_pool:
            if not isinstance(item, dict):
                continue
            label = str(item.get("label") or "").strip()
            cdp_url = ProjectService._normalize_browser_cdp_url(item.get("cdp_url"))
            source = str(item.get("source") or "manual").strip() or "manual"
            if not label or not cdp_url or cdp_url in seen_urls:
                continue
            seen_urls.add(cdp_url)
            browser_id = str(item.get("id") or item.get("browser_id") or "").strip()
            payload = {
                "label": label,
                "cdp_url": cdp_url,
                "source": source if source in {"manual", "managed"} else "manual",
            }
            if browser_id:
                payload["id"] = browser_id
            normalized.append(
                BrowserPoolEntry(**payload)
            )

        if active_cdp_url and active_cdp_url not in seen_urls:
            normalized.insert(
                0,
                BrowserPoolEntry(
                    label="Primary browser",
                    cdp_url=active_cdp_url,
                ),
            )
        return normalized[:20]

    @staticmethod
    def _normalize_browser_cookies(browser_cookies: Optional[List[dict]]) -> List[dict]:
        if not browser_cookies:
            return []

        normalized: List[dict] = []
        for cookie in browser_cookies:
            if not isinstance(cookie, dict):
                continue
            name = str(cookie.get("name") or "").strip()
            value = str(cookie.get("value") or "")
            domain = str(cookie.get("domain") or "").strip()
            path = str(cookie.get("path") or "/").strip() or "/"
            if not name or not value or not domain:
                continue
            normalized.append(
                {
                    "name": name,
                    "value": value,
                    "domain": domain,
                    "path": path,
                    "httpOnly": bool(cookie.get("httpOnly", False)),
                    "secure": bool(cookie.get("secure", False)),
                    "sameSite": cookie.get("sameSite"),
                    "expires": cookie.get("expires"),
                }
            )
        return normalized[:500]
