<template>
  <div class="library-container">
    <!-- 动态背景光球 -->
    <div class="mesh-gradients">
      <div class="gradient-blob blob-1"></div>
      <div class="gradient-blob blob-2"></div>
      <div class="gradient-blob blob-3"></div>
    </div>

    <!-- 磨砂玻璃导航栏 -->
    <nav :class="['glass-navbar', { 'navbar-fixed': isNavbarFixed }]">
      <div class="nav-content">
        <div class="logo" @click="goToHome">
          <span class="logo-icon logo-icon-pulse">
            <i class="ri-book-3-fill"></i>
          </span>
          <span class="logo-text">线上书店</span>
        </div>

        <div class="nav-tabs">
          <a href="#" @click.prevent="goToHome" class="nav-tab">探索</a>
          <a href="#" class="nav-tab active">书库</a>
          <a href="#" class="nav-tab">Pro会员</a>
        </div>

        <div class="nav-actions">
          <div class="cart-icon" @click="toggleCart">
            <i class="ri-shopping-cart-line"></i>
            <span class="cart-count" v-if="cartItemCount > 0">{{ cartItemCount }}</span>
          </div>

          <div v-if="isLoggedIn" class="user-info">
            <div class="user-avatar-simple" @click="goToProfile">
              <i class="ri-user-line"></i>
            </div>
          </div>
          <button v-else class="login-btn" @click="goToLogin">
            登录
          </button>
        </div>
      </div>
    </nav>

    <!-- 主要内容 -->
    <div class="content-wrapper">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>书库</h1>
        <p>探索我们精心策划的图书收藏</p>
      </div>

      <!-- 搜索和筛选 -->
      <div class="search-filter-section">
        <div class="search-box">
          <i class="ri-search-line"></i>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索书名、作者或ISBN..."
            @input="handleSearch"
          >
        </div>

        <div class="filter-tabs">
          <button
            v-for="category in categories"
            :key="category"
            :class="['filter-btn', { active: selectedCategory === category }]"
            @click="selectCategory(category)"
          >
            {{ category }}
          </button>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-container">
          <div class="loading-spinner-ios">
            <div class="spinner-blade" v-for="n in 12" :key="n"></div>
          </div>
          <p class="loading-text">正在加载图书数据</p>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="filteredBooks.length === 0" class="empty-state">
        <i class="ri-book-line"></i>
        <p>暂无符合条件的图书</p>
      </div>

      <!-- 图书网格 -->
      <div v-else class="books-grid">
        <div
          v-for="(book, index) in filteredBooks"
          :key="book.id"
          class="book-card"
        >
          <!-- 图书封面 -->
          <div class="book-cover" @click="handleCardClick(book)">
            <div class="cover-placeholder"></div>
            <!-- 评分标签 -->
            <div class="rating-badge">
              <i class="ri-star-fill"></i>
              {{ book.rating?.toFixed(1) || '4.5' }}
            </div>
          </div>

          <!-- 图书信息 -->
          <div class="book-info">
            <h3 class="book-title">{{ book.title }}</h3>
            <p class="book-author">{{ book.author }}</p>
            <div class="book-footer">
              <span class="book-price">¥{{ typeof book.price === 'number' ? book.price.toFixed(2) : parseFloat(book.price).toFixed(2) }}</span>
              <button class="add-btn" @click="addToCart(book)">
                <i class="ri-add-line"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 回到顶部按钮 -->
    <div
      class="back-to-top"
      :class="{ 'show': showBackToTop }"
      @click="scrollToTop"
      title="返回顶部"
    >
      <i class="ri-arrow-up-line"></i>
    </div>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>Designed by doob. &copy; 2025 BookStore.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllBooks, getAllCategories, type Book } from '../api/bookApi'
import { getCart, addToCart as addToCartApi } from '../api/cartApi'

const router = useRouter()
const route = useRoute()
const cartItemCount = ref(0)
const showBackToTop = ref(false)
const isNavbarFixed = ref(false)
const searchQuery = ref('')
const selectedCategory = ref('全部')
const categories = ref<string[]>(['全部'])
const books = ref<Book[]>([])
const loading = ref(false)
const isLoggedIn = ref(false)

// 加载分类数据
const loadCategories = async () => {
  try {
    const categoriesData = await getAllCategories()
    categories.value = ['全部', ...categoriesData.map(cat => cat.name)]
  } catch (error) {
    console.error('加载分类失败:', error)
    categories.value = ['全部', '技术', '文学', '历史', '科学', '艺术', '哲学', '心理学', '经济', '管理', '生活']
  }
}

// 加载图书数据
const loadBooks = async () => {
  loading.value = true
  try {
    const booksData = await getAllBooks()
    books.value = booksData.map(book => ({
      ...book,
      price: typeof book.price === 'number' ? book.price.toFixed(2) : book.price,
      rating: book.rating || 4.5,
      image: book.image || '/images/book-placeholder.svg'
    }))
  } catch (error) {
    console.error('加载图书失败:', error)
    ElMessage.error('加载图书数据失败，请刷新页面重试')
  } finally {
    loading.value = false
  }
}

// 过滤图书
const filteredBooks = computed(() => {
  let result = books.value

  // 按分类筛选
  if (selectedCategory.value !== '全部') {
    result = result.filter(book => book.category === selectedCategory.value)
  }

  // 按搜索关键词筛选
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(book =>
      book.title.toLowerCase().includes(query) ||
      book.author?.toLowerCase().includes(query) ||
      book.isbn?.toLowerCase().includes(query)
    )
  }

  // 按ID排序，确保顺序一致
  return result.sort((a, b) => a.id - b.id)
})

const selectCategory = (category: string) => {
  selectedCategory.value = category
}

const handleSearch = () => {
  // 搜索会自动通过 computed 触发
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

const handleCardClick = (book: Book) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  router.push(`/book/${book.id}`)
}

// 添加到购物车 - 使用真实API
const addToCart = async (book: Book) => {
  if (!isLoggedIn.value) {
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
    await addToCartApi(userId, book.id, 1)
    ElMessage.success(`《${book.title}》已添加到购物车！`)

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

const goToHome = () => {
  router.push('/')
}

const goToLogin = () => {
  router.push('/login')
}

const toggleCart = () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  router.push('/cart')
}

const goToProfile = () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  router.push('/profile')
}

const scrollToTop = () => {
  const scrollDuration = 1000
  const startScrollTop = window.scrollY
  const startTime = performance.now()

  const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3)

  const scrollAnimation = (currentTime: number) => {
    const elapsedTime = currentTime - startTime
    const progress = Math.min(elapsedTime / scrollDuration, 1)
    const easeProgress = easeOutCubic(progress)

    window.scrollTo(0, startScrollTop * (1 - easeProgress))

    if (progress < 1) {
      requestAnimationFrame(scrollAnimation)
    }
  }

  requestAnimationFrame(scrollAnimation)
}

const handleScroll = () => {
  const currentScrollY = window.scrollY
  showBackToTop.value = currentScrollY > 300

  if (currentScrollY > 100) {
    isNavbarFixed.value = true
  } else {
    isNavbarFixed.value = false
  }
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

const checkLoginStatus = () => {
  const loginStatus = localStorage.getItem('isLoggedIn')
  isLoggedIn.value = loginStatus === 'true'
}

onMounted(async () => {
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('cart-updated', updateCartCount as any)
  window.addEventListener('user-logout', () => {
    cartItemCount.value = 0
  })

  checkLoginStatus()
  loadCategories()
  loadBooks()

  // 加载购物车数量
  await updateCartCount()

  // 从 URL 查询参数中获取搜索关键词
  const searchParam = route.query.search as string
  if (searchParam) {
    searchQuery.value = searchParam
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('cart-updated', updateCartCount as any)
})
</script>

<style scoped>
/* 引入 Remix Icon */
@import url('https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css');

.library-container {
  min-height: 100vh;
  background: #F5F5F7;
  position: relative;
  overflow-x: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* ========== 动态背景光球 ========== */
.mesh-gradients {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
  pointer-events: none;
}

.gradient-blob {
  position: absolute;
  width: 384px;
  height: 384px;
  border-radius: 50%;
  mix-blend-mode: multiply;
  filter: blur(64px);
  opacity: 0.3;
}

.blob-1 {
  top: 0;
  left: 25%;
  background: #BFDBFE;
  animation: blob 10s infinite;
}

.blob-2 {
  top: 0;
  right: 25%;
  background: #BBF7D0;
  animation: blob 10s infinite 2s;
}

.blob-3 {
  bottom: -128px;
  left: 33%;
  background: #DDD6FE;
  animation: blob 10s infinite 4s;
}

@keyframes blob {
  0%, 100% {
    transform: translate(0px, 0px) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

/* ========== 磨砂玻璃导航栏 ========== */
.glass-navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: saturate(180%) blur(24px);
  -webkit-backdrop-filter: saturate(180%) blur(24px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
}

.navbar-fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 3rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: transform 0.3s ease;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: #007AFF;
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  position: relative;
}

.logo-icon-pulse::before {
  content: '';
  position: absolute;
  inset: 0;
  background: #007AFF;
  border-radius: 10px;
  animation: logo-pulse 2s cubic-bezier(0, 0, 0.2, 1) infinite;
  z-index: -1;
}

@keyframes logo-pulse {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.15);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
}

.logo-text {
  color: #1D1D1F;
}

.nav-tabs {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.nav-tab {
  position: relative;
  color: #86868B;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 0.5rem 0;
  transition: color 0.3s ease;
}

.nav-tab:hover {
  color: #1D1D1F;
}

.nav-tab.active {
  color: #1D1D1F;
  font-weight: 600;
}

.nav-tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: #000000;
  border-radius: 2px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.cart-icon {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 20px;
  color: #1D1D1F;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 50%;
  transition: all 0.3s ease;
}

.cart-icon:hover {
  background: rgba(0, 122, 255, 0.1);
  color: #007AFF;
  transform: scale(1.05);
}

.cart-count {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #FF3B30;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
}

.user-avatar-simple {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 20px;
  color: #1D1D1F;
  transition: all 0.3s ease;
}

.user-avatar-simple:hover {
  background: rgba(0, 122, 255, 0.1);
  color: #007AFF;
  transform: scale(1.05);
}

.login-btn {
  background: #000000;
  border: none;
  color: white;
  font-weight: 600;
  border-radius: 20px;
  padding: 8px 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.login-btn:hover {
  background: #2c2c2e;
  transform: translateY(-1px);
}

/* ========== 主要内容 ========== */
.content-wrapper {
  position: relative;
  z-index: 10;
  padding-top: 60px;
  max-width: 1400px;
  margin: 0 auto;
  padding-left: 3rem;
  padding-right: 3rem;
  padding-bottom: 80px;
}

/* ========== 页面标题 ========== */
.page-header {
  margin-bottom: 40px;
  text-align: center;
}

.page-header h1 {
  font-size: 3rem;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0 0 0.5rem 0;
  letter-spacing: -0.02em;
}

.page-header p {
  font-size: 1.125rem;
  color: #86868B;
  margin: 0;
}

/* ========== 搜索和筛选 ========== */
.search-filter-section {
  margin-bottom: 40px;
}

.search-box {
  max-width: 600px;
  margin: 0 auto 30px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: white;
  border: 1.5px solid #E5E5E7;
  border-radius: 16px;
  padding: 0.75rem 1rem;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.search-box:hover {
  border-color: #C7C7CC;
}

.search-box:focus-within {
  border-color: #007AFF;
  box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
}

.search-box i {
  font-size: 20px;
  color: #86868B;
}

.search-box input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
  color: #1D1D1F;
  background: transparent;
}

.search-box input::placeholder {
  color: #86868B;
}

.filter-tabs {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #E5E5E7;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  color: #6B7280;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  border-color: #007AFF;
  color: #007AFF;
}

.filter-btn.active {
  background: #000000;
  border-color: #000000;
  color: white;
}

/* ========== 加载和空状态 ========== */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 100px 20px;
}

.loading-container {
  text-align: center;
}

/* iOS 风格加载动画 */
.loading-spinner-ios {
  position: relative;
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
}

.spinner-blade {
  position: absolute;
  left: 50%;
  top: 0;
  width: 3px;
  height: 12px;
  margin-left: -1.5px;
  background: #8E8E93;
  border-radius: 3px;
  transform-origin: 50% 20px;
  opacity: 0.25;
}

.spinner-blade:nth-child(1) {
  transform: rotate(0deg);
  animation: ios-spinner-fade 1s linear infinite;
  animation-delay: 0s;
}

.spinner-blade:nth-child(2) {
  transform: rotate(30deg);
  animation: ios-spinner-fade 1s linear infinite;
  animation-delay: 0.083s;
}

.spinner-blade:nth-child(3) {
  transform: rotate(60deg);
  animation: ios-spinner-fade 1s linear infinite;
  animation-delay: 0.166s;
}

.spinner-blade:nth-child(4) {
  transform: rotate(90deg);
  animation: ios-spinner-fade 1s linear infinite;
  animation-delay: 0.249s;
}

.spinner-blade:nth-child(5) {
  transform: rotate(120deg);
  animation: ios-spinner-fade 1s linear infinite;
  animation-delay: 0.332s;
}

.spinner-blade:nth-child(6) {
  transform: rotate(150deg);
  animation: ios-spinner-fade 1s linear infinite;
  animation-delay: 0.415s;
}

.spinner-blade:nth-child(7) {
  transform: rotate(180deg);
  animation: ios-spinner-fade 1s linear infinite;
  animation-delay: 0.498s;
}

.spinner-blade:nth-child(8) {
  transform: rotate(210deg);
  animation: ios-spinner-fade 1s linear infinite;
  animation-delay: 0.581s;
}

.spinner-blade:nth-child(9) {
  transform: rotate(240deg);
  animation: ios-spinner-fade 1s linear infinite;
  animation-delay: 0.664s;
}

.spinner-blade:nth-child(10) {
  transform: rotate(270deg);
  animation: ios-spinner-fade 1s linear infinite;
  animation-delay: 0.747s;
}

.spinner-blade:nth-child(11) {
  transform: rotate(300deg);
  animation: ios-spinner-fade 1s linear infinite;
  animation-delay: 0.830s;
}

.spinner-blade:nth-child(12) {
  transform: rotate(330deg);
  animation: ios-spinner-fade 1s linear infinite;
  animation-delay: 0.913s;
}

@keyframes ios-spinner-fade {
  0% {
    opacity: 1;
  }
  100% {
    opacity: 0.25;
  }
}

.loading-text {
  font-size: 17px;
  font-weight: 400;
  color: #86868B;
  margin: 0;
  letter-spacing: -0.01em;
}

.empty-state {
  text-align: center;
  padding: 100px 20px;
  color: #86868B;
}

.empty-state i {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 20px;
}

/* ========== 图书网格 ========== */
.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.5rem;
}

.book-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* 图书封面 */
.book-cover {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  overflow: hidden;
  cursor: pointer;
  background: #F5F5F7;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #E5E5E7 0%, #F5F5F7 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}

.book-cover:hover .cover-placeholder {
  transform: scale(1.05);
}

/* 评分标签 */
.rating-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.rating-badge i {
  color: #FCD34D;
  font-size: 12px;
}

/* 图书信息 */
.book-info {
  padding: 16px;
}

/* 图书标题 */
.book-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #1D1D1F;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 作者名 */
.book-author {
  font-size: 13px;
  color: #86868B;
  margin: 0 0 12px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 底部操作区 */
.book-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.book-price {
  font-size: 18px;
  font-weight: 700;
  color: #1D1D1F;
}

.add-btn {
  width: 36px;
  height: 36px;
  background: #000000;
  color: white;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 20px;
}

.add-btn:hover {
  background: #2c2c2e;
  transform: scale(1.1);
}

/* ========== 回到顶部按钮 ========== */
.back-to-top {
  position: fixed;
  bottom: 100px;
  right: 30px;
  width: 56px;
  height: 56px;
  background: #000000;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 999;
  color: white;
  font-size: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateY(30px);
  pointer-events: none;
}

.back-to-top.show {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

.back-to-top:hover {
  background: #2c2c2e;
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

/* ========== 页脚 ========== */
.footer {
  position: relative;
  z-index: 10;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(12px);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  margin-top: 4rem;
}

.footer-content {
  text-align: center;
  padding: 2rem;
  color: #86868B;
  font-size: 14px;
}

/* ========== 响应式设计 ========== */
@media (max-width: 1024px) {
  .content-wrapper {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .nav-content {
    padding: 1rem 1.5rem;
  }

  .page-header h1 {
    font-size: 2.5rem;
  }
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 2rem;
  }

  .nav-tabs {
    display: none;
  }

  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 1rem;
  }

  .back-to-top {
    bottom: 80px;
    right: 20px;
    width: 48px;
    height: 48px;
  }
}
</style>
