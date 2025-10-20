<template>
  <div class="login-container">
    <!-- 动态粒子背景 -->
    <div class="dynamic-bg">
      <div ref="canvasContainer" class="canvas-container"></div>
    </div>

    <!-- 注册卡片 -->
    <div class="login-card">
      <div class="login-header">
        <h2>用户注册</h2>
        <p class="login-subtitle">创建您的科技书城账号</p>
      </div>
      <div class="login-form">
        <el-form :model="formData" label-width="0">
          <el-form-item>
            <div class="input-group">
              <label class="input-label">
                <el-icon class="input-icon"><User /></el-icon>
                用户名
              </label>
              <div class="cyber-input-wrapper">
                <el-input 
                  v-model="formData.username" 
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
                <el-icon class="input-icon"><Message /></el-icon>
                邮箱地址
              </label>
              <div class="cyber-input-wrapper">
                <el-input
                  v-model="formData.email"
                  placeholder="请输入您的邮箱地址"
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
                  v-model="formData.password" 
                  type="password" 
                  placeholder="请设置您的密码" 
                  show-password
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
                确认密码
              </label>
              <div class="cyber-input-wrapper">
                <el-input 
                  v-model="formData.confirmPassword" 
                  type="password" 
                  placeholder="请再次输入密码" 
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
                @click="handleRegister"
                :disabled="loading"
                type="button"
              >
                <span class="btn-text">{{ loading ? '注册中...' : '立即注册' }}</span>
                <span class="btn-icon" v-if="!loading">→</span>
              </button>
              <button class="login-btn secondary-btn" @click="goToLogin" type="button">
                <span class="btn-text">已有账号</span>
                <span class="btn-icon">←</span>
              </button>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
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
const canvasContainer = ref<HTMLDivElement | null>(null)

// 处理注册
const handleRegister = async () => {
  // 简单的表单验证
  if (!formData.value.username) {
    ElMessage.warning('请输入用户名')
    return
  }

  // 用户名格式验证
  if (formData.value.username.length < 3) {
    ElMessage.warning('用户名长度至少为3位')
    return
  }

  if (!formData.value.email) {
    ElMessage.warning('请输入邮箱地址')
    return
  }

  // 邮箱格式验证
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(formData.value.email)) {
    ElMessage.warning('请输入有效的邮箱地址')
    return
  }

  if (!formData.value.password) {
    ElMessage.warning('请设置密码')
    return
  }

  // 密码强度验证
  if (formData.value.password.length < 6) {
    ElMessage.warning('密码长度至少为6位')
    return
  }

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

    ElMessage.success('注册成功，请登录')

    // 注册成功后跳转到登录页
    router.push('/login')
  } catch (error: any) {
    console.error('注册失败:', error)
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('注册失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

// 跳转到登录页面
const goToLogin = () => {
  router.push('/login')
}

// 动态粒子背景（与Login.vue相同的实现）
let animationId: number | null = null
let particles: Array<any> = []
let mousePosition = { x: 0, y: 0 }
let prevMousePosition = { x: 0, y: 0 }
let mouseVelocity = { x: 0, y: 0 }

class Particle {
  x: number; y: number; size: number; baseSize: number; speedX: number; speedY: number
  color: string; canvas: HTMLCanvasElement; ctx: CanvasRenderingContext2D
  opacity: number; maxOpacity: number; minOpacity: number
  isInteracting: boolean; forceFactor: number; maxSizeMultiplier: number

  constructor(canvas: HTMLCanvasElement, ctx: CanvasRenderingContext2D) {
    this.canvas = canvas; this.ctx = ctx
    this.x = Math.random() * canvas.width; this.y = Math.random() * canvas.height
    this.size = Math.random() * 3 + 1.5; this.baseSize = this.size
    this.speedX = (Math.random() - 0.5) * 0.3; this.speedY = (Math.random() - 0.5) * 0.3
    const colors = ['#10b981', '#34d399', '#6ee7b7', '#059669']
    this.color = colors[Math.floor(Math.random() * colors.length)]
    this.opacity = Math.random() * 0.7 + 0.3; this.maxOpacity = 1; this.minOpacity = 0.2
    this.isInteracting = false; this.forceFactor = 0.02; this.maxSizeMultiplier = 1.8
  }

  update() {
    const dx = this.x - mousePosition.x, dy = this.y - mousePosition.y
    const distanceToMouse = Math.sqrt(dx * dx + dy * dy)
    if (distanceToMouse < 150) {
      this.isInteracting = true
      this.opacity = this.maxOpacity * (1 - distanceToMouse / 150)
      const sizeMultiplier = 1 + (this.maxSizeMultiplier - 1) * (1 - distanceToMouse / 150)
      this.size = this.baseSize * sizeMultiplier
      const angle = Math.atan2(dy, dx), force = (1 - distanceToMouse / 150) * this.forceFactor
      this.speedX += Math.cos(angle) * force; this.speedY += Math.sin(angle) * force
      if (Math.abs(mouseVelocity.x) > 0.1 || Math.abs(mouseVelocity.y) > 0.1) {
        this.speedX += mouseVelocity.x * 0.001; this.speedY += mouseVelocity.y * 0.001
      }
    } else {
      if (this.isInteracting) this.isInteracting = false
      if (this.opacity > this.minOpacity) this.opacity -= 0.02
      else this.opacity = this.minOpacity
      if (this.size > this.baseSize) this.size = Math.max(this.baseSize, this.size - 0.05)
    }
    const maxSpeed = 0.8, speed = Math.sqrt(this.speedX * this.speedX + this.speedY * this.speedY)
    if (speed > maxSpeed) { this.speedX = (this.speedX / speed) * maxSpeed; this.speedY = (this.speedY / speed) * maxSpeed }
    this.x += this.speedX; this.y += this.speedY
    if (this.x < 0 || this.x > this.canvas.width) { this.speedX *= -0.8; this.x = Math.max(0, Math.min(this.canvas.width, this.x)) }
    if (this.y < 0 || this.y > this.canvas.height) { this.speedY *= -0.8; this.y = Math.max(0, Math.min(this.canvas.height, this.y)) }
    this.draw()
  }

  draw() {
    this.ctx.fillStyle = this.color; this.ctx.globalAlpha = this.opacity
    this.ctx.beginPath(); this.ctx.arc(this.x, this.y, this.size / 2, 0, Math.PI * 2)
    this.ctx.fill(); this.ctx.globalAlpha = 1
  }
}

function connectParticles(ctx: CanvasRenderingContext2D) {
  const maxDistance = 150
  for (let a = 0; a < particles.length; a++) {
    for (let b = a; b < particles.length; b++) {
      const dx = particles[a].x - particles[b].x, dy = particles[a].y - particles[b].y
      const distance = Math.sqrt(dx * dx + dy * dy)
      if (distance < maxDistance) {
        const opacity = 1 - distance / maxDistance
        ctx.strokeStyle = `rgba(16, 185, 129, ${opacity * 0.5})`; ctx.lineWidth = 0.7
        ctx.beginPath(); ctx.moveTo(particles[a].x, particles[a].y); ctx.lineTo(particles[b].x, particles[b].y); ctx.stroke()
      }
    }
  }
}

function initCanvas() {
  if (!canvasContainer.value) return
  canvasContainer.value.innerHTML = ''
  const canvas = document.createElement('canvas'), ctx = canvas.getContext('2d')
  if (!ctx) return
  canvas.width = window.innerWidth; canvas.height = window.innerHeight
  canvas.className = 'dynamic-bg-canvas'; canvasContainer.value.appendChild(canvas)
  canvas.addEventListener('mousemove', (e) => {
    mouseVelocity.x = e.clientX - prevMousePosition.x; mouseVelocity.y = e.clientY - prevMousePosition.y
    prevMousePosition.x = mousePosition.x; prevMousePosition.y = mousePosition.y
    mousePosition.x = e.clientX; mousePosition.y = e.clientY
  })
  mousePosition.x = canvas.width / 2; mousePosition.y = canvas.height / 2
  particles = []
  const particleCount = Math.floor((window.innerWidth * window.innerHeight) / 5000)
  for (let i = 0; i < particleCount; i++) particles.push(new Particle(canvas, ctx))
  function animate() {
    if (!ctx) return
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    particles.forEach(particle => particle.update()); connectParticles(ctx)
    animationId = requestAnimationFrame(animate)
  }
  animate()
}

function handleResize() {
  if (animationId) cancelAnimationFrame(animationId)
  initCanvas()
}

onMounted(() => {
  initCanvas()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  window.removeEventListener('resize', handleResize)
})
</script>

<script lang="ts">
import { User, Lock, Message } from '@element-plus/icons-vue'
export default {
  components: {
    User,
    Lock,
    Message
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
  transform: rotate(-90deg);
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