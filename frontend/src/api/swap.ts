import request from '@/utils/request'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

export interface SwapItem {
  id: string
  userId: string
  userName: string
  offeredGoodsId: string
  offeredGoodsName: string
  offeredGoodsImage: string
  wantedGoodsDescription: string
  status: 'open' | 'matched' | 'completed' | 'cancelled'
  createdAt: string
}

export function getSwapList(params?: {
  status?: string
  page?: number
  pageSize?: number
}): Promise<ApiResponse<PaginatedResponse<SwapItem>>> {
  return request.get('/swaps', { params })
}

export function createSwap(data: {
  offeredGoodsId: string
  wantedGoodsDescription: string
}): Promise<ApiResponse<void>> {
  return request.post('/swaps', data)
}

export function matchSwap(id: string): Promise<ApiResponse<void>> {
  return request.put(`/swaps/${id}/match`)
}

export function completeSwap(id: string): Promise<ApiResponse<void>> {
  return request.put(`/swaps/${id}/complete`)
}

export function cancelSwap(id: string): Promise<ApiResponse<void>> {
  return request.put(`/swaps/${id}/cancel`)
}
