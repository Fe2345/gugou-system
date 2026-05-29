import request from '@/utils/request'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

export interface SwapItem {
  exchange_id: string
  owner_id: string
  owner_name: string
  offered_asset_id: string
  offered_asset_name: string
  target_condition: string
  status: 'active' | 'matched' | 'completed' | 'cancelled' | 'expired'
  created_at: string
}

export interface SwapDetailItem extends SwapItem {
  price_difference_note: string
  updated_at: string
  matches: SwapMatchItem[]
  status_logs: SwapStatusLogItem[]
}

export interface SwapMatchItem {
  match_id: string
  applicant_id: string
  applicant_name: string
  applicant_asset_id: string
  applicant_asset_name: string
  status: 'pending' | 'accepted' | 'rejected' | 'expired'
  created_at: string
}

export interface SwapStatusLogItem {
  log_id: string
  from_status: string
  to_status: string
  operator_id: string
  operator_name: string
  note: string
  created_at: string
}

export function getSwapList(params?: {
  status?: string
  page?: number
  page_size?: number
}): Promise<ApiResponse<PaginatedResponse<SwapItem>>> {
  return request.get('/exchanges/', { params })
}

export function getSwapDetail(id: string): Promise<ApiResponse<SwapDetailItem>> {
  return request.get(`/exchanges/${id}/`)
}

export function getMySwaps(params?: {
  page?: number
  page_size?: number
}): Promise<ApiResponse<PaginatedResponse<SwapItem>>> {
  return request.get('/exchanges/my/', { params })
}

export function createSwap(data: {
  offered_asset_id: string
  target_condition?: string
  price_difference_note?: string
}): Promise<ApiResponse<SwapDetailItem>> {
  return request.post('/exchanges/create/', data)
}

export function matchSwap(id: string, data: {
  applicant_asset_id: string
}): Promise<ApiResponse<{ match_id: string }>> {
  return request.post(`/exchanges/${id}/match/`, data)
}

export function acceptMatch(exchangeId: string, matchId: string): Promise<ApiResponse<void>> {
  return request.post(`/exchanges/${exchangeId}/match/${matchId}/accept/`)
}

export function rejectMatch(exchangeId: string, matchId: string, reason?: string): Promise<ApiResponse<void>> {
  return request.post(`/exchanges/${exchangeId}/match/${matchId}/reject/`, { reason })
}

export function completeSwap(id: string): Promise<ApiResponse<void>> {
  return request.post(`/exchanges/${id}/complete/`)
}

export function cancelSwap(id: string): Promise<ApiResponse<void>> {
  return request.post(`/exchanges/${id}/cancel/`)
}
