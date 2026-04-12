from app.domain.models.mcp_config import MCPTransport
from app.domain.models.mcp_inventory import (
    MCPServerInventory as MCPServersResponse,
    MCPServerSummary as MCPServerSummaryResponse,
)
from app.domain.models.mcp_management import (
    MCPConnectorStatus as MCPConnectorResponse,
    MCPServerDetail as MCPServerDetailResponse,
)
from pydantic import BaseModel, Field, field_validator


class MCPExportConfigResponse(BaseModel):
    mcpServers: dict[str, dict]


class ImportMCPServersRequest(BaseModel):
    mcpServers: dict[str, dict] = Field(default_factory=dict)


class ImportMCPRemoteServerRequest(BaseModel):
    name: str
    url: str = Field(min_length=1, max_length=2048)
    transport: MCPTransport = MCPTransport.STREAMABLE_HTTP
    enabled: bool = True
    description: str | None = None

class UpsertMCPServerRequest(BaseModel):
    name: str
    transport: MCPTransport
    enabled: bool = True
    description: str | None = None
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    url: str | None = None
    headers: dict[str, str] | None = None
    env: dict[str, str] | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Name is required")
        return normalized


class ConfigureMCPConnectorRequest(BaseModel):
    enabled: bool = True
    values: dict[str, str | None] = Field(default_factory=dict)
    clear_keys: list[str] = Field(default_factory=list)
