import request from '@/utils/request'
import type { GoodsItem } from '@/types/goods'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

export function getGoodsList(params?: {
  keyword?: string
  category?: string
  page?: number
  pageSize?: number
}): Promise<ApiResponse<PaginatedResponse<GoodsItem>>> {
  return request.get('/goods', { params })
}

export function getGoodsDetail(id: string): Promise<ApiResponse<GoodsItem>> {
  return request.get(`/goods/${id}`)
}

export function addGoods(data: Partial<GoodsItem>): Promise<ApiResponse<void>> {
  return request.post('/goods', data)
}

export function updateGoods(id: string, data: Partial<GoodsItem>): Promise<ApiResponse<void>> {
  return request.put(`/goods/${id}`, data)
}

export function deleteGoods(id: string): Promise<ApiResponse<void>> {
  return request.delete(`/goods/${id}`)
}

export function getGoodsCategories(): Promise<ApiResponse<string[]>> {
  return request.get('/goods/categories')
}
