export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  results: T[]
  count: number
  page: number
  page_size: number
  stats?: {
    total: number
    active: number
    sold: number
    cancelled: number
  }
  status_counts?: Record<string, number>
}
