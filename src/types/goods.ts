export interface GoodsItem {
  id: string
  name: string
  price: number
  image: string
  ip: string
  role: string
  category: string
  description: string
  status: 'pending' | 'approved' | 'rejected'
  createdAt: string
}

export interface GoodsForm {
  name: string
  price: string
  ip: string
  role: string
  category: string
}
