import type { AssetItem, AssetForm, AssetOperation } from '@/types/assets'
import type { ApiResponse } from '@/types/api'
import request from '@/utils/request'

export async function getAssetsList(params?: {
  keyword?: string
  status?: string
  category?: string
  sortBy?: string
}): Promise<ApiResponse<{ list: AssetItem[]; summary: { totalCount: number; categoryCount: number; totalCost: number; totalValue: number; valueChange: number } }>> {
  return request.get('/assets', { params })
}

export async function getAssetDetail(id: string): Promise<ApiResponse<AssetItem>> {
  return request.get(`/assets/${id}`)
}

export async function addAsset(data: AssetForm): Promise<ApiResponse<void>> {
  return request.post('/assets', data)
}

export async function updateAsset(id: string, data: Partial<AssetItem>): Promise<ApiResponse<void>> {
  return request.put(`/assets/${id}`, data)
}

export async function deleteAsset(id: string): Promise<ApiResponse<void>> {
  return request.delete(`/assets/${id}`)
}

export async function operateAsset(operation: AssetOperation): Promise<ApiResponse<void>> {
  return request.post(`/assets/${operation.assetId}/operate`, operation)
}
