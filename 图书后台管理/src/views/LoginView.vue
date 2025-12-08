<template>
  <div class="login-container">
    <!-- 动态背景 -->
    <div class="dynamic-bg">
      <div ref="canvasContainer" class="canvas-container"></div>
    </div>
    
    <!-- 登录表单卡片 -->
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <span>线上书店管理系统 - 管理员登录</span>
        </div>
      </template>
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" class="login-form">
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            autocomplete="on"
            @keyup.enter="$refs.passwordInput?.focus()"
          ></el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            ref="passwordInput"
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            autocomplete="current-password"
            @keyup.enter="handleLogin"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="login-btn" @click="handleLogin" :loading="loading">
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { loginUser, checkUserStatus } from '../api/userApi'

const loginFormRef = ref<FormInstance>();
const loading = ref(false);
const canvasContainer = ref<HTMLDivElement>();

const loginForm = reactive({
  username: '',
  password: ''
});

const loginRules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
});

const router = useRouter()

const handleLogin = async () => {
  try {
    loading.value = true;
    await loginFormRef.value?.validate();
    
    // 先检查用户状态
    try {
      const userStatus = await checkUserStatus(loginForm.username);
      
      if (userStatus.exists && userStatus.status === 'inactive') {
        ElMessage.error('该用户已被禁用，请寻找管理员处理');
        loading.value = false;
        return;
      }
    } catch (error) {
      console.error('检查用户状态时出错:', error);
      // 继续尝试登录，不因状态检查失败而中断登录流程
    }
    
    // 调用后端登录API进行验证
    const loginResult = await loginUser({
      username: loginForm.username,
      password: loginForm.password
    });
    
    // 检查用户角色，只允许管理员登录
            if (loginResult.role !== 'admin') {
              ElMessage.error('普通用户不能登录管理系统');
              loading.value = false;
              return;
            }
    
    // 登录成功后的处理
    ElMessage.success('登录成功');
    
    // 存储登录状态和用户信息
    localStorage.setItem('isLoggedIn', 'true');
    localStorage.setItem('token', loginResult.token);
    localStorage.setItem('username', loginResult.username);
    localStorage.setItem('role', loginResult.role);
    
    // 跳转到首页
    router.push({ name: 'home' });
  } catch (error) {
    console.error('登录失败:', error);
    // 检查错误类型，区分用户被禁用和其他错误
    if (error instanceof Error && (error.message.includes('禁用') || error.message.includes('inactive'))) {
      ElMessage.error('该用户已被禁用，请寻找管理员处理');
    } else {
      ElMessage.error('用户名或密码错误');
    }
  } finally {
    loading.value = false;
  }
};

// 动态背景相关逻辑
let animationId: number | null = null;
let particles: Array<Particle> = [];
let mousePosition = { x: 0, y: 0 };
let prevMousePosition = { x: 0, y: 0 };
let mouseVelocity = { x: 0, y: 0 };

// Particle类定义 - TRAE风格
class Particle {
  x: number;
  y: number;
  size: number;
  speedX: number;
  speedY: number;
  color: string;
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  opacity: number;
  maxOpacity: number;
  minOpacity: number;

  constructor(canvas: HTMLCanvasElement, ctx: CanvasRenderingContext2D) {
    this.canvas = canvas;
    this.ctx = ctx;
    this.x = Math.random() * canvas.width;
    this.y = Math.random() * canvas.height;
    this.size = Math.random() * 3 + 1.5; // 增加粒子大小
    this.baseSize = this.size; // 存储基础大小
    // 略微增加移动速度使效果更明显
    this.speedX = (Math.random() - 0.5) * 0.3;
    this.speedY = (Math.random() - 0.5) * 0.3;
    // 使用iOS风格的翠绿色系
    const colors = ['#34C759', '#30d158', '#32d74b', '#2db34b'];
    this.color = colors[Math.floor(Math.random() * colors.length)];
    this.opacity = Math.random() * 0.7 + 0.3; // 增加基础透明度
    this.maxOpacity = 1; // 增加最大透明度
    this.minOpacity = 0.2; // 增加最小透明度
    // 鼠标交互相关属性
    this.isInteracting = false;
    this.forceFactor = 0.02; // 鼠标影响的力大小
    this.maxSizeMultiplier = 1.8; // 鼠标附近粒子最大放大倍数
  }

  update() {
    // 计算到鼠标的距离和方向
    const dx = this.x - mousePosition.x;
    const dy = this.y - mousePosition.y;
    const distanceToMouse = Math.sqrt(dx * dx + dy * dy);

    // 鼠标交互效果
    if (distanceToMouse < 150) {
      // 靠近鼠标时的效果
      this.isInteracting = true;
      
      // 调整透明度
      this.opacity = this.maxOpacity * (1 - distanceToMouse / 150);
      
      // 调整大小（鼠标越近，粒子越大）
      const sizeMultiplier = 1 + (this.maxSizeMultiplier - 1) * (1 - distanceToMouse / 150);
      this.size = this.baseSize * sizeMultiplier;
      
      // 添加排斥力（粒子远离鼠标）
      const angle = Math.atan2(dy, dx);
      const force = (1 - distanceToMouse / 150) * this.forceFactor;
      this.speedX += Math.cos(angle) * force;
      this.speedY += Math.sin(angle) * force;
      
      // 鼠标移动时的跟随效果
      if (Math.abs(mouseVelocity.x) > 0.1 || Math.abs(mouseVelocity.y) > 0.1) {
        this.speedX += mouseVelocity.x * 0.001;
        this.speedY += mouseVelocity.y * 0.001;
      }
    } else {
      // 远离鼠标时逐渐恢复
      if (this.isInteracting) {
        this.isInteracting = false;
      }
      
      // 恢复基础透明度
      if (this.opacity > this.minOpacity) {
        this.opacity -= 0.02;
      } else {
        this.opacity = this.minOpacity;
      }
      
      // 恢复基础大小
      if (this.size > this.baseSize) {
        this.size = Math.max(this.baseSize, this.size - 0.05);
      }
    }

    // 限制最大速度
    const maxSpeed = 0.8;
    const speed = Math.sqrt(this.speedX * this.speedX + this.speedY * this.speedY);
    if (speed > maxSpeed) {
      this.speedX = (this.speedX / speed) * maxSpeed;
      this.speedY = (this.speedY / speed) * maxSpeed;
    }

    // 更新位置
    this.x += this.speedX;
    this.y += this.speedY;

    // 边界检查 - 让粒子在边界处反弹
    if (this.x < 0 || this.x > this.canvas.width) {
      this.speedX *= -0.8; // 略微减少能量
      this.x = Math.max(0, Math.min(this.canvas.width, this.x));
    }
    if (this.y < 0 || this.y > this.canvas.height) {
      this.speedY *= -0.8;
      this.y = Math.max(0, Math.min(this.canvas.height, this.y));
    }

    this.draw();
  }

  draw() {
    this.ctx.fillStyle = this.color;
    this.ctx.globalAlpha = this.opacity;
    this.ctx.beginPath();
    this.ctx.arc(this.x, this.y, this.size / 2, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.globalAlpha = 1;
  }
}

// 连接靠近的粒子，创建网格效果
function connectParticles(ctx: CanvasRenderingContext2D) {
  const maxDistance = 150; // 增加连接距离
  
  for (let a = 0; a < particles.length; a++) {
    for (let b = a; b < particles.length; b++) {
      const dx = particles[a].x - particles[b].x;
      const dy = particles[a].y - particles[b].y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      // 如果粒子足够近，绘制连接线
      if (distance < maxDistance) {
        // 线的透明度根据距离变化
        const opacity = 1 - distance / maxDistance;
        ctx.strokeStyle = `rgba(52, 199, 89, ${opacity * 0.5})`; // iOS绿色连接线
        ctx.lineWidth = 0.7; // 增加线宽
        ctx.beginPath();
        ctx.moveTo(particles[a].x, particles[a].y);
        ctx.lineTo(particles[b].x, particles[b].y);
        ctx.stroke();
      }
    }
  }
}

function initCanvas() {
  if (!canvasContainer.value) return;

  // 清空容器
  canvasContainer.value.innerHTML = '';

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  canvas.className = 'dynamic-bg-canvas';
  canvasContainer.value.appendChild(canvas);

  // 监听鼠标移动事件 - 增强版
  canvas.addEventListener('mousemove', (e) => {
    // 计算鼠标速度
    mouseVelocity.x = e.clientX - prevMousePosition.x;
    mouseVelocity.y = e.clientY - prevMousePosition.y;
    
    // 更新鼠标位置
    prevMousePosition.x = mousePosition.x;
    prevMousePosition.y = mousePosition.y;
    mousePosition.x = e.clientX;
    mousePosition.y = e.clientY;
  });

  // 初始化鼠标位置到中心
  mousePosition.x = canvas.width / 2;
  mousePosition.y = canvas.height / 2;

  // 创建更多的粒子以达到TRAE风格的密集效果
  particles = [];
  const particleCount = Math.floor((window.innerWidth * window.innerHeight) / 5000); // 增加粒子数量
  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle(canvas, ctx));
  }

  // 动画循环
  function animate() {
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 先更新所有粒子
    particles.forEach(particle => particle.update());
    
    // 然后绘制粒子之间的连接线
    connectParticles(ctx);
    
    animationId = requestAnimationFrame(animate);
  }

  animate();
}

function handleResize() {
  if (animationId) {
    cancelAnimationFrame(animationId);
  }
  initCanvas();
}

onMounted(() => {
  initCanvas();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId);
  }
  window.removeEventListener('resize', handleResize);
  // 移除所有canvas事件监听器
  const canvas = document.querySelector('.dynamic-bg-canvas');
  if (canvas) {
    canvas.removeEventListener('mousemove', () => {});
  }
});
</script>

<style scoped lang="scss">
/* iOS风格登录页面 */
.login-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  overflow: hidden;
  background-color: #0a0a0a;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* 渐变波纹背景 - 第一层（红-橙-黄-绿光谱） */
.login-container::before {
  content: '';
  position: fixed;
  width: 200%;
  height: 200%;
  left: -50%;
  top: -50%;
  background:
    radial-gradient(circle at 20% 30%, rgba(255, 20, 50, 1) 0%, rgba(255, 60, 80, 0.9) 15%, transparent 35%),
    radial-gradient(circle at 50% 20%, rgba(255, 140, 0, 1) 0%, rgba(255, 170, 40, 0.8) 18%, transparent 40%),
    radial-gradient(circle at 80% 35%, rgba(255, 210, 0, 1) 0%, rgba(255, 230, 80, 0.8) 20%, transparent 45%),
    radial-gradient(circle at 35% 60%, rgba(50, 255, 100, 1) 0%, rgba(120, 255, 150, 0.7) 18%, transparent 38%);
  background-size: 100% 100%;
  animation: flowingWave1 12s ease-in-out infinite;
  filter: blur(80px);
  opacity: 0.65;
  z-index: 0;
  pointer-events: none;
}

/* 渐变波纹背景 - 第二层（青-蓝-紫-品红光谱） */
.login-container::after {
  content: '';
  position: fixed;
  width: 200%;
  height: 200%;
  left: -50%;
  top: -50%;
  background:
    radial-gradient(circle at 65% 70%, rgba(0, 255, 200, 1) 0%, rgba(80, 255, 220, 0.9) 15%, transparent 38%),
    radial-gradient(circle at 15% 45%, rgba(30, 130, 255, 1) 0%, rgba(80, 170, 255, 0.8) 18%, transparent 42%),
    radial-gradient(circle at 85% 60%, rgba(140, 30, 255, 1) 0%, rgba(170, 80, 255, 0.8) 20%, transparent 45%),
    radial-gradient(circle at 50% 85%, rgba(255, 20, 180, 1) 0%, rgba(255, 80, 210, 0.7) 18%, transparent 38%);
  background-size: 100% 100%;
  animation: flowingWave2 15s ease-in-out infinite;
  filter: blur(85px);
  opacity: 0.6;
  z-index: 0;
  pointer-events: none;
}

@keyframes flowingWave1 {
  0% {
    transform: translate(0%, 0%) rotate(0deg) scale(1);
  }
  25% {
    transform: translate(-15%, 10%) rotate(90deg) scale(1.1);
  }
  50% {
    transform: translate(-10%, -15%) rotate(180deg) scale(1.05);
  }
  75% {
    transform: translate(15%, -8%) rotate(270deg) scale(1.12);
  }
  100% {
    transform: translate(0%, 0%) rotate(360deg) scale(1);
  }
}

@keyframes flowingWave2 {
  0% {
    transform: translate(0%, 0%) rotate(0deg) scale(1);
  }
  20% {
    transform: translate(12%, -10%) rotate(-72deg) scale(1.08);
  }
  40% {
    transform: translate(-8%, -12%) rotate(-144deg) scale(1.15);
  }
  60% {
    transform: translate(-15%, 8%) rotate(-216deg) scale(1.06);
  }
  80% {
    transform: translate(10%, 15%) rotate(-288deg) scale(1.12);
  }
  100% {
    transform: translate(0%, 0%) rotate(-360deg) scale(1);
  }
}

.dynamic-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  background-color: transparent;
}

.canvas-container {
  width: 100%;
  height: 100%;
  display: none;
}

.dynamic-bg-canvas {
  display: none;
}

.login-card {
  position: relative;
  width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
  border-radius: 20px;
  overflow: hidden;
  z-index: 1;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border: 0.5px solid rgba(0, 0, 0, 0.04);
}

.login-header {
  text-align: center;
  font-size: 22px;
  font-weight: 700;
  color: #1C1C1E;
  padding: 28px 0;
  letter-spacing: -0.5px;
}

.login-form {
  padding: 0 32px 32px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
  background: #34C759;
  border: none;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  box-shadow: 0 4px 12px rgba(52, 199, 89, 0.3);
  color: white;
}

.login-btn:hover {
  background: #2db34b;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(52, 199, 89, 0.4);
}

.login-btn:active {
  transform: translateY(0);
}

.login-btn:disabled {
  background: #34C759;
  opacity: 0.5;
  transform: none;
}

/* iOS风格输入框 */
:deep(.el-input) {
  margin-bottom: 16px;
  width: 100%;
}

:deep(.el-input__wrapper) {
  background-color: #F9F9F9;
  border: 1px solid #E5E5EA;
  border-radius: 12px;
  transition: all 0.3s ease;
  padding: 0 14px;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  box-shadow: none;
}

:deep(.el-input__wrapper:hover) {
  border-color: #C7C7CC;
  box-shadow: none;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #34C759;
  box-shadow: 0 0 0 3px rgba(52, 199, 89, 0.1);
  background-color: white;
}

:deep(.el-input__inner) {
  color: #1C1C1E;
  background-color: transparent;
  width: 100%;
  box-sizing: border-box;
  font-size: 15px;
}

:deep(.el-input__inner::placeholder) {
  color: #8E8E93;
}

:deep(.el-input__prefix) {
  margin-right: 8px;
}

:deep(.el-input__icon) {
  color: #8E8E93;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* iOS风格表单标签 */
:deep(.el-form-item__label) {
  color: #1C1C1E;
  font-weight: 600;
  font-size: 14px;
}
</style>