<template>
  <div class="home-container">
    <!-- 欢迎屏幕 -->
    <div v-if="showWelcome" class="welcome-screen">
      <h1 class="welcome-text" :class="{ 'fly-out': welcomeAnimating }">
        欢迎来到科技书城
      </h1>
    </div>

    <!-- 赛博朋克背景 -->
    <div class="cyber-background">
      <!-- 网格线背景 -->
      <div class="grid-lines">
        <div class="grid-line horizontal" v-for="i in 20" :key="`h-${i}`"></div>
        <div class="grid-line vertical" v-for="i in 20" :key="`v-${i}`"></div>
      </div>
      
      <!-- 霓虹光效 -->
      <div class="neon-lights">
        <div class="neon neon-1"></div>
        <div class="neon neon-2"></div>
        <div class="neon neon-3"></div>
        <div class="neon neon-4"></div>
      </div>
      
      <!-- 简化的数字雨 -->
      <div class="matrix-rain-simple">
        <div v-for="i in 15" :key="i" class="rain-column-simple" :style="{ left: `${i * 6.66}%`, animationDelay: `${i * 0.3}s` }">
          <span v-for="j in 8" :key="j" class="matrix-dot"></span>
        </div>
      </div>

      <!-- 故障效果 -->
      <div class="glitch-overlay"></div>
    </div>
    
    <!-- 导航栏 -->
    <nav class="navbar" :class="{ 'fade-in': !showWelcome, 'fade-in-delay-1': !showWelcome }">
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
const searchQuery = ref('')
const isLoggedIn = ref(false)
const username = ref('')
const showWelcome = ref(true)
const welcomeAnimating = ref(false)

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
  showBackToTop.value = window.scrollY > 300
}

// 监听登录事件
const handleLoginSuccess = () => {
  checkLoginStatus()
}

onMounted(() => {
  window.addEventListener('cart-updated', updateCartCount as EventListener)
  window.addEventListener('add-to-cart', handleAddToCart as EventListener)
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('login-success', handleLoginSuccess as EventListener)

  // 初始检查登录状态
  checkLoginStatus()

  // 欢迎动画时序控制
  // 1. 显示欢迎文字 1秒
  setTimeout(() => {
    // 2. 开始向上飞出动画
    welcomeAnimating.value = true
  }, 1000)

  // 3. 飞出动画完成后隐藏欢迎屏幕，主页内容开始淡入
  setTimeout(() => {
    showWelcome.value = false
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('cart-updated', updateCartCount as EventListener)
  window.removeEventListener('add-to-cart', handleAddToCart as EventListener)
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('login-success', handleLoginSuccess as EventListener)
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a0033 50%, #330066 100%);
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
  background: linear-gradient(135deg, #0a0a0a 0%, #1a0033 50%, #330066 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  overflow: hidden;
}

.welcome-text {
  font-size: 48px;
  font-weight: 700;
  background: linear-gradient(135deg, #00ffff, #ff00ff, #ffff00);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 40px rgba(0, 255, 255, 0.5);
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

/* 赛博朋克背景 */
.cyber-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a0033 50%, #330066 100%);
  overflow: hidden;
  z-index: 0;
  pointer-events: none;
}

/* 网格线背景 */
.grid-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.3;
}

.grid-line {
  position: absolute;
  background: linear-gradient(90deg, transparent, #00ffff, transparent);
}

.grid-line.horizontal {
  width: 100%;
  height: 1px;
}

.grid-line.vertical {
  width: 1px;
  height: 100%;
  background: linear-gradient(180deg, transparent, #ff00ff, transparent);
}

/* 霓虹灯效果 */
.neon-lights {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.neon {
  position: absolute;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.6;
  animation: neon-pulse 4s ease-in-out infinite;
}

.neon-1 {
  width: 300px;
  height: 300px;
  background: #00ffff;
  top: 10%;
  left: 20%;
  animation-delay: 0s;
}

.neon-2 {
  width: 250px;
  height: 250px;
  background: #ff00ff;
  top: 60%;
  right: 15%;
  animation-delay: 1s;
}

.neon-3 {
  width: 200px;
  height: 200px;
  background: #ffff00;
  bottom: 20%;
  left: 40%;
  animation-delay: 2s;
}

.neon-4 {
  width: 350px;
  height: 350px;
  background: #ff0066;
  top: 30%;
  right: 30%;
  animation-delay: 3s;
}

@keyframes neon-pulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.1); }
}

/* 简化的数字雨 */
.matrix-rain-simple {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.3;
}

.rain-column-simple {
  position: absolute;
  top: 0;
  width: 10px;
  height: 100%;
  animation: matrix-fall-simple 12s linear infinite;
}

.matrix-dot {
  display: block;
  width: 2px;
  height: 2px;
  background: #00ff00;
  margin: 8px 0;
  border-radius: 50%;
  opacity: 0.6;
  animation: dot-glow 2s ease-in-out infinite;
}

@keyframes matrix-fall-simple {
  0% { transform: translateY(-100vh); }
  100% { transform: translateY(100vh); }
}

@keyframes dot-glow {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.8; }
}

/* 故障效果 */
.glitch-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 255, 255, 0.03) 2px,
    rgba(0, 255, 255, 0.03) 4px
  );
  animation: glitch 0.5s infinite;
}

@keyframes glitch {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-2px); }
  40% { transform: translateX(2px); }
  60% { transform: translateX(-1px); }
  80% { transform: translateX(1px); }
}

/* 导航栏 */
.navbar {
  position: relative;
  z-index: 100;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 255, 255, 0.2);
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
  background: linear-gradient(135deg, #00ffff, #ff00ff, #00ffff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
  animation: logo-glow 2s ease-in-out infinite alternate;
}

@keyframes logo-glow {
  0% { text-shadow: 0 0 20px rgba(0, 255, 255, 0.5); }
  100% { text-shadow: 0 0 30px rgba(255, 0, 255, 0.7); }
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
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 20px;
  padding: 0 1rem;
  height: 38px;
  color: #fff;
  font-size: 14px;
  backdrop-filter: blur(15px);
  transition: all 0.3s ease;
  box-shadow: 
    0 0 5px rgba(0, 255, 255, 0.1);
}

.search-input:hover {
  box-shadow: 
    0 0 8px rgba(0, 255, 255, 0.2);
  transform: translateY(-0.5px);
}

.search-input:focus-within {
  box-shadow: 
    0 0 12px rgba(0, 255, 255, 0.3);
  transform: translateY(-1px);
  border-color: rgba(0, 255, 255, 0.6);
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
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
}

.search-input :deep(.el-input__prefix) {
  color: rgba(0, 255, 255, 0.7);
  margin-right: 0.4rem;
  font-size: 14px;
}



.search-btn {
  background: rgba(0, 255, 255, 0.15);
  border: 1px solid rgba(0, 255, 255, 0.4);
  border-radius: 20px;
  padding: 0.5rem 1.2rem;
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 
    0 0 5px rgba(0, 255, 255, 0.2);
  position: relative;
}



.search-btn:hover {
  transform: translateY(-1px) scale(1.03);
  box-shadow: 
    0 4px 10px rgba(0, 255, 255, 0.3);
  background: rgba(0, 255, 255, 0.25);
}

.search-btn:active {
  transform: translateY(0);
  box-shadow: 
    0 2px 5px rgba(0, 255, 255, 0.2);
}



@keyframes neon-pulse {
  0%, 100% { 
    box-shadow: 
      0 0 20px rgba(0, 255, 255, 0.5),
      inset 0 0 20px rgba(255, 255, 255, 0.2);
  }
  50% { 
    box-shadow: 
      0 0 40px rgba(255, 0, 255, 0.8),
      inset 0 0 30px rgba(255, 255, 255, 0.4);
  }
}



.login-btn {
  background: linear-gradient(135deg, #00ffff, #ff00ff);
  border: none;
  color: white;
  font-weight: 600;
  padding: 0.5rem 1.5rem;
  border-radius: 25px;
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 255, 255, 0.3);
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
  background: rgba(0, 255, 255, 0.1);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 25px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-dropdown:hover {
  background: rgba(0, 255, 255, 0.2);
  border-color: rgba(0, 255, 255, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(0, 255, 255, 0.2);
}

.user-icon {
  color: #00ffff;
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
  text-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
}

.hero-subtitle {
  background: linear-gradient(135deg, #00ffff, #ff00ff, #00ffff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: subtitle-breathe 3s ease-in-out infinite;
}

@keyframes subtitle-breathe {
  0%, 100% { opacity: 0.8; }
  50% { opacity: 1; }
}

.hero-description {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.8);
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
  background: linear-gradient(135deg, #00ffff, #ff00ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
}

.stat-label {
  display: block;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
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
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid rgba(0, 255, 255, 0.3);
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
  background: linear-gradient(135deg, #00ffff, #ff00ff);
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
  transform: translateY(-50%) scale(1.05);
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
}

.cart-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff00ff;
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
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(0, 255, 255, 0.2);
  margin-top: 4rem;
}

.footer-content {
  text-align: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.7);
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
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 28px;
  }
  
  .logo-text {
    font-size: 24px;
  }
  
  .nav-links {
    font-size: 14px;
  }
}

/* 回到顶部按钮 - 赛博朋克风格升级版 */
.back-to-top {
  position: fixed;
  bottom: 100px;
  right: 30px;
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #00ffff, #ff00ff, #00ffff);
  border: 2px solid rgba(0, 255, 255, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 99999;
  color: white;
  box-shadow: 
    0 0 20px rgba(0, 255, 255, 0.4),
    0 0 40px rgba(255, 0, 255, 0.2),
    inset 0 0 20px rgba(0, 255, 255, 0.1);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  opacity: 0;
  transform: translateY(30px) rotate(180deg);
  pointer-events: none;
  overflow: hidden;
}

.back-to-top::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent,
    rgba(255, 255, 255, 0.1),
    transparent
  );
  transform: rotate(45deg);
  transition: all 0.6s ease;
  opacity: 0;
}

.back-to-top:hover::before {
  opacity: 1;
  transform: rotate(45deg) translateX(100%);
}

.back-to-top.show {
  opacity: 1;
  transform: translateY(0) rotate(0deg);
  pointer-events: auto;
}

.back-to-top:hover {
  transform: translateY(-8px) scale(1.15);
  box-shadow: 
    0 0 30px rgba(0, 255, 255, 0.8),
    0 0 60px rgba(255, 0, 255, 0.4),
    inset 0 0 30px rgba(0, 255, 255, 0.2);
  border-color: rgba(0, 255, 255, 1);
}

.back-to-top:active {
  transform: translateY(-4px) scale(1.05);
}

.back-to-top-icon {
  font-size: 24px;
  color: #ffffff;
  filter: drop-shadow(0 0 5px rgba(255, 255, 255, 0.8));
  transition: all 0.3s ease;
}

.back-to-top:hover .back-to-top-icon {
  transform: translateY(-2px);
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 1));
}

/* 脉冲动画效果 */
.back-to-top.show {
  animation: cyber-pulse 2s ease-in-out infinite;
}

@keyframes cyber-pulse {
  0%, 100% {
    box-shadow: 
      0 0 20px rgba(0, 255, 255, 0.4),
      0 0 40px rgba(255, 0, 255, 0.2),
      inset 0 0 20px rgba(0, 255, 255, 0.1);
  }
  50% {
    box-shadow: 
      0 0 30px rgba(0, 255, 255, 0.6),
      0 0 60px rgba(255, 0, 255, 0.4),
      inset 0 0 30px rgba(0, 255, 255, 0.2);
  }
}

/* 数字雨效果 */
.back-to-top::after {
  content: '↑';
  position: absolute;
  font-size: 12px;
  color: rgba(0, 255, 255, 0.6);
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  opacity: 0;
  transition: all 0.3s ease;
}

.back-to-top:hover::after {
  opacity: 1;
  top: -15px;
}

/* 移动端适配 */
@media (max-width: 768px) {
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