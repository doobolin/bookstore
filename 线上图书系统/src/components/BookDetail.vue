<template>
  <div class="book-detail-page">
    <!-- 顶部导航 -->
    <nav class="glass-nav">
      <a @click="goBack" class="back-button">
        <i class="ri-arrow-left-s-line"></i>
      </a>
      <span class="nav-title">{{ book?.title }}</span>

      <div class="nav-actions">
        <div class="cart-icon" @click="toggleCart">
          <i class="ri-shopping-cart-line"></i>
          <span class="cart-count" v-if="cartItemCount > 0">{{ cartItemCount }}</span>
        </div>

        <div v-if="isLoggedIn" class="user-info">
          <el-dropdown @command="handleUserCommand">
            <div class="user-avatar-simple">
              <i class="ri-user-line"></i>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <i class="ri-user-line"></i>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item command="orders">
                  <i class="ri-file-list-3-line"></i>
                  我的订单
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <i class="ri-logout-box-line"></i>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <button v-else class="login-btn" @click="goToLogin">
          登录
        </button>

        <a @click="toggleFavorite" class="favorite-button">
          <i :class="isFavorite ? 'ri-heart-fill' : 'ri-heart-line'"></i>
        </a>
      </div>
    </nav>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载图书详情...</p>
    </div>

    <!-- 主要内容 -->
    <div v-else-if="book" class="detail-container">
      <!-- Hero 区域 -->
      <div class="hero-section">
        <!-- 动态模糊背景 -->
        <div class="ambient-bg">
          <div class="bg-overlay"></div>
          <div class="bg-blur" :style="{ backgroundImage: `url(${bookCover})` }"></div>
        </div>

        <div class="hero-content">
          <!-- 左侧：封面图 -->
          <div class="cover-column">
            <div class="cover-wrapper">
              <img :src="bookCover" :alt="book.title" class="book-cover">
              <div class="cover-shine"></div>
            </div>
          </div>

          <!-- 中间：核心信息 -->
          <div class="info-column">
            <h1 class="book-title">{{ book.title }}</h1>
            <h2 class="book-subtitle">{{ book.subtitle || book.description?.substring(0, 50) + '...' }}</h2>

            <!-- 作者行 -->
            <div class="author-section">
              <div class="author-info">
                <p class="author-name">{{ book.author }}</p>
                <p class="author-role">著名作家</p>
              </div>
            </div>

            <!-- 评分摘要 -->
            <div class="rating-summary">
              <div class="rating-block">
                <div class="stars-container">
                  <span class="rating-number">{{ book.rating?.toFixed(1) || '4.5' }}</span>
                  <div class="stars">
                    <i class="ri-star-fill" v-for="n in Math.floor(book.rating || 4.5)" :key="n"></i>
                    <i class="ri-star-half-fill" v-if="(book.rating || 4.5) % 1 !== 0"></i>
                  </div>
                </div>
                <p class="rating-count" v-if="book.rating">基于评分</p>
              </div>
              <div class="divider" v-if="book.category"></div>
              <div class="rank-block" v-if="book.category">
                <p class="rank-number">{{ book.category }}</p>
                <p class="rank-category">分类</p>
              </div>
            </div>

            <!-- 标签 -->
            <div class="tags-container">
              <span v-for="tag in tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>

          <!-- 右侧：统计卡片 (Desktop) -->
          <div class="stats-column">
            <div class="price-card">
              <p class="card-label">价格</p>
              <div class="price-display">
                <span class="current-price">¥{{ formattedPrice }}</span>
              </div>
            </div>

            <div class="stat-card">
              <i class="ri-translate-2"></i>
              <span class="stat-value">中文</span>
              <span class="stat-label">语言</span>
            </div>
            <div class="vip-card">
              <div class="vip-icon">
                <i class="ri-vip-crown-fill"></i>
              </div>
              <div class="vip-text">
                <p class="vip-title">TechPro 会员免费</p>
                <p class="vip-desc">加入会员畅读全站</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 内容详情区 -->
      <main class="content-main">
        <!-- 左侧主要内容 -->
        <div class="main-content">
          <!-- 简介 -->
          <section class="section">
            <div class="flex items-center justify-between mb-4">
              <h3 class="section-title">简介</h3>
            </div>
            <div class="description-text" :class="{ 'clamp-3': !showFullDesc }">
              {{ book.description || '暂无简介' }}
            </div>
            <button @click="showFullDesc = !showFullDesc" class="expand-button">
              {{ showFullDesc ? '收起' : '展开全部' }}
              <i :class="showFullDesc ? 'ri-arrow-up-s-line' : 'ri-arrow-down-s-line'"></i>
            </button>
          </section>
        </div>

        <!-- 右侧边栏 -->
        <aside class="sidebar-content" v-if="recommendedBooks.length > 0">
          <!-- 推荐图书 -->
          <div class="sidebar-card">
            <h3 class="sidebar-title">看过的人也买了</h3>
            <div class="recommendations-list">
              <div
                v-for="recommendedBook in recommendedBooks"
                :key="recommendedBook.id"
                class="recommendation-item"
                @click="goToBook(recommendedBook.id)"
              >
                <div class="recommendation-cover">
                  <div class="recommendation-cover-placeholder"></div>
                </div>
                <div class="recommendation-info">
                  <h4 class="recommendation-title">{{ recommendedBook.title }}</h4>
                  <p class="recommendation-author">{{ recommendedBook.author }}</p>
                  <div class="recommendation-footer">
                    <span class="recommendation-price">¥{{ typeof recommendedBook.price === 'number' ? recommendedBook.price.toFixed(2) : parseFloat(recommendedBook.price).toFixed(2) }}</span>
                    <div class="recommendation-rating">
                      <i class="ri-star-fill"></i>
                      {{ recommendedBook.rating?.toFixed(1) || '4.5' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </aside>

      </main>

      <!-- 底部悬浮购买栏 -->
      <div class="purchase-bar">
        <div class="purchase-content">
          <div class="purchase-info">
            <img :src="bookCover" class="purchase-cover">
            <div class="purchase-details">
              <p class="purchase-title">{{ book.title }}</p>
              <p class="purchase-author">{{ book.author }}</p>
            </div>
          </div>

          <div class="purchase-actions">
            <div class="purchase-price">
              <span class="price">¥{{ formattedPrice }}</span>
              <span class="vip-discount">VIP 专享 8 折</span>
            </div>
            <div class="action-buttons">
              <button class="add-to-cart-btn" @click="addToCart">加入购物车</button>
              <button class="buy-now-btn" @click="buyNow">
                立即购买 <i class="ri-arrow-right-line"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getBookById, getAllBooks, type Book } from '../api/bookApi'
import { getCart, addToCart as addToCartApi } from '../api/cartApi'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const book = ref<Book | null>(null)
const showFullDesc = ref(false)
const isFavorite = ref(false)
const cartItemCount = ref(0)
const isLoggedIn = ref(false)

// 计算属性
const bookCover = computed(() => book.value?.image || 'https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&q=80&w=800')
const originalPrice = computed(() => {
  const price = parseFloat(book.value?.price || '0')
  return (price / 0.7).toFixed(2)
})
const discount = computed(() => Math.round((1 - parseFloat(book.value?.price || '0') / parseFloat(originalPrice.value)) * 100))
const tags = computed(() => book.value?.category ? [book.value.category] : [])

// 格式化价格为两位小数
const formattedPrice = computed(() => {
  const price = typeof book.value?.price === 'number'
    ? book.value.price
    : parseFloat(book.value?.price?.toString() || '0')
  return price.toFixed(2)
})

const chapters = ref<any[]>([])
const reviewsList = ref<any[]>([])
const recommendedBooks = ref<any[]>([])

// 加载图书详情
const loadBookDetail = async () => {
  loading.value = true
  try {
    const bookId = route.params.id as string
    const bookData = await getBookById(parseInt(bookId))
    book.value = bookData

    // 加载推荐图书（同分类的其他图书）
    if (bookData && bookData.category) {
      await loadRecommendations(bookData.category, bookData.id)
    }

    // 检查收藏状态
    checkFavoriteStatus()
  } catch (error) {
    console.error('加载图书详情失败:', error)
    ElMessage.error('加载图书详情失败')
  } finally {
    loading.value = false
  }
}

// 加载推荐图书
const loadRecommendations = async (category: string, currentBookId: number) => {
  try {
    const allBooks = await getAllBooks()
    // 筛选同类图书，排除当前图书，最多显示3本
    recommendedBooks.value = allBooks
      .filter(b => b.category === category && b.id !== currentBookId)
      .slice(0, 3)
  } catch (error) {
    console.error('加载推荐图书失败:', error)
  }
}

const goBack = () => {
  router.back()
}

// 检查是否已收藏
const checkFavoriteStatus = () => {
  if (!book.value) return

  const favorites = JSON.parse(localStorage.getItem('favorites') || '[]')
  isFavorite.value = favorites.some((item: any) => item.id === book.value?.id)
}

// 切换收藏状态
const toggleFavorite = () => {
  if (!book.value) return

  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
  if (!isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]')
    const existingIndex = favorites.findIndex((item: any) => item.id === book.value?.id)

    if (existingIndex !== -1) {
      // 已收藏，移除收藏
      favorites.splice(existingIndex, 1)
      localStorage.setItem('favorites', JSON.stringify(favorites))
      isFavorite.value = false
      ElMessage.success('已取消收藏')
    } else {
      // 未收藏，添加收藏
      favorites.push({
        id: book.value.id,
        title: book.value.title,
        author: book.value.author,
        price: book.value.price,
        image: book.value.image,
        category: book.value.category
      })
      localStorage.setItem('favorites', JSON.stringify(favorites))
      isFavorite.value = true
      ElMessage.success('已添加到收藏')
    }
  } catch (error) {
    console.error('收藏操作失败:', error)
    ElMessage.error('收藏操作失败')
  }
}

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

const goToBook = (bookId: number) => {
  router.push(`/book/${bookId}`)
  // 滚动到顶部
  window.scrollTo(0, 0)
  // 重新加载图书详情
  loadBookDetail()
}

// 添加到购物车 - 使用真实API
const addToCart = async () => {
  if (!book.value) return

  if (!checkUserLogin()) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  const userId = getUserId()
  if (!userId) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    await addToCartApi(userId, book.value.id, 1)
    ElMessage.success(`《${book.value.title}》已添加到购物车！`)

    // 更新购物车数量
    const response = await getCart(userId)
    const totalQuantity = response.items.reduce((total, item) => total + item.quantity, 0)

    const event = new CustomEvent('cart-updated', {
      detail: { count: totalQuantity }
    })
    window.dispatchEvent(event)
  } catch (error) {
    console.error('添加到购物车失败:', error)
    ElMessage.error('添加到购物车失败')
  }
}

// 立即购买 - 使用真实API
const buyNow = async () => {
  if (!book.value) return

  if (!checkUserLogin()) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  const userId = getUserId()
  if (!userId) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    // 将商品信息存储到 sessionStorage，传递给订单确认页面
    const checkoutData = {
      items: [{
        book_id: book.value.id,
        title: book.value.title,
        author: book.value.author,
        price: typeof book.value.price === 'number' ? book.value.price : parseFloat(book.value.price.toString()),
        quantity: 1
      }]
    }
    sessionStorage.setItem('checkoutCart', JSON.stringify(checkoutData))

    // 直接跳转到结算页面
    router.push('/checkout')
  } catch (error) {
    console.error('购买失败:', error)
    ElMessage.error('购买失败')
  }
}

const toggleCart = () => {
  router.push('/cart')
}

const goToLogin = () => {
  router.push('/login')
}

const handleUserCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })

      localStorage.removeItem('token')
      localStorage.removeItem('user_id')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
      localStorage.removeItem('isLoggedIn')

      isLoggedIn.value = false

      const event = new CustomEvent('user-logout')
      window.dispatchEvent(event)

      ElMessage.success('已退出登录')
      router.push('/')
    } catch (error) {
      // 用户取消
    }
  } else if (command === 'orders') {
    router.push('/orders')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}

const checkLoginStatus = () => {
  const loginStatus = localStorage.getItem('isLoggedIn')
  isLoggedIn.value = loginStatus === 'true'
}

// 更新购物车数量
const updateCartCount = async (event?: CustomEvent) => {
  if (event && event.detail && typeof event.detail.count !== 'undefined') {
    cartItemCount.value = event.detail.count
    return
  }

  const userId = getUserId()
  if (!userId || !checkUserLogin()) {
    cartItemCount.value = 0
    return
  }

  try {
    const response = await getCart(userId)
    const totalQuantity = response.items.reduce((total, item) => total + item.quantity, 0)
    cartItemCount.value = totalQuantity
  } catch (error) {
    console.error('获取购物车数量失败:', error)
    cartItemCount.value = 0
  }
}

onMounted(async () => {
  // 滚动到页面顶部
  window.scrollTo(0, 0)
  loadBookDetail()
  checkLoginStatus()

  // 加载购物车数量
  await updateCartCount()

  // 监听购物车更新事件
  window.addEventListener('cart-updated', updateCartCount as EventListener)
  window.addEventListener('user-logout', () => {
    cartItemCount.value = 0
  })
})

onUnmounted(() => {
  window.removeEventListener('cart-updated', updateCartCount as EventListener)
})
</script>

<style scoped>
/* 引入 Remix Icon */
@import url('https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css');

.book-detail-page {
  min-height: 100vh;
  background: #FAFAFA;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  padding-bottom: 100px;
}

/* ========== 顶部导航 ========== */
.glass-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 100;
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
  font-weight: 600;
  font-size: 14px;
  color: #1D1D1F;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.cart-icon {
  position: relative;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  color: #1D1D1F;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.cart-icon:hover {
  background: rgba(0, 122, 255, 0.1);
  color: #007AFF;
}

.cart-count {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #FF3B30;
  color: white;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
}

.user-avatar-simple {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  color: #1D1D1F;
  transition: all 0.3s ease;
}

.user-avatar-simple:hover {
  background: rgba(0, 122, 255, 0.1);
  color: #007AFF;
}

.login-btn {
  background: #000000;
  border: none;
  color: white;
  font-weight: 600;
  border-radius: 16px;
  padding: 6px 16px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.login-btn:hover {
  background: #2c2c2e;
  transform: translateY(-1px);
}

.favorite-button {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 20px;
  color: #1D1D1F;
}

.favorite-button:hover {
  background: rgba(0, 0, 0, 0.05);
}

.favorite-button .ri-heart-fill {
  color: #FF3B30;
}

/* ========== 加载状态 ========== */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  color: #86868B;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(0, 122, 255, 0.2);
  border-top-color: #007AFF;
  border-radius: 50%;
  margin-bottom: 25px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ========== Hero 区域 ========== */
.detail-container {
  padding-top: 56px;
}

.hero-section {
  position: relative;
  width: 100%;
  padding: 96px 24px 48px;
  overflow: hidden;
}

@media (min-width: 1024px) {
  .hero-section {
    padding: 128px 24px 80px;
  }
}

.ambient-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.bg-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.6);
  z-index: 10;
}

.bg-blur {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  filter: blur(80px);
  opacity: 0.6;
  transform: scale(1.1);
}

.hero-content {
  position: relative;
  z-index: 10;
  max-width: 1152px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 40px;
  align-items: start;
}

@media (min-width: 768px) {
  .hero-content {
    grid-template-columns: 300px 1fr;
  }
}

@media (min-width: 1024px) {
  .hero-content {
    grid-template-columns: 340px 1fr 300px;
  }
}

/* 封面列 */
.cover-column {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.cover-wrapper {
  position: relative;
  width: 240px;
  aspect-ratio: 2/3;
  border-radius: 12px;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.15);
  background: #E5E5E7;
  overflow: hidden;
  margin-bottom: 24px;
}

@media (min-width: 768px) {
  .cover-wrapper {
    width: 100%;
  }
}

.book-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-shine {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom right, rgba(255, 255, 255, 0.2), transparent);
  opacity: 0;
  transition: opacity 0.5s;
}

.cover-wrapper:hover .cover-shine {
  opacity: 1;
}

/* 信息列 */
.info-column {
  text-align: center;
  padding-top: 8px;
}

@media (min-width: 768px) {
  .info-column {
    text-align: left;
  }
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6B7280;
  backdrop-filter: blur(12px);
  margin-bottom: 16px;
}

.badge i {
  color: #FCD34D;
}

.book-title {
  font-size: 1.875rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 8px;
  color: #1F2937;
}

@media (min-width: 768px) {
  .book-title {
    font-size: 3rem;
  }
}

.book-subtitle {
  font-size: 1.25rem;
  color: #6B7280;
  margin-bottom: 24px;
  font-weight: 500;
}

.author-section {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

@media (min-width: 768px) {
  .author-section {
    justify-content: flex-start;
  }
}

.author-info {
  text-align: center;
}

@media (min-width: 768px) {
  .author-info {
    text-align: left;
  }
}

.author-name {
  font-size: 14px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0;
}

.author-role {
  font-size: 12px;
  color: #86868B;
  margin: 0;
}

.rating-summary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  padding: 20px 0;
  margin-bottom: 24px;
}

@media (min-width: 768px) {
  .rating-summary {
    justify-content: flex-start;
  }
}

.rating-block {
  text-align: left;
}

.stars-container {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.rating-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1D1D1F;
}

.stars {
  display: flex;
  gap: 2px;
  color: #FCD34D;
  font-size: 18px;
}

.rating-count {
  font-size: 12px;
  color: #86868B;
  margin: 0;
}

.divider {
  width: 1px;
  height: 40px;
  background: rgba(0, 0, 0, 0.1);
}

.rank-block {
  text-align: left;
}

.rank-number {
  font-size: 18px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0 0 4px 0;
}

.rank-category {
  font-size: 12px;
  color: #86868B;
  margin: 0;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

@media (min-width: 768px) {
  .tags-container {
    justify-content: flex-start;
  }
}

.tag {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  border-radius: 8px;
  font-size: 14px;
  color: #6B7280;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* 统计列 */
.stats-column {
  display: none;
}

@media (min-width: 1024px) {
  .stats-column {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    align-content: start;
  }
}

.price-card {
  grid-column: span 2;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid white;
}

.card-label {
  font-size: 11px;
  color: #86868B;
  text-transform: uppercase;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.price-display {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  margin-bottom: 8px;
}

.current-price {
  font-size: 2rem;
  font-weight: 700;
  color: #1D1D1F;
}

.original-price {
  font-size: 14px;
  color: #9CA3AF;
  text-decoration: line-through;
  margin-bottom: 4px;
}

.discount-badge {
  display: inline-block;
  font-size: 12px;
  color: #10B981;
  background: #DCFCE7;
  padding: 2px 8px;
  border-radius: 4px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  padding: 16px;
  border-radius: 16px;
  border: 1px solid white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.stat-card i {
  font-size: 1.5rem;
  color: #007AFF;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #1D1D1F;
}

.stat-label {
  font-size: 10px;
  color: #86868B;
  text-transform: uppercase;
}

.vip-card {
  grid-column: span 2;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  padding: 16px;
  border-radius: 16px;
  border: 1px solid white;
  display: flex;
  align-items: center;
  gap: 12px;
}

.vip-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #000000;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.vip-text {
  flex: 1;
}

.vip-title {
  font-size: 12px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0 0 2px 0;
}

.vip-desc {
  font-size: 12px;
  color: #86868B;
  margin: 0;
}

/* ========== 内容详情区 ========== */
.content-main {
  max-width: 1152px;
  margin: 0 auto 32px;
  padding: 80px 24px 0;
  display: grid;
  grid-template-columns: 1fr;
  gap: 40px;
}

@media (min-width: 1024px) {
  .content-main {
    grid-template-columns: 1fr 340px;
  }
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0;
}

.section .flex {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section .mb-4 {
  margin-bottom: 16px;
}

.description-text {
  color: #6B7280;
  line-height: 1.6;
}

.description-text p {
  margin-bottom: 16px;
}

.description-text.clamp-3 p:not(:first-child) {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.expand-button {
  margin-top: 8px;
  color: #007AFF;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  transition: opacity 0.3s;
}

.expand-button:hover {
  opacity: 0.7;
}

/* ========== 侧边栏 ========== */
.sidebar-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.sidebar-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #F3F4F6;
}

.sidebar-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0 0 20px 0;
  padding-bottom: 16px;
  border-bottom: 1px solid #F3F4F6;
}

/* ========== 推荐图书列表 ========== */
.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-item {
  display: flex;
  gap: 12px;
  cursor: pointer;
  padding: 12px;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: #FAFAFA;
}

.recommendation-item:hover {
  background: #F5F5F7;
  transform: translateX(4px);
}

.recommendation-cover {
  flex-shrink: 0;
  width: 80px;
  height: 106px;
  border-radius: 8px;
  overflow: hidden;
  background: #F5F5F7;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.recommendation-cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #E5E5E7 0%, #F5F5F7 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.recommendation-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
}

.recommendation-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #1D1D1F;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
}

.recommendation-author {
  font-size: 12px;
  color: #86868B;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommendation-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.recommendation-price {
  font-size: 16px;
  font-weight: 700;
  color: #1D1D1F;
}

.recommendation-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #86868B;
  flex-shrink: 0;
}

.recommendation-rating i {
  color: #FCD34D;
  font-size: 12px;
}

/* ========== 底部购买栏 ========== */
.purchase-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(48px);
  -webkit-backdrop-filter: blur(48px);
  border-top: 1px solid #E5E5E7;
  padding: 16px;
  z-index: 50;
  animation: slide-up 0.3s ease;
}

@keyframes slide-up {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.purchase-content {
  max-width: 1152px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.purchase-info {
  display: none;
}

@media (min-width: 768px) {
  .purchase-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.purchase-cover {
  width: 40px;
  height: 56px;
  object-fit: cover;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #F3F4F6;
}

.purchase-details {
  text-align: left;
}

.purchase-title {
  font-weight: 700;
  font-size: 14px;
  color: #1D1D1F;
  margin: 0 0 2px 0;
}

.purchase-author {
  font-size: 12px;
  color: #86868B;
  margin: 0;
}

.purchase-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  flex: 1;
}

@media (min-width: 768px) {
  .purchase-actions {
    flex: none;
  }
}

.purchase-price {
  display: flex;
  flex-direction: column;
}

@media (min-width: 768px) {
  .purchase-price {
    align-items: flex-end;
  }
}

.price {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1D1D1F;
}

.vip-discount {
  font-size: 12px;
  color: #10B981;
  font-weight: 600;
  display: none;
}

@media (min-width: 768px) {
  .vip-discount {
    display: block;
  }
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex: 1;
}

@media (min-width: 768px) {
  .action-buttons {
    flex: none;
  }
}

.add-to-cart-btn {
  flex: 1;
  background: #F3F4F6;
  color: #1D1D1F;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: background 0.3s;
}

@media (min-width: 768px) {
  .add-to-cart-btn {
    flex: none;
  }
}

.add-to-cart-btn:hover {
  background: #E5E7EB;
}

.buy-now-btn {
  flex: 2;
  background: #000000;
  color: white;
  padding: 12px 32px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

@media (min-width: 768px) {
  .buy-now-btn {
    flex: none;
  }
}

.buy-now-btn:hover {
  background: #2c2c2e;
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

/* ========== 响应式设计 ========== */
@media (max-width: 768px) {
  .nav-title {
    opacity: 0;
  }

  .hero-section {
    padding: 64px 16px 48px;
  }

  .book-title {
    font-size: 2rem;
  }

  .book-subtitle {
    font-size: 1rem;
  }
}
</style>
