export interface OrderItem {
  id: string
  goodsId: string
  goodsName: string
  goodsImage: string
  price: number
  quantity: number
  status: 'pending' | 'paid' | 'shipped' | 'completed' | 'cancelled'
  buyerId: string
  sellerId: string
  createdAt: string
}
