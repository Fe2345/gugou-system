import request from '@/utils/request'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

export interface MarketItem {
  id: string
  goodsId: string
  goodsName: string
  goodsImage: string
  price: number
  sellerId: string
  sellerName: string
  status: 'active' | 'sold' | 'cancelled'
  createdAt: string
}

export function getMarketList(params?: {
  keyword?: string
  category?: string
  sort?: 'price_asc' | 'price_desc' | 'newest'
  page?: number
  pageSize?: number
}): Promise<ApiResponse<PaginatedResponse<MarketItem>>> {
  return request.get('/market', { params })
}

export function publishToMarket(data: {
  goodsId: string
  price: number
}): Promise<ApiResponse<void>> {
  return request.post('/market', data)
}

export function removeFromMarket(id: string): Promise<ApiResponse<void>> {
  return request.delete(`/market/${id}`)
}
