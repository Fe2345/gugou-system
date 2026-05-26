import type { ApiResponse } from '@/types/api'

export interface DivisionItem {
  code: string
  name: string
  level: number
}

export interface AddressItem {
  id: number
  receiver_name: string
  receiver_phone: string
  province: DivisionItem
  city: DivisionItem
  district: DivisionItem
  street: string
  detail: string
  is_default: boolean
}

export interface AddressForm {
  receiver_name: string
  receiver_phone: string
  province_code: string
  city_code: string
  district_code: string
  street: string
  detail: string
  is_default: boolean
}

// 区划查询
export async function getDivisions(parentCode?: string): Promise<ApiResponse<DivisionItem[]>> {
  const { default: request } = await import('@/utils/request')
  return request.get('/divisions', { params: parentCode ? { parent_code: parentCode } : {} })
}

// 地址 CRUD
export async function getAddresses(): Promise<ApiResponse<AddressItem[]>> {
  const { default: request } = await import('@/utils/request')
  return request.get('/user/addresses')
}

export async function addAddress(data: AddressForm): Promise<ApiResponse<AddressItem>> {
  const { default: request } = await import('@/utils/request')
  return request.post('/user/addresses', data)
}

export async function updateAddress(id: number, data: AddressForm): Promise<ApiResponse<AddressItem>> {
  const { default: request } = await import('@/utils/request')
  return request.put(`/user/addresses/${id}`, data)
}

export async function deleteAddress(id: number): Promise<ApiResponse<void>> {
  const { default: request } = await import('@/utils/request')
  return request.delete(`/user/addresses/${id}`)
}
