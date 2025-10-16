<template>
  <div class="shopping-cart">
    <div class="cart-header">
      <h3 class="cart-title">购物车</h3>
      <div class="cart-count">
        <span class="count-number">{{ cartItems.length }}</span>
        <span class="count-text">件商品</span>
      </div>
    </div>
    
    <div v-if="cartItems.length === 0" class="empty-cart">
      <div class="empty-icon">
        <el-icon size="48"><ShoppingCart /></el-icon>
      </div>
      <p class="empty-text">购物车是空的</p>
      <p class="empty-subtext">快去挑选心仪的书籍吧！</p>
    </div>
    
    <div v-else class="cart-items">
      <div 
        v-for="item in cartItems" 
        :key="item.id"
        class="cart-item"
      >
        <div class="item-image">
          <img :src="item.image" :alt="item.title" @error="handleImageError" />
        </div>
        
        <div class="item-details">
          <h4 class="item-title">{{ item.title }}</h4>
          <p class="item-author">{{ item.author }}</p>
          <p class="item-price">¥{{ item.price }}</p>
          
          <div class="quantity-control">
            <el-button 
              size="small" 
              @click="decreaseQuantity(item)"
              :disabled="item.quantity <= 1"
              class="quantity-btn"
            >
              <el-icon><Minus /></el-icon>
            </el-button>
            <span class="quantity-display">{{ item.quantity }}</span>
            <el-button 
              size="small" 
              @click="increaseQuantity(item)"
              class="quantity-btn"
            >
              <el-icon><Plus /></el-icon>
            </el-button>
          </div>
        </div>
        
        <div class="item-actions">
          <el-button 
            type="danger" 
            size="small"
            @click="removeFromCart(item)"
            class="remove-btn"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
    
    <div v-if="cartItems.length > 0" class="cart-summary">
      <div class="summary-row">
        <span class="summary-label">总计:</span>
        <span class="summary-total">¥{{ cartTotal }}</span>
      </div>
      <el-button 
        type="primary" 
        class="checkout-btn"
        @click="checkout"
      >
        立即结算
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ShoppingCart, Delete, Plus, Minus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { getCart, addToCart as addToCartApi, updateCartItem, removeFromCart as removeFromCartApi, clearCart } from '../api/cartApi'
import { createOrder } from '../api/orderApi'

const router = useRouter()

interface CartItem {
  id: number
  book_id: number
  title: string
  author: string
  price: number
  image: string
  quantity: number
  stock: number
}

const cartItems = ref<CartItem[]>([])
const loading = ref(false)

const cartTotal = computed(() => {
  return cartItems.value
    .reduce((total, item) => total + item.price * item.quantity, 0)
    .toFixed(2)
})

// 获取当前用户ID
const getUserId = (): number | null => {
  const userId = localStorage.getItem('user_id')
  return userId ? parseInt(userId) : null
}

// 检查用户是否登录
const checkUserLogin = (): boolean => {
  const isLoggedIn = localStorage.getItem('isLoggedIn')
  return isLoggedIn === 'true'
}

// 加载购物车数据
const loadCart = async () => {
  const userId = getUserId()
  if (!userId || !checkUserLogin()) {
    // 如果未登录，清空购物车
    cartItems.value = []
    emitCartUpdate()
    return
  }

  try {
    loading.value = true
    const response = await getCart(userId)
    cartItems.value = response.items
    emitCartUpdate()
  } catch (error) {
    console.error('加载购物车失败:', error)
    ElMessage.error('加载购物车失败')
  } finally {
    loading.value = false
  }
}

// 发送购物车更新事件
const emitCartUpdate = () => {
  const totalQuantity = cartItems.value.reduce((total, item) => total + item.quantity, 0)
  const cartUpdateEvent = new CustomEvent('cart-updated', {
    detail: { count: totalQuantity }
  })
  window.dispatchEvent(cartUpdateEvent)
}

const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  target.src = '/images/book-placeholder.svg'
}

const addToCart = async (book: any) => {
  const userId = getUserId()
  if (!userId || !checkUserLogin()) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    await addToCartApi(userId, book.id, 1)
    ElMessage.success(`《${book.title}》已加入购物车！`)
    // 重新加载购物车
    await loadCart()
  } catch (error) {
    console.error('添加到购物车失败:', error)
    ElMessage.error('添加到购物车失败')
  }
}

const removeFromCart = async (item: CartItem) => {
  try {
    await removeFromCartApi(item.id)
    ElMessage.success(`《${item.title}》已从购物车移除`)
    // 重新加载购物车
    await loadCart()
  } catch (error) {
    console.error('删除购物车项失败:', error)
    ElMessage.error('删除购物车项失败')
  }
}

const increaseQuantity = async (item: CartItem) => {
  if (item.quantity >= item.stock) {
    ElMessage.warning('已达库存上限')
    return
  }

  try {
    await updateCartItem(item.id, item.quantity + 1)
    item.quantity++
    emitCartUpdate()
  } catch (error) {
    console.error('更新购物车失败:', error)
    ElMessage.error('更新购物车失败')
  }
}

const decreaseQuantity = async (item: CartItem) => {
  if (item.quantity <= 1) {
    return
  }

  try {
    await updateCartItem(item.id, item.quantity - 1)
    item.quantity--
    emitCartUpdate()
  } catch (error) {
    console.error('更新购物车失败:', error)
    ElMessage.error('更新购物车失败')
  }
}

const checkout = async () => {
  if (cartItems.value.length === 0) {
    ElMessage.warning('购物车为空')
    return
  }

  const userId = getUserId()
  if (!userId || !checkUserLogin()) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    // 确认订单
    await ElMessageBox.confirm(
      `确认提交订单？共 ${cartItems.value.length} 件商品，总金额：¥${cartTotal.value}`,
      '确认订单',
      {
        confirmButtonText: '确认提交',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 创建订单 - 简化版
    const orderData = {
      user_id: userId,
      items: cartItems.value.map(item => ({
        book_id: item.book_id,
        quantity: item.quantity
      }))
    }

    const response = await createOrder(orderData)

    ElMessage.success(`订单提交成功！订单号：${response.order_number}，总金额：¥${response.total_amount.toFixed(2)}`)

    // 清空购物车
    await clearCart(userId)
    await loadCart()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('提交订单失败:', error)
      ElMessage.error('提交订单失败')
    }
  }
}

const handleAddToCart = (event: CustomEvent) => {
  addToCart(event.detail.book)
}

// 监听用户登录事件
const handleUserLogin = () => {
  loadCart()
}

// 监听用户登出事件
const handleUserLogout = () => {
  cartItems.value = []
  emitCartUpdate()
}

onMounted(() => {
  window.addEventListener('add-to-cart', handleAddToCart as EventListener)
  window.addEventListener('user-login', handleUserLogin as EventListener)
  window.addEventListener('user-logout', handleUserLogout as EventListener)

  // 初始加载购物车
  loadCart()
})

onUnmounted(() => {
  window.removeEventListener('add-to-cart', handleAddToCart as EventListener)
  window.removeEventListener('user-login', handleUserLogin as EventListener)
  window.removeEventListener('user-logout', handleUserLogout as EventListener)
})
</script>

<style scoped>
.shopping-cart {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
  max-width: 400px;
  margin: 20px auto;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 255, 255, 0.2);
}

.cart-title {
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(135deg, #00ffff, #ff00ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.cart-count {
  display: flex;
  align-items: center;
  gap: 5px;
}

.count-number {
  color: #00ffff;
  font-weight: 700;
  font-size: 18px;
}

.count-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.empty-cart {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 15px;
}

.empty-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 10px 0;
}

.empty-subtext {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin: 0;
}

.cart-items {
  margin-bottom: 20px;
}

.cart-item {
  display: flex;
  gap: 15px;
  padding: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: background-color 0.3s ease;
}

.cart-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.item-image {
  width: 60px;
  height: 80px;
  flex-shrink: 0;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.item-details {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin: 0 0 5px 0;
  line-height: 1.3;
}

.item-author {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 5px 0;
}

.item-price {
  font-size: 16px;
  font-weight: 700;
  color: #00ffff;
}

.item-actions {
  display: flex;
  align-items: center;
}

.remove-btn {
  background: transparent;
  border: 1px solid rgba(255, 77, 79, 0.5);
  color: #ff4d4f;
}

.remove-btn:hover {
  background: rgba(255, 77, 79, 0.1);
  border-color: #ff4d4f;
}

.cart-summary {
  padding-top: 15px;
  border-top: 1px solid rgba(0, 255, 255, 0.2);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.summary-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
  font-weight: 600;
}

.summary-total {
  font-size: 20px;
  font-weight: 800;
  color: #00ffff;
}

.checkout-btn {
  width: 100%;
  background: linear-gradient(135deg, #00ffff, #ff00ff);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  font-size: 16px;
  padding: 12px;
  transition: all 0.3s ease;
}

.checkout-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(0, 255, 255, 0.3);
}

.checkout-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.quantity-display {
  min-width: 30px;
  text-align: center;
  font-weight: bold;
  color: #00ffff;
}

.quantity-btn {
  padding: 4px 8px;
  height: 28px;
  width: 28px;
  background: rgba(0, 255, 255, 0.1);
  border: 1px solid rgba(0, 255, 255, 0.3);
  color: #00ffff;
}

.quantity-btn:hover {
  background: rgba(0, 255, 255, 0.2);
  border-color: #00ffff;
}

.quantity-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>