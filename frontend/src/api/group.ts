import request from '@/utils/request'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

export interface TeamItemOption {
  item_id: string
  name: string
  is_selected: boolean
  selected_user_name: string | null
  selected_at: string | null
  sort_order: number
}

export interface GroupItem {
  team_id: string
  product_name: string
  product_name_display: string
  product_price: number | null
  creator_id: string
  creator_name: string
  target_count: number
  current_count: number
  team_price: number
  deadline: string
  status: 'recruiting' | 'success' | 'failed' | 'cancelled'
  is_expired: boolean
  current_user_joined: boolean
  created_at: string
  items_count: number
  items_selected_count: number
}

export interface GroupDetailItem extends GroupItem {
  updated_at: string
  participants: GroupParticipantItem[]
  items: TeamItemOption[]
}

export interface GroupParticipantItem {
  participant_id: string
  user_id: string
  user_name: string
  status: 'joined' | 'cancelled' | 'refunded'
  joined_at: string
  selected_item_id: string | null
  selected_item_name: string | null
}

export function getGroupList(params?: {
  keyword?: string
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
  product_name: string
  team_price: number
  deadline_hours?: number
  items: string[]
}): Promise<ApiResponse<GroupDetailItem>> {
  return request.post('/teams/create/', data)
}

export function joinGroup(id: string, data: { item_id: string; address_id?: number }): Promise<ApiResponse<GroupDetailItem>> {
  return request.post(`/teams/${id}/join/`, data)
}

export function leaveGroup(id: string): Promise<ApiResponse<GroupDetailItem>> {
  return request.post(`/teams/${id}/leave/`)
}

export function cancelGroup(id: string): Promise<ApiResponse<void>> {
  return request.post(`/teams/${id}/cancel/`)
}

// 拼团订单相关接口
export interface TeamOrderItem {
  order_id: string
  buyer_id: string
  buyer_name: string
  seller_id: string
  seller_name: string
  product_id: string
  product_name: string
  quantity: number
  amount: number
  status: string
  paid_at: string | null
  completed_at: string | null
  created_at: string
  team_id: string
  shipping_address_id: number | null
  receiver_name: string
  receiver_phone: string
  shipping_address_text: string
}

export function getMyTeamOrder(teamId: string): Promise<ApiResponse<TeamOrderItem>> {
  return request.get(`/teams/${teamId}/my-order/`)
}

export function payTeamOrder(teamId: string, data: {
  pay_method?: string
  address_id: number
}): Promise<ApiResponse<void>> {
  return request.post(`/teams/${teamId}/pay/`, data)
}

export function confirmTeamOrder(teamId: string): Promise<ApiResponse<void>> {
  return request.post(`/teams/${teamId}/confirm/`)
}

export function returnTeamOrder(teamId: string, data?: {
  reason?: string
}): Promise<ApiResponse<void>> {
  return request.post(`/teams/${teamId}/return/`, data)
}
