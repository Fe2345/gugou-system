import request from '@/utils/request'
import type { LoginForm, RegisterForm, LoginResult, UserInfo } from '@/types/user'
import type { ApiResponse } from '@/types/api'

export function login(params: LoginForm): Promise<ApiResponse<LoginResult>> {
  return request.post('/auth/login', params)
}

export function register(params: RegisterForm): Promise<ApiResponse<void>> {
  return request.post('/auth/register', {
    phone: params.phone,
    password: params.password
  })
}

export function getUserInfo(): Promise<ApiResponse<UserInfo>> {
  return request.get('/user/info')
}

export function updateUserInfo(data: Partial<UserInfo>): Promise<ApiResponse<void>> {
  return request.put('/user/info', data)
}

export function logout(): Promise<ApiResponse<void>> {
  return request.post('/auth/logout')
}

export function resetPassword(params: { phone: string; password: string }): Promise<ApiResponse<void>> {
  return request.post('/auth/reset-password', params)
}
