import type { PriceItem, PriceQuery } from '@/types/pricing'
import type { ApiResponse } from '@/types/api'
import request from '@/utils/request'

export async function queryPrice(params: PriceQuery): Promise<ApiResponse<PriceItem | null>> {
  return request.get('/pricing/query', { params })
}

export async function getHotPrices(): Promise<ApiResponse<PriceItem[]>> {
  return request.get('/pricing/hot')
}

export async function getMyAssetPrices(range: string): Promise<ApiResponse<(PriceItem & { quantity: number; acquirePrice: number | null })[]>> {
  return request.get('/pricing/my-assets', { params: { range } })
}
