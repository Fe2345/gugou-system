export interface AssetItem {
  id: string
  productId: string
  productName: string
  ipName: string
  characterName: string
  category: string
  mainImage: string
  quantity: number
  acquirePrice: number
  currentValue: number
  status: 'holding' | 'selling' | 'exchanging' | 'sold' | 'invalid'
  description: string
  createdAt: string
  updatedAt: string
}

export interface AssetForm {
  productId?: string
  productName: string
  ipName: string
  characterName: string
  category: string
  mainImage?: string
  quantity: number
  acquirePrice: number
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
