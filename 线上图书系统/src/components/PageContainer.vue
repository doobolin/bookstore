<template>
  <div class="page-container">
    <!-- 顶部导航栏 -->
    <nav class="page-navbar">
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
    <div class="page-content">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { HomeFilled, User, ArrowDown, Tickets, SwitchButton } from '@element-plus/icons-vue'

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
    router.push('/orders')
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
  background: #f5f7fa;
}

/* 顶部导航栏 */
.page-navbar {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  cursor: pointer;
  transition: transform 0.3s;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-text {
  font-size: 20px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info {
  margin-left: 10px;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.3s;
}

.user-dropdown:hover {
  background: #f5f7fa;
}

.user-icon {
  font-size: 18px;
  color: #409eff;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.arrow-icon {
  font-size: 12px;
  color: #909399;
}

/* 主要内容区域 */
.page-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 20px;
  min-height: calc(100vh - 60px);
}
</style>
