import { apiClient, ApiResponse } from './client'
import type {
  ListSkillsResponse,
  ListWorkersResponse,
  MemoryResponse,
  SkillResponse,
  WorkerLane,
  WorkerResponse,
  WorkerRole,
} from '@/types/response'

export interface CreateSkillPayload {
  project_id?: string | null
  name: string
  description?: string | null
  instructions: string
  enabled?: boolean
}

export interface UpdateSkillPayload {
  project_id?: string | null
  name?: string
  description?: string | null
  instructions?: string
  enabled?: boolean
}

export interface CreateWorkerPayload {
  project_id?: string | null
  name: string
  description?: string | null
  role: WorkerRole
  lane: WorkerLane
  instructions: string
  tool_names?: string[]
  enabled?: boolean
}

export interface UpdateWorkerPayload {
  project_id?: string | null
  name?: string
  description?: string | null
  role?: WorkerRole
  lane?: WorkerLane
  instructions?: string
  tool_names?: string[]
  enabled?: boolean
}

export async function getSkills(projectId?: string | null): Promise<ListSkillsResponse> {
  const response = await apiClient.get<ApiResponse<ListSkillsResponse>>('/capabilities/skills', {
    params: { project_id: projectId ?? undefined },
  })
  return response.data.data
}

export async function createSkill(payload: CreateSkillPayload): Promise<SkillResponse> {
  const response = await apiClient.post<ApiResponse<SkillResponse>>('/capabilities/skills', payload)
  return response.data.data
}

export async function updateSkill(skillId: string, payload: UpdateSkillPayload): Promise<SkillResponse> {
  const response = await apiClient.patch<ApiResponse<SkillResponse>>(`/capabilities/skills/${skillId}`, payload)
  return response.data.data
}

export async function deleteSkill(skillId: string): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`/capabilities/skills/${skillId}`)
}

export async function getMemory(projectId?: string | null): Promise<MemoryResponse> {
  const response = await apiClient.get<ApiResponse<MemoryResponse>>('/capabilities/memory', {
    params: { project_id: projectId ?? undefined },
  })
  return response.data.data
}

export async function updateMemory(projectId: string | null | undefined, content: string): Promise<MemoryResponse> {
  const response = await apiClient.put<ApiResponse<MemoryResponse>>('/capabilities/memory', {
    project_id: projectId ?? undefined,
    content,
  })
  return response.data.data
}

export async function getWorkers(projectId?: string | null): Promise<ListWorkersResponse> {
  const response = await apiClient.get<ApiResponse<ListWorkersResponse>>('/capabilities/workers', {
    params: { project_id: projectId ?? undefined },
  })
  return response.data.data
}

export async function createWorker(payload: CreateWorkerPayload): Promise<WorkerResponse> {
  const response = await apiClient.post<ApiResponse<WorkerResponse>>('/capabilities/workers', payload)
  return response.data.data
}

export async function updateWorker(workerId: string, payload: UpdateWorkerPayload): Promise<WorkerResponse> {
  const response = await apiClient.patch<ApiResponse<WorkerResponse>>(`/capabilities/workers/${workerId}`, payload)
  return response.data.data
}

export async function deleteWorker(workerId: string): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`/capabilities/workers/${workerId}`)
}
