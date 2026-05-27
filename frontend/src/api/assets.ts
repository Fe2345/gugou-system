import type { AssetItem, AssetForm, AssetSummary, AssetOperation } from '@/types/assets'
import type { ApiResponse, PaginatedResponse } from '@/types/api'

const USE_MOCK = false

const mockAssets: AssetItem[] = [
  { id: 'A001', productId: '1', productName: '鸣神 千本樱姬 限定徽章', ipName: '哈利波特', characterName: '千本樱姬', category: '徽章', mainImage: '', quantity: 2, acquirePrice: 76, currentValue: 96, status: 'holding', description: '限定版徽章', createdAt: '2026-04-01', updatedAt: '2026-05-01' },
  { id: 'A002', productId: '2', productName: '哈利波特 影山飞雄 亚克力立牌', ipName: '哈利波特', characterName: '影山飞雄', category: '亚克力', mainImage: '', quantity: 1, acquirePrice: 88, currentValue: 82, status: 'holding', description: '亚克力立牌', createdAt: '2026-04-02', updatedAt: '2026-05-02' },
  { id: 'A003', productId: '3', productName: '精灵宝可梦 皮卡丘 限定明信片', ipName: '精灵宝可梦', characterName: '皮卡丘', category: '明信片', mainImage: '', quantity: 3, acquirePrice: 45, currentValue: 72, status: 'selling', description: '限定明信片套装', createdAt: '2026-04-03', updatedAt: '2026-05-03' },
  { id: 'A004', productId: '4', productName: '原神 风 岩神角色挂件', ipName: '原神', characterName: '风', category: '挂件', mainImage: '', quantity: 1, acquirePrice: 58, currentValue: 64, status: 'exchanging', description: '角色挂件', createdAt: '2026-04-04', updatedAt: '2026-05-04' },
  { id: 'A005', productId: '5', productName: '崩坏星穹铁道 刃 色纸', ipName: '崩坏星穹铁道', characterName: '刃', category: '色纸', mainImage: '', quantity: 1, acquirePrice: 35, currentValue: 35, status: 'holding', description: '限定色纸', createdAt: '2026-04-05', updatedAt: '2026-05-05' },
  { id: 'A006', productId: '6', productName: '圣斗士星矢 瞬 门票', ipName: '圣斗士星矢', characterName: '瞬', category: '票据', mainImage: '', quantity: 4, acquirePrice: 40, currentValue: 52, status: 'holding', description: '活动门票', createdAt: '2026-04-06', updatedAt: '2026-05-06' },
  { id: 'A007', productId: '7', productName: '新世纪福音战士 明日香 限定套装', ipName: '新世纪福音战士', characterName: '明日香', category: '限定套装', mainImage: '', quantity: 1, acquirePrice: 120, currentValue: 108, status: 'selling', description: '限定套装', createdAt: '2026-04-07', updatedAt: '2026-05-07' },
  { id: 'A008', productId: '8', productName: '时光代理人 陆光 透卡', ipName: '时光代理人', characterName: '陆光', category: '透卡', mainImage: '', quantity: 2, acquirePrice: 30, currentValue: 38, status: 'sold', description: '限定透卡', createdAt: '2026-04-08', updatedAt: '2026-05-08' },
]

function delay(ms = 500) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// 计算资产概览
function calculateSummary(assets: AssetItem[]): AssetSummary {
  const totalCount = assets.reduce((sum, a) => sum + a.quantity, 0)
  const categoryCount = new Set(assets.map(a => a.category)).size
  const totalCost = assets.reduce((sum, a) => sum + a.acquirePrice * a.quantity, 0)
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
        a.productName.toLowerCase().includes(kw) ||
        a.ipName.toLowerCase().includes(kw) ||
        a.characterName.toLowerCase().includes(kw)
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
      list.sort((a, b) => (b.currentValue - b.acquirePrice) - (a.currentValue - a.acquirePrice))
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
      productId: data.productId || '',
      productName: data.productName,
      ipName: data.ipName,
      characterName: data.characterName,
      category: data.category,
      mainImage: data.mainImage || '',
      quantity: data.quantity,
      acquirePrice: data.acquirePrice,
      currentValue: data.acquirePrice,
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
