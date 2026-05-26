import type { AssetItem, AssetForm, AssetSummary, AssetOperation } from '@/types/assets'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

const USE_MOCK = true

const mockAssets: AssetItem[] = [
  { id: 'A001', goodsId: '1', name: '鸣神 千本樱姬 限定徽章', ip: '哈利波特', role: '千本樱姬', category: '徽章', image: '', quantity: 2, costPrice: 76, currentValue: 96, status: 'holding', description: '限定版徽章', createdAt: '2026-04-01', updatedAt: '2026-05-01' },
  { id: 'A002', goodsId: '2', name: '哈利波特 影山飞雄 亚克力立牌', ip: '哈利波特', role: '影山飞雄', category: '亚克力', image: '', quantity: 1, costPrice: 88, currentValue: 82, status: 'holding', description: '亚克力立牌', createdAt: '2026-04-02', updatedAt: '2026-05-02' },
  { id: 'A003', goodsId: '3', name: '精灵宝可梦 皮卡丘 限定明信片', ip: '精灵宝可梦', role: '皮卡丘', category: '明信片', image: '', quantity: 3, costPrice: 45, currentValue: 72, status: 'selling', description: '限定明信片套装', createdAt: '2026-04-03', updatedAt: '2026-05-03' },
  { id: 'A004', goodsId: '4', name: '原神 风 岩神角色挂件', ip: '原神', role: '风', category: '挂件', image: '', quantity: 1, costPrice: 58, currentValue: 64, status: 'trading', description: '角色挂件', createdAt: '2026-04-04', updatedAt: '2026-05-04' },
  { id: 'A005', goodsId: '5', name: '崩坏星穹铁道 刃 色纸', ip: '崩坏星穹铁道', role: '刃', category: '色纸', image: '', quantity: 1, costPrice: 35, currentValue: 35, status: 'holding', description: '限定色纸', createdAt: '2026-04-05', updatedAt: '2026-05-05' },
  { id: 'A006', goodsId: '6', name: '圣斗士星矢 瞬 门票', ip: '圣斗士星矢', role: '瞬', category: '票据', image: '', quantity: 4, costPrice: 40, currentValue: 52, status: 'holding', description: '活动门票', createdAt: '2026-04-06', updatedAt: '2026-05-06' },
  { id: 'A007', goodsId: '7', name: '新世纪福音战士 明日香 限定套装', ip: '新世纪福音战士', role: '明日香', category: '限定套装', image: '', quantity: 1, costPrice: 120, currentValue: 108, status: 'selling', description: '限定套装', createdAt: '2026-04-07', updatedAt: '2026-05-07' },
  { id: 'A008', goodsId: '8', name: '时光代理人 陆光 透卡', ip: '时光代理人', role: '陆光', category: '透卡', image: '', quantity: 2, costPrice: 30, currentValue: 38, status: 'sold', description: '限定透卡', createdAt: '2026-04-08', updatedAt: '2026-05-08' },
]

function delay(ms = 500) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// 计算资产概览
function calculateSummary(assets: AssetItem[]): AssetSummary {
  const totalCount = assets.reduce((sum, a) => sum + a.quantity, 0)
  const categoryCount = new Set(assets.map(a => a.category)).size
  const totalCost = assets.reduce((sum, a) => sum + a.costPrice * a.quantity, 0)
  const totalValue = assets.reduce((sum, a) => sum + a.currentValue * a.quantity, 0)
  const valueChange = totalValue - totalCost
  return { totalCount, categoryCount, totalCost, totalValue, valueChange }
}

export async function getAssetsList(params?: {
  keyword?: string
  status?: string
  category?: string
  sortBy?: string
}): Promise<ApiResponse<{ list: AssetItem[]; summary: AssetSummary }>> {
  if (USE_MOCK) {
    await delay()
    let list = [...mockAssets]
    if (params?.keyword) {
      const kw = params.keyword.toLowerCase()
      list = list.filter(a =>
        a.name.toLowerCase().includes(kw) ||
        a.ip.toLowerCase().includes(kw) ||
        a.role.toLowerCase().includes(kw)
      )
    }
    if (params?.status && params.status !== 'all') {
      list = list.filter(a => a.status === params.status)
    }
    if (params?.category) {
      list = list.filter(a => a.category === params.category)
    }
    if (params?.sortBy === 'value') {
      list.sort((a, b) => b.currentValue - a.currentValue)
    } else if (params?.sortBy === 'change') {
      list.sort((a, b) => (b.currentValue - b.costPrice) - (a.currentValue - a.costPrice))
    }
    const summary = calculateSummary(list)
    return { code: 200, message: 'ok', data: { list, summary } }
  }
  const { default: request } = await import('@/utils/request')
  return request.get('/assets', { params })
}

export async function getAssetDetail(id: string): Promise<ApiResponse<AssetItem>> {
  if (USE_MOCK) {
    await delay()
    const item = mockAssets.find(a => a.id === id)
    if (!item) throw { response: { data: { message: '资产不存在' } } }
    return { code: 200, message: 'ok', data: item }
  }
  const { default: request } = await import('@/utils/request')
  return request.get(`/assets/${id}`)
}

export async function addAsset(data: AssetForm): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    mockAssets.unshift({
      id: 'A' + String(mockAssets.length + 1).padStart(3, '0'),
      goodsId: data.goodsId || '',
      name: data.name,
      ip: data.ip,
      role: data.role,
      category: data.category,
      image: data.image || '',
      quantity: data.quantity,
      costPrice: data.costPrice,
      currentValue: data.costPrice,
      status: 'holding',
      description: data.description || '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    })
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.post('/assets', data)
}

export async function updateAsset(id: string, data: Partial<AssetItem>): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    const idx = mockAssets.findIndex(a => a.id === id)
    if (idx !== -1) Object.assign(mockAssets[idx], data, { updatedAt: new Date().toISOString() })
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.put(`/assets/${id}`, data)
}

export async function deleteAsset(id: string): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    const idx = mockAssets.findIndex(a => a.id === id)
    if (idx !== -1) mockAssets.splice(idx, 1)
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.delete(`/assets/${id}`)
}

// 资产操作：上架、下架、卖出
export async function operateAsset(operation: AssetOperation): Promise<ApiResponse<void>> {
  if (USE_MOCK) {
    await delay()
    const asset = mockAssets.find(a => a.id === operation.assetId)
    if (!asset) throw { response: { data: { message: '资产不存在' } } }
    switch (operation.type) {
      case 'list':
        asset.status = 'selling'
        break
      case 'delist':
        asset.status = 'holding'
        break
      case 'sold':
        asset.status = 'sold'
        break
    }
    asset.updatedAt = new Date().toISOString()
    return { code: 200, message: 'ok', data: undefined }
  }
  const { default: request } = await import('@/utils/request')
  return request.post(`/assets/${operation.assetId}/operate`, operation)
}
