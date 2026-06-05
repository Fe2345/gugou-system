import request from '@/utils/request'
import type { GoodsItem } from '@/types/goods'
import type { ApiResponse, PaginatedResponse } from '@/types/api'
import type { SwapItem, SwapDetailItem } from '@/api/swap'
import type { GroupItem, GroupDetailItem, GroupParticipantItem } from '@/api/group'

const USE_MOCK = false

function delay(ms = 500) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// ─── 管理员仪表盘类型 ───

export interface DashboardStats {
  user_count: number
  product_count: number
  order_count: number
  pending_count: number
  new_users_week: number
  orders_today: number
}

// ─── 管理员仪表盘 API ───

export async function getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
  return request.get('/admin/dashboard/')
}

// ─── 管理员用户类型 ───
export interface AdminUser {
  id: string
  name: string
  phone: string
  assets: number
  credit: number
  registered: string
  status: 'normal' | 'frozen' | 'disabled' | 'deleted'
}

// ─── 管理员价格记录类型 ───
export interface AdminPriceRecord {
  id: string
  productId?: string
  name: string
  price: number
  period: string
  change: number
  time: string
}

export interface AdminPriceHistoryPoint {
  date: string
  time: string
  price: number
}

// ─── 管理员商品 API ───

export async function getAdminGoodsList(params?: {
  keyword?: string
  status?: string
  category?: string
  page?: number
  page_size?: number
}): Promise<ApiResponse<PaginatedResponse<GoodsItem & { seller: string; submittedAt: string; stock: number }> & { stats?: { active: number; inactive: number; frozen: number; total: number } }>> {
  return request.get('/admin/goods', { params })
}

export async function createAdminGoods(data: Partial<GoodsItem>): Promise<ApiResponse<GoodsItem & { seller: string; submittedAt: string; stock: number }>> {
  return request.post('/admin/goods', data)
}

export async function approveGoods(id: string): Promise<ApiResponse<void>> {
  return request.put(`/admin/goods/${id}/approve`)
}

export async function rejectGoods(id: string): Promise<ApiResponse<void>> {
  return request.put(`/admin/goods/${id}/reject`)
}

export async function offlineGoods(id: string): Promise<ApiResponse<void>> {
  return request.put(`/admin/goods/${id}/offline`)
}

export async function editGoods(id: string, data: Partial<GoodsItem>): Promise<ApiResponse<void>> {
  return request.put(`/admin/goods/${id}/edit`, data)
}

// ─── 管理员用户 API ───

export async function getAdminUsersList(params?: {
  keyword?: string
  status?: string
  creditLevel?: string
}): Promise<ApiResponse<PaginatedResponse<AdminUser>>> {
  return request.get('/admin/users', { params })
}

export async function disableUser(id: string): Promise<ApiResponse<void>> {
  return request.put(`/admin/users/${id}/disable`)
}

export async function enableUser(id: string): Promise<ApiResponse<void>> {
  return request.put(`/admin/users/${id}/enable`)
}

// ─── 管理员价格 API ───

export async function getAdminPriceRecords(params?: {
  keyword?: string
  period?: string
  change?: string
  productId?: string
  startDate?: string
  endDate?: string
}): Promise<ApiResponse<AdminPriceRecord[]>> {
  return request.get('/admin/prices', { params })
}

export async function addPriceRecord(data: {
  productId?: string
  name: string
  price: number
  period: string
  change: number
  note?: string
  recordedAt?: string
}): Promise<ApiResponse<void>> {
  return request.post('/admin/prices', data)
}

export async function getAdminPriceHistory(params: {
  productId: string
  range?: string
  startDate?: string
  endDate?: string
}): Promise<ApiResponse<{ productId: string; points: AdminPriceHistoryPoint[] }>> {
  return request.get('/admin/prices/history', { params })
}

// ─── 管理员换物 API ───

export function getAdminExchangeList(params?: {
  keyword?: string
  status?: string
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}): Promise<ApiResponse<PaginatedResponse<SwapItem>>> {
  return request.get('/exchanges/admin/list/', { params })
}

export function getAdminExchangeDetail(id: string): Promise<ApiResponse<SwapDetailItem>> {
  return request.get(`/exchanges/admin/${id}/`)
}

export function adminExpireExchange(id: string): Promise<ApiResponse<void>> {
  return request.post(`/exchanges/admin/${id}/expire/`)
}

export function adminCancelExchange(id: string, reason?: string): Promise<ApiResponse<void>> {
  return request.post(`/exchanges/admin/${id}/cancel/`, { reason })
}

export function adminCompleteExchange(id: string): Promise<ApiResponse<void>> {
  return request.post(`/exchanges/admin/${id}/complete/`)
}

export function adminHandleAbnormalExchange(id: string, reason: string): Promise<ApiResponse<void>> {
  return request.post(`/exchanges/admin/${id}/handle-abnormal/`, { reason })
}

// ─── 管理员拼团 API ───

export function getAdminTeamList(params?: {
  keyword?: string
  status?: string
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}): Promise<ApiResponse<PaginatedResponse<GroupItem>>> {
  return request.get('/teams/admin/list/', { params })
}

export function getAdminTeamDetail(id: string): Promise<ApiResponse<GroupDetailItem>> {
  return request.get(`/teams/admin/${id}/`)
}

export function getAdminTeamParticipants(id: string): Promise<ApiResponse<GroupParticipantItem[]>> {
  return request.get(`/teams/admin/${id}/participants/`)
}

export function adminCancelTeam(id: string, reason?: string): Promise<ApiResponse<void>> {
  return request.post(`/teams/admin/${id}/cancel/`, { reason })
}

export function adminFailTeam(id: string): Promise<ApiResponse<void>> {
  return request.post(`/teams/admin/${id}/fail/`)
}

export function adminSuccessTeam(id: string): Promise<ApiResponse<void>> {
  return request.post(`/teams/admin/${id}/success/`)
}
