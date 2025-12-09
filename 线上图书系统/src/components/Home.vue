<template>
  <div class="home-container">
    <!-- 动态背景光球 (Mesh Gradients) -->
    <div class="mesh-gradients">
      <div class="gradient-blob blob-1"></div>
      <div class="gradient-blob blob-2"></div>
      <div class="gradient-blob blob-3"></div>
    </div>

    <!-- 磨砂玻璃导航栏 -->
    <nav class="glass-navbar" :class="{ 'navbar-fixed': isNavbarFixed }">
      <div class="nav-content">
        <div class="logo" @click="refreshPage">
          <span class="logo-icon">
            <i class="ri-book-3-fill"></i>
          </span>
          <span class="logo-text">线上书店</span>
        </div>

        <div class="nav-tabs">
          <a href="#" class="nav-tab active">探索</a>
          <a href="#" @click.prevent="goToLibrary" class="nav-tab">书库</a>
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


    <!-- 导航栏占位符 -->
    <div v-if="isNavbarFixed" class="navbar-placeholder"></div>

    <!-- 主要内容 -->
    <div class="content-wrapper">

      <!-- Hero区域 - 左右分栏 -->
      <section class="hero-section">
        <div class="hero-grid">
          <!-- 左侧：文案 -->
          <div class="hero-left">
            <div class="status-badge">
              <span class="pulse-dot"></span>
              NEW RELEASE 2025
            </div>

            <h1 class="hero-title">
              阅读，<br>
              <span class="hero-gradient">重塑思维</span> 的力量。
            </h1>

            <p class="hero-description">
              TechBooks 汇集全球顶尖技术与科学著作，为您打造沉浸式的深度阅读体验。加入 10,000+ 开发者社区。
            </p>

            <!-- 搜索框 -->
            <div class="hero-search-wrapper">
              <div class="hero-search-glow"></div>
              <div class="hero-search-box">
                <i class="ri-search-line"></i>
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="搜索书名、ISBN 或作者..."
                  @keyup.enter="handleSearch"
                >
                <button @click="handleSearch">Go</button>
              </div>
            </div>
          </div>

          <!-- 右侧：3D视觉展示 -->
          <div class="hero-right">
            <div class="featured-card-bg"></div>
            <div class="featured-card" v-if="latestBook">
              <div class="featured-card-header">
                <span class="featured-badge">最新上架</span>
                <div class="featured-stars">
                  <i class="ri-star-fill" v-for="n in Math.floor(latestBook.rating)" :key="n"></i>
                  <i class="ri-star-half-fill" v-if="latestBook.rating % 1 !== 0"></i>
                </div>
              </div>
              <div class="featured-cover" @click="viewBookDetail(latestBook)">
                <div class="featured-cover-placeholder">
                </div>
              </div>
              <h3 class="featured-title">{{ latestBook.title }}</h3>
              <p class="featured-desc">{{ latestBook.description?.substring(0, 30) }}...</p>
              <button class="featured-action-btn" @click="addToCart(latestBook)">立即购买</button>
            </div>
            <div class="stats-mini-card">
              <div class="stats-mini-icon">
                <i class="ri-star-line"></i>
              </div>
              <div class="stats-mini-text">
                <p class="stats-mini-value">新书上新！</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Bento Grid统计区域 -->
      <section class="bento-section">
        <div class="bento-grid">
          <!-- 大方块：主推 -->
          <div class="bento-main" @click="viewAllBooks">
            <div class="bento-main-bg"></div>
            <div class="bento-main-content">
              <h2>浏览所有书籍</h2>
            </div>
            <div class="bento-main-action">
              <span>查看更多</span>
              <i class="ri-arrow-right-line"></i>
            </div>
          </div>

          <!-- 统计数据卡片 -->
          <div class="bento-stat-card">
            <div class="bento-stat-icon books">
              <i class="ri-book-open-line"></i>
            </div>
            <div class="bento-stat-number">1.2万+</div>
            <div class="bento-stat-label">精选书籍</div>
          </div>

          <div class="bento-stat-card green">
            <div class="bento-stat-icon users">
              <i class="ri-user-smile-line"></i>
            </div>
            <div class="bento-stat-number">850+</div>
            <div class="bento-stat-label">活跃作者</div>
          </div>

          <!-- 分类入口 -->
          <div class="bento-category" @click="viewAllBooks">
            <div class="bento-category-content">
              <h3>热门分类</h3>
              <div class="category-tags">
                <span>技术</span>
                <span>文学</span>
                <span>科学</span>
              </div>
            </div>
            <div class="category-glow"></div>
            <button class="category-btn">
              <i class="ri-arrow-right-line"></i>
            </button>
          </div>
        </div>
      </section>

      <!-- 图书展示区 -->
      <section class="books-section">
        <div class="section-header">
          <div class="section-title">
            <h2>精选图书</h2>
            <p>每周更新的优质技术读物</p>
          </div>
        </div>

        <!-- 书籍卡片容器 -->
        <CardContainer />
      </section>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import CardContainer from './CardContainer.vue'
import { getAllBooks, type Book } from '../api/bookApi'

const router = useRouter()
const cartItemCount = ref(0)
const showBackToTop = ref(false)
const isNavbarFixed = ref(false)
const lastScrollY = ref(0)
const searchQuery = ref('')
const isLoggedIn = ref(false)
const username = ref('')
const latestBook = ref<Book | null>(null)

// 书籍颜色数组
const bookColors = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
]

const getBookColor = (index: number) => {
  return bookColors[index % bookColors.length]
}

// 检查登录状态
const checkLoginStatus = () => {
  const loginStatus = localStorage.getItem('isLoggedIn')
  const storedUsername = localStorage.getItem('username')

  isLoggedIn.value = loginStatus === 'true'
  username.value = storedUsername || ''

  if (isLoggedIn.value) {
    const event = new CustomEvent('user-login')
    window.dispatchEvent(event)
  }
}

const goToLogin = () => {
  router.push('/login')
}

const goToLibrary = () => {
  router.push('/library')
}

const refreshPage = () => {
  window.location.reload()
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
      username.value = ''

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

const toggleCart = () => {
  router.push('/cart')
}

const updateCartCount = (event: CustomEvent) => {
  if (event.detail && typeof event.detail.count !== 'undefined') {
    cartItemCount.value = event.detail.count
  } else {
    const cartData = JSON.parse(localStorage.getItem('cart') || '[]')
    cartItemCount.value = cartData.length
  }
}

const handleAddToCart = (event: CustomEvent) => {
  // cart-updated事件会处理正确的数量更新
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

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    const searchEvent = new CustomEvent('book-search', {
      detail: { query: searchQuery.value.trim() }
    })
    window.dispatchEvent(searchEvent)
  }
}

const handleScroll = () => {
  const currentScrollY = window.scrollY
  showBackToTop.value = currentScrollY > 300

  if (currentScrollY > 100) {
    isNavbarFixed.value = true
  } else {
    isNavbarFixed.value = false
  }

  lastScrollY.value = currentScrollY
}

const handleLoginSuccess = () => {
  checkLoginStatus()
}

// 加载最新图书
const loadLatestBook = async () => {
  try {
    const books = await getAllBooks()
    if (books && books.length > 0) {
      // 获取最新的图书（假设按ID降序或时间排序）
      latestBook.value = books[0]
    }
  } catch (error) {
    console.error('加载最新图书失败:', error)
  }
}

// 查看图书详情
const viewBookDetail = (book: Book) => {
  router.push(`/book/${book.id}`)
}

// 添加到购物车
const addToCart = (book: Book) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]')

    // 检查是否已在购物车中
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

      // 触发购物车更新事件
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

// 查看所有图书
const viewAllBooks = () => {
  // 滚动到图书展示区域
  const booksSection = document.querySelector('.books-section')
  if (booksSection) {
    booksSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

onMounted(() => {
  window.addEventListener('cart-updated', updateCartCount as EventListener)
  window.addEventListener('add-to-cart', handleAddToCart as EventListener)
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('login-success', handleLoginSuccess as EventListener)

  checkLoginStatus()
  loadLatestBook()
})

onUnmounted(() => {
  window.removeEventListener('cart-updated', updateCartCount as EventListener)
  window.removeEventListener('add-to-cart', handleAddToCart as EventListener)
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('login-success', handleLoginSuccess as EventListener)
})
</script>

<style scoped>
/* 引入 Remix Icon */
@import url('https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css');

.home-container {
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
  position: relative;
  z-index: 100;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: saturate(180%) blur(24px);
  -webkit-backdrop-filter: saturate(180%) blur(24px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.navbar-fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
}

.navbar-placeholder {
  height: 64px;
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

.logo-light {
  font-weight: 400;
  color: #86868B;
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
  padding-top: 80px;
  max-width: 1400px;
  margin: 0 auto;
  padding-left: 3rem;
  padding-right: 3rem;
}

/* ========== Hero区域 ========== */
.hero-section {
  margin-bottom: 80px;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 3rem;
  align-items: center;
}

@media (min-width: 1024px) {
  .hero-grid {
    grid-template-columns: 1fr 1fr;
  }

  .nav-links {
    display: flex;
  }
}

.hero-left {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #007AFF;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  width: fit-content;
}

.pulse-dot {
  position: relative;
  width: 8px;
  height: 8px;
  background: #007AFF;
  border-radius: 50%;
}

.pulse-dot::before {
  content: '';
  position: absolute;
  inset: 0;
  background: #60A5FA;
  border-radius: 50%;
  animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite;
}

@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  color: #1D1D1F;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.hero-gradient {
  background: linear-gradient(135deg, #007AFF 0%, #06B6D4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.125rem;
  color: #86868B;
  line-height: 1.6;
  max-width: 540px;
}

/* Hero搜索框 */
.hero-search-wrapper {
  position: relative;
  max-width: 540px;
}

.hero-search-glow {
  position: absolute;
  inset: -4px;
  background: linear-gradient(135deg, #DBEAFE, #D1FAE5);
  border-radius: 16px;
  filter: blur(8px);
  opacity: 0.25;
  transition: opacity 0.3s ease;
}

.hero-search-wrapper:hover .hero-search-glow {
  opacity: 0.5;
}

.hero-search-box {
  position: relative;
  display: flex;
  align-items: center;
  background: white;
  border: 1.5px solid #E5E5E7;
  border-radius: 16px;
  padding: 0.75rem;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.hero-search-box:hover {
  border-color: #C7C7CC;
}

.hero-search-box:focus-within {
  border-color: #007AFF;
  box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
}

.hero-search-box i {
  font-size: 20px;
  color: #86868B;
  margin-right: 0.75rem;
}

.hero-search-box input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
  color: #1D1D1F;
  background: transparent;
  height: 44px;
}

.hero-search-box input::placeholder {
  color: #86868B;
  font-weight: 400;
}

.hero-search-box button {
  background: #000000;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  white-space: nowrap;
}

.hero-search-box button:hover {
  background: #2c2c2e;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.trust-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 1rem;
}

.avatars-group {
  display: flex;
  align-items: center;
}

.avatars-group img,
.avatar-count {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid white;
  margin-left: -12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.avatars-group img:first-child {
  margin-left: 0;
}

.avatar-count {
  background: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #6B7280;
}

.trust-text {
  font-size: 14px;
}

.trust-rating {
  font-weight: 700;
  color: #1D1D1F;
  margin: 0;
}

.trust-subtitle {
  color: #86868B;
  margin: 0;
}

/* 右侧3D展示 */
.hero-right {
  position: relative;
  height: 500px;
  display: none;
}

@media (min-width: 1024px) {
  .hero-right {
    display: block;
  }
}

.featured-card-bg {
  position: absolute;
  top: 40px;
  right: 40px;
  width: 75%;
  height: 75%;
  background: linear-gradient(135deg, #F3F4F6, white);
  border-radius: 40px;
  border: 1px solid white;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
  transform: rotate(3deg);
}

.featured-card {
  position: absolute;
  top: 0;
  right: 80px;
  width: 320px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(24px);
  padding: 1.5rem;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
  border: 1px solid white;
  z-index: 10;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.featured-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.featured-badge {
  font-size: 11px;
  font-weight: 700;
  color: #86868B;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.featured-stars {
  display: flex;
  gap: 2px;
  color: #FCD34D;
  font-size: 12px;
}

.featured-cover {
  position: relative;
  width: 100%;
  height: 192px;
  border-radius: 12px;
  margin-bottom: 1rem;
  overflow: hidden;
  cursor: pointer;
}

.featured-cover-placeholder {
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

.featured-cover-placeholder::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.05) 0%, rgba(52, 199, 89, 0.05) 100%);
  z-index: 0;
}

.featured-cover:hover .featured-cover-placeholder {
  transform: scale(1.05);
}

.play-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.play-btn {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.featured-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 0.25rem;
  color: #1D1D1F;
}

.featured-desc {
  font-size: 14px;
  color: #6B7280;
  margin-bottom: 1rem;
}

.featured-action-btn {
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

.featured-action-btn:hover {
  background: #2c2c2e;
}

.stats-mini-card {
  position: absolute;
  bottom: 80px;
  right: 0;
  background: white;
  padding: 1rem;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border: 1px solid #F3F4F6;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 20;
  animation: float 6s ease-in-out infinite 1s;
}

.stats-mini-icon {
  width: 40px;
  height: 40px;
  background: #D1FAE5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #10B981;
  font-size: 18px;
}

.stats-mini-text p {
  margin: 0;
  font-size: 12px;
}

.stats-mini-text p:first-child {
  color: #6B7280;
}

.stats-mini-value {
  font-weight: 700;
  font-size: 14px;
  color: #1D1D1F;
}

/* ========== Bento Grid区域 ========== */
.bento-section {
  margin-bottom: 80px;
}

.bento-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  grid-auto-rows: 180px;
}

@media (min-width: 768px) {
  .bento-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .bento-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.bento-main {
  grid-column: span 1;
  grid-row: span 2;
  background: white;
  border: 1px solid #E5E5E7;
  color: #1D1D1F;
  border-radius: 32px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

@media (min-width: 768px) {
  .bento-main {
    grid-column: span 2;
  }
}

.bento-main:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.bento-main-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.05) 0%, rgba(52, 199, 89, 0.05) 100%);
  z-index: 0;
}

.bento-main-content {
  position: relative;
  z-index: 10;
}

.bento-main-content h2 {
  font-size: 1.875rem;
  font-weight: 700;
  margin: 0;
  max-width: 320px;
  line-height: 1.2;
  color: #1D1D1F;
}

.bento-main-action {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 14px;
  font-weight: 600;
  color: #007AFF;
}

.bento-stat-card {
  background: white;
  border: 1px solid #E5E5E7;
  border-radius: 32px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
  transition: all 0.3s ease;
}

.bento-stat-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.bento-stat-card.green {
  background: #DCFCE7;
  border-color: #BBF7D0;
}

.bento-stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 0.75rem;
}

.bento-stat-icon.books {
  background: #DBEAFE;
  color: #007AFF;
}

.bento-stat-icon.users {
  background: white;
  color: #10B981;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.bento-stat-number {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1D1D1F;
  margin-bottom: 0.25rem;
}

.bento-stat-label {
  font-size: 11px;
  color: #6B7280;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.bento-category {
  grid-column: span 1;
  background: white;
  border: 1px solid #E5E5E7;
  border-radius: 32px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

@media (min-width: 768px) {
  .bento-category {
    grid-column: span 2;
  }
}

.bento-category:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.bento-category-content {
  position: relative;
  z-index: 10;
}

.bento-category-content h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: #1D1D1F;
}

.category-tags {
  display: flex;
  gap: 0.5rem;
}

.category-tags span {
  padding: 0.5rem 0.75rem;
  background: #F3F4F6;
  border-radius: 8px;
  font-size: 12px;
  color: #6B7280;
}

.category-glow {
  position: absolute;
  width: 96px;
  height: 96px;
  background: linear-gradient(135deg, #A78BFA, #60A5FA);
  border-radius: 50%;
  filter: blur(40px);
  bottom: -16px;
  right: -16px;
  opacity: 0.5;
}

.category-btn {
  width: 40px;
  height: 40px;
  background: #000000;
  color: white;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-btn:hover {
  background: #2c2c2e;
  transform: scale(1.05);
}

/* ========== 图书区域 ========== */
.books-section {
  margin-bottom: 80px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 2rem;
}

.section-title h2 {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0 0 0.5rem 0;
}

.section-title p {
  color: #86868B;
  margin: 0;
  font-size: 14px;
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
  .hero-title {
    font-size: 2.5rem;
  }

  .content-wrapper {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .nav-content {
    padding: 1rem 1.5rem;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-description {
    font-size: 1rem;
  }

  .nav-tabs {
    display: none;
  }

  .back-to-top {
    bottom: 80px;
    right: 20px;
    width: 48px;
    height: 48px;
  }
}
</style>
