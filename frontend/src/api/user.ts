import type { LoginForm, RegisterForm, LoginResult, UserInfo } from '@/types/user'
import type { ApiResponse } from '@/types/api'

// Mock 开关：设为 true 使用本地模拟数据
const USE_MOCK = false

// Mock 用户数据
const mockUsers: Record<string, { password: string; user: UserInfo }> = {
  '13800000000': {
    password: '123456',
    user: { id: '1', phone: '13800000000', nickname: '测试用户', avatar: '', role: 'user', createdAt: '2026-01-01' },
  },
  'admin': {
    password: '123456',
    user: { id: '100', phone: '13999999999', nickname: '管理员', avatar: '', role: 'admin', createdAt: '2026-01-01' },
  },
}

function delay(ms = 500) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export async function login(params: LoginForm): Promise<ApiResponse<LoginResult>> {
  if (USE_MOCK) {
    await delay()
    const found = mockUsers[params.account]
    if (!found || found.password !== params.password) {
      throw { response: { data: { message: '账号或密码错误' } } }
    }
    return { code: 200, message: 'ok', data: { token: 'mock-token-' + Date.now(), user: found.user } }
  }
  const { default: request } = await import('@/utils/request')
  return request.post('/auth/login', params)
}

export async function register(params: RegisterForm): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    if (mockUsers[params.phone]) {
      throw { response: { data: { message: '该手机号已注册' } } }
    }
    mockUsers[params.phone] = {
      password: params.password,
      user: { id: String(Object.keys(mockUsers).length + 1), phone: params.phone, nickname: '新用户', avatar: '', role: 'user', createdAt: new Date().toISOString() },
    }
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.post('/auth/register', { phone: params.phone, password: params.password })
}

export async function getUserInfo(): Promise<ApiResponse<UserInfo>> {
  if (USE_MOCK) {
    await delay()
    return { code: 200, message: 'ok', data: mockUsers['13800000000'].user }
  }
  const { default: request } = await import('@/utils/request')
  return request.get('/user/info')
}

export async function updateUserInfo(data: Partial<UserInfo>): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.put('/user/info', data)
}

export async function logout(): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay(200)
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.post('/auth/logout')
}

export async function resetPassword(params: { phone: string; password: string }): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    if (!mockUsers[params.phone]) {
      throw { response: { data: { message: '未找到该手机号' } } }
    }
    mockUsers[params.phone].password = params.password
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.post('/auth/reset-password', params)
}
