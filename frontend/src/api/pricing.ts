import type { PriceItem, PriceQuery } from '@/types/pricing'
import type { ApiResponse } from '@/types/api'

const USE_MOCK = false

const mockPriceData: PriceItem[] = [
  {
    id: 'P001',
    name: '玛奇朵 亚克力砖',
    ipName: '女神异闻录3',
    characterName: '玛奇朵',
    category: '亚克力砖',
    currentPrice: 286,
    avgPrice: 274,
    maxPrice: 335,
    minPrice: 218,
    changePercent: 12.4,
    trend: [
      { date: '3月第1周', price: 232 },
      { date: '3月第2周', price: 248 },
      { date: '3月第3周', price: 240 },
      { date: '3月第4周', price: 262 },
      { date: '4月第1周', price: 276 },
      { date: '4月第2周', price: 292 },
      { date: '4月第3周', price: 285 },
      { date: '4月第4周', price: 305 },
      { date: '5月第1周', price: 286 },
    ],
    transactions: [
      { date: '2026-05-03', name: '玛奇朵 亚克力砖', price: 286, condition: '全新未拆', method: '平台担保' },
      { date: '2026-04-28', name: '玛奇朵 亚克力砖', price: 292, condition: '全新未拆', method: '平台担保' },
      { date: '2026-04-21', name: '玛奇朵 亚克力砖', price: 276, condition: '微瑕疵', method: '平台担保' },
      { date: '2026-04-12', name: '玛奇朵 亚克力砖', price: 281, condition: '全新未拆', method: '平台担保' },
      { date: '2026-03-26', name: '玛奇朵 亚克力砖', price: 256, condition: '拆封未用', method: '平台担保' },
    ],
  },
  {
    id: 'P002',
    name: '鸣神 千本樱姬 限定徽章',
    ipName: '哈利波特',
    characterName: '千本樱姬',
    category: '徽章',
    currentPrice: 96,
    avgPrice: 88,
    maxPrice: 112,
    minPrice: 68,
    changePercent: 8.2,
    trend: [
      { date: '3月第1周', price: 68 },
      { date: '3月第2周', price: 72 },
      { date: '3月第3周', price: 78 },
      { date: '3月第4周', price: 85 },
      { date: '4月第1周', price: 90 },
      { date: '4月第2周', price: 95 },
      { date: '4月第3周', price: 88 },
      { date: '4月第4周', price: 102 },
      { date: '5月第1周', price: 96 },
    ],
    transactions: [
      { date: '2026-05-02', name: '鸣神 千本樱姬 限定徽章', price: 96, condition: '全新未拆', method: '平台担保' },
      { date: '2026-04-25', name: '鸣神 千本樱姬 限定徽章', price: 102, condition: '全新未拆', method: '平台担保' },
      { date: '2026-04-18', name: '鸣神 千本樱姬 限定徽章', price: 88, condition: '拆封', method: '平台担保' },
      { date: '2026-04-05', name: '鸣神 千本樱姬 限定徽章', price: 90, condition: '全新未拆', method: '平台担保' },
    ],
  },
  {
    id: 'P003',
    name: '精灵宝可梦 皮卡丘 限定明信片',
    ipName: '精灵宝可梦',
    characterName: '皮卡丘',
    category: '明信片',
    currentPrice: 72,
    avgPrice: 65,
    maxPrice: 85,
    minPrice: 48,
    changePercent: -3.5,
    trend: [
      { date: '3月第1周', price: 75 },
      { date: '3月第2周', price: 78 },
      { date: '3月第3周', price: 82 },
      { date: '3月第4周', price: 85 },
      { date: '4月第1周', price: 80 },
      { date: '4月第2周', price: 76 },
      { date: '4月第3周', price: 70 },
      { date: '4月第4周', price: 68 },
      { date: '5月第1周', price: 72 },
    ],
    transactions: [
      { date: '2026-05-01', name: '精灵宝可梦 皮卡丘 限定明信片', price: 72, condition: '拆封', method: '平台担保' },
      { date: '2026-04-22', name: '精灵宝可梦 皮卡丘 限定明信片', price: 68, condition: '全新未拆', method: '平台担保' },
      { date: '2026-04-10', name: '精灵宝可梦 皮卡丘 限定明信片', price: 76, condition: '全新未拆', method: '平台担保' },
    ],
  },
  {
    id: 'P004',
    name: '原神 风 岩神角色挂件',
    ipName: '原神',
    characterName: '风',
    category: '挂件',
    currentPrice: 64,
    avgPrice: 58,
    maxPrice: 72,
    minPrice: 45,
    changePercent: 5.8,
    trend: [
      { date: '3月第1周', price: 45 },
      { date: '3月第2周', price: 48 },
      { date: '3月第3周', price: 52 },
      { date: '3月第4周', price: 55 },
      { date: '4月第1周', price: 58 },
      { date: '4月第2周', price: 62 },
      { date: '4月第3周', price: 60 },
      { date: '4月第4周', price: 66 },
      { date: '5月第1周', price: 64 },
    ],
    transactions: [
      { date: '2026-05-04', name: '原神 风 岩神角色挂件', price: 64, condition: '全新未拆', method: '平台担保' },
      { date: '2026-04-20', name: '原神 风 岩神角色挂件', price: 60, condition: '拆封', method: '平台担保' },
      { date: '2026-04-08', name: '原神 风 岩神角色挂件', price: 58, condition: '全新未拆', method: '平台担保' },
    ],
  },
  {
    id: 'P005',
    name: '崩坏星穹铁道 刃 色纸',
    ipName: '崩坏星穹铁道',
    characterName: '刃',
    category: '色纸',
    currentPrice: 35,
    avgPrice: 33,
    maxPrice: 42,
    minPrice: 25,
    changePercent: 0,
    trend: [
      { date: '3月第1周', price: 28 },
      { date: '3月第2周', price: 30 },
      { date: '3月第3周', price: 32 },
      { date: '3月第4周', price: 35 },
      { date: '4月第1周', price: 38 },
      { date: '4月第2周', price: 42 },
      { date: '4月第3周', price: 38 },
      { date: '4月第4周', price: 36 },
      { date: '5月第1周', price: 35 },
    ],
    transactions: [
      { date: '2026-05-03', name: '崩坏星穹铁道 刃 色纸', price: 35, condition: '全新未拆', method: '平台担保' },
      { date: '2026-04-15', name: '崩坏星穹铁道 刃 色纸', price: 38, condition: '全新未拆', method: '平台担保' },
    ],
  },
]

function delay(ms = 500) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export async function queryPrice(params: PriceQuery): Promise<ApiResponse<PriceItem | null>> {
  if (USE_MOCK) {
    await delay()
    const kw = params.keyword.toLowerCase()
    const item = mockPriceData.find(p =>
      p.name.toLowerCase().includes(kw) ||
      p.ipName.toLowerCase().includes(kw) ||
      p.characterName.toLowerCase().includes(kw)
    )
    return { code: 200, message: 'ok', data: item || null }
  }
  const { default: request } = await import('@/utils/request')
  return request.get('/pricing/query', { params })
}

export async function getHotPrices(): Promise<ApiResponse<PriceItem[]>> {
  if (USE_MOCK) {
    await delay()
    return { code: 200, message: 'ok', data: mockPriceData.slice(0, 3) }
  }
  const { default: request } = await import('@/utils/request')
  return request.get('/pricing/hot')
}
