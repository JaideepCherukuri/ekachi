import re

from app.application.errors.exceptions import NotFoundError, ServerError, ValidationError
from app.domain.models.mcp_config import MCPConfig, MCPServerConfig, MCPTransport
from app.domain.models.mcp_inventory import MCPServerInventory, MCPServerSummary
from app.domain.models.mcp_management import (
    MCPConnectorField,
    MCPConnectorFieldState,
    MCPConnectorStatus,
    MCPConnectorValueSource,
    MCPServerDetail,
)
from app.domain.repositories.mcp_repository import MCPRepository


class MCPService:
    def __init__(self, mcp_repository: MCPRepository):
        self.mcp_repository = mcp_repository

    def _validate_server_name(self, name: str) -> str:
        normalized = name.strip()
        if not normalized:
            raise ValidationError("MCP server name is required")
        if not re.fullmatch(r"[A-Za-z0-9._-]+", normalized):
            raise ValidationError("MCP server name may only contain letters, numbers, dot, underscore, and hyphen")
        return normalized

    def _detail_from_config(self, name: str, server: MCPServerConfig) -> MCPServerDetail:
        return MCPServerDetail(
            name=name,
            transport=server.transport,
            enabled=server.enabled,
            description=server.description,
            command=server.command,
            args=server.args or [],
            url=server.url,
            headers=server.headers,
            env=server.env,
        )

    def _connector_definitions(self) -> list[MCPConnectorStatus]:
        return [
            MCPConnectorStatus(
                connector_id="notion",
                server_name="notion",
                name="Notion",
                description="Workspace integration for reading and editing Notion pages and databases.",
                category="Knowledge",
                docs_url="https://developers.notion.com/docs/mcp",
                tags=["knowledge", "docs", "pages"],
                transport=MCPTransport.STDIO,
                command="npx",
                args=["-y", "@notionhq/notion-mcp-server"],
                field_states=[
                    MCPConnectorFieldState(
                        key="NOTION_TOKEN",
                        label="Notion Token",
                        description="Internal integration token from the Notion developer portal.",
                        placeholder="ntn_...",
                        required=True,
                        secret=True,
                        source=MCPConnectorValueSource.ENV,
                    ),
                ],
            ),
            MCPConnectorStatus(
                connector_id="google-calendar",
                server_name="google-calendar",
                name="Google Calendar",
                description="Calendar scheduling and availability tools backed by a Google OAuth credentials file.",
                category="Productivity",
                docs_url="https://www.npmjs.com/package/@teamsparta/mcp-server-google-calendar",
                tags=["calendar", "oauth", "scheduling"],
                transport=MCPTransport.STDIO,
                command="npx",
                args=["-y", "@teamsparta/mcp-server-google-calendar"],
                field_states=[
                    MCPConnectorFieldState(
                        key="GOOGLE_CREDENTIALS_PATH",
                        label="Credentials File",
                        description="Absolute path to the Google Calendar MCP credentials JSON file.",
                        placeholder="/home/user/.config/gcalendar-server-credentials.json",
                        required=True,
                        secret=False,
                        source=MCPConnectorValueSource.ENV,
                    ),
                ],
            ),
            MCPConnectorStatus(
                connector_id="github",
                server_name="github",
                name="GitHub",
                description="Repository, issues, pull requests, and code search tools using the GitHub MCP server.",
                category="Engineering",
                docs_url="https://github.com/github/github-mcp-server",
                tags=["git", "code", "pull-requests"],
                transport=MCPTransport.STDIO,
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                field_states=[
                    MCPConnectorFieldState(
                        key="GITHUB_PERSONAL_ACCESS_TOKEN",
                        label="Personal Access Token",
                        description="GitHub token with repository access for the repositories you want the agent to use.",
                        placeholder="github_pat_...",
                        required=True,
                        secret=True,
                        source=MCPConnectorValueSource.ENV,
                    ),
                ],
            ),
            MCPConnectorStatus(
                connector_id="slack",
                server_name="slack",
                name="Slack",
                description="Workspace messaging tools for posting messages, reading channels, and replying in threads.",
                category="Communication",
                docs_url="https://www.npmjs.com/package/@modelcontextprotocol/server-slack",
                tags=["messaging", "channels", "notifications"],
                transport=MCPTransport.STDIO,
                command="npx",
                args=["-y", "@modelcontextprotocol/server-slack"],
                field_states=[
                    MCPConnectorFieldState(
                        key="SLACK_BOT_TOKEN",
                        label="Bot Token",
                        description="Slack bot token that starts with xoxb-.",
                        placeholder="xoxb-...",
                        required=True,
                        secret=True,
                        source=MCPConnectorValueSource.ENV,
                    ),
                    MCPConnectorFieldState(
                        key="SLACK_TEAM_ID",
                        label="Team ID",
                        description="Slack workspace or organization ID that starts with T.",
                        placeholder="T01234567",
                        required=True,
                        secret=False,
                        source=MCPConnectorValueSource.ENV,
                    ),
                    MCPConnectorFieldState(
                        key="SLACK_CHANNEL_IDS",
                        label="Allowed Channels",
                        description="Optional comma-separated channel IDs to scope access.",
                        placeholder="C01234567,C76543210",
                        required=False,
                        secret=False,
                        source=MCPConnectorValueSource.ENV,
                    ),
                ],
            ),
        ]

    def _get_connector_definition(self, connector_id: str) -> MCPConnectorStatus:
        for definition in self._connector_definitions():
            if definition.connector_id == connector_id:
                return definition
        raise NotFoundError("MCP connector not found")

    def _read_connector_value(self, server: MCPServerConfig | None, field: MCPConnectorField) -> str | None:
        if not server:
            return None
        if field.source == MCPConnectorValueSource.HEADER:
            return (server.headers or {}).get(field.key)
        return (server.env or {}).get(field.key)

    def _build_connector_status(
        self,
        definition: MCPConnectorStatus,
        config_servers: dict[str, MCPServerConfig],
    ) -> MCPConnectorStatus:
        server = config_servers.get(definition.server_name)
        field_states: list[MCPConnectorFieldState] = []
        missing_required_fields: list[str] = []

        for field in definition.field_states:
            configured_value = self._read_connector_value(server, field)
            is_configured = bool(configured_value)
            field_state = field.model_copy(deep=True)
            field_state.configured = is_configured
            field_state.value = None if field.secret else configured_value
            field_states.append(field_state)
            if field.required and not is_configured:
                missing_required_fields.append(field.key)

        return definition.model_copy(
            update={
                "installed": server is not None,
                "enabled": bool(server.enabled) if server else False,
                "configured": server is not None and not missing_required_fields,
                "missing_required_fields": missing_required_fields,
                "field_states": field_states,
            }
        )

    async def get_connector_catalog(self) -> list[MCPConnectorStatus]:
        config = await self.mcp_repository.get_mcp_config()
        return [self._build_connector_status(definition, config.mcpServers) for definition in self._connector_definitions()]

    async def get_connector(self, connector_id: str) -> MCPConnectorStatus:
        definition = self._get_connector_definition(connector_id)
        config = await self.mcp_repository.get_mcp_config()
        return self._build_connector_status(definition, config.mcpServers)

    async def configure_connector(
        self,
        *,
        connector_id: str,
        enabled: bool,
        values: dict[str, str | None],
        clear_keys: list[str],
    ) -> MCPConnectorStatus:
        definition = self._get_connector_definition(connector_id)
        config = await self.mcp_repository.get_mcp_config()
        existing_server = config.mcpServers.get(definition.server_name)
        env = dict(existing_server.env or {}) if existing_server else {}
        headers = dict(existing_server.headers or {}) if existing_server else {}

        definition_fields = {field.key: field for field in definition.field_states}
        unknown_keys = sorted(set(values.keys()) - set(definition_fields.keys()))
        if unknown_keys:
            raise ValidationError(f"Unsupported connector fields: {', '.join(unknown_keys)}")

        for key in clear_keys:
            field = definition_fields.get(key)
            if not field:
                raise ValidationError(f"Unsupported connector field: {key}")
            if field.source == MCPConnectorValueSource.HEADER:
                headers.pop(key, None)
            else:
                env.pop(key, None)

        for key, value in values.items():
            field = definition_fields[key]
            normalized = (value or "").strip()
            target = headers if field.source == MCPConnectorValueSource.HEADER else env
            if normalized:
                target[key] = normalized
            elif key in clear_keys:
                target.pop(key, None)

        missing_required_fields = [
            field.key
            for field in definition.field_states
            if field.required and not (headers if field.source == MCPConnectorValueSource.HEADER else env).get(field.key)
        ]
        if missing_required_fields:
            raise ValidationError(
                f"Missing required connector fields: {', '.join(missing_required_fields)}"
            )

        try:
            server = MCPServerConfig(
                transport=definition.transport,
                enabled=enabled,
                description=definition.description,
                command=definition.command,
                args=definition.args or [],
                url=definition.url,
                headers=headers or None,
                env=env or None,
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        config.mcpServers[definition.server_name] = server
        try:
            await self.mcp_repository.save_mcp_config(config)
        except OSError as exc:
            raise ServerError(f"Failed to write MCP config: {exc}") from exc

        return self._build_connector_status(definition, config.mcpServers)

    async def delete_connector(self, connector_id: str) -> None:
        definition = self._get_connector_definition(connector_id)
        config = await self.mcp_repository.get_mcp_config()
        if definition.server_name not in config.mcpServers:
            raise NotFoundError("MCP connector is not installed")

        del config.mcpServers[definition.server_name]
        try:
            await self.mcp_repository.save_mcp_config(config)
        except OSError as exc:
            raise ServerError(f"Failed to write MCP config: {exc}") from exc

    async def get_server_inventory(self) -> MCPServerInventory:
        config = await self.mcp_repository.get_mcp_config()
        servers = [
            MCPServerSummary(
                name=name,
                transport=server.transport,
                enabled=server.enabled,
                description=server.description,
                command=server.command,
                args=server.args or [],
                url=server.url,
                has_headers=bool(server.headers),
                has_env=bool(server.env),
            )
            for name, server in config.mcpServers.items()
        ]
        return MCPServerInventory(configured=bool(servers), servers=servers)

    async def get_server_detail(self, name: str) -> MCPServerDetail:
        normalized = self._validate_server_name(name)
        config = await self.mcp_repository.get_mcp_config()
        server = config.mcpServers.get(normalized)
        if not server:
            raise NotFoundError("MCP server not found")
        return self._detail_from_config(normalized, server)

    async def export_config(self) -> MCPConfig:
        return await self.mcp_repository.get_mcp_config()

    async def import_servers(self, imported_servers: dict[str, dict]) -> MCPServerInventory:
        config = await self.mcp_repository.get_mcp_config()
        for raw_name, raw_server in imported_servers.items():
            normalized_name = self._validate_server_name(raw_name)
            try:
                config.mcpServers[normalized_name] = MCPServerConfig.model_validate(raw_server)
            except ValueError as exc:
                raise ValidationError(f"Invalid MCP server '{normalized_name}': {exc}") from exc
        try:
            await self.mcp_repository.save_mcp_config(config)
        except OSError as exc:
            raise ServerError(f"Failed to write MCP config: {exc}") from exc
        return await self.get_server_inventory()

    async def import_remote_server(
        self,
        *,
        name: str,
        url: str,
        transport: MCPTransport,
        enabled: bool,
        description: str | None,
    ) -> MCPServerDetail:
        if transport not in {MCPTransport.SSE, MCPTransport.STREAMABLE_HTTP}:
            raise ValidationError("Remote MCP servers must use sse or streamable-http transport")
        return await self.upsert_server(
            name=name,
            transport=transport,
            enabled=enabled,
            description=description,
            command=None,
            args=[],
            url=url,
            headers=None,
            env=None,
        )

    async def upsert_server(
        self,
        *,
        name: str,
        transport: str,
        enabled: bool,
        description: str | None,
        command: str | None,
        args: list[str],
        url: str | None,
        headers: dict[str, str] | None,
        env: dict[str, str] | None,
        existing_name: str | None = None,
    ) -> MCPServerDetail:
        new_name = self._validate_server_name(name)
        old_name = self._validate_server_name(existing_name) if existing_name else None
        config = await self.mcp_repository.get_mcp_config()

        if old_name and old_name != new_name and new_name in config.mcpServers:
            raise ValidationError("An MCP server with that name already exists")
        if not old_name and new_name in config.mcpServers:
            raise ValidationError("An MCP server with that name already exists")
        if old_name and old_name not in config.mcpServers:
            raise NotFoundError("MCP server not found")

        try:
            server = MCPServerConfig(
                transport=transport,
                enabled=enabled,
                description=description,
                command=command.strip() if command else None,
                args=[arg.strip() for arg in args if arg.strip()],
                url=url.strip() if url else None,
                headers=headers or None,
                env=env or None,
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        if old_name and old_name != new_name:
            del config.mcpServers[old_name]
        config.mcpServers[new_name] = server

        try:
            await self.mcp_repository.save_mcp_config(config)
        except OSError as exc:
            raise ServerError(f"Failed to write MCP config: {exc}") from exc

        return self._detail_from_config(new_name, server)

    async def delete_server(self, name: str) -> None:
        normalized = self._validate_server_name(name)
        config = await self.mcp_repository.get_mcp_config()
        if normalized not in config.mcpServers:
            raise NotFoundError("MCP server not found")

        del config.mcpServers[normalized]
        try:
            await self.mcp_repository.save_mcp_config(config)
        except OSError as exc:
            raise ServerError(f"Failed to write MCP config: {exc}") from exc
