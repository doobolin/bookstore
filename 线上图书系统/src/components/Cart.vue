<template>
  <div class="cart-page">
    <!-- 顶部导航 -->
    <nav class="glass-nav">
      <div class="nav-container">
        <div class="nav-left">
          <a @click="goBack" class="back-button">
            <i class="ri-arrow-left-s-line"></i>
          </a>
          <h1 class="nav-title">购物车 <span class="item-count">({{ totalItems }})</span></h1>
        </div>
      </div>
    </nav>

    <main class="main-container">
      <!-- 左侧：商品列表 -->
      <div class="cart-content">
        <!-- 列表头部控制 -->
        <div v-if="cartItems.length > 0" class="list-header">
          <label class="select-all-label">
            <input type="checkbox" class="custom-checkbox" :checked="isAllSelected" @change="toggleSelectAll">
            <span>全选</span>
          </label>
          <button @click="clearAllItems" class="delete-all-button">
            <i class="ri-delete-bin-line"></i>
          </button>
        </div>

        <!-- 空状态 -->
        <div v-if="cartItems.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="ri-shopping-bag-3-fill"></i>
          </div>
          <h3>购物袋是空的</h3>
          <p>看来您还没有发现心仪的技术书籍，去首页逛逛吧。</p>
          <button @click="goToHome" class="explore-button">去逛逛</button>
        </div>

        <!-- 商品列表 -->
        <transition-group name="list" tag="div" class="cart-items">
          <div v-for="(item, index) in cartItems" :key="item.id" class="cart-item">
            <!-- 勾选框 -->
            <div class="checkbox-container">
              <input type="checkbox" class="custom-checkbox" v-model="item.selected">
            </div>

            <!-- 图书封面 -->
            <div class="item-cover">
              <img :src="item.image" :alt="item.title" class="cover-image">
              <div v-if="!item.stock" class="out-of-stock">无货</div>
            </div>

            <!-- 信息主体 -->
            <div class="item-info">
              <div class="item-header">
                <h3 class="item-title">{{ item.title }}</h3>
                <button @click="removeItem(index)" class="remove-button">
                  <i class="ri-delete-bin-line"></i>
                </button>
              </div>
              <p class="item-author">{{ item.author }}</p>
              <div class="item-tags">
                <span class="tag">纸质书</span>
              </div>

              <!-- 价格与数量控制 -->
              <div class="item-footer">
                <div class="price-section">
                  <span class="current-price">¥{{ typeof item.price === 'number' ? item.price.toFixed(2) : parseFloat(item.price).toFixed(2) }}</span>
                </div>

                <!-- 步进器 -->
                <div class="quantity-stepper">
                  <button @click="changeQty(index, -1)" :disabled="item.quantity <= 1" class="stepper-btn">
                    <i class="ri-subtract-line"></i>
                  </button>
                  <input type="text" readonly :value="item.quantity" class="quantity-input">
                  <button @click="changeQty(index, 1)" class="stepper-btn">
                    <i class="ri-add-line"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </transition-group>

        <!-- 猜你喜欢 -->
        <div v-if="recommendedBooks.length > 0" class="recommendations">
          <h4 class="recommendations-title">猜你喜欢</h4>
          <div class="recommendations-grid">
            <div v-for="book in recommendedBooks" :key="book.id" class="recommendation-card">
              <div class="recommendation-cover" @click="goToBook(book.id)">
                <img :src="book.image" :alt="book.title" class="recommendation-cover-image">
              </div>
              <div class="recommendation-info">
                <h5 class="recommendation-title" @click="goToBook(book.id)">{{ book.title }}</h5>
                <p class="recommendation-author">{{ book.author }}</p>
                <div class="recommendation-footer">
                  <span class="recommendation-price">¥{{ typeof book.price === 'number' ? book.price.toFixed(2) : parseFloat(book.price).toFixed(2) }}</span>
                  <button @click.stop="addRecommendedToCart(book)" class="add-recommendation-btn">
                    <i class="ri-shopping-cart-line"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：结算中心 (Desktop) -->
      <div class="checkout-sidebar">
        <!-- 价格明细卡片 -->
        <div class="summary-card">
          <h3 class="summary-title">订单摘要</h3>

          <div class="summary-details">
            <div class="summary-row">
              <span class="summary-label">商品总额</span>
              <span class="summary-value">¥{{ subtotal }}</span>
            </div>
            <div class="summary-row">
              <span class="summary-label">运费</span>
              <span class="summary-value">¥0.00</span>
            </div>
            <div class="summary-row discount-row">
              <span class="summary-label"><i class="ri-vip-diamond-fill"></i> 会员优惠</span>
              <span class="summary-value">-¥{{ discount }}</span>
            </div>
          </div>

          <div class="summary-total">
            <div class="total-wrapper">
              <span class="total-label">总计</span>
              <div class="total-price-wrapper">
                <span class="total-price">¥{{ finalTotal }}</span>
              </div>
            </div>
          </div>

          <button @click="handleCheckout" :disabled="selectedCount === 0" class="checkout-button">
            立即结算 <i class="ri-arrow-right-line"></i>
          </button>
        </div>
      </div>
    </main>

    <!-- Mobile Fixed Bottom Bar -->
    <div class="mobile-bottom-bar">
      <div class="mobile-summary">
        <span class="mobile-info">已选 {{ selectedCount }} 件，优惠 ¥{{ discount }}</span>
      </div>
      <div class="mobile-actions">
        <div class="mobile-total">
          <p class="mobile-total-label">合计</p>
          <p class="mobile-total-price">¥{{ finalTotal }}</p>
        </div>
        <button @click="handleCheckout" :disabled="selectedCount === 0" class="mobile-checkout-btn">
          去结算 ({{ selectedCount }})
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllBooks, type Book } from '../api/bookApi'
import { getCart, updateCartItem, removeFromCart as removeFromCartApi, type CartItem as ApiCartItem } from '../api/cartApi'

const router = useRouter()

const loading = ref(false)

interface CartItem {
  id: number
  book_id: number
  title: string
  author: string
  price: string | number
  image: string
  quantity: number
  selected: boolean
  stock: number
}

const cartItems = ref<CartItem[]>([])
const recommendedBooks = ref<Book[]>([])

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

// 计算属性
const totalItems = computed(() => cartItems.value.length)

const selectedItems = computed(() => cartItems.value.filter(item => item.selected))

const selectedCount = computed(() => selectedItems.value.reduce((acc, item) => acc + item.quantity, 0))

const isAllSelected = computed(() => {
  return cartItems.value.length > 0 && cartItems.value.every(item => item.selected)
})

const subtotal = computed(() => {
  let sum = 0
  selectedItems.value.forEach(item => {
    const price = typeof item.price === 'number' ? item.price : parseFloat(item.price.toString())
    sum += price * item.quantity
  })
  return sum.toFixed(2)
})

const discount = computed(() => {
  // 每满100减10
  const rawTotal = parseFloat(subtotal.value)
  if (rawTotal > 0) {
    return Math.floor(rawTotal / 100) * 10
  }
  return 0
})

const finalTotal = computed(() => {
  return (parseFloat(subtotal.value) - discount.value).toFixed(2)
})

// 发送购物车更新事件
const emitCartUpdate = () => {
  const totalQuantity = cartItems.value.reduce((total, item) => total + item.quantity, 0)
  const cartUpdateEvent = new CustomEvent('cart-updated', {
    detail: { count: totalQuantity }
  })
  window.dispatchEvent(cartUpdateEvent)
}

// 方法
const loadCartItems = async () => {
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
    // 将 API 返回的数据转换为本地格式，添加 selected 属性
    cartItems.value = response.items.map((item: ApiCartItem) => ({
      ...item,
      selected: true
    }))
    emitCartUpdate()
  } catch (error) {
    console.error('加载购物车失败:', error)
    ElMessage.error('加载购物车失败')
  } finally {
    loading.value = false
  }
}

const loadRecommendations = async () => {
  try {
    const allBooks = await getAllBooks()
    // 随机选择4本书作为推荐
    const shuffled = [...allBooks].sort(() => Math.random() - 0.5)
    recommendedBooks.value = shuffled.slice(0, 4)
  } catch (error) {
    console.error('加载推荐图书失败:', error)
  }
}

const toggleSelectAll = () => {
  const currentStatus = isAllSelected.value
  cartItems.value.forEach(item => item.selected = !currentStatus)
}

const changeQty = async (index: number, delta: number) => {
  const item = cartItems.value[index]
  const newQty = item.quantity + delta

  if (newQty < 1) {
    return
  }

  if (newQty > item.stock) {
    ElMessage.warning('已达库存上限')
    return
  }

  try {
    await updateCartItem(item.id, newQty)
    item.quantity = newQty
    emitCartUpdate()
  } catch (error) {
    console.error('更新购物车失败:', error)
    ElMessage.error('更新购物车失败')
  }
}

const removeItem = async (index: number) => {
  const item = cartItems.value[index]

  try {
    await ElMessageBox.confirm('确定要删除这本书吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await removeFromCartApi(item.id)
    ElMessage.success(`《${item.title}》已从购物车移除`)
    // 重新加载购物车
    await loadCartItems()
  } catch (error: any) {
    // 用户取消或删除失败
    if (error !== 'cancel') {
      console.error('删除购物车项失败:', error)
      ElMessage.error('删除购物车项失败')
    }
  }
}

const clearAllItems = async () => {
  if (cartItems.value.length === 0) {
    return
  }

  try {
    await ElMessageBox.confirm('确定要删除购物车中的所有图书吗？', '提示', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 删除所有购物车项
    for (const item of cartItems.value) {
      await removeFromCartApi(item.id)
    }

    ElMessage.success('已清空购物车')
    // 重新加载购物车
    await loadCartItems()
  } catch (error: any) {
    // 用户取消或删除失败
    if (error !== 'cancel') {
      console.error('清空购物车失败:', error)
      ElMessage.error('清空购物车失败')
    }
  }
}

const goBack = () => {
  router.back()
}

const goToHome = () => {
  router.push('/')
}

const goToBook = (bookId: number) => {
  router.push(`/book/${bookId}`)
}

const handleCheckout = () => {
  if (selectedCount.value === 0) {
    ElMessage.warning('请选择要结算的商品')
    return
  }

  const userId = getUserId()
  if (!userId || !checkUserLogin()) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  // 将选中的购物车数据存储到 sessionStorage，传递给订单确认页面
  const checkoutData = {
    items: selectedItems.value.map(item => ({
      book_id: item.book_id,
      title: item.title,
      author: item.author,
      price: typeof item.price === 'number' ? item.price : parseFloat(item.price.toString()),
      quantity: item.quantity
    }))
  }
  sessionStorage.setItem('checkoutCart', JSON.stringify(checkoutData))

  // 跳转到订单确认页面
  router.push('/checkout')
}

const addRecommendedToCart = async (book: Book) => {
  const userId = getUserId()
  if (!userId || !checkUserLogin()) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    const existingItem = cartItems.value.find(item => item.book_id === book.id)

    if (existingItem) {
      ElMessage.info('该书籍已在购物车中')
    } else {
      // 使用 cartApi 添加到购物车
      const { addToCart } = await import('../api/cartApi')
      await addToCart(userId, book.id, 1)
      ElMessage.success(`《${book.title}》已添加到购物车！`)
      // 重新加载购物车
      await loadCartItems()
    }
  } catch (error) {
    console.error('添加到购物车失败:', error)
    ElMessage.error('添加失败')
  }
}

// 监听用户登录事件
const handleUserLogin = () => {
  loadCartItems()
}

// 监听用户登出事件
const handleUserLogout = () => {
  cartItems.value = []
  emitCartUpdate()
}

onMounted(() => {
  window.addEventListener('user-login', handleUserLogin as EventListener)
  window.addEventListener('user-logout', handleUserLogout as EventListener)

  // 初始加载购物车
  loadCartItems()
  loadRecommendations()
})

onUnmounted(() => {
  window.removeEventListener('user-login', handleUserLogin as EventListener)
  window.removeEventListener('user-logout', handleUserLogout as EventListener)
})
</script>

<style scoped>
/* 引入 Remix Icon */
@import url('https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css');

.cart-page {
  min-height: 100vh;
  background: #F5F5F7;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  padding-bottom: 140px;
}

@media (min-width: 1024px) {
  .cart-page {
    padding-bottom: 48px;
  }
}

/* ========== 顶部导航 ========== */
.glass-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  height: 64px;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-button {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.3s;
  font-size: 20px;
  color: #1D1D1F;
}

.back-button:hover {
  background: rgba(0, 0, 0, 0.05);
}

.nav-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1D1D1F;
  letter-spacing: -0.02em;
}

.item-count {
  color: #86868B;
  font-weight: 400;
  font-size: 1rem;
}

.edit-button {
  color: #007AFF;
  font-weight: 600;
  font-size: 14px;
  padding: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
}

/* ========== 主要容器 ========== */
.main-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  align-items: start;
}

@media (min-width: 1024px) {
  .main-container {
    grid-template-columns: 1fr 380px;
  }
}

/* ========== 左侧内容 ========== */
.cart-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.list-header {
  background: white;
  border-radius: 1rem;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.select-all-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #6B7280;
}

.delete-all-button {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 0.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: #FF3B30;
  font-size: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.delete-all-button:hover {
  background: rgba(255, 59, 48, 0.08);
  border-color: rgba(255, 59, 48, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 59, 48, 0.15);
}

/* 自定义复选框 */
.custom-checkbox {
  appearance: none;
  width: 22px;
  height: 22px;
  border: 2px solid #D1D1D6;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  flex-shrink: 0;
}

.custom-checkbox:checked {
  background-color: #007AFF;
  border-color: #007AFF;
}

.custom-checkbox:checked::after {
  content: '✔';
  position: absolute;
  color: white;
  font-size: 14px;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}

/* ========== 空状态 ========== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 1.25rem;
  text-align: center;
}

.empty-icon {
  width: 96px;
  height: 96px;
  background: #F3F4F6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: #D1D5DB;
  margin-bottom: 1.5rem;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #6B7280;
  margin-bottom: 2rem;
  max-width: 20rem;
}

.explore-button {
  background: #000000;
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 999px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  transition: all 0.3s;
}

.explore-button:hover {
  background: #2c2c2e;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

/* ========== 商品列表 ========== */
.cart-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cart-item {
  background: white;
  padding: 1.25rem;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  display: flex;
  gap: 1rem;
  position: relative;
  transition: all 0.3s;
}

.cart-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.checkbox-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-cover {
  width: 80px;
  height: 112px;
  flex-shrink: 0;
  border-radius: 8px;
  background: #F5F5F7;
  overflow: hidden;
  position: relative;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #E5E5E7 0%, #F5F5F7 100%);
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recommendation-cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.out-of-stock {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 700;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.25rem 0;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.item-title {
  font-weight: 700;
  font-size: 1rem;
  color: #1F2937;
  line-height: 1.4;
  margin: 0;
  padding-right: 2.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.remove-button {
  position: absolute;
  top: 1rem;
  right: 1rem;
  color: #D1D5DB;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  font-size: 18px;
  transition: color 0.3s;
}

.remove-button:hover {
  color: #FF3B30;
}

.item-author {
  font-size: 14px;
  color: #6B7280;
  margin: 0.25rem 0 0.5rem 0;
}

.item-tags {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.tag {
  font-size: 10px;
  padding: 0.125rem 0.5rem;
  background: #F3F4F6;
  color: #6B7280;
  border-radius: 4px;
  font-weight: 500;
}

.item-footer {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-top: 0.75rem;
}

.price-section {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.current-price {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1D1D1F;
}

/* 步进器 */
.quantity-stepper {
  display: flex;
  align-items: center;
  background: #F3F4F6;
  border-radius: 8px;
  padding: 0.25rem;
  height: 32px;
}

.stepper-btn {
  width: 28px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6B7280;
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  font-size: 12px;
}

.stepper-btn:hover:not(:disabled) {
  background: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.stepper-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quantity-input {
  width: 32px;
  background: transparent;
  text-align: center;
  font-size: 14px;
  font-weight: 700;
  border: none;
  outline: none;
  padding: 0;
  color: #1D1D1F;
}

/* 列表动画 */
.list-leave-active {
  transition: all 0.4s ease;
}

.list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
  height: 0;
  margin: 0;
  padding: 0;
}

/* ========== 推荐区域 ========== */
.recommendations {
  padding-top: 2rem;
  margin-top: 2rem;
  border-top: 1px solid #F3F4F6;
}

.recommendations-title {
  font-weight: 700;
  font-size: 1.125rem;
  color: #1F2937;
  margin-bottom: 1.5rem;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1.25rem;
}

@media (max-width: 768px) {
  .recommendations-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
}

.recommendation-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #F3F4F6;
  transition: all 0.3s ease;
}

.recommendation-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-4px);
}

.recommendation-cover {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  overflow: hidden;
  cursor: pointer;
  background: #F5F5F7;
}

.recommendation-cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.recommendation-cover:hover .recommendation-cover-image {
  transform: scale(1.05);
}

.recommendation-info {
  padding: 0.75rem;
}

.recommendation-title {
  font-weight: 700;
  font-size: 14px;
  color: #1D1D1F;
  margin: 0 0 0.25rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.3;
  cursor: pointer;
  transition: color 0.3s ease;
}

.recommendation-title:hover {
  color: #007AFF;
}

.recommendation-author {
  font-size: 12px;
  color: #86868B;
  margin: 0 0 0.75rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommendation-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.recommendation-price {
  font-weight: 700;
  font-size: 16px;
  color: #1D1D1F;
}

.add-recommendation-btn {
  width: 32px;
  height: 32px;
  background: #000000;
  color: white;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
}

.add-recommendation-btn:hover {
  background: #2c2c2e;
  transform: scale(1.1);
}

/* ========== 右侧结算栏 ========== */
.checkout-sidebar {
  display: none;
}

@media (min-width: 1024px) {
  .checkout-sidebar {
    display: block;
    position: sticky;
    top: 96px;
  }
}

.summary-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.1);
  border: 1px solid #F3F4F6;
  margin-bottom: 1.5rem;
}

.summary-title {
  font-size: 1.125rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: #1D1D1F;
}

.summary-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.summary-label {
  color: #6B7280;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.summary-value {
  font-weight: 500;
  color: #1D1D1F;
}

.discount-row {
  color: #34C759;
}

.discount-row .summary-value {
  color: #34C759;
}

.summary-total {
  border-top: 1px solid #F3F4F6;
  padding-top: 1rem;
  margin-bottom: 1.5rem;
}

.total-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.total-label {
  color: #6B7280;
  font-weight: 500;
}

.total-price-wrapper {
  text-align: right;
}

.total-price {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1D1D1F;
  letter-spacing: -0.02em;
}

.checkout-button {
  width: 100%;
  background: #000000;
  color: white;
  font-weight: 700;
  padding: 1rem;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 1.125rem;
}

.checkout-button:hover:not(:disabled) {
  background: #2c2c2e;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.checkout-button:disabled {
  background: #D1D5DB;
  cursor: not-allowed;
  box-shadow: none;
}

/* ========== 移动端底部栏 ========== */
.mobile-bottom-bar {
  display: block;
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(48px);
  -webkit-backdrop-filter: blur(48px);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  padding: 1rem;
  padding-bottom: 2rem;
  z-index: 50;
}

@media (min-width: 1024px) {
  .mobile-bottom-bar {
    display: none;
  }
}

.mobile-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.mobile-info {
  font-size: 14px;
  color: #6B7280;
}

.mobile-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.mobile-total {
  flex: 1;
}

.mobile-total-label {
  font-size: 12px;
  color: #6B7280;
  margin: 0;
}

.mobile-total-price {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1F2937;
  margin: 0;
  line-height: 1;
}

.mobile-checkout-btn {
  flex: 2;
  background: #000000;
  color: white;
  font-weight: 700;
  padding: 0.875rem 1.5rem;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  transition: all 0.3s;
}

.mobile-checkout-btn:hover:not(:disabled) {
  background: #2c2c2e;
}

.mobile-checkout-btn:disabled {
  background: #D1D5DB;
  cursor: not-allowed;
  box-shadow: none;
}
</style>
