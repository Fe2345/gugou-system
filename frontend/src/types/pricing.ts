export interface PriceItem {
  id: string
  name: string
  ip: string
  role: string
  category: string
  currentPrice: number
  avgPrice: number
  maxPrice: number
  minPrice: number
  changePercent: number
  trend: PriceTrendPoint[]
  transactions: PriceTransaction[]
}

export interface PriceTrendPoint {
  date: string
  price: number
}

export interface PriceTransaction {
  date: string
  name: string
  price: number
  condition: string
  method: string
}

export interface PriceQuery {
  keyword: string
  range: '7d' | '30d' | '90d'
}

export interface PriceConclusion {
  text: string
}
