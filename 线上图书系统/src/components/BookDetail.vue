<template>
  <div class="book-detail-page">
    <!-- 顶部导航 -->
    <nav class="glass-nav">
      <a @click="goBack" class="back-button">
        <i class="ri-arrow-left-s-line"></i>
      </a>
      <span class="nav-title">{{ book?.title }}</span>
      <div class="nav-actions">
        <i class="ri-share-forward-line"></i>
        <i class="ri-bookmark-line"></i>
      </div>
    </nav>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载图书详情...</p>
    </div>

    <!-- 主要内容 -->
    <div v-else-if="book" class="detail-container">
      <!-- Hero 区域 -->
      <div class="hero-section">
        <!-- 动态模糊背景 -->
        <div class="ambient-bg">
          <div class="bg-overlay"></div>
          <div class="bg-blur" :style="{ backgroundImage: `url(${bookCover})` }"></div>
        </div>

        <div class="hero-content">
          <!-- 左侧：封面图 -->
          <div class="cover-column">
            <div class="cover-wrapper">
              <img :src="bookCover" :alt="book.title" class="book-cover">
              <div class="cover-shine"></div>
            </div>
            <button class="preview-button">
              <i class="ri-book-read-line"></i> 免费试读第一章
            </button>
          </div>

          <!-- 中间：核心信息 -->
          <div class="info-column">
            <div class="badge">
              <i class="ri-award-fill"></i> Best Seller
            </div>

            <h1 class="book-title">{{ book.title }}</h1>
            <h2 class="book-subtitle">{{ book.subtitle || book.description?.substring(0, 50) + '...' }}</h2>

            <!-- 作者行 -->
            <div class="author-section">
              <img :src="authorAvatar" class="author-avatar">
              <div class="author-info">
                <p class="author-name">{{ book.author }}</p>
                <p class="author-role">著名作家</p>
              </div>
            </div>

            <!-- 评分摘要 -->
            <div class="rating-summary">
              <div class="rating-block">
                <div class="stars-container">
                  <span class="rating-number">{{ book.rating?.toFixed(1) || '4.5' }}</span>
                  <div class="stars">
                    <i class="ri-star-fill" v-for="n in Math.floor(book.rating || 4.5)" :key="n"></i>
                    <i class="ri-star-half-fill" v-if="(book.rating || 4.5) % 1 !== 0"></i>
                  </div>
                </div>
                <p class="rating-count">{{ reviews }} 条评价</p>
              </div>
              <div class="divider"></div>
              <div class="rank-block">
                <p class="rank-number">Top 1</p>
                <p class="rank-category">{{ book.category }}榜</p>
              </div>
            </div>

            <!-- 标签 -->
            <div class="tags-container">
              <span v-for="tag in tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>

          <!-- 右侧：统计卡片 (Desktop) -->
          <div class="stats-column">
            <div class="price-card">
              <p class="card-label">价格</p>
              <div class="price-display">
                <span class="current-price">¥{{ book.price }}</span>
                <span class="original-price">¥{{ originalPrice }}</span>
              </div>
              <div class="discount-badge">省 {{ discount }}%</div>
            </div>

            <div class="stat-card">
              <i class="ri-file-text-line"></i>
              <span class="stat-value">{{ pages }}</span>
              <span class="stat-label">页数</span>
            </div>
            <div class="stat-card">
              <i class="ri-translate-2"></i>
              <span class="stat-value">中文</span>
              <span class="stat-label">语言</span>
            </div>
            <div class="vip-card">
              <div class="vip-icon">
                <i class="ri-vip-crown-fill"></i>
              </div>
              <div class="vip-text">
                <p class="vip-title">TechPro 会员免费</p>
                <p class="vip-desc">加入会员畅读全站</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 内容详情区 -->
      <main class="content-main">
        <!-- 左侧主要内容 -->
        <div class="main-content">
          <!-- 简介 -->
          <section class="section">
            <div class="flex items-center justify-between mb-4">
              <h3 class="section-title">简介</h3>
            </div>
            <div class="description-text" :class="{ 'clamp-3': !showFullDesc }">
              {{ book.description || '暂无简介' }}
            </div>
            <button @click="showFullDesc = !showFullDesc" class="expand-button">
              {{ showFullDesc ? '收起' : '展开全部' }}
              <i :class="showFullDesc ? 'ri-arrow-up-s-line' : 'ri-arrow-down-s-line'"></i>
            </button>
          </section>

          <!-- 本书亮点 -->
          <section class="section">
            <h3 class="section-title">本书亮点</h3>
            <div class="highlights-grid">
              <div class="highlight-card">
                <div class="highlight-icon blue">
                  <i class="ri-code-s-slash-line"></i>
                </div>
                <h4 class="highlight-title">实战重构案例</h4>
                <p class="highlight-desc">包含 50+ 真实项目代码重构前后的对比分析。</p>
              </div>
              <div class="highlight-card">
                <div class="highlight-icon orange">
                  <i class="ri-mind-map"></i>
                </div>
                <h4 class="highlight-title">思维模式升级</h4>
                <p class="highlight-desc">从"写完代码"转变为"设计系统"的架构师思维。</p>
              </div>
            </div>
          </section>

          <!-- 目录 -->
          <section class="section">
            <h3 class="section-title">目录</h3>
            <div class="chapters-list">
              <div v-for="(chapter, i) in chapters" :key="i" class="chapter-item">
                <div class="chapter-info">
                  <span class="chapter-number">{{ String(i + 1).padStart(2, '0') }}</span>
                  <span class="chapter-title">{{ chapter.title }}</span>
                </div>
                <span v-if="chapter.free" class="free-badge">试读</span>
                <i v-else class="ri-lock-line lock-icon"></i>
              </div>
            </div>
          </section>

          <!-- 评论区 -->
          <section class="section pb-10">
            <div class="section-header">
              <h3 class="section-title">读者评价 (2.3k)</h3>
              <button class="write-review-btn">写评论</button>
            </div>

            <div class="reviews-list">
              <div v-for="(review, i) in reviewsList" :key="i" class="review-item">
                <img :src="review.avatar" class="review-avatar">
                <div class="review-content">
                  <div class="review-header">
                    <div>
                      <h5 class="reviewer-name">{{ review.name }}</h5>
                      <div class="review-stars">
                        <i class="ri-star-fill" v-for="n in review.rating" :key="n"></i>
                      </div>
                    </div>
                    <span class="review-time">{{ review.time }}</span>
                  </div>
                  <p class="review-text">{{ review.text }}</p>
                </div>
              </div>
              <div class="review-divider"></div>
            </div>
          </section>
        </div>

        <!-- 右侧边栏 -->
        <div class="sidebar-content">
          <!-- 关于作者 -->
          <div class="sidebar-card">
            <h4 class="sidebar-title">关于作者</h4>
            <p class="sidebar-text">
              Robert 是 Clean Code 运动的发起人，拥有超过 40 年的软件开发经验。他是 Agile Alliance 的首任主席。
            </p>
            <div class="social-links">
              <a href="#" class="social-link">
                <i class="ri-twitter-x-line"></i>
              </a>
              <a href="#" class="social-link">
                <i class="ri-linkedin-fill"></i>
              </a>
              <a href="#" class="social-link">
                <i class="ri-github-fill"></i>
              </a>
            </div>
          </div>

          <!-- 相关推荐 -->
          <div class="recommendations">
            <h4 class="sidebar-title">看过的人也买了</h4>
            <div class="recommend-list">
              <div v-for="item in recommendedBooks" :key="item.id" class="recommend-item">
                <img :src="item.cover" class="recommend-cover">
                <div class="recommend-info">
                  <p class="recommend-title">{{ item.title }}</p>
                  <p class="recommend-author">{{ item.author }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- 底部悬浮购买栏 -->
      <div class="purchase-bar">
        <div class="purchase-content">
          <div class="purchase-info">
            <img :src="bookCover" class="purchase-cover">
            <div class="purchase-details">
              <p class="purchase-title">{{ book.title }}</p>
              <p class="purchase-author">{{ book.author }}</p>
            </div>
          </div>

          <div class="purchase-actions">
            <div class="purchase-price">
              <span class="price">¥{{ book.price }}</span>
              <span class="vip-discount">VIP 专享 8 折</span>
            </div>
            <div class="action-buttons">
              <button class="add-to-shelf-btn" @click="addToBookshelf">加入书架</button>
              <button class="buy-now-btn" @click="buyNow">
                立即购买 <i class="ri-arrow-right-line"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getBookById, type Book } from '../api/bookApi'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const book = ref<Book | null>(null)
const showFullDesc = ref(false)

// 计算属性
const bookCover = computed(() => book.value?.image || 'https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&q=80&w=800')
const authorAvatar = computed(() => 'https://i.pravatar.cc/150?img=11')
const originalPrice = computed(() => {
  const price = parseFloat(book.value?.price || '0')
  return (price / 0.7).toFixed(2)
})
const discount = computed(() => Math.round((1 - parseFloat(book.value?.price || '0') / parseFloat(originalPrice.value)) * 100))
const pages = computed(() => 482)
const reviews = computed(() => '2.3k')
const tags = computed(() => [book.value?.category || '技术', 'Best Practice', '必读经典'])

const chapters = ref([
  { title: '第一章：核心概念', free: true },
  { title: '第二章：基础实践', free: true },
  { title: '第三章：进阶技巧', free: false },
  { title: '第四章：高级应用', free: false },
  { title: '第五章：案例分析', free: false },
  { title: '第六章：最佳实践', free: false },
])

const reviewsList = ref([
  {
    name: 'Jason Chen',
    avatar: 'https://i.pravatar.cc/100?img=12',
    rating: 5,
    time: '2天前',
    text: '这本书完全改变了我的学习方式。内容深入浅出，案例丰富实用，强烈推荐！'
  },
  {
    name: 'Sarah Wu',
    avatar: 'https://i.pravatar.cc/100?img=33',
    rating: 4,
    time: '1周前',
    text: '翻译质量很棒，没有生硬的技术词汇堆砌。思想是通用的，值得一读。'
  }
])

const recommendedBooks = ref([
  {
    id: 2,
    title: '深入理解计算机系统',
    author: 'Randal E. Bryant',
    cover: 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&q=80&w=200'
  },
  {
    id: 3,
    title: '设计模式精解',
    author: 'Gang of Four',
    cover: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&q=80&w=200'
  }
])

// 加载图书详情
const loadBookDetail = async () => {
  loading.value = true
  try {
    const bookId = route.params.id as string
    const bookData = await getBookById(parseInt(bookId))
    book.value = bookData
  } catch (error) {
    console.error('加载图书详情失败:', error)
    ElMessage.error('加载图书详情失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const addToBookshelf = () => {
  ElMessage.success('已加入书架')
}

const buyNow = () => {
  if (!book.value) return

  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
  if (!isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]')
    const existingItem = cart.find((item: any) => item.id === book.value?.id)

    if (!existingItem) {
      cart.push({
        id: book.value.id,
        title: book.value.title,
        author: book.value.author,
        price: book.value.price,
        image: book.value.image,
        quantity: 1
      })
      localStorage.setItem('cart', JSON.stringify(cart))

      const event = new CustomEvent('cart-updated', {
        detail: { count: cart.length }
      })
      window.dispatchEvent(event)
    }

    router.push('/checkout')
  } catch (error) {
    console.error('购买失败:', error)
    ElMessage.error('购买失败')
  }
}

onMounted(() => {
  // 滚动到页面顶部
  window.scrollTo(0, 0)
  loadBookDetail()
})
</script>

<style scoped>
/* 引入 Remix Icon */
@import url('https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css');

.book-detail-page {
  min-height: 100vh;
  background: #FAFAFA;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  padding-bottom: 100px;
}

/* ========== 顶部导航 ========== */
.glass-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 100;
}

.back-button {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.3s;
  font-size: 20px;
  color: #1D1D1F;
}

.back-button:hover {
  background: rgba(0, 0, 0, 0.05);
}

.nav-title {
  font-weight: 600;
  font-size: 14px;
  color: #1D1D1F;
}

.nav-actions {
  display: flex;
  gap: 16px;
  font-size: 20px;
  color: #1D1D1F;
}

.nav-actions i {
  cursor: pointer;
  transition: color 0.3s;
}

.nav-actions i:hover {
  color: #007AFF;
}

/* ========== 加载状态 ========== */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  color: #86868B;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(0, 122, 255, 0.2);
  border-top-color: #007AFF;
  border-radius: 50%;
  margin-bottom: 25px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ========== Hero 区域 ========== */
.detail-container {
  padding-top: 56px;
}

.hero-section {
  position: relative;
  width: 100%;
  padding: 96px 24px 48px;
  overflow: hidden;
}

@media (min-width: 1024px) {
  .hero-section {
    padding: 128px 24px 80px;
  }
}

.ambient-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.bg-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.6);
  z-index: 10;
}

.bg-blur {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  filter: blur(80px);
  opacity: 0.6;
  transform: scale(1.1);
}

.hero-content {
  position: relative;
  z-index: 10;
  max-width: 1152px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 40px;
  align-items: start;
}

@media (min-width: 768px) {
  .hero-content {
    grid-template-columns: 300px 1fr;
  }
}

@media (min-width: 1024px) {
  .hero-content {
    grid-template-columns: 340px 1fr 300px;
  }
}

/* 封面列 */
.cover-column {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.cover-wrapper {
  position: relative;
  width: 240px;
  aspect-ratio: 2/3;
  border-radius: 12px;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.15);
  background: #E5E5E7;
  overflow: hidden;
  margin-bottom: 24px;
}

@media (min-width: 768px) {
  .cover-wrapper {
    width: 100%;
  }
}

.book-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-shine {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom right, rgba(255, 255, 255, 0.2), transparent);
  opacity: 0;
  transition: opacity 0.5s;
}

.cover-wrapper:hover .cover-shine {
  opacity: 1;
}

.preview-button {
  width: 240px;
  padding: 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  font-weight: 600;
  font-size: 14px;
  color: #1D1D1F;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

@media (min-width: 768px) {
  .preview-button {
    width: 100%;
  }
}

.preview-button:hover {
  background: white;
}

/* 信息列 */
.info-column {
  text-align: center;
  padding-top: 8px;
}

@media (min-width: 768px) {
  .info-column {
    text-align: left;
  }
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6B7280;
  backdrop-filter: blur(12px);
  margin-bottom: 16px;
}

.badge i {
  color: #FCD34D;
}

.book-title {
  font-size: 1.875rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 8px;
  color: #1F2937;
}

@media (min-width: 768px) {
  .book-title {
    font-size: 3rem;
  }
}

.book-subtitle {
  font-size: 1.25rem;
  color: #6B7280;
  margin-bottom: 24px;
  font-weight: 500;
}

.author-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
}

@media (min-width: 768px) {
  .author-section {
    justify-content: flex-start;
  }
}

.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.author-info {
  text-align: left;
}

.author-name {
  font-size: 14px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0;
}

.author-role {
  font-size: 12px;
  color: #86868B;
  margin: 0;
}

.rating-summary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  padding: 20px 0;
  margin-bottom: 24px;
}

@media (min-width: 768px) {
  .rating-summary {
    justify-content: flex-start;
  }
}

.rating-block {
  text-align: left;
}

.stars-container {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.rating-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1D1D1F;
}

.stars {
  display: flex;
  gap: 2px;
  color: #FCD34D;
  font-size: 18px;
}

.rating-count {
  font-size: 12px;
  color: #86868B;
  margin: 0;
}

.divider {
  width: 1px;
  height: 40px;
  background: rgba(0, 0, 0, 0.1);
}

.rank-block {
  text-align: left;
}

.rank-number {
  font-size: 18px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0 0 4px 0;
}

.rank-category {
  font-size: 12px;
  color: #86868B;
  margin: 0;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

@media (min-width: 768px) {
  .tags-container {
    justify-content: flex-start;
  }
}

.tag {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  border-radius: 8px;
  font-size: 14px;
  color: #6B7280;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* 统计列 */
.stats-column {
  display: none;
}

@media (min-width: 1024px) {
  .stats-column {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    align-content: start;
  }
}

.price-card {
  grid-column: span 2;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid white;
}

.card-label {
  font-size: 11px;
  color: #86868B;
  text-transform: uppercase;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.price-display {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  margin-bottom: 8px;
}

.current-price {
  font-size: 2rem;
  font-weight: 700;
  color: #1D1D1F;
}

.original-price {
  font-size: 14px;
  color: #9CA3AF;
  text-decoration: line-through;
  margin-bottom: 4px;
}

.discount-badge {
  display: inline-block;
  font-size: 12px;
  color: #10B981;
  background: #DCFCE7;
  padding: 2px 8px;
  border-radius: 4px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  padding: 16px;
  border-radius: 16px;
  border: 1px solid white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.stat-card i {
  font-size: 1.5rem;
  color: #007AFF;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #1D1D1F;
}

.stat-label {
  font-size: 10px;
  color: #86868B;
  text-transform: uppercase;
}

.vip-card {
  grid-column: span 2;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  padding: 16px;
  border-radius: 16px;
  border: 1px solid white;
  display: flex;
  align-items: center;
  gap: 12px;
}

.vip-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #000000;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.vip-text {
  flex: 1;
}

.vip-title {
  font-size: 12px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0 0 2px 0;
}

.vip-desc {
  font-size: 12px;
  color: #86868B;
  margin: 0;
}

/* ========== 内容详情区 ========== */
.content-main {
  max-width: 1152px;
  margin: 0 auto 32px;
  padding: 80px 24px 0;
  display: grid;
  grid-template-columns: 1fr;
  gap: 48px;
}

@media (min-width: 1024px) {
  .content-main {
    grid-template-columns: 1fr 340px;
  }
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0;
}

.section .flex {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section .mb-4 {
  margin-bottom: 16px;
}

.description-text {
  color: #6B7280;
  line-height: 1.6;
}

.description-text p {
  margin-bottom: 16px;
}

.description-text.clamp-3 p:not(:first-child) {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.expand-button {
  margin-top: 8px;
  color: #007AFF;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  transition: opacity 0.3s;
}

.expand-button:hover {
  opacity: 0.7;
}

.highlights-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

@media (min-width: 768px) {
  .highlights-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.highlight-card {
  padding: 20px;
  border-radius: 16px;
  background: white;
  border: 1px solid #F3F4F6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.3s;
}

.highlight-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.highlight-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-bottom: 12px;
}

.highlight-icon.blue {
  background: #EFF6FF;
  color: #007AFF;
}

.highlight-icon.orange {
  background: #FEF3C7;
  color: #FF9500;
}

.highlight-title {
  font-weight: 700;
  color: #1D1D1F;
  margin: 0 0 4px 0;
}

.highlight-desc {
  font-size: 14px;
  color: #6B7280;
  margin: 0;
}

.chapters-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chapter-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-radius: 12px;
  background: #F9FAFB;
  cursor: pointer;
  transition: background 0.3s;
}

.chapter-item:hover {
  background: #F3F4F6;
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.chapter-number {
  font-family: monospace;
  font-size: 14px;
  color: #9CA3AF;
  width: 24px;
}

.chapter-title {
  font-weight: 600;
  color: #1D1D1F;
}

.free-badge {
  font-size: 12px;
  font-weight: 700;
  color: #007AFF;
  background: #EFF6FF;
  padding: 4px 8px;
  border-radius: 4px;
}

.lock-icon {
  color: #D1D5DB;
}

.pb-10 {
  padding-bottom: 40px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.write-review-btn {
  font-size: 14px;
  color: #007AFF;
  font-weight: 600;
  background: none;
  border: none;
  cursor: pointer;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.review-item {
  display: flex;
  gap: 16px;
}

.review-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #E5E5E7;
}

.review-content {
  flex: 1;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.reviewer-name {
  font-weight: 700;
  font-size: 14px;
  color: #1D1D1F;
  margin: 0 0 4px 0;
}

.review-stars {
  display: flex;
  gap: 2px;
  color: #FCD34D;
  font-size: 12px;
}

.review-time {
  font-size: 12px;
  color: #9CA3AF;
}

.review-text {
  font-size: 14px;
  color: #6B7280;
  line-height: 1.6;
  margin: 0;
}

.review-divider {
  width: 100%;
  height: 1px;
  background: #F3F4F6;
}

/* ========== 侧边栏 ========== */
.sidebar-content {
  display: none;
}

@media (min-width: 1024px) {
  .sidebar-content {
    display: block;
  }
}

.recommendations {
  margin-top: 24px;
}

.sidebar-card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #F3F4F6;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 700;
  color: #6B7280;
  text-transform: uppercase;
  margin: 0 0 16px 0;
  letter-spacing: 0.05em;
}

.sidebar-text {
  font-size: 14px;
  color: #6B7280;
  line-height: 1.6;
  margin: 0 0 16px 0;
}

.social-links {
  display: flex;
  gap: 8px;
}

.social-link {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6B7280;
  transition: all 0.3s;
  text-decoration: none;
}

.social-link:hover {
  background: #000000;
  color: white;
}

.recommend-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommend-item {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 8px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.recommend-item:hover {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.recommend-cover {
  width: 48px;
  height: 64px;
  object-fit: cover;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.recommend-info {
  flex: 1;
}

.recommend-title {
  font-weight: 700;
  font-size: 14px;
  color: #1D1D1F;
  margin: 0 0 4px 0;
  transition: color 0.3s;
}

.recommend-item:hover .recommend-title {
  color: #007AFF;
}

.recommend-author {
  font-size: 12px;
  color: #86868B;
  margin: 0;
}

/* ========== 底部购买栏 ========== */
.purchase-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(48px);
  -webkit-backdrop-filter: blur(48px);
  border-top: 1px solid #E5E5E7;
  padding: 16px;
  z-index: 50;
  animation: slide-up 0.3s ease;
}

@keyframes slide-up {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.purchase-content {
  max-width: 1152px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.purchase-info {
  display: none;
}

@media (min-width: 768px) {
  .purchase-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.purchase-cover {
  width: 40px;
  height: 56px;
  object-fit: cover;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #F3F4F6;
}

.purchase-details {
  text-align: left;
}

.purchase-title {
  font-weight: 700;
  font-size: 14px;
  color: #1D1D1F;
  margin: 0 0 2px 0;
}

.purchase-author {
  font-size: 12px;
  color: #86868B;
  margin: 0;
}

.purchase-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  flex: 1;
}

@media (min-width: 768px) {
  .purchase-actions {
    flex: none;
  }
}

.purchase-price {
  display: flex;
  flex-direction: column;
}

@media (min-width: 768px) {
  .purchase-price {
    align-items: flex-end;
  }
}

.price {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1D1D1F;
}

.vip-discount {
  font-size: 12px;
  color: #10B981;
  font-weight: 600;
  display: none;
}

@media (min-width: 768px) {
  .vip-discount {
    display: block;
  }
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex: 1;
}

@media (min-width: 768px) {
  .action-buttons {
    flex: none;
  }
}

.add-to-shelf-btn {
  flex: 1;
  background: #F3F4F6;
  color: #1D1D1F;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: background 0.3s;
}

@media (min-width: 768px) {
  .add-to-shelf-btn {
    flex: none;
  }
}

.add-to-shelf-btn:hover {
  background: #E5E7EB;
}

.buy-now-btn {
  flex: 2;
  background: #000000;
  color: white;
  padding: 12px 32px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

@media (min-width: 768px) {
  .buy-now-btn {
    flex: none;
  }
}

.buy-now-btn:hover {
  background: #2c2c2e;
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

/* ========== 响应式设计 ========== */
@media (max-width: 768px) {
  .nav-title {
    opacity: 0;
  }

  .hero-section {
    padding: 64px 16px 48px;
  }

  .book-title {
    font-size: 2rem;
  }

  .book-subtitle {
    font-size: 1rem;
  }
}
</style>
