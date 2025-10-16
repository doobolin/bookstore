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

// 定义订单接口（简化版）
export interface Order {
  id: number
  order_number: string
  user_id?: number
  total_amount: number
  created_at: string
  items?: OrderItem[]
}

// 定义创建订单请求接口（简化版）
export interface CreateOrderRequest {
  user_id: number
  items: Array<{
    book_id: number
    quantity: number
  }>
}

// 定义创建订单响应接口
export interface CreateOrderResponse {
  order_id: number
  order_number: string
  total_amount: number
}

// 创建订单
export const createOrder = async (orderData: CreateOrderRequest): Promise<CreateOrderResponse> => {
  try {
    const response = await axiosInstance.post('/orders/create', orderData)
    if (response && response.data) {
      return response.data
    }
    throw new Error('创建订单失败')
  } catch (error) {
    console.error('创建订单失败:', error)
    throw error
  }
}

// 获取用户订单列表
export const getOrders = async (userId: number): Promise<Order[]> => {
  try {
    const response = await axiosInstance.get('/orders', {
      params: { user_id: userId }
    })
    if (response && response.data && response.data.orders) {
      return response.data.orders
    }
    return []
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

// 取消订单（删除订单）
export const cancelOrder = async (orderId: number): Promise<void> => {
  try {
    await axiosInstance.delete(`/orders/${orderId}/cancel`)
  } catch (error) {
    console.error('取消订单失败:', error)
    throw error
  }
}
