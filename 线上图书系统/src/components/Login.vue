<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { loginUser, checkUserStatus } from '../api/userApi'

const router = useRouter()

// 表单数据
const username = ref('')
const password = ref('')
const loading = ref(false)
const pixelCanvas = ref<HTMLCanvasElement | null>(null)

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
  console.log('跳转到注册页面')
  router.push('/register')
}

// 初始化像素矩阵动画
const initPixelMatrix = () => {
  if (!pixelCanvas.value) return

  const canvas = pixelCanvas.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const resizeCanvas = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  resizeCanvas()
  window.addEventListener('resize', resizeCanvas)

  const pixelSize = 4
  const spacing = 15
  const cols = Math.ceil(canvas.width / spacing)
  const rows = Math.ceil(canvas.height / spacing)

  interface Pixel {
    x: number
    y: number
    opacity: number
    speed: number
    color: string
    phase: number
  }

  const pixels: Pixel[] = []
  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      if (Math.random() > 0.3) {
        const colors = ['#10b981', '#34d399', '#6ee7b7', '#059669', '#047857', '#666666', '#888888', '#999999']
        pixels.push({
          x: i * spacing,
          y: j * spacing,
          opacity: Math.random() * 0.5 + 0.1,
          speed: Math.random() * 0.02 + 0.005,
          color: colors[Math.floor(Math.random() * colors.length)],
          phase: Math.random() * Math.PI * 2
        })
      }
    }
  }

  let animationId: number
  const animate = () => {
    ctx.fillStyle = '#000000'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    pixels.forEach(pixel => {
      pixel.phase += pixel.speed
      pixel.opacity = Math.sin(pixel.phase) * 0.4 + 0.4

      ctx.fillStyle = pixel.color
      ctx.globalAlpha = pixel.opacity
      ctx.fillRect(pixel.x, pixel.y, pixelSize, pixelSize)
    })

    ctx.globalAlpha = 1
    animationId = requestAnimationFrame(animate)
  }

  animate()

  return () => {
    window.removeEventListener('resize', resizeCanvas)
    cancelAnimationFrame(animationId)
  }
}

onMounted(() => {
  const cleanup = initPixelMatrix()
  return () => {
    if (cleanup) cleanup()
  }
})

</script>

<template>
  <div class="login-container">
    <!-- TRAE 风格像素矩阵背景 -->
    <div class="trae-background">
      <canvas ref="pixelCanvas" class="pixel-matrix"></canvas>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="login-header">
        <h2>用户登录</h2>
        <p class="login-subtitle">欢迎来到科技书城</p>
      </div>
      <div class="login-form">
        <el-form :model="{
          username: username,
          password: password
        }" label-width="0">
          <el-form-item>
            <div class="input-group">
              <label class="input-label">
                <el-icon class="input-icon"><User /></el-icon>
                用户名
              </label>
              <div class="cyber-input-wrapper">
                <el-input 
                  v-model="username" 
                  placeholder="请输入您的用户名"
                  clearable
                  class="cyber-input"
                />
                <div class="input-glow"></div>
              </div>
            </div>
          </el-form-item>
          <el-form-item>
            <div class="input-group">
              <label class="input-label">
                <el-icon class="input-icon"><Lock /></el-icon>
                密码
              </label>
              <div class="cyber-input-wrapper">
                <el-input 
                  v-model="password" 
                  type="password" 
                  placeholder="请输入您的密码"
                  show-password
                  class="cyber-input"
                />
                <div class="input-glow"></div>
              </div>
            </div>
          </el-form-item>
          <el-form-item class="button-wrapper">
            <div class="form-buttons">
              <button
                class="login-btn primary-btn"
                @click="handleLogin"
                :disabled="loading"
                type="button"
              >
                <span class="btn-text">{{ loading ? '登录中...' : '立即登录' }}</span>
                <span class="btn-icon" v-if="!loading">→</span>
              </button>
              <button class="login-btn secondary-btn" @click="handleRegister" type="button">
                <span class="btn-text">注册</span>
                <span class="btn-icon">+</span>
              </button>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { User, Lock } from '@element-plus/icons-vue'
export default {
  components: {
    User,
    Lock
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: #000000;
}

/* 淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* TRAE 风格背景 */
.trae-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #000000;
  overflow: hidden;
  z-index: 0;
}

.pixel-matrix {
  width: 100%;
  height: 100%;
  display: block;
}

/* 登录卡片样式 */
.login-card {
  width: 100%;
  max-width: 420px;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
  padding: 45px 40px;
  border: 1px solid rgba(16, 185, 129, 0.2);
  z-index: 10;
  position: relative;
  animation: fadeIn 0.8s ease-out forwards;
  opacity: 0;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h2 {
  margin: 0 0 10px 0;
  color: #10b981;
  font-size: 32px;
  font-weight: 700;
  text-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

.login-subtitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 16px;
  font-weight: 300;
}

.login-form {
  width: 100%;
}

.input-group {
  margin-bottom: 25px;
}

.input-label {
  display: flex;
  align-items: center;
  color: white;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
}

.input-icon {
  margin-right: 8px;
  font-size: 18px;
  color: #10b981;
}

.cyber-input-wrapper {
  position: relative;
}

.cyber-input {
  width: 100%;
}

.cyber-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 12px;
  box-shadow: none;
  transition: all 0.3s ease;
  padding: 0;
}

.cyber-input :deep(.el-input__wrapper):hover {
  border-color: rgba(16, 185, 129, 0.4);
}

.cyber-input :deep(.el-input__wrapper).is-focus {
  border-color: #10b981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1);
}

.cyber-input :deep(.el-input__inner) {
  color: white;
  font-size: 16px;
  padding: 15px 20px;
  background: transparent;
  border: none;
  outline: none;
}

.cyber-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4);
}

.cyber-input :deep(.el-input__prefix) {
  color: #10b981;
}

.input-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 12px;
  background: rgba(16, 185, 129, 0.1);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  z-index: -1;
}

.cyber-input-wrapper:hover .input-glow {
  opacity: 0.3;
}

.cyber-input :deep(.el-input__wrapper).is-focus + .input-glow {
  opacity: 0.5;
}

.button-wrapper {
  margin-bottom: 0;
  margin-top: 35px;
}

.form-buttons {
  display: flex;
  flex-direction: row;
  gap: 20px;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.login-btn {
  flex: 1;
  padding: 16px 28px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
  white-space: nowrap;
  box-sizing: border-box;
}

.primary-btn {
  background: #10b981;
  color: white;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.primary-btn:hover {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(16, 185, 129, 0.5);
}

.secondary-btn {
  background: transparent;
  color: #10b981;
  border: 2px solid #10b981;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15);
}

.secondary-btn:hover {
  background: rgba(16, 185, 129, 0.1);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(16, 185, 129, 0.3);
}

.btn-text {
  font-weight: 600;
  letter-spacing: 0.2px;
}

.btn-icon {
  font-size: 18px;
  transition: transform 0.3s ease;
}

.login-btn:hover .btn-icon {
  transform: translateX(3px);
}

.secondary-btn:hover .btn-icon {
  transform: rotate(90deg);
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    padding: 35px 30px;
    margin: 15px;
    max-width: none;
  }

  .login-header h2 {
    font-size: 28px;
  }

  .login-subtitle {
    font-size: 14px;
  }

  .form-buttons {
    flex-direction: column;
    gap: 15px;
  }

  .login-btn {
    min-width: 100%;
    max-width: none;
    padding: 14px 24px;
    font-size: 16px;
  }

  .input-label {
    font-size: 15px;
  }
}
</style>