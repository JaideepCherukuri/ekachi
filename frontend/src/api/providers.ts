import { apiClient, ApiResponse } from './client'

export interface ProviderResponse {
  provider_id: string
  label: string
  model_provider: string
  api_base?: string | null
  available_models: string[]
  default_model_name: string
  enabled: boolean
  is_system: boolean
  has_api_key: boolean
  created_at?: string | null
  updated_at?: string | null
}

export interface ListProvidersResponse {
  providers: ProviderResponse[]
}

export interface CreateProviderPayload {
  label: string
  model_provider: string
  api_base?: string | null
  api_key?: string | null
  available_models: string[]
  default_model_name?: string | null
  enabled: boolean
}

export interface UpdateProviderPayload {
  label?: string
  model_provider?: string
  api_base?: string | null
  api_key?: string | null
  clear_api_key?: boolean
  available_models?: string[]
  default_model_name?: string | null
  enabled?: boolean
}

export interface TestProviderResponse {
  provider_id: string
  model_name: string
  ok: boolean
}

export async function getProviders(): Promise<ListProvidersResponse> {
  const response = await apiClient.get<ApiResponse<ListProvidersResponse>>('/providers')
  return response.data.data
}

export async function createProvider(payload: CreateProviderPayload): Promise<ProviderResponse> {
  const response = await apiClient.post<ApiResponse<ProviderResponse>>('/providers', payload)
  return response.data.data
}

export async function updateProvider(providerId: string, payload: UpdateProviderPayload): Promise<ProviderResponse> {
  const response = await apiClient.patch<ApiResponse<ProviderResponse>>(`/providers/${providerId}`, payload)
  return response.data.data
}

export async function deleteProvider(providerId: string): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`/providers/${providerId}`)
}

export async function testProvider(providerId: string, modelName?: string | null): Promise<TestProviderResponse> {
  const response = await apiClient.post<ApiResponse<TestProviderResponse>>(`/providers/${providerId}/test`, {
    model_name: modelName || undefined,
  })
  return response.data.data
}
