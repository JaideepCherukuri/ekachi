import pytest

from app.application.errors.exceptions import NotFoundError, ValidationError
from app.application.services.mcp_service import MCPService
from app.domain.models.mcp_config import MCPConfig


class InMemoryMCPRepository:
    def __init__(self):
        self.config = MCPConfig(mcpServers={})

    async def get_mcp_config(self) -> MCPConfig:
        return self.config.model_copy(deep=True)

    async def save_mcp_config(self, config: MCPConfig) -> MCPConfig:
        self.config = config.model_copy(deep=True)
        return self.config.model_copy(deep=True)


@pytest.mark.asyncio
async def test_configure_connector_installs_curated_server():
    repository = InMemoryMCPRepository()
    service = MCPService(repository)

    connector = await service.configure_connector(
        connector_id="github",
        enabled=True,
        values={"GITHUB_PERSONAL_ACCESS_TOKEN": "github_pat_test"},
        clear_keys=[],
    )

    assert connector.installed is True
    assert connector.configured is True
    assert connector.transport == "stdio"
    stored_server = repository.config.mcpServers["github"]
    assert stored_server.command == "npx"
    assert stored_server.args == ["-y", "@modelcontextprotocol/server-github"]
    assert stored_server.env == {"GITHUB_PERSONAL_ACCESS_TOKEN": "github_pat_test"}


@pytest.mark.asyncio
async def test_connector_catalog_redacts_secret_values_but_keeps_non_secret_values():
    repository = InMemoryMCPRepository()
    service = MCPService(repository)

    await service.configure_connector(
        connector_id="slack",
        enabled=True,
        values={
            "SLACK_BOT_TOKEN": "xoxb-secret",
            "SLACK_TEAM_ID": "T123456",
            "SLACK_CHANNEL_IDS": "C1,C2",
        },
        clear_keys=[],
    )

    connector = await service.get_connector("slack")
    field_states = {field.key: field for field in connector.field_states}

    assert field_states["SLACK_BOT_TOKEN"].configured is True
    assert field_states["SLACK_BOT_TOKEN"].value is None
    assert field_states["SLACK_TEAM_ID"].value == "T123456"
    assert field_states["SLACK_CHANNEL_IDS"].value == "C1,C2"


@pytest.mark.asyncio
async def test_configure_connector_preserves_existing_secret_when_value_omitted():
    repository = InMemoryMCPRepository()
    service = MCPService(repository)

    await service.configure_connector(
        connector_id="slack",
        enabled=True,
        values={
            "SLACK_BOT_TOKEN": "xoxb-secret",
            "SLACK_TEAM_ID": "T123456",
        },
        clear_keys=[],
    )

    await service.configure_connector(
        connector_id="slack",
        enabled=False,
        values={"SLACK_TEAM_ID": "T999999"},
        clear_keys=[],
    )

    stored_server = repository.config.mcpServers["slack"]
    assert stored_server.enabled is False
    assert stored_server.env["SLACK_BOT_TOKEN"] == "xoxb-secret"
    assert stored_server.env["SLACK_TEAM_ID"] == "T999999"


@pytest.mark.asyncio
async def test_configure_connector_rejects_missing_required_fields():
    repository = InMemoryMCPRepository()
    service = MCPService(repository)

    with pytest.raises(ValidationError):
        await service.configure_connector(
            connector_id="google-calendar",
            enabled=True,
            values={},
            clear_keys=[],
        )


@pytest.mark.asyncio
async def test_delete_connector_removes_installed_server():
    repository = InMemoryMCPRepository()
    service = MCPService(repository)

    await service.configure_connector(
        connector_id="notion",
        enabled=True,
        values={"NOTION_TOKEN": "ntn_test"},
        clear_keys=[],
    )

    await service.delete_connector("notion")

    assert "notion" not in repository.config.mcpServers

    with pytest.raises(NotFoundError):
        await service.delete_connector("notion")


@pytest.mark.asyncio
async def test_import_servers_merges_local_config():
    repository = InMemoryMCPRepository()
    service = MCPService(repository)

    inventory = await service.import_servers(
        {
            "filesystem": {
                "transport": "stdio",
                "enabled": True,
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            }
        }
    )

    assert inventory.configured is True
    assert "filesystem" in repository.config.mcpServers


@pytest.mark.asyncio
async def test_export_config_returns_current_servers():
    repository = InMemoryMCPRepository()
    service = MCPService(repository)

    await service.configure_connector(
        connector_id="github",
        enabled=True,
        values={"GITHUB_PERSONAL_ACCESS_TOKEN": "github_pat_test"},
        clear_keys=[],
    )

    exported = await service.export_config()

    assert "github" in exported.mcpServers


@pytest.mark.asyncio
async def test_import_remote_server_creates_http_transport_server():
    repository = InMemoryMCPRepository()
    service = MCPService(repository)

    server = await service.import_remote_server(
        name="remote-acme",
        url="https://mcp.example.com/server",
        transport="streamable-http",
        enabled=True,
        description="Hosted server",
    )

    assert server.name == "remote-acme"
    assert repository.config.mcpServers["remote-acme"].url == "https://mcp.example.com/server"
