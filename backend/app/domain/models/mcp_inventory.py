from typing import Optional

from pydantic import BaseModel, Field

from app.domain.models.mcp_config import MCPTransport


class MCPServerSummary(BaseModel):
    name: str
    transport: MCPTransport
    enabled: bool
    description: Optional[str] = None
    command: Optional[str] = None
    args: list[str] = Field(default_factory=list)
    url: Optional[str] = None
    has_headers: bool = False
    has_env: bool = False


class MCPServerInventory(BaseModel):
    configured: bool
    servers: list[MCPServerSummary] = Field(default_factory=list)
