// 收货地址API接口
import axiosInstance from './axiosInstance'

// 地址类型定义
export interface Address {
  id?: number
  receiver_name: string
  receiver_phone: string
  province: string
  city: string
  district: string
  detail_address: string
  postal_code?: string
  is_default?: boolean
  created_at?: string
  full_address?: string
}

// 获取用户所有收货地址
export const getAddresses = (userId: number) => {
  return axiosInstance.get('/addresses', {
    params: { user_id: userId }
  })
}

// 添加收货地址
export const addAddress = (addressData: Address & { user_id: number }) => {
  return axiosInstance.post('/addresses', addressData)
}

// 更新收货地址
export const updateAddress = (addressId: number, addressData: Partial<Address>) => {
  return axiosInstance.put(`/addresses/${addressId}`, addressData)
}

// 删除收货地址
export const deleteAddress = (addressId: number) => {
  return axiosInstance.delete(`/addresses/${addressId}`)
}

// 设置默认地址
export const setDefaultAddress = (addressId: number) => {
  return axiosInstance.put(`/addresses/${addressId}/set-default`)
}
