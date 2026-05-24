export interface AssetItem {
  id: string
  goodsId: string
  name: string
  ip: string
  role: string
  category: string
  image: string
  quantity: number
  costPrice: number
  currentValue: number
  status: 'holding' | 'selling' | 'trading' | 'sold'
  description: string
  createdAt: string
  updatedAt: string
}

export interface AssetForm {
  goodsId?: string
  name: string
  ip: string
  role: string
  category: string
  image?: string
  quantity: number
  costPrice: number
  description?: string
}

export interface AssetSummary {
  totalCount: number
  categoryCount: number
  totalCost: number
  totalValue: number
  valueChange: number
}

export type AssetStatus = AssetItem['status']

export interface AssetOperation {
  type: 'list' | 'delist' | 'sold'
  assetId: string
  targetUserId?: string
  reason?: string
}
