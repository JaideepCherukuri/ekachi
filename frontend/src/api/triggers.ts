import { apiClient, ApiResponse } from './client'
import type {
  ListTriggerRunsResponse,
  ListTriggersResponse,
  TriggerResponse,
  TriggerRunResponse,
  TriggerStatus,
  TriggerType,
} from '@/types/response'

export interface CreateTriggerPayload {
  project_id?: string | null
  name: string
  prompt: string
  trigger_type: TriggerType
  status?: TriggerStatus
  schedule_cron?: string | null
  schedule_timezone?: string
}

export interface UpdateTriggerPayload {
  project_id?: string | null
  name?: string
  prompt?: string
  status?: TriggerStatus
  schedule_cron?: string | null
  schedule_timezone?: string
}

export async function getTriggers(projectId?: string | null): Promise<ListTriggersResponse> {
  const response = await apiClient.get<ApiResponse<ListTriggersResponse>>('/triggers', {
    params: { project_id: projectId ?? undefined },
  })
  return response.data.data
}

export async function getTriggerRuns(projectId?: string | null, triggerId?: string | null): Promise<ListTriggerRunsResponse> {
  const response = await apiClient.get<ApiResponse<ListTriggerRunsResponse>>('/triggers/runs', {
    params: {
      project_id: projectId ?? undefined,
      trigger_id: triggerId ?? undefined,
    },
  })
  return response.data.data
}

export async function getTriggerRun(runId: string): Promise<TriggerRunResponse> {
  const response = await apiClient.get<ApiResponse<TriggerRunResponse>>(`/triggers/runs/${runId}`)
  return response.data.data
}

export async function createTrigger(payload: CreateTriggerPayload): Promise<TriggerResponse> {
  const response = await apiClient.post<ApiResponse<TriggerResponse>>('/triggers', payload)
  return response.data.data
}

export async function updateTrigger(triggerId: string, payload: UpdateTriggerPayload): Promise<TriggerResponse> {
  const response = await apiClient.patch<ApiResponse<TriggerResponse>>(`/triggers/${triggerId}`, payload)
  return response.data.data
}

export async function deleteTrigger(triggerId: string): Promise<void> {
  await apiClient.delete<ApiResponse<void>>(`/triggers/${triggerId}`)
}

export async function executeTrigger(triggerId: string, inputPayload?: Record<string, unknown> | null): Promise<TriggerRunResponse> {
  const response = await apiClient.post<ApiResponse<TriggerRunResponse>>(`/triggers/${triggerId}/execute`, {
    input_payload: inputPayload ?? undefined,
  })
  return response.data.data
}

export async function retryTriggerRun(runId: string): Promise<TriggerRunResponse> {
  const response = await apiClient.post<ApiResponse<TriggerRunResponse>>(`/triggers/runs/${runId}/retry`)
  return response.data.data
}

export async function cancelTriggerRun(runId: string): Promise<TriggerRunResponse> {
  const response = await apiClient.post<ApiResponse<TriggerRunResponse>>(`/triggers/runs/${runId}/cancel`)
  return response.data.data
}
