export interface GoodsItem {
  id: string
  name: string
  ipName: string
  characterName: string
  category: string
  referencePrice: number
  mainImage: string
  description: string
  status: 'active' | 'inactive' | 'frozen' | 'archived'
  createdAt: string
}

export interface GoodsForm {
  name: string
  ipName: string
  characterName: string
  category: string
  referencePrice: string
  description?: string
}
