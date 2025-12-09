<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { loginUser, checkUserStatus } from '../api/userApi'

const router = useRouter()

// 表单数据
const username = ref('')
const password = ref('')
const loading = ref(false)

// 处理登录
const handleLogin = async () => {
  if (!username.value || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    // 调用登录API
    const response = await loginUser({
      username: username.value,
      password: password.value
    })

    // 检查用户角色 - 只允许普通用户登录
    if (response.role !== 'user') {
      ElMessage.error('管理员请使用后台管理系统登录')
      loading.value = false
      return
    }

    // 检查用户状态 - 只允许活跃用户登录
    // 假设后端返回的数据中包含status字段，如果没有需要额外请求
    // 这里我们需要调用用户状态检查API
    const statusCheck = await checkUserStatus(username.value)

    if (!statusCheck.exists) {
      ElMessage.error('用户不存在')
      loading.value = false
      return
    }

    if (statusCheck.status !== 'active') {
      ElMessage.error('您的账号已被停用，请联系管理员')
      loading.value = false
      return
    }

    // 保存登录信息到localStorage
    localStorage.setItem('token', response.token)
    localStorage.setItem('user_id', response.user_id.toString())
    localStorage.setItem('username', response.username)
    localStorage.setItem('role', response.role)
    localStorage.setItem('isLoggedIn', 'true')

    ElMessage.success('登录成功')

    // 触发登录成功事件
    const loginSuccessEvent = new CustomEvent('login-success')
    window.dispatchEvent(loginSuccessEvent)

    // 登录成功后跳转到主页
    router.push('/')
  } catch (error: any) {
    console.error('登录失败:', error)
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('登录失败，请检查用户名和密码')
    }
  } finally {
    loading.value = false
  }
}

// 处理注册
const handleRegister = () => {
  router.push('/register')
}
</script>

<template>
  <div class="login-container">
    <!-- 动态背景光球 -->
    <div class="mesh-gradients">
      <div class="gradient-blob blob-1"></div>
      <div class="gradient-blob blob-2"></div>
      <div class="gradient-blob blob-3"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">
          <i class="ri-book-3-fill"></i>
        </div>
        <h2>线上书店</h2>
        <p class="login-subtitle">登录您的账户</p>
      </div>
      <div class="login-form">
        <el-form :model="{
          username: username,
          password: password
        }" label-width="0">
          <el-form-item>
            <div class="input-group">
              <label class="input-label">用户名</label>
              <input
                v-model="username"
                type="text"
                placeholder="请输入用户名"
                class="custom-input"
                @keyup.enter="handleLogin"
              />
            </div>
          </el-form-item>
          <el-form-item>
            <div class="input-group">
              <label class="input-label">密码</label>
              <input
                v-model="password"
                type="password"
                placeholder="请输入密码"
                class="custom-input"
                @keyup.enter="handleLogin"
              />
            </div>
          </el-form-item>
          <el-form-item class="button-wrapper">
            <button
              class="login-btn"
              @click="handleLogin"
              :disabled="loading"
              type="button"
            >
              {{ loading ? '登录中...' : '登录' }}
            </button>
          </el-form-item>
          <div class="register-link">
            <span>还没有账户？</span>
            <button class="link-btn" @click="handleRegister" type="button">立即注册</button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 引入 Remix Icon */
@import url('https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css');
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: #F5F5F7;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* 动态背景光球 */
.mesh-gradients {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.gradient-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
  animation: blob-move 20s ease-in-out infinite;
}

.blob-1 {
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  top: -10%;
  left: -10%;
  animation-delay: 0s;
}

.blob-2 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  top: 60%;
  right: -5%;
  animation-delay: 4s;
}

.blob-3 {
  width: 550px;
  height: 550px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  bottom: -10%;
  left: 40%;
  animation-delay: 2s;
}

@keyframes blob-move {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

/* 登录卡片样式 */
.login-card {
  width: 100%;
  max-width: 440px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 32px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
  padding: 48px 40px;
  border: 1px solid white;
  z-index: 10;
  position: relative;
  margin: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  width: 72px;
  height: 72px;
  background: #007AFF;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-size: 36px;
  color: white;
}

.login-header h2 {
  margin: 0 0 8px 0;
  color: #1D1D1F;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.login-subtitle {
  margin: 0;
  color: #86868B;
  font-size: 15px;
  font-weight: 400;
}

.login-form {
  width: 100%;
}

.input-group {
  margin-bottom: 16px;
}

.input-label {
  display: block;
  color: #1D1D1F;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
}

.custom-input {
  width: 100%;
  height: 50px;
  padding: 0 16px;
  background: white;
  border: 1.5px solid #E5E5E7;
  border-radius: 14px;
  font-size: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', Roboto, sans-serif;
  color: #1D1D1F;
  outline: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.custom-input::placeholder {
  color: #86868B;
  font-weight: 400;
}

.custom-input:hover {
  border-color: #007AFF;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.12);
}

.custom-input:focus {
  border-color: #007AFF;
  box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
  background: white;
}

.custom-input:disabled {
  background: #F5F5F7;
  cursor: not-allowed;
  opacity: 0.6;
}

.button-wrapper {
  margin-bottom: 0;
  margin-top: 24px;
}

.login-btn {
  width: 100%;
  padding: 14px;
  background: #000000;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.login-btn:hover:not(:disabled) {
  background: #2c2c2e;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.register-link {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: #86868B;
}

.link-btn {
  background: none;
  border: none;
  color: #007AFF;
  font-weight: 600;
  cursor: pointer;
  margin-left: 4px;
  transition: opacity 0.2s ease;
}

.link-btn:hover {
  opacity: 0.7;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    padding: 32px 24px;
    margin: 16px;
    border-radius: 24px;
  }

  .logo-icon {
    width: 64px;
    height: 64px;
    font-size: 32px;
  }

  .login-header h2 {
    font-size: 24px;
  }

  .login-subtitle {
    font-size: 14px;
  }

  .input-label {
    font-size: 13px;
  }

  .ios-input :deep(.el-input__inner) {
    font-size: 16px;
    padding: 0 14px;
  }
}
</style>