<template>
  <div class="page-container">
    <!-- 顶部导航栏 -->
    <nav v-if="!hideNavbar" class="page-navbar">
      <div class="nav-content">
        <div class="logo" @click="goToHome">
          <span class="logo-text">科技书城</span>
        </div>
        <div class="nav-actions">
          <el-button link @click="goToHome">
            <el-icon><HomeFilled /></el-icon>
            返回首页
          </el-button>
          <div v-if="isLoggedIn" class="user-info">
            <el-dropdown @command="handleUserCommand">
              <span class="user-dropdown">
                <el-icon class="user-icon"><User /></el-icon>
                <span class="username">{{ username }}</span>
                <el-icon class="arrow-icon"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人资料
                  </el-dropdown-item>
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
        </div>
      </div>
    </nav>

    <!-- 主要内容区域 -->
    <div class="page-content" :class="{ 'no-navbar': hideNavbar }">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { HomeFilled, User, ArrowDown, Tickets, SwitchButton } from '@element-plus/icons-vue'

// 定义props
const props = defineProps<{
  hideNavbar?: boolean
}>()

const router = useRouter()
const isLoggedIn = ref(false)
const username = ref('')

// 检查登录状态
const checkLoginStatus = () => {
  const loginStatus = localStorage.getItem('isLoggedIn')
  const storedUsername = localStorage.getItem('username')

  if (loginStatus === 'true' && storedUsername) {
    isLoggedIn.value = true
    username.value = storedUsername
  }
}

// 返回首页
const goToHome = () => {
  router.push('/')
}

// 处理用户下拉菜单命令
const handleUserCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })

      localStorage.removeItem('isLoggedIn')
      localStorage.removeItem('username')
      localStorage.removeItem('user_id')
      localStorage.removeItem('token')

      isLoggedIn.value = false
      username.value = ''

      ElMessage.success('已退出登录')
      router.push('/login')
    } catch (error) {
      // 用户取消
    }
  } else if (command === 'orders') {
    router.push('/profile')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}

onMounted(() => {
  checkLoginStatus()
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #f5f5f7;
}

/* 顶部导航栏 - iOS风格 */
.page-navbar {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.logo:hover {
  transform: scale(1.02);
}

.logo-text {
  font-size: 22px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.5px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 返回首页按钮 - iOS风格 */
.nav-actions :deep(.el-button) {
  padding: 8px 16px;
  border-radius: 12px;
  font-weight: 500;
  font-size: 14px;
  color: #007aff;
  background: rgba(0, 122, 255, 0.08);
  border: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-actions :deep(.el-button:hover) {
  background: rgba(0, 122, 255, 0.15);
  transform: translateY(-1px);
}

.nav-actions :deep(.el-icon) {
  font-size: 16px;
}

.user-info {
  margin-left: 8px;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.03);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.user-dropdown:hover {
  background: rgba(0, 0, 0, 0.06);
  transform: scale(1.02);
}

.user-icon {
  font-size: 18px;
  color: #007aff;
}

.username {
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.2px;
}

.arrow-icon {
  font-size: 12px;
  color: #6e6e73;
}

/* 下拉菜单 - iOS风格 */
.user-info :deep(.el-dropdown-menu) {
  border-radius: 14px;
  border: 0.5px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: 6px;
  margin-top: 8px;
}

.user-info :deep(.el-dropdown-menu__item) {
  border-radius: 10px;
  padding: 10px 16px;
  margin: 2px 0;
  font-size: 14px;
  font-weight: 500;
  color: #1d1d1f;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.user-info :deep(.el-dropdown-menu__item:hover) {
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
}

.user-info :deep(.el-dropdown-menu__item.is-disabled) {
  color: #c0c4cc;
}

.user-info :deep(.el-dropdown-menu__item--divided) {
  margin-top: 6px;
  border-top: 0.5px solid rgba(0, 0, 0, 0.06);
  padding-top: 10px;
}

.user-info :deep(.el-dropdown-menu__item .el-icon) {
  margin-right: 8px;
  font-size: 16px;
}

/* 主要内容区域 */
.page-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 20px;
  min-height: calc(100vh - 64px);
}

.page-content.no-navbar {
  min-height: 100vh;
  padding: 0;
}
</style>
