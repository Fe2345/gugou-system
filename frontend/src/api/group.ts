import request from '@/utils/request'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

export interface GroupItem {
  team_id: string
  product_id: string
  product_name: string
  product_price: number
  creator_id: string
  creator_name: string
  target_count: number
  current_count: number
  team_price: number
  deadline: string
  status: 'recruiting' | 'success' | 'failed' | 'cancelled'
  is_expired: boolean
  created_at: string
}

export interface GroupDetailItem extends GroupItem {
  updated_at: string
  participants: GroupParticipantItem[]
}

export interface GroupParticipantItem {
  participant_id: string
  user_id: string
  user_name: string
  status: 'joined' | 'cancelled' | 'refunded'
  joined_at: string
}

export function getGroupList(params?: {
  status?: string
  product_id?: string
  page?: number
  page_size?: number
}): Promise<ApiResponse<PaginatedResponse<GroupItem>>> {
  return request.get('/teams/', { params })
}

export function getGroupDetail(id: string): Promise<ApiResponse<GroupDetailItem>> {
  return request.get(`/teams/${id}/`)
}

export function getMyGroups(params?: {
  page?: number
  page_size?: number
}): Promise<ApiResponse<PaginatedResponse<GroupItem>>> {
  return request.get('/teams/my/', { params })
}

export function createGroup(data: {
  product_id: string
  target_count: number
  team_price: number
  deadline_hours?: number
}): Promise<ApiResponse<GroupDetailItem>> {
  return request.post('/teams/create/', data)
}

export function joinGroup(id: string): Promise<ApiResponse<GroupDetailItem>> {
  return request.post(`/teams/${id}/join/`)
}

export function leaveGroup(id: string): Promise<ApiResponse<GroupDetailItem>> {
  return request.post(`/teams/${id}/leave/`)
}

export function cancelGroup(id: string): Promise<ApiResponse<void>> {
  return request.post(`/teams/${id}/cancel/`)
}
