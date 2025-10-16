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
  console.log('跳转到注册页面')
  router.push('/register')
}

// 简化随机字符（用于数字雨）
const randomBinary = () => {
  return Math.random() > 0.5 ? '1' : '0'
}

</script>

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
  animation: fadeIn 0.8s ease-out forwards;
  opacity: 0;
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