<template>
  <div class="book-detail-container">
    <!-- TRAE 风格像素矩阵背景 -->
    <div class="trae-background">
      <canvas ref="pixelCanvas" class="pixel-matrix"></canvas>
    </div>

    <!-- 详情内容 -->
    <div class="detail-content">
      <button class="back-btn" @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </button>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在加载图书详情...</p>
      </div>

      <div v-else-if="book" class="book-detail">
        <!-- 左侧图片区域 -->
        <div class="book-image-section">
          <div class="book-cover">
            <img :src="book.image" :alt="book.title" @error="handleImageError" />
            <div class="image-glow"></div>
          </div>
          <div class="book-basic-info">
            <span class="category-tag" :class="getCategoryClass(book.category)">{{ book.category }}</span>
            <div class="book-rating">
              <el-rate
                v-model="book.rating"
                disabled
                :max="5"
                :colors="['#10b981', '#10b981', '#10b981']"
                :void-color="'rgba(255,255,255,0.2)'"
              />
              <span class="rating-text">{{ book.rating.toFixed(1) }}</span>
            </div>
          </div>
        </div>
        
        <!-- 右侧信息区域 -->
        <div class="book-info-section">
          <div class="info-header">
            <h1 class="book-title">{{ book.title }}</h1>
            <h2 class="book-author">作者：{{ book.author }}</h2>
          </div>
          
          <div class="price-section">
            <div class="price-container">
              <span class="price-symbol">¥</span>
              <span class="price-number">{{ book.price }}</span>
            </div>
          </div>
          
          <div class="book-description">
            <h3 class="section-heading">内容简介</h3>
            <p>{{ book.description }}</p>
            <p class="expanded-desc">
              这是一本关于{{ book.category }}的优质图书，由著名作者{{ book.author }}精心编写。
              本书涵盖了{{ book.category }}领域的核心知识点和最新发展趋势，适合各个层次的读者学习和参考。
              通过阅读本书，您将获得对{{ book.category }}的全面理解和深入洞察。
            </p>
          </div>
          
          <div class="book-details">
            <h3 class="section-heading">图书详情</h3>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">分类：</span>
                <span class="detail-value">{{ book.category }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">评分：</span>
                <span class="detail-value">{{ book.rating.toFixed(1) }} (满分5.0)</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">价格：</span>
                <span class="detail-value">¥{{ book.price }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">库存：</span>
                <span class="detail-value">有货</span>
              </div>
            </div>
          </div>
          

        </div>
      </div>
      
      <div v-else class="no-book">
        <el-icon size="48"><Document /></el-icon>
        <p>无法找到该图书信息</p>
        <button class="back-btn" @click="goBack">返回列表</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getBookById, type Book } from '../api/bookApi'

const router = useRouter()
const route = useRoute()

const book = ref<Book | null>(null)
const loading = ref(false)
const pixelCanvas = ref<HTMLCanvasElement | null>(null)

// 从后端加载图书详情
const loadBookDetail = async (bookId: number) => {
  loading.value = true
  try {
    const bookData = await getBookById(bookId)
    if (bookData) {
      // 转换数据格式以适配前端需求
      book.value = {
        ...bookData,
        price: typeof bookData.price === 'number' ? bookData.price.toFixed(2) : bookData.price,
        rating: bookData.rating || 4.5,
        image: bookData.image || '/images/book-placeholder.svg'
      }
      console.log('成功加载图书详情:', book.value)
    } else {
      ElMessage.error('未找到该图书信息')
    }
  } catch (error) {
    console.error('加载图书详情失败:', error)
    ElMessage.error('加载图书详情失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 初始化像素矩阵背景
  const cleanupPixelMatrix = initPixelMatrix()

  // 获取路由参数中的图书ID
  const bookId = Number(route.params.id)

  if (bookId && !isNaN(bookId)) {
    loadBookDetail(bookId)
  } else {
    ElMessage.error('无效的图书ID')
  }

  // 返回清理函数
  return () => {
    if (cleanupPixelMatrix) cleanupPixelMatrix()
  }
})

const goBack = () => {
  router.back()
}

const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  target.src = '/images/book-placeholder.svg'
}

const getCategoryClass = (category: string) => {
  const classMap: Record<string, string> = {
    '技术': 'tech',
    '文学': 'literature',
    '历史': 'history',
    '科学': 'science',
    '艺术': 'art',
    '哲学': 'philosophy',
    '心理学': 'psychology',
    '经济': 'economy',
    '管理': 'management',
    '生活': 'lifestyle'
  }
  return classMap[category] || 'default'
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
</script>

<style scoped>
.book-detail-container {
  min-height: 100vh;
  background: #000000;
  position: relative;
  overflow-x: hidden;
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

/* 详情内容 */
.detail-content {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  animation: fadeIn 0.8s ease-out forwards;
  opacity: 0;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  margin-bottom: 30px;
  background: rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #10b981;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.back-btn:hover {
  background: rgba(16, 185, 129, 0.1);
  border-color: #10b981;
  transform: translateX(-5px);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

/* 加载状态样式 */
.loading-state {
  text-align: center;
  padding: 120px 20px;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(16, 185, 129, 0.2);
  color: rgba(255, 255, 255, 0.8);
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(16, 185, 129, 0.2);
  border-top-color: #10b981;
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  font-size: 18px;
  font-weight: 500;
}

.book-detail {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 40px;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px;
  border: 1px solid rgba(16, 185, 129, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
}

/* 左侧图片区域 */
.book-image-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.book-cover {
  position: relative;
  width: 280px;
  height: 400px;
  border-radius: 15px;
  overflow: hidden;
  border: 2px solid rgba(16, 185, 129, 0.3);
  transition: all 0.5s ease;
  box-shadow: 0 0 30px rgba(16, 185, 129, 0.2);
}

.book-cover:hover {
  transform: translateY(-10px);
  box-shadow: 0 0 40px rgba(16, 185, 129, 0.4);
  border-color: #10b981;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
  position: relative;
}

.image-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, transparent, rgba(16, 185, 129, 0.2), transparent);
  animation: glow-shift 3s ease-in-out infinite;
  z-index: 2;
  pointer-events: none;
}

@keyframes glow-shift {
  0%, 100% { transform: translateX(-100%) translateY(-100%); }
  50% { transform: translateX(100%) translateY(100%); }
}

.book-basic-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.category-tag {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: white;
  background: #10b981;
  transition: all 0.3s ease;
}

.category-tag:hover {
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.6);
  background: #059669;
}

/* 分类标签颜色 - 保持绿色系 */
.category-tag.tech { background: #10b981; }
.category-tag.literature { background: #059669; }
.category-tag.history { background: #34d399; }
.category-tag.science { background: #10b981; }
.category-tag.art { background: #059669; }
.category-tag.philosophy { background: #047857; }
.category-tag.psychology { background: #10b981; }
.category-tag.economy { background: #059669; }
.category-tag.management { background: #34d399; }
.category-tag.lifestyle { background: #6ee7b7; color: #000; }

.book-rating {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rating-text {
  color: #10b981;
  font-size: 16px;
  font-weight: 700;
}

/* 右侧信息区域 */
.book-info-section {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.info-header {
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(16, 185, 129, 0.2);
}

.book-title {
  font-size: 36px;
  font-weight: 800;
  color: #10b981;
  margin: 0 0 10px 0;
  text-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

.book-author {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.price-section {
  display: flex;
  align-items: center;
  gap: 30px;
}

.price-container {
  display: flex;
  align-items: baseline;
  gap: 5px;
}

.price-symbol {
  font-size: 24px;
  color: #10b981;
}

.price-number {
  font-size: 48px;
  font-weight: 800;
  color: #10b981;
  text-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

.book-description {
  background: rgba(16, 185, 129, 0.05);
  padding: 20px;
  border-radius: 10px;
  border-left: 3px solid #10b981;
}

.section-heading {
  font-size: 20px;
  font-weight: 700;
  color: #10b981;
  margin: 0 0 15px 0;
  text-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
}

.book-description p {
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.8;
  margin: 0 0 15px 0;
}

.book-description p:last-child {
  margin-bottom: 0;
}

.expanded-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6) !important;
}

.book-details {
  background: rgba(16, 185, 129, 0.05);
  padding: 20px;
  border-radius: 10px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.detail-item {
  display: flex;
  gap: 10px;
  align-items: center;
}

.detail-label {
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
  min-width: 60px;
}

.detail-value {
  color: rgba(255, 255, 255, 0.9);
}

.purchase-actions {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.buy-now-btn {
  padding: 15px 30px;
  background: #10b981;
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.buy-now-btn:hover {
  background: #059669;
  transform: translateY(-3px);
  box-shadow: 0 6px 25px rgba(16, 185, 129, 0.5);
}

.add-to-cart-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: rgba(16, 185, 129, 0.1);
  border: 2px solid rgba(16, 185, 129, 0.3);
  border-radius: 8px;
  color: #10b981;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.add-to-cart-btn:hover {
  background: rgba(16, 185, 129, 0.2);
  border-color: #10b981;
  transform: translateY(-3px);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
}

.add-to-cart-btn.large {
  padding: 15px 30px;
  font-size: 18px;
}

.no-book {
  text-align: center;
  padding: 80px 20px;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.no-book el-icon {
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 20px;
}

.no-book p {
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 20px 0;
  font-size: 18px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .book-detail {
    grid-template-columns: 1fr;
    gap: 30px;
    padding: 30px;
  }

  .book-cover {
    width: 240px;
    height: 340px;
    margin: 0 auto;
  }

  .book-image-section {
    align-items: center;
  }

  .price-section {
    justify-content: center;
  }

  .purchase-actions {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .detail-content {
    padding: 15px;
  }

  .book-detail {
    padding: 20px;
  }

  .book-title {
    font-size: 28px;
  }

  .book-author {
    font-size: 18px;
  }

  .price-number {
    font-size: 36px;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .purchase-actions {
    flex-direction: column;
  }

  .buy-now-btn,
  .add-to-cart-btn.large {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .back-btn {
    margin-bottom: 20px;
    padding: 8px 16px;
  }

  .book-cover {
    width: 200px;
    height: 280px;
  }

  .book-title {
    font-size: 24px;
  }

  .price-number {
    font-size: 30px;
  }

  .book-description,
  .book-details {
    padding: 15px;
  }
}
</style>