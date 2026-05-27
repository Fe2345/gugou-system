import request from '@/utils/request'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

export interface GroupItem {
  id: string
  goodsId: string
  goodsName: string
  goodsImage: string
  targetCount: number
  currentCount: number
  price: number
  status: 'recruiting' | 'full' | 'completed' | 'cancelled'
  createdAt: string
}

export function getGroupList(params?: {
  status?: string
  page?: number
  pageSize?: number
}): Promise<ApiResponse<PaginatedResponse<GroupItem>>> {
  return request.get('/groups', { params })
}

export function getGroupDetail(id: string): Promise<ApiResponse<GroupItem>> {
  return request.get(`/groups/${id}`)
}

export function createGroup(data: {
  goodsId: string
  targetCount: number
  price: number
}): Promise<ApiResponse<void>> {
  return request.post('/groups', data)
}

export function joinGroup(id: string): Promise<ApiResponse<void>> {
  return request.put(`/groups/${id}/join`)
}

export function leaveGroup(id: string): Promise<ApiResponse<void>> {
  return request.put(`/groups/${id}/leave`)
}
