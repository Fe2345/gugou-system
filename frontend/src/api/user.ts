import type { LoginForm, RegisterForm, LoginResult, UserInfo } from '@/types/user'
import type { ApiResponse } from '@/types/api'
import request from '@/utils/request'

export async function login(params: LoginForm): Promise<ApiResponse<LoginResult>> {
  return request.post('/auth/login', params)
}

export async function register(params: RegisterForm): Promise<ApiResponse<void>> {
  return request.post('/auth/register', { phone: params.phone, password: params.password })
}

export async function getUserInfo(): Promise<ApiResponse<UserInfo>> {
  return request.get('/user/info')
}

export async function updateUserInfo(data: Partial<UserInfo>): Promise<ApiResponse<void>> {
  return request.put('/user/info', data)
}

export async function logout(): Promise<ApiResponse<void>> {
  return request.post('/auth/logout')
}

export async function resetPassword(params: { phone: string; password: string }): Promise<ApiResponse<void>> {
  return request.post('/auth/reset-password', params)
}

export async function changePassword(oldPassword: string, newPassword: string): Promise<ApiResponse<void>> {
  return request.post('/user/change-password', { old_password: oldPassword, new_password: newPassword })
}

export interface LoginRecordItem {
  ip: string; ua: string; time: string
}

export async function getLoginRecords(): Promise<ApiResponse<LoginRecordItem[]>> {
  return request.get('/user/login-records')
}

export async function changePhone(phone: string): Promise<ApiResponse<UserInfo>> {
  return request.put('/user/change-phone', { phone })
}

export async function deleteAccount(): Promise<ApiResponse<void>> {
  return request.post('/user/delete-account')
}

export async function uploadAvatar(file: File): Promise<ApiResponse<{ avatar: string }>> {
  const formData = new FormData()
  formData.append('avatar', file)
  return request.post('/user/avatar/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
