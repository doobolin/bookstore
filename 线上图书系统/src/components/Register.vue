<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { registerUser } from '../api/userApi'

const router = useRouter()

// 表单数据
const formData = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})
const loading = ref(false)

// 处理注册
const handleRegister = async () => {
  // 表单验证
  if (!formData.value.username || !formData.value.email || !formData.value.password || !formData.value.confirmPassword) {
    ElMessage.warning('请填写完整的注册信息')
    return
  }

  // 验证邮箱格式
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(formData.value.email)) {
    ElMessage.warning('请输入有效的邮箱地址')
    return
  }

  // 验证密码长度
  if (formData.value.password.length < 6) {
    ElMessage.warning('密码长度至少为6位')
    return
  }

  // 验证两次密码是否一致
  if (formData.value.password !== formData.value.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    // 调用注册API
    await registerUser({
      username: formData.value.username,
      email: formData.value.email,
      password: formData.value.password
    })

    ElMessage.success('注册成功！请登录')

    // 延迟跳转到登录页面
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (error: any) {
    console.error('注册失败:', error)
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('注册失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

// 跳转到登录页面
const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="register-container">
    <!-- 动态背景光球 -->
    <div class="mesh-gradients">
      <div class="gradient-blob blob-1"></div>
      <div class="gradient-blob blob-2"></div>
      <div class="gradient-blob blob-3"></div>
    </div>

    <!-- 注册卡片 -->
    <div class="register-card">
      <div class="register-header">
        <div class="logo-icon">
          <i class="ri-book-3-fill"></i>
        </div>
        <h2>线上书店</h2>
        <p class="register-subtitle">创建您的账户</p>
      </div>
      <div class="register-form">
        <el-form :model="formData" label-width="0">
          <el-form-item>
            <div class="input-group">
              <label class="input-label">用户名</label>
              <input
                v-model="formData.username"
                type="text"
                placeholder="请输入用户名"
                class="custom-input"
                @keyup.enter="handleRegister"
              />
            </div>
          </el-form-item>
          <el-form-item>
            <div class="input-group">
              <label class="input-label">邮箱地址</label>
              <input
                v-model="formData.email"
                type="email"
                placeholder="请输入邮箱地址"
                class="custom-input"
                @keyup.enter="handleRegister"
              />
            </div>
          </el-form-item>
          <el-form-item>
            <div class="input-group">
              <label class="input-label">密码</label>
              <input
                v-model="formData.password"
                type="password"
                placeholder="请设置密码（至少6位）"
                class="custom-input"
                @keyup.enter="handleRegister"
              />
            </div>
          </el-form-item>
          <el-form-item>
            <div class="input-group">
              <label class="input-label">确认密码</label>
              <input
                v-model="formData.confirmPassword"
                type="password"
                placeholder="请再次输入密码"
                class="custom-input"
                @keyup.enter="handleRegister"
              />
            </div>
          </el-form-item>
          <el-form-item class="button-wrapper">
            <button
              class="register-btn"
              @click="handleRegister"
              :disabled="loading"
              type="button"
            >
              {{ loading ? '注册中...' : '注册' }}
            </button>
          </el-form-item>
          <div class="login-link">
            <span>已有账户？</span>
            <button class="link-btn" @click="goToLogin" type="button">立即登录</button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 引入 Remix Icon */
@import url('https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css');

.register-container {
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

/* 注册卡片样式 */
.register-card {
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

.register-header {
  text-align: center;
  margin-bottom: 32px;
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

.register-header h2 {
  margin: 0 0 8px 0;
  color: #1D1D1F;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.register-subtitle {
  margin: 0;
  color: #86868B;
  font-size: 15px;
  font-weight: 400;
}

.register-form {
  width: 100%;
}

.input-group {
  margin-bottom: 14px;
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
  margin-top: 20px;
}

.register-btn {
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

.register-btn:hover:not(:disabled) {
  background: #2c2c2e;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.register-btn:active:not(:disabled) {
  transform: translateY(0);
}

.register-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-link {
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
  .register-card {
    padding: 32px 24px;
    margin: 16px;
    border-radius: 24px;
  }

  .logo-icon {
    width: 64px;
    height: 64px;
    font-size: 32px;
  }

  .register-header {
    margin-bottom: 28px;
  }

  .register-header h2 {
    font-size: 24px;
  }

  .register-subtitle {
    font-size: 14px;
  }

  .input-group {
    margin-bottom: 16px;
  }

  .input-label {
    font-size: 13px;
  }

  .ios-input :deep(.el-input__inner) {
    font-size: 16px;
    padding: 12px 14px;
  }
}
</style>
