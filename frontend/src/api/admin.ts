import request from '@/utils/request'
import type { GoodsItem } from '@/types/goods'
import type { ApiResponse, PaginatedResponse } from '@/types/api'
import type { SwapItem, SwapDetailItem } from '@/api/swap'
import type { GroupItem, GroupDetailItem, GroupParticipantItem } from '@/api/group'

const USE_MOCK = false

function delay(ms = 500) {
  return new Promise(resolve => setTimeout(resolve, ms))
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

// ─── Mock 数据 ───
const mockUsers: AdminUser[] = [
  { id: 'BJUT000001', name: '张三', phone: '13812345678', assets: 12500, credit: 95, registered: '2026-01-12', status: 'normal' },
  { id: 'BJUT000002', name: '李四', phone: '13987654321', assets: 8600, credit: 88, registered: '2026-02-03', status: 'frozen' },
  { id: 'BJUT000003', name: '王五', phone: '13711223344', assets: 15200, credit: 99, registered: '2026-03-15', status: 'normal' },
  { id: 'BJUT000004', name: '赵六', phone: '13655667788', assets: 6300, credit: 72, registered: '2026-04-01', status: 'normal' },
  { id: 'BJUT000005', name: '孙七', phone: '13599887766', assets: 21800, credit: 91, registered: '2025-12-20', status: 'frozen' },
]

const mockAdminGoods: any[] = [
  { id: 'G1001', name: '蓝色幻想系列 限定徽章套组', referencePrice: 128, mainImage: '', ipName: '蓝色幻想', characterName: '群像', category: '徽章/吧唧', description: '限定徽章套组', status: 'normal', createdAt: '2026-05-06', seller: 'BJUT000126', submittedAt: '10:28', stock: 12 },
  { id: 'G1002', name: '樱花季角色亚克力立牌', referencePrice: 68, mainImage: '', ipName: '樱花季', characterName: '主角', category: '亚克力立牌', description: '亚克力立牌', status: 'normal', createdAt: '2026-05-06', seller: 'BJUT000219', submittedAt: '09:52', stock: 8 },
  { id: 'G1003', name: '限定拍立得收藏卡 随机款', referencePrice: 45, mainImage: '', ipName: '限定系列', characterName: '随机', category: '拍立得/色纸', description: '拍立得收藏卡', status: 'inactive', createdAt: '2026-05-05', seller: 'BJUT000308', submittedAt: '昨天', stock: 20 },
  { id: 'G1004', name: '角色挂件 生日纪念款', referencePrice: 36, mainImage: '', ipName: '生日系列', characterName: '角色', category: '挂件', description: '生日纪念挂件', status: 'normal', createdAt: '2026-05-05', seller: 'BJUT000176', submittedAt: '昨天', stock: 15 },
  { id: 'G1005', name: '原神 甘雨 限定亚克力砖', referencePrice: 198, mainImage: '', ipName: '原神', characterName: '甘雨', category: '亚克力砖', description: '甘雨限定亚克力砖', status: 'normal', createdAt: '2026-05-06', seller: 'BJUT000333', submittedAt: '30 分钟前', stock: 5 },
]

const mockPriceRecords: AdminPriceRecord[] = [
  { id: 'PR202605060001', name: '吧唧限定 A', price: 56, period: '近7天', change: 8.5, time: '2026-05-06 08:00' },
  { id: 'PR202605060008', name: '色纸套组 B', price: 105, period: '近30天', change: -6.2, time: '2026-05-06 09:30' },
  { id: 'PR202605050022', name: '拍立得单张', price: 39, period: '近7天', change: 15, time: '2026-05-05 18:00' },
  { id: 'PR202605040015', name: '玛奇朵 亚克力砖', price: 286, period: '近30天', change: 12.4, time: '2026-05-04 10:00' },
  { id: 'PR202605030009', name: '崩坏星穹铁道 刃 色纸', price: 35, period: '近7天', change: 0, time: '2026-05-03 14:00' },
]

// ─── 管理员商品 API ───

export async function getAdminGoodsList(params?: {
  keyword?: string
  status?: string
  category?: string
  page?: number
  page_size?: number
}): Promise<ApiResponse<PaginatedResponse<GoodsItem & { seller: string; submittedAt: string; stock: number }> & { stats?: { active: number; inactive: number; frozen: number; total: number } }>> {
  if (USE_MOCK) {
    await delay()
    let list = [...mockAdminGoods]
    if (params?.keyword) {
      const kw = params.keyword.toLowerCase()
      list = list.filter(g => g.name.toLowerCase().includes(kw) || g.id.toLowerCase().includes(kw) || g.seller.toLowerCase().includes(kw))
    }
    if (params?.status && params.status !== 'all') {
      list = list.filter(g => g.status === params.status)
    }
    if (params?.category) {
      list = list.filter(g => g.category === params.category)
    }
    return { code: 200, message: 'ok', data: { results: list, count: list.length, page: 1, page_size: 20 } }
  }
  const { default: request } = await import('@/utils/request')
  return request.get('/admin/goods', { params })
}

export async function createAdminGoods(data: Partial<GoodsItem>): Promise<ApiResponse<GoodsItem & { seller: string; submittedAt: string; stock: number }>> {
  if (USE_MOCK) {
    await delay()
    const item = {
      id: 'G' + Date.now(),
      name: data.name || '',
      referencePrice: data.referencePrice || 0,
      mainImage: data.mainImage || '',
      ipName: data.ipName || '',
      characterName: data.characterName || '',
      category: data.category || 'other',
      description: data.description || '',
      status: 'active',
      createdAt: new Date().toISOString(),
      seller: 'ADMIN',
      submittedAt: new Date().toLocaleString(),
      stock: 0,
    } as GoodsItem & { seller: string; submittedAt: string; stock: number }
    mockAdminGoods.unshift(item)
    return { code: 200, message: 'ok', data: item }
  }
  const { default: request } = await import('@/utils/request')
  return request.post('/admin/goods', data)
}

export async function approveGoods(id: string): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    const item = mockAdminGoods.find(g => g.id === id)
    if (item) item.status = 'active'
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.put(`/admin/goods/${id}/approve`)
}

export async function rejectGoods(id: string): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    const item = mockAdminGoods.find(g => g.id === id)
    if (item) item.status = 'inactive'
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.put(`/admin/goods/${id}/reject`)
}

export async function offlineGoods(id: string): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    const item = mockAdminGoods.find(g => g.id === id)
    if (item) item.status = 'inactive'
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.put(`/admin/goods/${id}/offline`)
}

export async function editGoods(id: string, data: Partial<GoodsItem>): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    const item = mockAdminGoods.find(g => g.id === id)
    if (item) Object.assign(item, data)
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.put(`/admin/goods/${id}/edit`, data)
}

// ─── 管理员用户 API ───

export async function getAdminUsersList(params?: {
  keyword?: string
  status?: string
  creditLevel?: string
}): Promise<ApiResponse<PaginatedResponse<AdminUser>>> {
  if (USE_MOCK) {
    await delay()
    let list = [...mockUsers]
    if (params?.keyword) {
      const kw = params.keyword.toLowerCase()
      list = list.filter(u => u.name.toLowerCase().includes(kw) || u.id.toLowerCase().includes(kw) || u.phone.includes(kw))
    }
    if (params?.status === '正常') {
      list = list.filter(u => u.status === 'normal')
    } else if (params?.status === '冻结') {
      list = list.filter(u => u.status === 'frozen')
    }
    if (params?.creditLevel === '高') {
      list = list.filter(u => u.credit >= 90)
    } else if (params?.creditLevel === '中') {
      list = list.filter(u => u.credit >= 70 && u.credit < 90)
    } else if (params?.creditLevel === '低') {
      list = list.filter(u => u.credit < 70)
    }
    return { code: 200, message: 'ok', data: { results: list, count: list.length, page: 1, page_size: list.length } }
  }
  const { default: request } = await import('@/utils/request')
  return request.get('/admin/users', { params })
}

export async function freezeUser(id: string): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    const user = mockUsers.find(u => u.id === id)
    if (user) user.status = 'frozen'
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.put(`/admin/users/${id}/freeze`)
}

export async function unfreezeUser(id: string): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    const user = mockUsers.find(u => u.id === id)
    if (user) user.status = 'normal'
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.put(`/admin/users/${id}/unfreeze`)
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
  if (USE_MOCK) {
    await delay()
    let list = [...mockPriceRecords]
    if (params?.keyword) {
      const kw = params.keyword.toLowerCase()
      list = list.filter(r => r.name.toLowerCase().includes(kw) || r.id.toLowerCase().includes(kw))
    }
    if (params?.period && params.period !== '全部') {
      list = list.filter(r => r.period === params.period)
    }
    if (params?.change === '上涨') {
      list = list.filter(r => r.change > 0)
    } else if (params?.change === '下跌') {
      list = list.filter(r => r.change < 0)
    }
    return { code: 200, message: 'ok', data: list }
  }
  const { default: request } = await import('@/utils/request')
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
  if (USE_MOCK) {
    await delay()
    mockPriceRecords.unshift({
      id: 'PR' + Date.now(),
      name: data.name,
      price: data.price,
      period: data.period,
      change: data.change,
      time: new Date().toLocaleString(),
    })
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.post('/admin/prices', data)
}

export async function getAdminPriceHistory(params: {
  productId: string
  range?: string
  startDate?: string
  endDate?: string
}): Promise<ApiResponse<{ productId: string; points: AdminPriceHistoryPoint[] }>> {
  if (USE_MOCK) {
    await delay()
    const list = mockPriceRecords
      .filter(r => !params.productId || r.name.includes(params.productId) || r.id === params.productId)
      .map(r => ({ date: r.time.slice(0, 10), time: r.time, price: r.price }))
    return { code: 200, message: 'ok', data: { productId: params.productId, points: list } }
  }
  const { default: request } = await import('@/utils/request')
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
