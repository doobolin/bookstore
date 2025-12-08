<template>
  <div class="home-container">
    <!-- 侧边导航栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>线上书店管理系统</h2>
      </div>
      <nav class="sidebar-nav">
        <router-link
          to="/home"
          class="nav-item"
          :class="{ active: $route.name === 'home' }"
        >
          <i class="icon-home"></i>
          <span>首页</span>
        </router-link>
        <router-link
          to="/home/book-manage"
          class="nav-item"
          :class="{ active: $route.name === 'bookManage' }"
        >
          <i class="icon-book"></i>
          <span>图书管理</span>
        </router-link>
        <router-link
          to="/home/user-manage"
          class="nav-item"
          :class="{ active: $route.name === 'userManage' }"
        >
          <i class="icon-user"></i>
          <span>用户管理</span>
        </router-link>
        <router-link
          to="/home/order-manage"
          class="nav-item"
          :class="{ active: $route.name === 'orderManage' }"
        >
          <i class="icon-order"></i>
          <span>订单管理</span>
        </router-link>
        <div class="nav-item logout" @click="handleLogout">
          <i class="icon-logout"></i>
          <span>退出登录</span>
        </div>
      </nav>
    </aside>

    <!-- 主内容区域 -->
    <main class="main-content">
      <header class="content-header">
        <h1>{{ getPageTitle() }}</h1>
        <div class="user-info">
          <span>欢迎，管理员</span>
          <span class="current-time">{{ currentTime }}</span>
        </div>
      </header>
      
      <!-- 页面内容切换 -->
      <transition name="slide-fade" mode="out-in">
        <!-- 首页概览内容 - 仅在根路径时显示 -->
        <div v-if="isHomePage" key="dashboard" class="dashboard-content">
        <!-- 统计卡片区域 -->
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon book-icon">📚</div>
            <div class="stat-info">
              <div class="stat-value">{{ totalBooks }}</div>
              <div class="stat-label">图书总数</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon user-icon">👥</div>
            <div class="stat-info">
              <div class="stat-value">{{ totalUsers }}</div>
              <div class="stat-label">用户总数</div>
              <div class="stat-details">
                <span>活跃: {{ activeUsers }}</span>
                <span>禁用: {{ inactiveUsers }}</span>
              </div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon stock-icon">📦</div>
            <div class="stat-info">
              <div class="stat-value">{{ totalStock }}</div>
              <div class="stat-label">库存总量</div>
            </div>
          </div>
        </div>
        
        <!-- 快捷操作区域 -->
        <div class="quick-actions">
          <div class="action-buttons">
            <button class="action-btn" @click="navigateTo('bookManage')">
              <i class="action-icon">📊</i>
              <span>图书总览</span>
            </button>
            <button class="action-btn" @click="navigateTo('userManage')">
              <i class="action-icon">👤</i>
              <span>管理用户</span>
            </button>
            <button class="action-btn" @click="viewLowStock">
              <i class="action-icon">⚠️</i>
              <span>低库存提醒</span>
            </button>
          </div>
        </div>
        
        <!-- 系统通知 -->
        <div class="notifications">
          <div class="notification-list">
            <!-- 新书上架通知 -->
            <div 
              v-for="notification in newBookNotifications" 
              :key="notification.id" 
              class="notification-item new-book"
            >
              <span class="notification-icon">📚</span>
              <span class="notification-content">新书上架: 《{{ notification.title }}》 - {{ notification.author }}</span>
              <span class="notification-time">{{ formatNotificationTime(notification.time) }}</span>
            </div>
            
            <!-- 图书下架通知 -->
            <div 
              v-for="notification in bookRemovedNotifications" 
              :key="notification.id" 
              class="notification-item book-removed"
            >
              <span class="notification-icon">📭</span>
              <span class="notification-content">图书下架: 《{{ notification.title }}》 - {{ notification.author }}</span>
              <span class="notification-time">{{ formatNotificationTime(notification.time) }}</span>
            </div>
            
            <!-- 低库存提醒 -->
            <div v-if="lowStockCount > 0" class="notification-item">
              <span class="notification-icon">⚠️</span>
              <span class="notification-content">有{{ lowStockCount }}本图书库存低于阈值，需要补货</span>
              <span class="notification-time">今天 {{ new Date().getHours() }}:{{ new Date().getMinutes().toString().padStart(2, '0') }}</span>
            </div>
            <div v-else class="notification-item">
              <span class="notification-icon">✅</span>
              <span class="notification-content">当前没有图书需要补货</span>
              <span class="notification-time">今天 {{ new Date().getHours() }}:{{ new Date().getMinutes().toString().padStart(2, '0') }}</span>
            </div>
          </div>
        </div>
        </div>

        <!-- 路由视图内容 -->
        <div v-else :key="$route.fullPath" class="content-wrapper">
          <router-view />
        </div>
      </transition>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUsersCount, type UsersCountResponse } from '../api/userApi'
import { getBooksCount, getLowStockBooks, type BooksCountResponse, type LowStockResponse } from '../api/bookApi'
import { eventBus, EventTypes } from '../utils/eventBus'

const router = useRouter()

// 检查是否在首页根路径
const isHomePage = computed(() => {
  return router.currentRoute.value.path === '/home'
})

// 统计数据
const totalBooks = ref(125)
const totalUsers = ref(0)
const totalStock = ref(1520)

// 用户状态计数
const activeUsers = ref(0)
const inactiveUsers = ref(0)

// 当前时间
const currentTime = ref('')

// 低库存图书数量
const lowStockCount = ref(0)

// 新书上架通知
interface NewBookNotification {
  id: string
  title: string
  author: string
  time: Date
}

const newBookNotifications = ref<NewBookNotification[]>([])

// 图书下架通知
interface BookRemovedNotification {
  id: string
  title: string
  author: string
  time: Date
}

const bookRemovedNotifications = ref<BookRemovedNotification[]>([])

// 根据当前路由获取页面标题
const getPageTitle = () => {
  switch (router.currentRoute.value.name) {
    case 'bookManage':
      return '图书管理'
    case 'userManage':
      return '用户管理'
    case 'orderManage':
      return '订单管理'
    default:
      return '管理首页'
  }
}

// 导航到指定页面
const navigateTo = (routeName: string) => {
  router.push({ name: routeName })
}

// 查看低库存图书
const viewLowStock = () => {
  // 在实际应用中，这里可以添加筛选逻辑
  router.push({ name: 'bookManage', query: { filter: 'lowStock' } })
}

// 退出登录处理
const handleLogout = () => {
  // 清除登录状态
  localStorage.removeItem('isLoggedIn')
  // 跳转到登录页
  router.push({ name: 'login' })
}

// 更新当前时间
  const updateTime = () => {
    const now = new Date()
    currentTime.value = now.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  // 格式化通知时间
  const formatNotificationTime = (time: Date) => {
    const now = new Date()
    const notificationDate = new Date(time)
    const diffInMinutes = Math.floor((now.getTime() - notificationDate.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 1) {
      return '刚刚'
    } else if (diffInMinutes < 60) {
      return `${diffInMinutes}分钟前`
    } else if (diffInMinutes < 1440) {
      const hours = Math.floor(diffInMinutes / 60)
      return `${hours}小时前`
    } else {
      return notificationDate.toLocaleDateString('zh-CN')
    }
  }

// 获取用户总数数据
const fetchUsersCount = async () => {
  try {
    console.log('开始获取用户总数')
    const countData: UsersCountResponse = await getUsersCount()
    totalUsers.value = countData.total
    activeUsers.value = countData.active
    inactiveUsers.value = countData.inactive
    console.log('获取用户总数成功:', countData)
  } catch (error) {
    console.error('获取用户总数失败:', error)
    // 如果获取失败，可以保留现有数据或使用默认值
  }
}

// 获取图书总数数据
const fetchBooksCount = async () => {
  try {
    console.log('开始获取图书总数')
    const countData: BooksCountResponse = await getBooksCount()
    totalBooks.value = countData.total
    totalStock.value = countData.totalStock
    console.log('获取图书总数成功:', countData)
  } catch (error) {
    console.error('获取图书总数失败:', error)
    // 如果获取失败，可以保留现有数据或使用默认值
  }
}

// 获取低库存图书数据
const fetchLowStockBooks = async () => {
  try {
    console.log('开始获取低库存图书')
    const lowStockData: LowStockResponse = await getLowStockBooks()
    lowStockCount.value = lowStockData.total
    console.log('获取低库存图书成功:', lowStockData)
  } catch (error) {
    console.error('获取低库存图书失败:', error)
    // 如果获取失败，保持原值
  }
}

// 生命周期钩子
  onMounted(() => {
    updateTime()
    const timer = setInterval(updateTime, 1000)
    onUnmounted(() => clearInterval(timer))
    
    // 页面加载时获取用户总数、图书总数和低库存图书数量
    if (isHomePage.value) {
      fetchUsersCount()
      fetchBooksCount()
      fetchLowStockBooks()
    }
    
    // 监听路由变化，在切换到首页时重新获取数据
    const routeChangeHandler = () => {
      if (isHomePage.value) {
        fetchUsersCount()
        fetchBooksCount()
        fetchLowStockBooks()
      }
    }
    
    // 监听新书上架事件
    const handleNewBookAdded = (bookData: { title: string, author: string, time: Date }) => {
      const newNotification: NewBookNotification = {
        id: `book-${Date.now()}`,
        title: bookData.title,
        author: bookData.author,
        time: bookData.time
      }
      
      // 添加到通知列表开头
      newBookNotifications.value.unshift(newNotification)
      
      // 限制通知数量，只保留最近5条
      if (newBookNotifications.value.length > 5) {
        newBookNotifications.value = newBookNotifications.value.slice(0, 5)
      }
    }
    
    // 监听图书下架事件
    const handleBookRemoved = (bookData: { title: string, author: string, time: Date }) => {
      const newNotification: BookRemovedNotification = {
        id: `removed-${Date.now()}`,
        title: bookData.title,
        author: bookData.author,
        time: bookData.time
      }
      
      // 添加到通知列表开头
      bookRemovedNotifications.value.unshift(newNotification)
      
      // 限制通知数量，只保留最近5条
      if (bookRemovedNotifications.value.length > 5) {
        bookRemovedNotifications.value = bookRemovedNotifications.value.slice(0, 5)
      }
    }
    
    eventBus.on(EventTypes.NEW_BOOK_ADDED, handleNewBookAdded)
    eventBus.on(EventTypes.BOOK_REMOVED, handleBookRemoved)
    
    const unsubscribe = router.afterEach(routeChangeHandler)
    onUnmounted(() => {
      unsubscribe()
      eventBus.off(EventTypes.NEW_BOOK_ADDED, handleNewBookAdded)
      eventBus.off(EventTypes.BOOK_REMOVED, handleBookRemoved)
    })
  })
</script>

<style scoped lang="scss">
/* iOS风格全局样式 */
* {
  scrollbar-width: thin;
  scrollbar-color: #C7C7CC #f2f2f7;
}

*::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

*::-webkit-scrollbar-track {
  background: transparent;
}

*::-webkit-scrollbar-thumb {
  background: #C7C7CC;
  border-radius: 10px;

  &:hover {
    background: #8E8E93;
  }
}

.home-container {
  display: flex;
  height: 100vh;
  background-color: #F2F2F7;
  color: #1C1C1E;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* 侧边栏样式 - iOS磨砂玻璃效果 */
.sidebar {
  width: 240px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-right: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 20px rgba(0, 0, 0, 0.03);
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid #E5E5EA;
}

.sidebar-header h2 {
  margin: 0;
  color: #34C759;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin: 4px 0;
  color: #8E8E93;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  cursor: pointer;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
}

.nav-item:hover {
  background-color: rgba(52, 199, 89, 0.08);
  color: #34C759;
  transform: translateX(2px);
}

.nav-item.active {
  background-color: #34C759;
  color: white;
  box-shadow: 0 4px 12px rgba(52, 199, 89, 0.3);
}

.nav-item i {
  margin-right: 12px;
  font-size: 18px;
}

.logout {
  margin-top: auto;
  margin-bottom: 12px;
}

.logout:hover {
  color: #FF3B30 !important;
  background-color: rgba(255, 59, 48, 0.08) !important;
}

/* 主内容区域样式 - iOS风格 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #F2F2F7;
}

.content-header {
  padding: 20px 32px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid #E5E5EA;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
}

.content-header h1 {
  margin: 0;
  color: #1C1C1E;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.user-info {
  color: #8E8E93;
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 15px;
  font-weight: 500;
}

.current-time {
  font-size: 14px;
  color: #8E8E93;
  font-weight: 600;
}

/* 首页仪表盘内容 */
.dashboard-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: #F2F2F7;
}

.content-wrapper {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: #F2F2F7;
}

/* 统计卡片样式 - iOS风格 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  font-size: 32px;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(52, 199, 89, 0.1) 0%, rgba(52, 199, 89, 0.05) 100%);
}

.book-icon {
  color: #34C759;
  background: linear-gradient(135deg, rgba(52, 199, 89, 0.15) 0%, rgba(52, 199, 89, 0.08) 100%);
}

.user-icon {
  color: #007AFF;
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.15) 0%, rgba(0, 122, 255, 0.08) 100%);
}

.stock-icon {
  color: #FF9500;
  background: linear-gradient(135deg, rgba(255, 149, 0, 0.15) 0%, rgba(255, 149, 0, 0.08) 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: #1C1C1E;
  margin-bottom: 4px;
  letter-spacing: -0.5px;
}

.stat-label {
  font-size: 14px;
  color: #8E8E93;
  font-weight: 600;
}

.stat-details {
  display: flex;
  gap: 12px;
  margin-top: 8px;
  font-size: 12px;
  font-weight: 600;
}

.stat-details span:first-child {
  color: #34C759;
}

.stat-details span:last-child {
  color: #FF9500;
}

/* 快捷操作区域样式 - iOS风格 */
.quick-actions {
  background: white;
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
}

.quick-actions h3 {
  margin: 0 0 20px 0;
  color: #1C1C1E;
  font-size: 18px;
  font-weight: 700;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.action-btn {
  background: #F9F9F9;
  border: 1px solid #E5E5EA;
  border-radius: 14px;
  padding: 20px;
  color: #1C1C1E;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.action-btn:hover {
  background: white;
  border-color: #34C759;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(52, 199, 89, 0.15);
}

.action-icon {
  font-size: 28px;
}

/* 通知区域样式 - iOS风格 */
.notifications {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
}

.notifications h3 {
  margin: 0 0 20px 0;
  color: #1C1C1E;
  font-size: 18px;
  font-weight: 700;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notification-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #F9F9F9;
  border-radius: 12px;
  border: 1px solid #E5E5EA;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.notification-item.new-book {
  background: rgba(0, 122, 255, 0.06);
  border-color: rgba(0, 122, 255, 0.2);
}

.notification-item.new-book:hover {
  background: rgba(0, 122, 255, 0.1);
  border-color: #007AFF;
  transform: translateX(4px);
}

.notification-item.book-removed {
  background: rgba(255, 59, 48, 0.06);
  border-color: rgba(255, 59, 48, 0.2);
}

.notification-item.book-removed:hover {
  background: rgba(255, 59, 48, 0.1);
  border-color: #FF3B30;
  transform: translateX(4px);
}

.notification-item:hover {
  background: white;
  border-color: #34C759;
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.notification-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  color: #1C1C1E;
  font-size: 14px;
  font-weight: 500;
}

.notification-time {
  font-size: 12px;
  color: #8E8E93;
  flex-shrink: 0;
  font-weight: 600;
}

/* 图标样式（简化版本，实际项目中可使用图标库） */
.icon-home::before {
  content: "🏠";
}

.icon-book::before {
  content: "📚";
}

.icon-user::before {
  content: "👥";
}

.icon-order::before {
  content: "📋";
}

.icon-logout::before {
  content: "🚪";
}

/* 页面切换过渡动画 */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from {
  transform: translateX(20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}
</style>