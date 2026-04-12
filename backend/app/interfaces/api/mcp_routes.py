from fastapi import APIRouter, Depends

from app.application.services.mcp_service import MCPService
from app.domain.models.user import User
from app.interfaces.dependencies import get_current_user, get_mcp_service
from app.interfaces.schemas.base import APIResponse
from app.interfaces.schemas.mcp import (
    ConfigureMCPConnectorRequest,
    MCPConnectorResponse,
    MCPExportConfigResponse,
    MCPServerDetailResponse,
    MCPServersResponse,
    ImportMCPRemoteServerRequest,
    ImportMCPServersRequest,
    UpsertMCPServerRequest,
)

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.get("/connectors", response_model=APIResponse[list[MCPConnectorResponse]])
async def get_mcp_connectors(
    _: User = Depends(get_current_user),
    mcp_service: MCPService = Depends(get_mcp_service),
) -> APIResponse[list[MCPConnectorResponse]]:
    return APIResponse.success(await mcp_service.get_connector_catalog())


@router.get("/connectors/{connector_id}", response_model=APIResponse[MCPConnectorResponse])
async def get_mcp_connector(
    connector_id: str,
    _: User = Depends(get_current_user),
    mcp_service: MCPService = Depends(get_mcp_service),
) -> APIResponse[MCPConnectorResponse]:
    return APIResponse.success(await mcp_service.get_connector(connector_id))


@router.put("/connectors/{connector_id}", response_model=APIResponse[MCPConnectorResponse])
async def configure_mcp_connector(
    connector_id: str,
    request: ConfigureMCPConnectorRequest,
    _: User = Depends(get_current_user),
    mcp_service: MCPService = Depends(get_mcp_service),
) -> APIResponse[MCPConnectorResponse]:
    return APIResponse.success(
        await mcp_service.configure_connector(
            connector_id=connector_id,
            enabled=request.enabled,
            values=request.values,
            clear_keys=request.clear_keys,
        )
    )


@router.delete("/connectors/{connector_id}", response_model=APIResponse[dict])
async def delete_mcp_connector(
    connector_id: str,
    _: User = Depends(get_current_user),
    mcp_service: MCPService = Depends(get_mcp_service),
) -> APIResponse[dict]:
    await mcp_service.delete_connector(connector_id)
    return APIResponse.success({})


@router.get("/servers", response_model=APIResponse[MCPServersResponse])
async def get_mcp_servers(
    _: User = Depends(get_current_user),
    mcp_service: MCPService = Depends(get_mcp_service),
) -> APIResponse[MCPServersResponse]:
    return APIResponse.success(await mcp_service.get_server_inventory())


@router.get("/export", response_model=APIResponse[MCPExportConfigResponse])
async def export_mcp_config(
    _: User = Depends(get_current_user),
    mcp_service: MCPService = Depends(get_mcp_service),
) -> APIResponse[MCPExportConfigResponse]:
    config = await mcp_service.export_config()
    return APIResponse.success(MCPExportConfigResponse(mcpServers={name: server.model_dump(exclude_none=True) for name, server in config.mcpServers.items()}))


@router.post("/import/local", response_model=APIResponse[MCPServersResponse])
async def import_local_mcp_servers(
    request: ImportMCPServersRequest,
    _: User = Depends(get_current_user),
    mcp_service: MCPService = Depends(get_mcp_service),
) -> APIResponse[MCPServersResponse]:
    return APIResponse.success(await mcp_service.import_servers(request.mcpServers))


@router.post("/import/remote", response_model=APIResponse[MCPServerDetailResponse])
async def import_remote_mcp_server(
    request: ImportMCPRemoteServerRequest,
    _: User = Depends(get_current_user),
    mcp_service: MCPService = Depends(get_mcp_service),
) -> APIResponse[MCPServerDetailResponse]:
    return APIResponse.success(
        await mcp_service.import_remote_server(
            name=request.name,
            url=request.url,
            transport=request.transport,
            enabled=request.enabled,
            description=request.description,
        )
    )


@router.get("/servers/{name}", response_model=APIResponse[MCPServerDetailResponse])
async def get_mcp_server(
    name: str,
    _: User = Depends(get_current_user),
    mcp_service: MCPService = Depends(get_mcp_service),
) -> APIResponse[MCPServerDetailResponse]:
    return APIResponse.success(await mcp_service.get_server_detail(name))


@router.post("/servers", response_model=APIResponse[MCPServerDetailResponse])
async def create_mcp_server(
    request: UpsertMCPServerRequest,
    _: User = Depends(get_current_user),
    mcp_service: MCPService = Depends(get_mcp_service),
) -> APIResponse[MCPServerDetailResponse]:
    return APIResponse.success(await mcp_service.upsert_server(**request.model_dump()))


@router.put("/servers/{name}", response_model=APIResponse[MCPServerDetailResponse])
async def update_mcp_server(
    name: str,
    request: UpsertMCPServerRequest,
    _: User = Depends(get_current_user),
    mcp_service: MCPService = Depends(get_mcp_service),
) -> APIResponse[MCPServerDetailResponse]:
    return APIResponse.success(await mcp_service.upsert_server(existing_name=name, **request.model_dump()))


@router.delete("/servers/{name}", response_model=APIResponse[dict])
async def delete_mcp_server(
    name: str,
    _: User = Depends(get_current_user),
    mcp_service: MCPService = Depends(get_mcp_service),
) -> APIResponse[dict]:
    await mcp_service.delete_server(name)
    return APIResponse.success({})
