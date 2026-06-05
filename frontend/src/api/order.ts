import request from '@/utils/request'
import type { OrderItem } from '@/types/order'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

export function getOrderList(params?: {
  role?: 'buyer' | 'seller'
  status?: string
  keyword?: string
  page?: number
  page_size?: number
}): Promise<ApiResponse<PaginatedResponse<OrderItem>>> {
  return request.get('/orders/', { params })
}

export function getOrderDetail(id: string): Promise<ApiResponse<OrderItem>> {
  return request.get(`/orders/${id}/`)
}

export function createOrder(data: {
  listing_id: string
  quantity?: number
}): Promise<ApiResponse<OrderItem>> {
  return request.post('/orders/create/', data)
}

export function cancelOrder(id: string, reason?: string): Promise<ApiResponse<void>> {
  return request.post(`/orders/${id}/cancel/`, { reason })
}

export function confirmOrder(id: string): Promise<ApiResponse<void>> {
  return request.post(`/orders/${id}/complete/`)
}

export function createPayment(id: string, pay_method?: string): Promise<ApiResponse<{ payment_id: string }>> {
  return request.post(`/orders/${id}/payment/`, { pay_method })
}

export function confirmPayment(orderId: string, paymentId: string, addressId: number): Promise<ApiResponse<void>> {
  return request.post(`/orders/${orderId}/payment/${paymentId}/success/`, { address_id: addressId })
}

export function updateOrderAddress(orderId: string, addressId: number): Promise<ApiResponse<OrderItem>> {
  return request.post(`/orders/${orderId}/address/`, { address_id: addressId })
}

export function returnOrder(orderId: string, reason?: string): Promise<ApiResponse<void>> {
  return request.post(`/orders/${orderId}/return/`, { reason })
}
