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

// 定义订单状态类型
export type OrderStatus = 'pending' | 'processing' | 'shipping' | 'delivered' | 'cancelled'

// 定义订单接口
export interface Order {
  id: number
  order_number: string
  user_id?: number
  total_amount: number
  status?: OrderStatus
  created_at: string
  items?: OrderItem[]
  total_items?: number
  username?: string
}

// 定义创建订单请求接口
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

// 取消订单（将状态改为cancelled）
export const cancelOrder = async (orderId: number): Promise<void> => {
  try {
    await axiosInstance.put(`/orders/${orderId}/cancel`)
  } catch (error) {
    console.error('取消订单失败:', error)
    throw error
  }
}

// 更新订单状态
export const updateOrderStatus = async (
  orderId: number,
  status: OrderStatus
): Promise<void> => {
  try {
    await axiosInstance.put(`/orders/${orderId}/status`, { status })
  } catch (error) {
    console.error('更新订单状态失败:', error)
    throw error
  }
}

// 删除订单（仅限已取消和已完成的订单）
export const deleteOrder = async (orderId: number): Promise<void> => {
  try {
    await axiosInstance.delete(`/orders/${orderId}`)
  } catch (error) {
    console.error('删除订单失败:', error)
    throw error
  }
}
