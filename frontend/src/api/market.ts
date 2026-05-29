import request from '@/utils/request'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

export interface MarketItem {
  listing_id: string
  seller_id: string
  seller_name: string
  product_id: string
  product_name: string
  price: number
  quantity: number
  description: string
  status: 'active' | 'locked' | 'sold' | 'cancelled' | 'removed'
  images: { image_url: string; sort_order: number }[]
  created_at: string
}

export function getMarketList(params?: {
  status?: string
  product_id?: string
  min_price?: number
  max_price?: number
  page?: number
  page_size?: number
}): Promise<ApiResponse<PaginatedResponse<MarketItem>>> {
  return request.get('/market/', { params })
}

export function getMarketDetail(id: string): Promise<ApiResponse<MarketItem>> {
  return request.get(`/market/${id}/`)
}

export function publishToMarket(data: {
  product_id: string
  asset_id: string
  price: number
  quantity?: number
  description?: string
  images?: { image_url: string; sort_order?: number }[]
}): Promise<ApiResponse<MarketItem>> {
  return request.post('/market/create/', data)
}

export function cancelListing(id: string): Promise<ApiResponse<void>> {
  return request.post(`/market/${id}/cancel/`)
}

export function getMyListings(params?: {
  page?: number
  page_size?: number
}): Promise<ApiResponse<PaginatedResponse<MarketItem>>> {
  return request.get('/market/my/', { params })
}
