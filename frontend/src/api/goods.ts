import type { GoodsItem } from '@/types/goods'
import type { ApiResponse } from '@/types/api'
import request from '@/utils/request'

export async function getGoodsList(params?: {
  keyword?: string
  category?: string
  page?: number
  pageSize?: number
  mine?: boolean
}): Promise<ApiResponse<{ list: GoodsItem[]; total: number; page: number; pageSize: number }>> {
  return request.get('/products', { params })
}

export async function getGoodsDetail(id: string): Promise<ApiResponse<GoodsItem>> {
  return request.get(`/products/${id}`)
}

export async function addGoods(data: Partial<GoodsItem>): Promise<ApiResponse<void>> {
  return request.post('/products', data)
}

export async function getMyGoodsList(): Promise<ApiResponse<{ list: GoodsItem[]; total: number; page: number; pageSize: number }>> {
  return request.get('/products', { params: { mine: true, pageSize: 100 } })
}

export async function updateGoods(id: string, data: Partial<GoodsItem>): Promise<ApiResponse<void>> {
  return request.put(`/products/${id}`, data)
}

export async function deleteGoods(id: string): Promise<ApiResponse<void>> {
  return request.delete(`/products/${id}`)
}

export async function getGoodsCategories(): Promise<ApiResponse<{ value: string; label: string }[]>> {
  return request.get('/products/categories')
}
