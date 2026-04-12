import type { ListProjectsResponse, ProjectBrowserPoolEntry, ProjectResponse } from '@/types/response'
import { apiClient, ApiResponse } from './client'

export interface CreateProjectPayload {
  name: string
  color: string
  default_provider_id?: string | null
  default_model_name?: string | null
  preferred_search_provider?: string | null
  preferred_browser_engine?: string | null
  browser_cdp_url?: string | null
  browser_pool?: ProjectBrowserPoolEntry[]
  browser_cookie_profile?: string | null
  browser_extension_paths?: string[]
  browser_cookies?: Record<string, unknown>[]
}

export interface UpdateProjectPayload {
  name?: string
  color?: string
  default_provider_id?: string | null
  default_model_name?: string | null
  preferred_search_provider?: string | null
  preferred_browser_engine?: string | null
  browser_cdp_url?: string | null
  browser_pool?: ProjectBrowserPoolEntry[]
  browser_cookie_profile?: string | null
  browser_extension_paths?: string[]
  browser_cookies?: Record<string, unknown>[]
}

export async function getProjects(): Promise<ListProjectsResponse> {
  const response = await apiClient.get<ApiResponse<ListProjectsResponse>>('/projects')
  return response.data.data
}

export async function createProject(payload: CreateProjectPayload): Promise<ProjectResponse> {
  const response = await apiClient.post<ApiResponse<ProjectResponse>>('/projects', payload)
  return response.data.data
}

export async function updateProject(projectId: string, payload: UpdateProjectPayload): Promise<ProjectResponse> {
  const response = await apiClient.patch<ApiResponse<ProjectResponse>>(`/projects/${projectId}`, payload)
  return response.data.data
}

export async function deleteProject(projectId: string): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`/projects/${projectId}`)
}
