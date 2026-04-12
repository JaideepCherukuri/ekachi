import { apiClient, type ApiResponse } from './client'

export type MCPTransport = 'stdio' | 'sse' | 'streamable-http'

export interface MCPServerSummary {
  name: string
  transport: MCPTransport
  enabled: boolean
  description?: string | null
  command?: string | null
  args: string[]
  url?: string | null
  has_headers: boolean
  has_env: boolean
}

export interface MCPServerDetail {
  name: string
  transport: MCPTransport
  enabled: boolean
  description?: string | null
  command?: string | null
  args: string[]
  url?: string | null
  headers?: Record<string, string> | null
  env?: Record<string, string> | null
}

export interface UpsertMCPServerRequest extends MCPServerDetail {}

export interface MCPServersResponse {
  configured: boolean
  servers: MCPServerSummary[]
}

export interface MCPExportConfigResponse {
  mcpServers: Record<string, Record<string, unknown>>
}

export interface ImportMCPServersRequest {
  mcpServers: Record<string, Record<string, unknown>>
}

export interface ImportMCPRemoteServerRequest {
  name: string
  url: string
  transport?: MCPTransport
  enabled?: boolean
  description?: string | null
}

export type MCPConnectorValueSource = 'env' | 'headers'

export interface MCPConnectorFieldState {
  key: string
  label: string
  description?: string | null
  placeholder?: string | null
  required: boolean
  secret: boolean
  source: MCPConnectorValueSource
  configured: boolean
  value?: string | null
}

export interface MCPConnectorStatus {
  connector_id: string
  server_name: string
  name: string
  description: string
  category: string
  docs_url?: string | null
  tags: string[]
  transport: MCPTransport
  command?: string | null
  args: string[]
  url?: string | null
  installed: boolean
  enabled: boolean
  configured: boolean
  missing_required_fields: string[]
  field_states: MCPConnectorFieldState[]
}

export interface ConfigureMCPConnectorRequest {
  enabled: boolean
  values: Record<string, string | null>
  clear_keys: string[]
}

export async function getMcpConnectors(): Promise<MCPConnectorStatus[]> {
  const response = await apiClient.get<ApiResponse<MCPConnectorStatus[]>>('/mcp/connectors')
  return response.data.data
}

export async function getMcpConnector(connectorId: string): Promise<MCPConnectorStatus> {
  const response = await apiClient.get<ApiResponse<MCPConnectorStatus>>(`/mcp/connectors/${encodeURIComponent(connectorId)}`)
  return response.data.data
}

export async function configureMcpConnector(
  connectorId: string,
  request: ConfigureMCPConnectorRequest,
): Promise<MCPConnectorStatus> {
  const response = await apiClient.put<ApiResponse<MCPConnectorStatus>>(`/mcp/connectors/${encodeURIComponent(connectorId)}`, request)
  return response.data.data
}

export async function deleteMcpConnector(connectorId: string): Promise<{}> {
  const response = await apiClient.delete<ApiResponse<{}>>(`/mcp/connectors/${encodeURIComponent(connectorId)}`)
  return response.data.data
}

export async function getMcpServers(): Promise<MCPServersResponse> {
  const response = await apiClient.get<ApiResponse<MCPServersResponse>>('/mcp/servers')
  return response.data.data
}

export async function exportMcpConfig(): Promise<MCPExportConfigResponse> {
  const response = await apiClient.get<ApiResponse<MCPExportConfigResponse>>('/mcp/export')
  return response.data.data
}

export async function importLocalMcpServers(request: ImportMCPServersRequest): Promise<MCPServersResponse> {
  const response = await apiClient.post<ApiResponse<MCPServersResponse>>('/mcp/import/local', request)
  return response.data.data
}

export async function importRemoteMcpServer(request: ImportMCPRemoteServerRequest): Promise<MCPServerDetail> {
  const response = await apiClient.post<ApiResponse<MCPServerDetail>>('/mcp/import/remote', request)
  return response.data.data
}

export async function getMcpServer(name: string): Promise<MCPServerDetail> {
  const response = await apiClient.get<ApiResponse<MCPServerDetail>>(`/mcp/servers/${encodeURIComponent(name)}`)
  return response.data.data
}

export async function createMcpServer(request: UpsertMCPServerRequest): Promise<MCPServerDetail> {
  const response = await apiClient.post<ApiResponse<MCPServerDetail>>('/mcp/servers', request)
  return response.data.data
}

export async function updateMcpServer(
  name: string,
  request: UpsertMCPServerRequest,
): Promise<MCPServerDetail> {
  const response = await apiClient.put<ApiResponse<MCPServerDetail>>(`/mcp/servers/${encodeURIComponent(name)}`, request)
  return response.data.data
}

export async function deleteMcpServer(name: string): Promise<{}> {
  const response = await apiClient.delete<ApiResponse<{}>>(`/mcp/servers/${encodeURIComponent(name)}`)
  return response.data.data
}
