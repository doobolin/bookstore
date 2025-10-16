import axiosInstance from './axiosInstance'

// 定义购物车项接口
export interface CartItem {
  id: number
  book_id: number
  title: string
  author: string
  price: number
  image: string
  quantity: number
  stock: number
}

// 定义购物车响应接口
export interface CartResponse {
  items: CartItem[]
  total: number
}

// 获取用户购物车
export const getCart = async (userId: number): Promise<CartResponse> => {
  try {
    const response = await axiosInstance.get('/cart', {
      params: { user_id: userId }
    })
    if (response && response.data) {
      return response.data
    }
    return { items: [], total: 0 }
  } catch (error) {
    console.error('获取购物车失败:', error)
    throw error
  }
}

// 添加商品到购物车
export const addToCart = async (userId: number, bookId: number, quantity: number = 1): Promise<void> => {
  try {
    await axiosInstance.post('/cart/add', {
      user_id: userId,
      book_id: bookId,
      quantity: quantity
    })
  } catch (error) {
    console.error('添加到购物车失败:', error)
    throw error
  }
}

// 更新购物车商品数量
export const updateCartItem = async (cartId: number, quantity: number): Promise<void> => {
  try {
    await axiosInstance.put('/cart/update', {
      cart_id: cartId,
      quantity: quantity
    })
  } catch (error) {
    console.error('更新购物车失败:', error)
    throw error
  }
}

// 从购物车删除商品
export const removeFromCart = async (cartId: number): Promise<void> => {
  try {
    await axiosInstance.delete('/cart/remove', {
      params: { cart_id: cartId }
    })
  } catch (error) {
    console.error('删除购物车项失败:', error)
    throw error
  }
}

// 清空购物车
export const clearCart = async (userId: number): Promise<void> => {
  try {
    await axiosInstance.delete('/cart/clear', {
      params: { user_id: userId }
    })
  } catch (error) {
    console.error('清空购物车失败:', error)
    throw error
  }
}
