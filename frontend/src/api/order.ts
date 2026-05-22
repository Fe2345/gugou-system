import request from '@/utils/request'
import type { OrderItem } from '@/types/order'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

export function getOrderList(params?: {
  status?: string
  page?: number
  pageSize?: number
}): Promise<ApiResponse<PaginatedResponse<OrderItem>>> {
  return request.get('/orders', { params })
}

export function getOrderDetail(id: string): Promise<ApiResponse<OrderItem>> {
  return request.get(`/orders/${id}`)
}

export function createOrder(data: {
  goodsId: string
  quantity: number
}): Promise<ApiResponse<{ orderId: string }>> {
  return request.post('/orders', data)
}

export function cancelOrder(id: string): Promise<ApiResponse<void>> {
  return request.put(`/orders/${id}/cancel`)
}

export function confirmOrder(id: string): Promise<ApiResponse<void>> {
  return request.put(`/orders/${id}/confirm`)
}

export function payOrder(id: string): Promise<ApiResponse<{ payUrl: string }>> {
  return request.put(`/orders/${id}/pay`)
}
