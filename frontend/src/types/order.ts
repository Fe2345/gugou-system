export interface OrderItem {
  order_id: string
  buyer_id: string
  buyer_name: string
  seller_id: string
  seller_name: string
  product_id: string
  product_name: string
  quantity: number
  amount: number
  status: 'created' | 'pending_payment' | 'paid' | 'completed' | 'cancelled' | 'closed' | 'refunded'
  paid_at: string | null
  completed_at: string | null
  created_at: string
}
