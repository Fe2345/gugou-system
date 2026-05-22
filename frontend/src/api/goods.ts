import type { GoodsItem } from '@/types/goods'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

const USE_MOCK = true

const mockGoods: GoodsItem[] = [
  { id: '1', name: '玛奇朵限定徽章', price: 128, image: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80', ip: '精灵宝可梦联动', role: '玛奇朵', category: '徽章', description: '精灵宝可梦联动原版限定', status: 'approved', createdAt: '2026-05-01' },
  { id: '2', name: '深海明信片套装', price: 96, image: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80', ip: '原神', role: '深海龙蜥', category: '明信片', description: '原神深海系列明信片', status: 'approved', createdAt: '2026-05-02' },
  { id: '3', name: '春日限定徽章', price: 58, image: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80', ip: '初音未来', role: '初音', category: '徽章', description: '春日祭限定徽章', status: 'approved', createdAt: '2026-05-03' },
  { id: '4', name: '金色限定色纸', price: 168, image: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80', ip: '咒术回战', role: '五条悟', category: '色纸', description: '金色限定版色纸', status: 'approved', createdAt: '2026-05-04' },
  { id: '5', name: '亚克力立牌', price: 75, image: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80', ip: '间谍过家家', role: '阿尼亚', category: '亚克力', description: '阿尼亚表情包立牌', status: 'approved', createdAt: '2026-05-05' },
]

function delay(ms = 500) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export async function getGoodsList(params?: {
  keyword?: string
  category?: string
  page?: number
  pageSize?: number
}): Promise<ApiResponse<PaginatedResponse<GoodsItem>>> {
  if (USE_MOCK) {
    await delay()
    let list = [...mockGoods]
    if (params?.keyword) {
      const kw = params.keyword.toLowerCase()
      list = list.filter(g => g.name.toLowerCase().includes(kw) || g.ip.toLowerCase().includes(kw) || g.role.toLowerCase().includes(kw))
    }
    if (params?.category) {
      list = list.filter(g => g.category === params.category)
    }
    return { code: 200, message: 'ok', data: { list, total: list.length, page: params?.page || 1, pageSize: params?.pageSize || 10 } }
  }
  const { default: request } = await import('@/utils/request')
  return request.get('/goods', { params })
}

export async function getGoodsDetail(id: string): Promise<ApiResponse<GoodsItem>> {
  if (USE_MOCK) {
    await delay()
    const item = mockGoods.find(g => g.id === id)
    if (!item) throw { response: { data: { message: '商品不存在' } } }
    return { code: 200, message: 'ok', data: item }
  }
  const { default: request } = await import('@/utils/request')
  return request.get(`/goods/${id}`)
}

export async function addGoods(data: Partial<GoodsItem>): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    mockGoods.unshift({
      id: String(mockGoods.length + 1),
      name: data.name || '',
      price: data.price || 0,
      image: data.image || '',
      ip: data.ip || '',
      role: data.role || '',
      category: data.category || '',
      description: data.description || '',
      status: 'approved',
      createdAt: new Date().toISOString(),
    })
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.post('/goods', data)
}

export async function updateGoods(id: string, data: Partial<GoodsItem>): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    const idx = mockGoods.findIndex(g => g.id === id)
    if (idx !== -1) Object.assign(mockGoods[idx], data)
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.put(`/goods/${id}`, data)
}

export async function deleteGoods(id: string): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    const idx = mockGoods.findIndex(g => g.id === id)
    if (idx !== -1) mockGoods.splice(idx, 1)
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.delete(`/goods/${id}`)
}

export async function getGoodsCategories(): Promise<ApiResponse<string[]>> {
  if (USE_MOCK) {
    await delay(200)
    return { code: 200, message: 'ok', data: ['徽章', '色纸', '卡片', '亚克力', '明信片'] }
  }
  const { default: request } = await import('@/utils/request')
  return request.get('/goods/categories')
}
