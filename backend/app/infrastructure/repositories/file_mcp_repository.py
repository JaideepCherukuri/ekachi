import os
import json
import logging
from app.domain.repositories.mcp_repository import MCPRepository
from app.domain.models.mcp_config import MCPConfig
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class FileMCPRepository(MCPRepository):
    """Repository for MCP config stored in a file"""
    
    async def get_mcp_config(self) -> MCPConfig:
        """Get the MCP config from the file"""
        file_path = get_settings().mcp_config_path
        if not os.path.exists(file_path):
            return MCPConfig(mcpServers={})
        try:
            with open(file_path, "r") as file:
                return MCPConfig.model_validate_json(file.read())
        except Exception as e:
            logger.exception(f"Error reading MCP config file: {e}")
        
        return MCPConfig(mcpServers={})

    async def save_mcp_config(self, config: MCPConfig) -> MCPConfig:
        """Persist the MCP config to the file system."""
        file_path = get_settings().mcp_config_path
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        temp_path = f"{file_path}.tmp"
        payload = json.dumps(config.model_dump(mode="json", exclude_none=True), indent=2)
        with open(temp_path, "w") as file:
            file.write(payload)
            file.write("\n")
        os.replace(temp_path, file_path)
        return config
