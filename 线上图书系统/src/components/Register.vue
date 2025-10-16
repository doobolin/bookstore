<template>
  <div class="login-container">
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
      
      <!-- 扫描线 -->
      <div class="scan-line"></div>
      
      <!-- 故障效果 -->
      <div class="glitch-overlay"></div>
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
  z-index: -1;
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
  animation: scan-horizontal 3s linear infinite;
}

.grid-line.vertical {
  width: 1px;
  height: 100%;
  background: linear-gradient(180deg, transparent, #ff00ff, transparent);
  animation: scan-vertical 4s linear infinite;
}

@keyframes scan-horizontal {
  0% { transform: translateY(-100vh); }
  100% { transform: translateY(100vh); }
}

@keyframes scan-vertical {
  0% { transform: translateX(-100vw); }
  100% { transform: translateX(100vw); }
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

/* 扫描线 */
.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00ffff, transparent);
  animation: scan 2s linear infinite;
}

@keyframes scan {
  0% { transform: translateY(-100vh); }
  100% { transform: translateY(100vh); }
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

/* 登录卡片样式 */
.login-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  padding: 45px 40px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 10;
  position: relative;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h2 {
  margin: 0 0 10px 0;
  color: white;
  font-size: 32px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  background: linear-gradient(135deg, #00ffff, #ff00ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-subtitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
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
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.input-icon {
  margin-right: 8px;
  font-size: 18px;
  color: #00ffff;
}

.cyber-input-wrapper {
  position: relative;
}

.cyber-input {
  width: 100%;
}

.cyber-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 12px;
  box-shadow: 0 0 0 1px rgba(0, 255, 255, 0.1);
  transition: all 0.3s ease;
  padding: 0;
}

.cyber-input :deep(.el-input__wrapper):hover {
  border-color: rgba(0, 255, 255, 0.5);
  box-shadow: 0 0 0 2px rgba(0, 255, 255, 0.2);
}

.cyber-input :deep(.el-input__wrapper).is-focus {
  border-color: #00ffff;
  box-shadow: 0 0 0 3px rgba(0, 255, 255, 0.3);
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
  color: rgba(255, 255, 255, 0.6);
}

.cyber-input :deep(.el-input__prefix) {
  color: #00ffff;
}

.input-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(255, 0, 255, 0.1));
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
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
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
  border-radius: 50px;
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
  background: linear-gradient(135deg, #00ffff, #0080ff);
  color: white;
  box-shadow: 0 4px 15px rgba(0, 255, 255, 0.3);
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(0, 255, 255, 0.5);
}

.secondary-btn {
  background: transparent;
  color: #00ffff;
  border: 2px solid #00ffff;
  box-shadow: 0 4px 15px rgba(0, 255, 255, 0.15);
}

.secondary-btn:hover {
  background: linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(0, 128, 255, 0.1));
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(0, 255, 255, 0.3);
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