<template>
  <div class="library-container">
    <!-- 动态背景光球 -->
    <div class="mesh-gradients">
      <div class="gradient-blob blob-1"></div>
      <div class="gradient-blob blob-2"></div>
      <div class="gradient-blob blob-3"></div>
    </div>

    <!-- 磨砂玻璃导航栏 -->
    <nav class="glass-navbar">
      <div class="nav-content">
        <div class="logo" @click="goToHome">
          <span class="logo-icon">
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
        <div class="loading-spinner"></div>
        <p>正在加载图书数据...</p>
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
          <!-- 卡片头部 -->
          <div class="card-header">
            <span class="category-badge">{{ book.category }}</span>
            <div class="rating-stars">
              <i class="ri-star-fill" v-for="n in Math.floor(book.rating)" :key="n"></i>
              <i class="ri-star-half-fill" v-if="book.rating % 1 !== 0"></i>
            </div>
          </div>

          <!-- 图书封面 -->
          <div class="book-cover" @click="handleCardClick(book)">
            <div class="cover-placeholder"></div>
          </div>

          <!-- 图书信息 -->
          <h3 class="book-title">{{ book.title }}</h3>
          <p class="book-desc">{{ book.description?.substring(0, 30) }}...</p>
          <button class="action-btn" @click="addToCart(book)">立即购买</button>
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
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllBooks, getAllCategories, type Book } from '../api/bookApi'

const router = useRouter()
const cartItemCount = ref(0)
const showBackToTop = ref(false)
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

  return result
})

const selectCategory = (category: string) => {
  selectedCategory.value = category
}

const handleSearch = () => {
  // 搜索会自动通过 computed 触发
}

const handleCardClick = (book: Book) => {
  router.push(`/book/${book.id}`)
}

const addToCart = (book: Book) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]')
    const existingItem = cart.find((item: any) => item.id === book.id)

    if (existingItem) {
      ElMessage.info('该书籍已在购物车中')
    } else {
      cart.push({
        id: book.id,
        title: book.title,
        author: book.author,
        price: book.price,
        image: book.image,
        quantity: 1
      })

      localStorage.setItem('cart', JSON.stringify(cart))

      const event = new CustomEvent('cart-updated', {
        detail: { count: cart.length }
      })
      window.dispatchEvent(event)

      ElMessage.success('已添加到购物车')
    }
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
  router.push('/cart')
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
    } catch (error) {
      // 用户取消
    }
  } else if (command === 'orders') {
    router.push('/orders')
  } else if (command === 'profile') {
    router.push('/profile')
  }
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
  showBackToTop.value = window.scrollY > 300
}

const updateCartCount = (event: CustomEvent) => {
  if (event.detail && typeof event.detail.count !== 'undefined') {
    cartItemCount.value = event.detail.count
  } else {
    const cartData = JSON.parse(localStorage.getItem('cart') || '[]')
    cartItemCount.value = cartData.length
  }
}

const checkLoginStatus = () => {
  const loginStatus = localStorage.getItem('isLoggedIn')
  isLoggedIn.value = loginStatus === 'true'
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('cart-updated', updateCartCount as EventListener)
  checkLoginStatus()
  loadCategories()
  loadBooks()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('cart-updated', updateCartCount as EventListener)
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
  width: 32px;
  height: 32px;
  background: #000000;
  color: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
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
  text-align: center;
  padding: 100px 20px;
  color: #86868B;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(0, 122, 255, 0.2);
  border-top-color: #007AFF;
  border-radius: 50%;
  margin: 0 auto 25px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  font-size: 18px;
  font-weight: 500;
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
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
}

.book-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  padding: 1.5rem;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
  border: 1px solid white;
  animation: float 6s ease-in-out infinite;
  transition: all 0.3s ease;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.category-badge {
  font-size: 11px;
  font-weight: 700;
  color: #86868B;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.rating-stars {
  display: flex;
  gap: 2px;
  color: #FCD34D;
  font-size: 12px;
}

.book-cover {
  position: relative;
  width: 100%;
  height: 192px;
  border-radius: 12px;
  margin-bottom: 1rem;
  overflow: hidden;
  cursor: pointer;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
  color: #007AFF;
  transition: transform 0.5s ease;
  background: white;
  border: 1px solid #E5E5E7;
  position: relative;
}

.cover-placeholder::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.05) 0%, rgba(52, 199, 89, 0.05) 100%);
  z-index: 0;
}

.book-cover:hover .cover-placeholder {
  transform: scale(1.05);
}

.book-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 0.25rem;
  color: #1D1D1F;
}

.book-desc {
  font-size: 14px;
  color: #6B7280;
  margin-bottom: 1rem;
}

.action-btn {
  width: 100%;
  padding: 0.75rem;
  background: #000000;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: #2c2c2e;
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
    grid-template-columns: 1fr;
  }

  .back-to-top {
    bottom: 80px;
    right: 20px;
    width: 48px;
    height: 48px;
  }
}
</style>
