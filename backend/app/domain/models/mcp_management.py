from enum import Enum

from pydantic import BaseModel, Field

from app.domain.models.mcp_config import MCPTransport


class MCPServerDetail(BaseModel):
    name: str
    transport: MCPTransport
    enabled: bool = True
    description: str | None = None
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    url: str | None = None
    headers: dict[str, str] | None = None
    env: dict[str, str] | None = None


class MCPConnectorValueSource(str, Enum):
    ENV = "env"
    HEADER = "headers"


class MCPConnectorField(BaseModel):
    key: str
    label: str
    description: str | None = None
    placeholder: str | None = None
    required: bool = True
    secret: bool = False
    source: MCPConnectorValueSource = MCPConnectorValueSource.ENV


class MCPConnectorFieldState(MCPConnectorField):
    configured: bool = False
    value: str | None = None


class MCPConnectorStatus(BaseModel):
    connector_id: str
    server_name: str
    name: str
    description: str
    category: str
    docs_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    transport: MCPTransport
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    url: str | None = None
    installed: bool = False
    enabled: bool = False
    configured: bool = False
    missing_required_fields: list[str] = Field(default_factory=list)
    field_states: list[MCPConnectorFieldState] = Field(default_factory=list)
