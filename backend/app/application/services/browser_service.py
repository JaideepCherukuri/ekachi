from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import UTC, datetime
import json
from typing import Any, AsyncIterator, Optional
from urllib.parse import urljoin, urlparse

import httpx
import websockets

from app.application.errors.exceptions import BadRequestError, NotFoundError
from app.domain.models.project import BrowserPoolEntry, Project
from app.domain.repositories.project_repository import ProjectRepository


class BrowserService:
    def __init__(self, project_repository: ProjectRepository):
        self._project_repository = project_repository

    async def list_browser_pool(self, user_id: str, project_id: str) -> dict[str, Any]:
        project = await self._get_project(project_id, user_id)
        browsers: list[dict[str, Any]] = []
        active_browser_id: str | None = None
        active_cdp_url = self._normalize_browser_cdp_url(project.browser_cdp_url)
        for browser in project.browser_pool:
            is_active = browser.cdp_url == active_cdp_url
            if is_active:
                active_browser_id = browser.id
            browsers.append(await self._browser_pool_entry_status(browser, is_active))
        return {
            "active_browser_id": active_browser_id,
            "browsers": browsers,
        }

    async def add_browser_pool_entry(
        self,
        user_id: str,
        project_id: str,
        *,
        label: str,
        cdp_url: str,
        source: str,
        set_active: bool,
    ) -> dict[str, Any]:
        project = await self._get_project(project_id, user_id)
        normalized_label = label.strip()
        normalized_url = self._normalize_browser_cdp_url(cdp_url)
        if not normalized_label:
            raise BadRequestError("Browser label is required")
        if not normalized_url:
            raise BadRequestError("Browser CDP URL is required")
        self._validate_cdp_url(normalized_url)
        if any(entry.cdp_url == normalized_url for entry in project.browser_pool):
            raise BadRequestError("Browser endpoint is already present in the pool")

        browser = BrowserPoolEntry(
            label=normalized_label,
            cdp_url=normalized_url,
            source=source if source in {"manual", "managed"} else "manual",
        )
        project.browser_pool.append(browser)
        if set_active or not project.browser_cdp_url:
            project.browser_cdp_url = normalized_url
        project.updated_at = datetime.now(UTC)
        await self._project_repository.save(project)
        return await self.list_browser_pool(user_id, project_id)

    async def activate_browser_pool_entry(self, user_id: str, project_id: str, browser_id: str) -> dict[str, Any]:
        project = await self._get_project(project_id, user_id)
        browser = next((entry for entry in project.browser_pool if entry.id == browser_id), None)
        if not browser:
            raise NotFoundError("Browser pool entry not found")
        project.browser_cdp_url = browser.cdp_url
        project.updated_at = datetime.now(UTC)
        await self._project_repository.save(project)
        return await self.list_browser_pool(user_id, project_id)

    async def remove_browser_pool_entry(self, user_id: str, project_id: str, browser_id: str) -> dict[str, Any]:
        project = await self._get_project(project_id, user_id)
        browser = next((entry for entry in project.browser_pool if entry.id == browser_id), None)
        if not browser:
            raise NotFoundError("Browser pool entry not found")
        project.browser_pool = [entry for entry in project.browser_pool if entry.id != browser_id]
        if project.browser_cdp_url == browser.cdp_url:
            project.browser_cdp_url = project.browser_pool[0].cdp_url if project.browser_pool else None
        project.updated_at = datetime.now(UTC)
        await self._project_repository.save(project)
        return await self.list_browser_pool(user_id, project_id)

    async def test_connection(self, user_id: str, project_id: str) -> dict[str, Any]:
        project = await self._get_project(project_id, user_id)
        cdp_url = self._get_project_cdp_url(project)
        version_info, ws_url = await self._resolve_browser_connection(cdp_url)
        async with self._cdp_session(ws_url) as client:
            targets = await client.send("Target.getTargets")
            cookies = await client.send("Storage.getCookies")
        return {
            "cdp_url": cdp_url,
            "ws_url": ws_url,
            "browser": version_info.get("Browser"),
            "user_agent": version_info.get("User-Agent"),
            "protocol_version": version_info.get("Protocol-Version"),
            "context_count": len({target.get("browserContextId") for target in targets.get("targetInfos", []) if target.get("browserContextId")}),
            "page_count": len([target for target in targets.get("targetInfos", []) if target.get("type") == "page"]),
            "total_cookie_count": len(cookies.get("cookies", [])),
        }

    async def list_live_cookie_inventory(self, user_id: str, project_id: str) -> dict[str, Any]:
        project = await self._get_project(project_id, user_id)
        cookies = await self._get_live_cookies(self._get_project_cdp_url(project))
        return self._build_cookie_inventory("live", cookies)

    async def list_project_cookie_inventory(self, user_id: str, project_id: str) -> dict[str, Any]:
        project = await self._get_project(project_id, user_id)
        return self._build_cookie_inventory("project", project.browser_cookies)

    async def capture_live_cookies(self, user_id: str, project_id: str) -> dict[str, Any]:
        project = await self._get_project(project_id, user_id)
        cookies = await self._get_live_cookies(self._get_project_cdp_url(project))
        project.browser_cookies = self._normalize_cookies(cookies)
        await self._project_repository.save(project)
        return {
            "captured_count": len(project.browser_cookies),
            "inventory": self._build_cookie_inventory("project", project.browser_cookies),
        }

    async def apply_project_cookies(self, user_id: str, project_id: str) -> dict[str, Any]:
        project = await self._get_project(project_id, user_id)
        cdp_url = self._get_project_cdp_url(project)
        cookies = self._normalize_cookies(project.browser_cookies)
        if not cookies:
            raise BadRequestError("No project cookies are stored for this browser profile")

        _, ws_url = await self._resolve_browser_connection(cdp_url)
        async with self._cdp_session(ws_url) as client:
            await client.send("Storage.setCookies", {"cookies": cookies})
            refreshed = await client.send("Storage.getCookies")
        return {
            "applied_count": len(cookies),
            "inventory": self._build_cookie_inventory("live", refreshed.get("cookies", [])),
        }

    async def clear_project_cookies(
        self,
        user_id: str,
        project_id: str,
        domain: Optional[str] = None,
    ) -> dict[str, Any]:
        project = await self._get_project(project_id, user_id)
        original = list(project.browser_cookies)
        if domain:
            normalized_domain = self._normalize_domain(domain)
            remaining = [
                cookie for cookie in original
                if not self._cookie_matches_domain(str(cookie.get("domain") or ""), normalized_domain)
            ]
        else:
            remaining = []
        removed_count = len(original) - len(remaining)
        project.browser_cookies = remaining
        await self._project_repository.save(project)
        return {
            "removed_count": removed_count,
            "inventory": self._build_cookie_inventory("project", project.browser_cookies),
        }

    async def clear_live_cookies(
        self,
        user_id: str,
        project_id: str,
        domain: Optional[str] = None,
    ) -> dict[str, Any]:
        project = await self._get_project(project_id, user_id)
        cdp_url = self._get_project_cdp_url(project)
        _, ws_url = await self._resolve_browser_connection(cdp_url)
        async with self._cdp_session(ws_url) as client:
            current = (await client.send("Storage.getCookies")).get("cookies", [])
            if domain:
                normalized_domain = self._normalize_domain(domain)
                keep = [
                    cookie for cookie in current
                    if not self._cookie_matches_domain(str(cookie.get("domain") or ""), normalized_domain)
                ]
                await self._clear_all_browser_cookies(client)
                if keep:
                    await client.send("Storage.setCookies", {"cookies": self._normalize_cookies(keep)})
                refreshed = (await client.send("Storage.getCookies")).get("cookies", [])
                removed_count = len(current) - len(keep)
            else:
                await self._clear_all_browser_cookies(client)
                refreshed = []
                removed_count = len(current)
        return {
            "removed_count": removed_count,
            "inventory": self._build_cookie_inventory("live", refreshed),
        }

    async def _get_live_cookies(self, cdp_url: str) -> list[dict[str, Any]]:
        _, ws_url = await self._resolve_browser_connection(cdp_url)
        async with self._cdp_session(ws_url) as client:
            response = await client.send("Storage.getCookies")
        return self._normalize_cookies(response.get("cookies", []))

    async def _get_project(self, project_id: str, user_id: str) -> Project:
        project = await self._project_repository.find_by_id_and_user_id(project_id, user_id)
        if not project:
            raise NotFoundError("Project not found")
        return project

    def _get_project_cdp_url(self, project: Project) -> str:
        cdp_url = self._normalize_browser_cdp_url(project.browser_cdp_url) or ""
        if not cdp_url:
            raise BadRequestError("Project browser profile does not have a remote CDP endpoint configured")
        return cdp_url

    def _normalize_browser_cdp_url(self, cdp_url: str | None) -> str | None:
        if cdp_url is None:
            return None
        trimmed = cdp_url.strip()
        return trimmed or None

    def _validate_cdp_url(self, cdp_url: str) -> None:
        parsed = urlparse(cdp_url)
        if parsed.scheme not in {"http", "https", "ws", "wss"} or not parsed.netloc:
            raise BadRequestError("Browser CDP URL must be a valid http(s) or ws(s) URL")

    async def _resolve_browser_connection(self, cdp_url: str) -> tuple[dict[str, Any], str]:
        parsed = urlparse(cdp_url)
        if parsed.scheme in {"ws", "wss"}:
            version_info = await self._fetch_browser_version_from_websocket(cdp_url)
            return version_info, cdp_url
        if parsed.scheme not in {"http", "https"}:
            raise BadRequestError("Browser CDP URL must use http(s) or ws(s)")

        version_url = cdp_url if parsed.path.endswith("/json/version") else urljoin(cdp_url.rstrip("/") + "/", "json/version")
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(version_url)
            response.raise_for_status()
            payload = response.json()
        ws_url = payload.get("webSocketDebuggerUrl")
        if not ws_url:
            raise BadRequestError("Remote browser did not expose a webSocketDebuggerUrl")
        return payload, ws_url

    async def _fetch_browser_version_from_websocket(self, ws_url: str) -> dict[str, Any]:
        async with self._cdp_session(ws_url) as client:
            response = await client.send("Browser.getVersion")
        return {
            "Browser": response.get("product"),
            "User-Agent": response.get("userAgent"),
            "Protocol-Version": response.get("protocolVersion"),
        }

    @asynccontextmanager
    async def _cdp_session(self, ws_url: str) -> AsyncIterator["_CDPClient"]:
        client = _CDPClient(ws_url)
        await client.connect()
        try:
            yield client
        finally:
            await client.close()

    def _build_cookie_inventory(self, source: str, cookies: list[dict[str, Any]]) -> dict[str, Any]:
        grouped: dict[str, dict[str, Any]] = {}
        for cookie in cookies:
            domain = self._normalize_domain(str(cookie.get("domain") or ""))
            if not domain:
                continue
            record = grouped.setdefault(
                domain,
                {
                    "domain": domain,
                    "root_domain": self._extract_root_domain(domain),
                    "cookie_count": 0,
                    "http_only_count": 0,
                    "secure_count": 0,
                },
            )
            record["cookie_count"] += 1
            if cookie.get("httpOnly"):
                record["http_only_count"] += 1
            if cookie.get("secure"):
                record["secure_count"] += 1

        domains = sorted(grouped.values(), key=lambda item: (item["root_domain"], item["domain"]))
        return {
            "source": source,
            "total_cookie_count": len(cookies),
            "domains": domains,
        }

    async def _clear_all_browser_cookies(self, client: "_CDPClient") -> None:
        try:
            await client.send("Storage.clearCookies")
        except BadRequestError:
            await client.send("Network.clearBrowserCookies")

    def _normalize_cookies(self, cookies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()
        for cookie in cookies:
            if not isinstance(cookie, dict):
                continue
            name = str(cookie.get("name") or "").strip()
            value = str(cookie.get("value") or "")
            domain = self._normalize_domain(str(cookie.get("domain") or ""))
            path = str(cookie.get("path") or "/").strip() or "/"
            if not name or not value or not domain:
                continue
            dedupe_key = (domain, path, name)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            normalized_cookie: dict[str, Any] = {
                "name": name,
                "value": value,
                "domain": domain,
                "path": path,
                "httpOnly": bool(cookie.get("httpOnly", False)),
                "secure": bool(cookie.get("secure", False)),
            }
            same_site = cookie.get("sameSite")
            if same_site in {"Strict", "Lax", "None"}:
                normalized_cookie["sameSite"] = same_site
            expires = cookie.get("expires")
            if expires not in (None, "", -1):
                normalized_cookie["expires"] = float(expires)
            normalized.append(normalized_cookie)
        return normalized[:500]

    def _normalize_domain(self, domain: str) -> str:
        return domain.strip().lstrip(".").lower()

    def _extract_root_domain(self, domain: str) -> str:
        parts = self._normalize_domain(domain).split(".")
        if len(parts) <= 2:
            return self._normalize_domain(domain)
        return ".".join(parts[-2:])

    def _cookie_matches_domain(self, cookie_domain: str, target_domain: str) -> bool:
        normalized_cookie_domain = self._normalize_domain(cookie_domain)
        normalized_target = self._normalize_domain(target_domain)
        return (
            normalized_cookie_domain == normalized_target
            or normalized_cookie_domain.endswith(f".{normalized_target}")
        )

    async def _browser_pool_entry_status(self, browser: BrowserPoolEntry, active: bool) -> dict[str, Any]:
        try:
            version_info, ws_url = await self._resolve_browser_connection(browser.cdp_url)
            async with self._cdp_session(ws_url) as client:
                targets = await client.send("Target.getTargets")
                cookies = await client.send("Storage.getCookies")
            return {
                "browser_id": browser.id,
                "label": browser.label,
                "cdp_url": browser.cdp_url,
                "source": browser.source,
                "active": active,
                "healthy": True,
                "browser": version_info.get("Browser"),
                "page_count": len([target for target in targets.get("targetInfos", []) if target.get("type") == "page"]),
                "total_cookie_count": len(cookies.get("cookies", [])),
                "error": None,
            }
        except Exception as exc:
            return {
                "browser_id": browser.id,
                "label": browser.label,
                "cdp_url": browser.cdp_url,
                "source": browser.source,
                "active": active,
                "healthy": False,
                "browser": None,
                "page_count": 0,
                "total_cookie_count": 0,
                "error": str(exc),
            }


class _CDPClient:
    def __init__(self, ws_url: str):
        self._ws_url = ws_url
        self._connection = None
        self._message_id = 0

    async def connect(self) -> None:
        self._connection = await websockets.connect(self._ws_url, max_size=8 * 1024 * 1024)

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def send(self, method: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        if self._connection is None:
            raise RuntimeError("CDP session is not connected")
        self._message_id += 1
        message_id = self._message_id
        await self._connection.send(json.dumps({"id": message_id, "method": method, "params": params or {}}))
        while True:
            raw = await self._connection.recv()
            payload = json.loads(raw)
            if payload.get("id") != message_id:
                continue
            if "error" in payload:
                raise BadRequestError(f"{method} failed: {payload['error'].get('message', 'Unknown CDP error')}")
            return payload.get("result", {})
