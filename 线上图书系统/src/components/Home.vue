<template>
  <div class="home-container">
    <!-- 欢迎屏幕 -->
    <div v-if="showWelcome" class="welcome-screen">
      <h1 class="welcome-text" :class="{ 'fly-out': welcomeAnimating }">
        欢迎来到科技书城
      </h1>
    </div>

    <!-- 动态粒子背景 -->
    <div class="dynamic-bg">
      <div ref="canvasContainer" class="canvas-container"></div>
    </div>

    <!-- 导航栏 -->
    <nav class="navbar" :class="{ 'fade-in': !showWelcome, 'fade-in-delay-1': !showWelcome, 'navbar-fixed': isNavbarFixed, 'navbar-slide-down': showNavbarAnimation }">
      <div class="nav-content">
        <div class="logo" @click="refreshPage">
          <span class="logo-text">科技书城</span>
        </div>
        <div class="nav-search">
          <el-input
            v-model="searchQuery"
            placeholder="搜索书籍、作者、关键字..."
            class="search-input"
            prefix-icon="Search"
            @keyup.enter="handleSearch"
            clearable
          />
          <el-button class="search-btn" @click="handleSearch" type="primary">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </div>
        <div class="nav-actions">
          <div v-if="isLoggedIn" class="user-info">
            <el-dropdown @command="handleUserCommand">
              <span class="user-dropdown">
                <el-icon class="user-icon"><User /></el-icon>
                <span class="username">{{ username }}</span>
                <el-icon class="arrow-icon"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="orders">
                    <el-icon><Tickets /></el-icon>
                    我的订单
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <el-button v-else type="primary" class="login-btn" @click="goToLogin">
            登录/注册
          </el-button>
        </div>
      </div>
    </nav>

    <!-- 导航栏占位符，防止内容跳动 -->
    <div v-if="isNavbarFixed" class="navbar-placeholder"></div>

    <!-- 主要内容 -->
    <div class="content-wrapper" :class="{ 'fade-in': !showWelcome, 'fade-in-delay-2': !showWelcome }">
      <!-- 英雄区域 -->
      <section class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">
            探索图书海洋
            <br>
            <span class="hero-subtitle">开启你的阅读之旅</span>
          </h1>
          <p class="hero-description">
            汇聚全球优质书籍
            <br>
            让你尽情遨游在图书世界中
          </p>
          <div class="hero-stats">
            <div class="stat-item">
              <span class="stat-number">1000+</span>
              <span class="stat-label">精选书籍</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">50+</span>
              <span class="stat-label">包含领域</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">10000+</span>
              <span class="stat-label">读者信赖</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 书籍卡片区域 -->
      <section class="books-section" :class="{ 'fade-in': !showWelcome, 'fade-in-delay-3': !showWelcome }">
        <CardContainer />
      </section>
    </div>

    <!-- 购物车侧边栏 -->
    <div class="cart-sidebar" :class="{ 'cart-open': isCartOpen, 'fade-in-fixed': !showWelcome }">
      <div class="cart-toggle" @click="toggleCart">
        <el-icon size="20"><ShoppingCartIcon /></el-icon>
        <span class="cart-badge" v-if="cartItemCount > 0">{{ cartItemCount }}</span>
      </div>
      <div class="cart-content">
        <ShoppingCart />
      </div>
    </div>

    <!-- 回到顶部按钮 - 赛博朋克风格 -->
    <div
      v-show="!showWelcome"
      class="back-to-top"
      :class="{ 'show': showBackToTop }"
      @click="scrollToTop"
      title="返回顶部"
    >
      <div class="back-to-top-icon">
        <el-icon size="24"><ArrowUp /></el-icon>
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2025 科技书城. 让阅读更简单</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ShoppingCart as ShoppingCartIcon, ArrowUp, Search, User, ArrowDown, Tickets, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import CardContainer from './CardContainer.vue'
import ShoppingCart from './ShoppingCart.vue'

const router = useRouter()
const isCartOpen = ref(false)
const cartItemCount = ref(0)
const showBackToTop = ref(false)
const isNavbarFixed = ref(false)
const showNavbarAnimation = ref(false)
const lastScrollY = ref(0)
const searchQuery = ref('')
const isLoggedIn = ref(false)
const username = ref('')
const showWelcome = ref(true)
const welcomeAnimating = ref(false)
const canvasContainer = ref<HTMLDivElement | null>(null)

// 检查登录状态
const checkLoginStatus = () => {
  const loginStatus = localStorage.getItem('isLoggedIn')
  const storedUsername = localStorage.getItem('username')

  isLoggedIn.value = loginStatus === 'true'
  username.value = storedUsername || ''

  // 如果已登录，触发购物车加载
  if (isLoggedIn.value) {
    const event = new CustomEvent('user-login')
    window.dispatchEvent(event)
  }
}

const goToLogin = () => {
  router.push('/login')
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

      // 清除登录信息
      localStorage.removeItem('token')
      localStorage.removeItem('user_id')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
      localStorage.removeItem('isLoggedIn')

      // 更新状态
      isLoggedIn.value = false
      username.value = ''

      // 触发登出事件
      const event = new CustomEvent('user-logout')
      window.dispatchEvent(event)

      ElMessage.success('已退出登录')
    } catch (error) {
      // 用户取消
    }
  } else if (command === 'orders') {
    ElMessage.info('订单页面开发中...')
  }
}

const toggleCart = () => {
  isCartOpen.value = !isCartOpen.value
}

const updateCartCount = (event: CustomEvent) => {
  // 使用事件详情中的count值，而不是从localStorage读取
  if (event.detail && typeof event.detail.count !== 'undefined') {
    cartItemCount.value = event.detail.count
  } else {
    // 回退方案：从localStorage读取
    const cartData = JSON.parse(localStorage.getItem('cart') || '[]')
    cartItemCount.value = cartData.length
  }
}

const handleAddToCart = (event: CustomEvent) => {
  // 不再直接增加数量，因为cart-updated事件会处理正确的数量更新
  // cartItemCount.value++
}

const scrollToTop = () => {
  // 使用更高级的缓动函数实现更丝滑的滚动效果
  const scrollDuration = 1000;
  const startScrollTop = window.scrollY;
  const startTime = performance.now();

  // 使用easeOutCubic缓动函数
  const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);

  const scrollAnimation = (currentTime: number) => {
    const elapsedTime = currentTime - startTime;
    const progress = Math.min(elapsedTime / scrollDuration, 1);
    const easeProgress = easeOutCubic(progress);

    window.scrollTo(0, startScrollTop * (1 - easeProgress));

    if (progress < 1) {
      requestAnimationFrame(scrollAnimation);
    }
  };

  requestAnimationFrame(scrollAnimation);
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // 创建自定义事件，将搜索查询传递给CardContainer
    const searchEvent = new CustomEvent('book-search', {
      detail: { query: searchQuery.value.trim() }
    })
    window.dispatchEvent(searchEvent)
  }
}

const handleScroll = () => {
  const currentScrollY = window.scrollY
  showBackToTop.value = currentScrollY > 300

  // 判断滚动方向
  const isScrollingDown = currentScrollY > lastScrollY.value

  // 滚动超过100px时固定导航栏
  if (currentScrollY > 100) {
    // 如果是从未固定状态变为固定状态，且是向下滚动，显示动画
    if (!isNavbarFixed.value && isScrollingDown) {
      showNavbarAnimation.value = true
    }
    isNavbarFixed.value = true
  } else {
    isNavbarFixed.value = false
    showNavbarAnimation.value = false
  }

  lastScrollY.value = currentScrollY
}

// 监听登录事件
const handleLoginSuccess = () => {
  checkLoginStatus()
}

// 动态粒子背景相关逻辑
let animationId: number | null = null
let particles: Array<any> = []
let mousePosition = { x: 0, y: 0 }
let prevMousePosition = { x: 0, y: 0 }
let mouseVelocity = { x: 0, y: 0 }

// Particle类定义 - 翠绿色主题
class Particle {
  x: number
  y: number
  size: number
  baseSize: number
  speedX: number
  speedY: number
  color: string
  canvas: HTMLCanvasElement
  ctx: CanvasRenderingContext2D
  opacity: number
  maxOpacity: number
  minOpacity: number
  isInteracting: boolean
  forceFactor: number
  maxSizeMultiplier: number

  constructor(canvas: HTMLCanvasElement, ctx: CanvasRenderingContext2D) {
    this.canvas = canvas
    this.ctx = ctx
    this.x = Math.random() * canvas.width
    this.y = Math.random() * canvas.height
    this.size = Math.random() * 3 + 1.5
    this.baseSize = this.size
    this.speedX = (Math.random() - 0.5) * 0.3
    this.speedY = (Math.random() - 0.5) * 0.3
    // 使用翠绿色系
    const colors = ['#10b981', '#34d399', '#6ee7b7', '#059669']
    this.color = colors[Math.floor(Math.random() * colors.length)]
    this.opacity = Math.random() * 0.7 + 0.3
    this.maxOpacity = 1
    this.minOpacity = 0.2
    this.isInteracting = false
    this.forceFactor = 0.02
    this.maxSizeMultiplier = 1.8
  }

  update() {
    const dx = this.x - mousePosition.x
    const dy = this.y - mousePosition.y
    const distanceToMouse = Math.sqrt(dx * dx + dy * dy)

    if (distanceToMouse < 150) {
      this.isInteracting = true
      this.opacity = this.maxOpacity * (1 - distanceToMouse / 150)
      const sizeMultiplier = 1 + (this.maxSizeMultiplier - 1) * (1 - distanceToMouse / 150)
      this.size = this.baseSize * sizeMultiplier

      const angle = Math.atan2(dy, dx)
      const force = (1 - distanceToMouse / 150) * this.forceFactor
      this.speedX += Math.cos(angle) * force
      this.speedY += Math.sin(angle) * force

      if (Math.abs(mouseVelocity.x) > 0.1 || Math.abs(mouseVelocity.y) > 0.1) {
        this.speedX += mouseVelocity.x * 0.001
        this.speedY += mouseVelocity.y * 0.001
      }
    } else {
      if (this.isInteracting) {
        this.isInteracting = false
      }

      if (this.opacity > this.minOpacity) {
        this.opacity -= 0.02
      } else {
        this.opacity = this.minOpacity
      }

      if (this.size > this.baseSize) {
        this.size = Math.max(this.baseSize, this.size - 0.05)
      }
    }

    const maxSpeed = 0.8
    const speed = Math.sqrt(this.speedX * this.speedX + this.speedY * this.speedY)
    if (speed > maxSpeed) {
      this.speedX = (this.speedX / speed) * maxSpeed
      this.speedY = (this.speedY / speed) * maxSpeed
    }

    this.x += this.speedX
    this.y += this.speedY

    if (this.x < 0 || this.x > this.canvas.width) {
      this.speedX *= -0.8
      this.x = Math.max(0, Math.min(this.canvas.width, this.x))
    }
    if (this.y < 0 || this.y > this.canvas.height) {
      this.speedY *= -0.8
      this.y = Math.max(0, Math.min(this.canvas.height, this.y))
    }

    this.draw()
  }

  draw() {
    this.ctx.fillStyle = this.color
    this.ctx.globalAlpha = this.opacity
    this.ctx.beginPath()
    this.ctx.arc(this.x, this.y, this.size / 2, 0, Math.PI * 2)
    this.ctx.fill()
    this.ctx.globalAlpha = 1
  }
}

// 连接靠近的粒子，创建网格效果
function connectParticles(ctx: CanvasRenderingContext2D) {
  const maxDistance = 150

  for (let a = 0; a < particles.length; a++) {
    for (let b = a; b < particles.length; b++) {
      const dx = particles[a].x - particles[b].x
      const dy = particles[a].y - particles[b].y
      const distance = Math.sqrt(dx * dx + dy * dy)

      if (distance < maxDistance) {
        const opacity = 1 - distance / maxDistance
        ctx.strokeStyle = `rgba(16, 185, 129, ${opacity * 0.5})`
        ctx.lineWidth = 0.7
        ctx.beginPath()
        ctx.moveTo(particles[a].x, particles[a].y)
        ctx.lineTo(particles[b].x, particles[b].y)
        ctx.stroke()
      }
    }
  }
}

function initCanvas() {
  if (!canvasContainer.value) return

  canvasContainer.value.innerHTML = ''

  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  canvas.className = 'dynamic-bg-canvas'
  canvasContainer.value.appendChild(canvas)

  canvas.addEventListener('mousemove', (e) => {
    mouseVelocity.x = e.clientX - prevMousePosition.x
    mouseVelocity.y = e.clientY - prevMousePosition.y

    prevMousePosition.x = mousePosition.x
    prevMousePosition.y = mousePosition.y
    mousePosition.x = e.clientX
    mousePosition.y = e.clientY
  })

  mousePosition.x = canvas.width / 2
  mousePosition.y = canvas.height / 2

  particles = []
  const particleCount = Math.floor((window.innerWidth * window.innerHeight) / 5000)
  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle(canvas, ctx))
  }

  function animate() {
    if (!ctx) return
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    particles.forEach(particle => particle.update())
    connectParticles(ctx)

    animationId = requestAnimationFrame(animate)
  }

  animate()
}

function handleResize() {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  initCanvas()
}

onMounted(() => {
  initCanvas()
  window.addEventListener('resize', handleResize)
  window.addEventListener('cart-updated', updateCartCount as EventListener)
  window.addEventListener('add-to-cart', handleAddToCart as EventListener)
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('login-success', handleLoginSuccess as EventListener)

  // 初始检查登录状态
  checkLoginStatus()

  // 检查是否已登录，已登录则跳过欢迎动画
  const loginStatus = localStorage.getItem('isLoggedIn')
  if (loginStatus === 'true') {
    // 已登录，直接显示主页内容
    showWelcome.value = false
  } else {
    // 未登录，显示欢迎动画
    // 1. 显示欢迎文字 1秒
    setTimeout(() => {
      // 2. 开始向上飞出动画
      welcomeAnimating.value = true
    }, 1000)

    // 3. 飞出动画完成后隐藏欢迎屏幕，主页内容开始淡入
    setTimeout(() => {
      showWelcome.value = false
    }, 2000)
  }

})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('cart-updated', updateCartCount as EventListener)
  window.removeEventListener('add-to-cart', handleAddToCart as EventListener)
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('login-success', handleLoginSuccess as EventListener)
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #000000;
  position: relative;
  overflow-x: hidden;
}

/* 欢迎屏幕 */
.welcome-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: #000000;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  overflow: hidden;
}

.welcome-text {
  font-size: 48px;
  font-weight: 700;
  color: #10b981;
  text-shadow: 0 0 40px rgba(16, 185, 129, 0.5);
  animation: welcome-fade-in 1s ease-out;
}

/* 欢迎文字淡入动画 */
@keyframes welcome-fade-in {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* 文字向上飞出动画 */
.welcome-text.fly-out {
  animation: fly-out-up 1s ease-in forwards;
}

@keyframes fly-out-up {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-100vh) scale(0.5);
  }
}

/* 主页内容淡入动画 */
.fade-in {
  animation: fade-in-content 0.8s ease-out forwards;
  opacity: 0;
}

@keyframes fade-in-content {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 依次淡入的延迟效果 */
.fade-in-delay-1 {
  animation-delay: 0.1s;
}

.fade-in-delay-2 {
  animation-delay: 0.3s;
}

.fade-in-delay-3 {
  animation-delay: 0.5s;
}

/* fixed元素的淡入动画（不使用transform以保持定位） */
.fade-in-fixed {
  animation: fade-in-fixed-content 0.8s ease-out 0.5s forwards;
  opacity: 0;
}

@keyframes fade-in-fixed-content {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

/* 动态粒子背景 */
.dynamic-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #000000;
  z-index: 0;
  overflow: hidden;
}

.canvas-container {
  width: 100%;
  height: 100%;
}

.dynamic-bg-canvas {
  display: block;
  width: 100%;
  height: 100%;
}

/* 导航栏 */
.navbar {
  position: relative;
  z-index: 100;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(16, 185, 129, 0.1);
  transition: all 0.3s ease;
}

/* 固定导航栏 */
.navbar-fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(30px);
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.2);
}

/* 导航栏下滑动画 */
.navbar-slide-down {
  animation: slideDown 0.3s ease forwards;
}

@keyframes slideDown {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 导航栏占位符 */
.navbar-placeholder {
  height: 80px;
  width: 100%;
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
}

.logo {
  cursor: pointer;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-text {
  font-size: 28px;
  font-weight: 900;
  color: #10b981;
  text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
}

.nav-search {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex: 1;
  max-width: 450px;
  margin: 0 1.5rem;
  position: relative;
}

.search-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 8px;
  padding: 0 1rem;
  height: 38px;
  color: #fff;
  font-size: 14px;
  transition: all 0.3s ease;
}

.search-input:hover {
  border-color: rgba(16, 185, 129, 0.4);
  transform: translateY(-0.5px);
}

.search-input:focus-within {
  border-color: #10b981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1);
}

.search-input :deep(.el-input__wrapper) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}

.search-input :deep(.el-input__inner) {
  color: #fff;
  font-size: 14px;
  height: 100%;
  line-height: 38px;
}

.search-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
}

.search-input :deep(.el-input__prefix) {
  color: rgba(16, 185, 129, 0.7);
  margin-right: 0.4rem;
  font-size: 14px;
}

.search-btn {
  background: #10b981;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1.2rem;
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;
}

.search-btn:hover {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.search-btn:active {
  transform: translateY(0);
}

.login-btn {
  background: #10b981;
  border: none;
  color: white;
  font-weight: 600;
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.login-btn:hover {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(16, 185, 129, 0.3);
}

/* 用户信息样式 */
.user-info {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.5rem 1rem;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-dropdown:hover {
  background: rgba(16, 185, 129, 0.2);
  border-color: #10b981;
  transform: translateY(-1px);
}

.user-icon {
  color: #10b981;
  font-size: 18px;
}

.username {
  font-weight: 600;
  font-size: 14px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.arrow-icon {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  transition: transform 0.3s ease;
}

.user-dropdown:hover .arrow-icon {
  transform: translateY(2px);
}

/* 主要内容 */
.content-wrapper {
  position: relative;
  z-index: 10;
  padding-top: 2rem;
}

/* 英雄区域 */
.hero-section {
  text-align: center;
  padding: 4rem 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 48px;
  font-weight: 800;
  color: white;
  margin: 0 0 1rem 0;
  line-height: 1.2;
}

.hero-subtitle {
  color: #10b981;
}

.hero-description {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.7);
  margin: 1.5rem 0;
  line-height: 1.6;
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 3rem;
  margin-top: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 32px;
  font-weight: 800;
  color: #10b981;
}

.stat-label {
  display: block;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 0.5rem;
}

/* 书籍区域 */
.books-section {
  padding: 2rem 0;
}

/* 购物车侧边栏 */
.cart-sidebar {
  position: fixed;
  top: 50%;
  right: -350px;
  transform: translateY(-50%);
  width: 350px;
  height: 600px;
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 15px 0 0 15px;
  transition: right 0.3s ease;
  z-index: 1000;
}

.cart-sidebar.cart-open {
  right: 0;
}

.cart-toggle {
  position: absolute;
  top: 50%;
  left: -50px;
  transform: translateY(-50%);
  width: 50px;
  height: 50px;
  background: #10b981;
  border: none;
  border-radius: 15px 0 0 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: all 0.3s ease;
}

.cart-toggle:hover {
  background: #059669;
  transform: translateY(-50%) scale(1.05);
}

.cart-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cart-content {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
}

/* 页脚 */
.footer {
  position: relative;
  z-index: 10;
  background: rgba(0, 0, 0, 0.8);
  border-top: 1px solid rgba(16, 185, 129, 0.1);
  margin-top: 4rem;
}

.footer-content {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.5);
}

/* 回到顶部按钮 */
.back-to-top {
  position: fixed;
  bottom: 100px;
  right: 30px;
  width: 56px;
  height: 56px;
  background: #10b981;
  border: 2px solid #10b981;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 99999;
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
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
  background: #059669;
  transform: translateY(-8px);
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4);
}

.back-to-top:active {
  transform: translateY(-4px);
}

.back-to-top-icon {
  font-size: 24px;
  color: #ffffff;
  transition: all 0.3s ease;
}

.back-to-top:hover .back-to-top-icon {
  transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-content {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
  }

  .nav-search {
    max-width: 100%;
    margin: 0 0.8rem;
    order: 2;
    gap: 0.6rem;
  }

  .search-input {
    font-size: 0.85rem;
    height: 36px;
    padding: 0 0.8rem;
  }

  .search-btn {
    padding: 0.4rem 1rem;
    font-size: 13px;
  }

  .search-input :deep(.el-input__inner) {
    font-size: 14px;
  }

  .search-input :deep(.el-input__prefix) {
    font-size: 13px;
  }

  .hero-title {
    font-size: 36px;
  }

  .hero-description {
    font-size: 16px;
  }

  .hero-stats {
    flex-direction: column;
    gap: 1.5rem;
  }

  .cart-sidebar {
    width: 100%;
    right: -100%;
    height: 100vh;
    top: 0;
    transform: none;
    border-radius: 0;
  }

  .cart-sidebar.cart-open {
    right: 0;
  }

  .cart-toggle {
    left: -50px;
    top: 20px;
    transform: none;
    border-radius: 15px;
  }

  .back-to-top {
    bottom: 80px;
    right: 20px;
    width: 48px;
    height: 48px;
  }

  .back-to-top-icon {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 28px;
  }

  .logo-text {
    font-size: 24px;
  }

  .back-to-top {
    bottom: 70px;
    right: 15px;
    width: 44px;
    height: 44px;
  }

  .back-to-top-icon {
    font-size: 18px;
  }
}

</style>