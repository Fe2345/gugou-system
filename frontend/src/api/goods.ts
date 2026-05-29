import type { GoodsItem } from '@/types/goods'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

const USE_MOCK = false

const mockGoods: GoodsItem[] = [
  { id: '1', name: '玛奇朵限定徽章', referencePrice: 128, mainImage: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80', ipName: '精灵宝可梦联动', characterName: '玛奇朵', category: '徽章', description: '精灵宝可梦联动原版限定', status: 'active', createdAt: '2026-05-01' },
  { id: '2', name: '深海明信片套装', referencePrice: 96, mainImage: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80', ipName: '原神', characterName: '深海龙蜥', category: '明信片', description: '原神深海系列明信片', status: 'active', createdAt: '2026-05-02' },
  { id: '3', name: '春日限定徽章', referencePrice: 58, mainImage: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80', ipName: '初音未来', characterName: '初音', category: '徽章', description: '春日祭限定徽章', status: 'active', createdAt: '2026-05-03' },
  { id: '4', name: '金色限定色纸', referencePrice: 168, mainImage: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80', ipName: '咒术回战', characterName: '五条悟', category: '色纸', description: '金色限定版色纸', status: 'active', createdAt: '2026-05-04' },
  { id: '5', name: '亚克力立牌', referencePrice: 75, mainImage: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80', ipName: '间谍过家家', characterName: '阿尼亚', category: '亚克力', description: '阿尼亚表情包立牌', status: 'active', createdAt: '2026-05-05' },
]

function delay(ms = 500) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export async function getGoodsList(params?: {
  keyword?: string
  category?: string
  page?: number
  pageSize?: number
}): Promise<ApiResponse<{ list: GoodsItem[]; total: number; page: number; pageSize: number }>> {
  if (USE_MOCK) {
    await delay()
    let list = [...mockGoods]
    if (params?.keyword) {
      const kw = params.keyword.toLowerCase()
      list = list.filter(g => g.name.toLowerCase().includes(kw) || g.ipName.toLowerCase().includes(kw) || g.characterName.toLowerCase().includes(kw))
    }
    if (params?.category) {
      list = list.filter(g => g.category === params.category)
    }
    return { code: 200, message: 'ok', data: { list, total: list.length, page: params?.page || 1, pageSize: params?.pageSize || 10 } }
  }
  const { default: request } = await import('@/utils/request')
  return request.get('/products', { params })
}

export async function getGoodsDetail(id: string): Promise<ApiResponse<GoodsItem>> {
  if (USE_MOCK) {
    await delay()
    const item = mockGoods.find(g => g.id === id)
    if (!item) throw { response: { data: { message: '商品不存在' } } }
    return { code: 200, message: 'ok', data: item }
  }
  const { default: request } = await import('@/utils/request')
  return request.get(`/products/${id}`)
}

export async function addGoods(data: Partial<GoodsItem>): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    mockGoods.unshift({
      id: String(mockGoods.length + 1),
      name: data.name || '',
      referencePrice: data.referencePrice || 0,
      mainImage: data.mainImage || '',
      ipName: data.ipName || '',
      characterName: data.characterName || '',
      category: data.category || '',
      description: data.description || '',
      status: 'active',
      createdAt: new Date().toISOString(),
    })
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.post('/products', data)
}

export async function updateGoods(id: string, data: Partial<GoodsItem>): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    const idx = mockGoods.findIndex(g => g.id === id)
    if (idx !== -1) Object.assign(mockGoods[idx], data)
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.put(`/products/${id}`, data)
}

export async function deleteGoods(id: string): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    const idx = mockGoods.findIndex(g => g.id === id)
    if (idx !== -1) mockGoods.splice(idx, 1)
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.delete(`/products/${id}`)
}

export async function getGoodsCategories(): Promise<ApiResponse<{ value: string; label: string }[]>> {
  if (USE_MOCK) {
    await delay(200)
    return { code: 200, message: 'ok', data: [
      { value: 'figure', label: '手办' },
      { value: 'badge', label: '徽章' },
      { value: 'poster', label: '海报' },
      { value: 'acrylic', label: '亚克力' },
      { value: 'doll', label: '玩偶' },
      { value: 'card', label: '卡片' },
      { value: 'other', label: '其他' },
    ] }
  }
  const { default: request } = await import('@/utils/request')
  return request.get('/products/categories')
}
