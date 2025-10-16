import axiosInstance from './axiosInstance'

// 定义订单项接口
export interface OrderItem {
  book_id: number
  book_title?: string
  book_author?: string
  book_isbn?: string
  book_image?: string
  quantity: number
  unit_price?: number
  subtotal?: number
}

// 定义订单接口（简化版，适配新的数据库结构）
export interface Order {
  id: number
  order_number: string
  user_id: number
  username?: string
  total_amount: number
  created_at: string
  items?: OrderItem[]
}

// 定义订单列表响应接口
export interface OrderListResponse {
  orders: Order[]
  total: number
  page?: number
  page_size?: number
  total_pages?: number
}

// 获取所有订单列表
export const getAllOrders = async (): Promise<OrderListResponse> => {
  try {
    const response = await axiosInstance.get('/orders')
    if (response && response.data) {
      return response.data
    }
    return { orders: [], total: 0 }
  } catch (error) {
    console.error('获取订单列表失败:', error)
    throw error
  }
}

// 获取订单详情
export const getOrderDetail = async (orderId: number): Promise<Order | null> => {
  try {
    const response = await axiosInstance.get(`/orders/${orderId}`)
    if (response && response.data) {
      return response.data
    }
    return null
  } catch (error) {
    console.error('获取订单详情失败:', error)
    throw error
  }
}

// 更新订单状态（简化版不再需要）
export const updateOrderStatus = async (
  orderId: number,
  status: string
): Promise<void> => {
  // 简化版订单表不包含status字段，此接口保留但不实际使用
  console.warn('简化版订单表不支持状态更新')
  return Promise.resolve()
}

// 删除订单（取消订单）
export const deleteOrder = async (orderId: number): Promise<void> => {
  try {
    await axiosInstance.delete(`/orders/${orderId}/cancel`)
  } catch (error) {
    console.error('删除订单失败:', error)
    throw error
  }
}

