import { apiClient, type ApiResponse } from './client'

export interface PrivacySettings {
  help_improve: boolean
}

export interface UpdatePrivacySettingsRequest {
  help_improve: boolean
}

export async function getPrivacySettings(): Promise<PrivacySettings> {
  const response = await apiClient.get<ApiResponse<PrivacySettings>>('/user/privacy')
  return response.data.data
}

export async function updatePrivacySettings(
  request: UpdatePrivacySettingsRequest,
): Promise<PrivacySettings> {
  const response = await apiClient.put<ApiResponse<PrivacySettings>>('/user/privacy', request)
  return response.data.data
}
