import request from '@/utils/request'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

export interface CreditRecord {
  credit_record_id: string
  user_id: string
  user_name: string
  change_value: number
  reason: string
  related_order_id: string | null
  created_at: string
}

export interface CreditSummary {
  total_credit: number
  positive_count: number
  negative_count: number
  recent_records: CreditRecord[]
  restrictions: {
    level: string
    can_trade: boolean
    restrictions: string[]
  }
}

export interface TradingRestriction {
  level: string
  can_trade: boolean
  restrictions: string[]
}

export function getCreditRecords(params?: {
  page?: number
  page_size?: number
}): Promise<ApiResponse<PaginatedResponse<CreditRecord>>> {
  return request.get('/credits/', { params })
}

export function getCreditSummary(): Promise<ApiResponse<CreditSummary>> {
  return request.get('/credits/summary/')
}

export function adminAdjustCredit(data: {
  user_id: string
  change_value: number
  reason: string
}): Promise<ApiResponse<{ user_id: string; credit_score: number; change_value: number; reason: string }>> {
  return request.post('/credits/admin/adjust/', data)
}
