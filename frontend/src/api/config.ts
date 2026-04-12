import { apiClient, ApiResponse } from './client'

export interface ClientConfigResponse {
  auth_provider: string
  show_github_button: boolean
  github_repository_url: string
  google_analytics_id: string | null
  claw_enabled: boolean
  default_model_name: string
  available_models: string[]
}

export interface ControlPlaneConfigResponse {
  auth_provider: string
  model_provider: string
  default_model_name: string
  available_models: string[]
  browser_engine: string
  search_provider: string | null
  supported_search_providers: string[]
  supported_browser_engines: string[]
  show_github_button: boolean
  github_repository_url: string
  google_analytics_enabled: boolean
  claw_enabled: boolean
  email_enabled: boolean
  mcp_configured: boolean
}

let clientConfigCache: ClientConfigResponse | null = null
let isClientConfigLoaded = false
let controlPlaneConfigCache: ControlPlaneConfigResponse | null = null
let isControlPlaneConfigLoaded = false

/**
 * Get client runtime configuration.
 */
export async function getClientConfig(): Promise<ClientConfigResponse> {
  const response = await apiClient.get<ApiResponse<ClientConfigResponse>>('/config/frontend')
  return response.data.data
}

/**
 * Get client runtime configuration (cached after first call).
 * Returns null when config has not been fetched yet or fetch failed.
 */
export async function getCachedClientConfig(): Promise<ClientConfigResponse | null> {
  if (isClientConfigLoaded) {
    return clientConfigCache
  }

  try {
    clientConfigCache = await getClientConfig()
    isClientConfigLoaded = true
    return clientConfigCache
  } catch (error) {
    console.warn('Failed to load client runtime configuration:', error)
    isClientConfigLoaded = true
    return null
  }
}

/**
 * Read auth provider from client configuration.
 */
export async function getCachedAuthProvider(): Promise<string | null> {
  const clientConfig = await getCachedClientConfig()
  return clientConfig?.auth_provider || null
}

/**
 * Get richer non-secret runtime capability metadata for the settings control plane.
 */
export async function getControlPlaneConfig(): Promise<ControlPlaneConfigResponse> {
  const response = await apiClient.get<ApiResponse<ControlPlaneConfigResponse>>('/config/control-plane')
  return response.data.data
}

export async function getCachedControlPlaneConfig(): Promise<ControlPlaneConfigResponse | null> {
  if (isControlPlaneConfigLoaded) {
    return controlPlaneConfigCache
  }

  try {
    controlPlaneConfigCache = await getControlPlaneConfig()
    isControlPlaneConfigLoaded = true
    return controlPlaneConfigCache
  } catch (error) {
    console.warn('Failed to load control plane configuration:', error)
    isControlPlaneConfigLoaded = true
    return null
  }
}
