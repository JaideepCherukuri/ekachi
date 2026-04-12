import { apiClient, ApiResponse } from './client'
import type {
  BrowserPoolResponse,
  BrowserConnectionResponse,
  BrowserCookieInventoryResponse,
  BrowserCookieMutationResponse,
} from '@/types/response'

export interface AddBrowserPoolEntryPayload {
  label: string
  cdp_url: string
  source?: string
  set_active?: boolean
}

export async function testBrowserConnection(projectId: string): Promise<BrowserConnectionResponse> {
  const response = await apiClient.get<ApiResponse<BrowserConnectionResponse>>(`/browser/projects/${projectId}/connection`)
  return response.data.data
}

export async function getBrowserPool(projectId: string): Promise<BrowserPoolResponse> {
  const response = await apiClient.get<ApiResponse<BrowserPoolResponse>>(`/browser/projects/${projectId}/pool`)
  return response.data.data
}

export async function addBrowserPoolEntry(projectId: string, payload: AddBrowserPoolEntryPayload): Promise<BrowserPoolResponse> {
  const response = await apiClient.post<ApiResponse<BrowserPoolResponse>>(`/browser/projects/${projectId}/pool`, payload)
  return response.data.data
}

export async function activateBrowserPoolEntry(projectId: string, browserId: string): Promise<BrowserPoolResponse> {
  const response = await apiClient.post<ApiResponse<BrowserPoolResponse>>(`/browser/projects/${projectId}/pool/${encodeURIComponent(browserId)}/activate`)
  return response.data.data
}

export async function deleteBrowserPoolEntry(projectId: string, browserId: string): Promise<BrowserPoolResponse> {
  const response = await apiClient.delete<ApiResponse<BrowserPoolResponse>>(`/browser/projects/${projectId}/pool/${encodeURIComponent(browserId)}`)
  return response.data.data
}

export async function getProjectBrowserCookies(projectId: string): Promise<BrowserCookieInventoryResponse> {
  const response = await apiClient.get<ApiResponse<BrowserCookieInventoryResponse>>(`/browser/projects/${projectId}/cookies/project`)
  return response.data.data
}

export async function getLiveBrowserCookies(projectId: string): Promise<BrowserCookieInventoryResponse> {
  const response = await apiClient.get<ApiResponse<BrowserCookieInventoryResponse>>(`/browser/projects/${projectId}/cookies/live`)
  return response.data.data
}

export async function captureLiveBrowserCookies(projectId: string): Promise<BrowserCookieMutationResponse> {
  const response = await apiClient.post<ApiResponse<BrowserCookieMutationResponse>>(`/browser/projects/${projectId}/cookies/capture`)
  return response.data.data
}

export async function applyProjectBrowserCookies(projectId: string): Promise<BrowserCookieMutationResponse> {
  const response = await apiClient.post<ApiResponse<BrowserCookieMutationResponse>>(`/browser/projects/${projectId}/cookies/apply`)
  return response.data.data
}

export async function clearProjectBrowserCookies(projectId: string, domain?: string): Promise<BrowserCookieMutationResponse> {
  const suffix = domain ? `/project/${encodeURIComponent(domain)}` : '/project'
  const response = await apiClient.delete<ApiResponse<BrowserCookieMutationResponse>>(`/browser/projects/${projectId}/cookies${suffix}`)
  return response.data.data
}

export async function clearLiveBrowserCookies(projectId: string, domain?: string): Promise<BrowserCookieMutationResponse> {
  const suffix = domain ? `/live/${encodeURIComponent(domain)}` : '/live'
  const response = await apiClient.delete<ApiResponse<BrowserCookieMutationResponse>>(`/browser/projects/${projectId}/cookies${suffix}`)
  return response.data.data
}
