<template>
  <div class="card-container">
    <div class="container-header">
      <h3 class="section-title">精选图书大全</h3>
      <p class="section-subtitle">探索知识的无限可能</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在加载图书数据...</p>
    </div>

    <div v-else-if="books.length === 0" class="empty-state">
      <p>暂无图书数据</p>
    </div>

    <!-- 瀑布流网格布局 -->
    <div v-else class="masonry-grid">
      <div
        v-for="(book, index) in filteredBooks"
        :key="book.id"
        class="masonry-item"
        :class="getCardSizeClass(index)"
        @click="handleCardClick(book)"
      >
        <!-- 图书封面 -->
        <div class="book-cover" :style="{ background: getBookColor(index) }">
          <div class="cover-overlay">
            <div class="overlay-content">
              <div class="quick-actions">
                <button class="action-btn view-btn" @click.stop="handleCardClick(book)">
                  <el-icon><View /></el-icon>
                </button>
                <button class="action-btn cart-btn" @click.stop="addToCart(book)">
                  <el-icon><ShoppingCart /></el-icon>
                </button>
              </div>
            </div>
          </div>
          <!-- 分类标签 -->
          <div class="category-badge">{{ book.category }}</div>
          <!-- 评分角标 -->
          <div class="rating-badge">
            <el-icon class="star-icon"><Star /></el-icon>
            <span>{{ book.rating.toFixed(1) }}</span>
          </div>
        </div>

        <!-- 图书信息 -->
        <div class="book-info">
          <h4 class="book-title">{{ book.title }}</h4>
          <p class="book-author">
            <el-icon class="author-icon"><User /></el-icon>
            {{ book.author }}
          </p>
          <p class="book-description">{{ book.description }}</p>

          <!-- 底部信息栏 -->
          <div class="info-footer">
            <div class="price-tag">
              <span class="price-symbol">¥</span>
              <span class="price-value">{{ book.price }}</span>
            </div>
            <button class="buy-now-btn" @click.stop="addToCart(book)">
              立即购买
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ShoppingCart, View, Star, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getAllBooks, getAllCategories, searchBooks, type Book, type SearchBooksParams } from '../api/bookApi'

const router = useRouter()

const categories = ref<string[]>(['全部'])
const selectedCategory = ref('全部')
const searchQuery = ref('')
const loading = ref(false)

const books = ref<Book[]>([])

// 从后端加载分类数据
const loadCategories = async () => {
  try {
    const categoriesData = await getAllCategories()
    // 添加"全部"选项并合并后端返回的分类名称
    categories.value = ['全部', ...categoriesData.map(cat => cat.name)]
    console.log('成功加载分类:', categories.value)
  } catch (error) {
    console.error('加载分类失败:', error)
    // 如果加载失败，使用默认分类
    categories.value = ['全部', '技术', '文学', '历史', '科学', '艺术', '哲学', '心理学', '经济', '管理', '生活']
  }
}

// 从后端加载图书数据
const loadBooks = async () => {
  loading.value = true
  try {
    const booksData = await getAllBooks()
    // 转换数据格式以适配前端需求
    books.value = booksData.map(book => ({
      ...book,
      price: typeof book.price === 'number' ? book.price.toFixed(2) : book.price,
      rating: book.rating || 4.5,
      image: book.image || '/images/book-placeholder.svg'
    }))
    console.log('成功加载图书:', books.value.length, '本')
  } catch (error) {
    console.error('加载图书失败:', error)
    ElMessage.error('加载图书数据失败，请刷新页面重试')
  } finally {
    loading.value = false
  }
}

// 执行搜索
const performSearch = async () => {
  loading.value = true
  try {
    // 构建搜索参数
    const params: SearchBooksParams = {}

    if (searchQuery.value.trim()) {
      params.q = searchQuery.value.trim()
    }

    if (selectedCategory.value && selectedCategory.value !== '全部') {
      params.category = selectedCategory.value
    }

    // 如果既没有搜索词也没有选择分类，则加载所有图书
    if (!params.q && !params.category) {
      await loadBooks()
      return
    }

    // 调用搜索API
    const searchResults = await searchBooks(params)

    // 转换数据格式
    books.value = searchResults.map(book => ({
      ...book,
      price: typeof book.price === 'number' ? book.price.toFixed(2) : book.price,
      rating: book.rating || 4.5,
      image: book.image || '/images/book-placeholder.svg'
    }))

    console.log(`搜索成功，找到 ${books.value.length} 本图书`)

    if (books.value.length === 0) {
      ElMessage.info('未找到符合条件的图书')
    }
  } catch (error) {
    console.error('搜索图书失败:', error)
    ElMessage.error('搜索失败，请重试')
  } finally {
    loading.value = false
  }
}

// 页面加载时获取分类和图书
onMounted(() => {
  loadCategories()
  loadBooks()
  window.addEventListener('book-search', handleSearch as EventListener)
})

onUnmounted(() => {
  window.removeEventListener('book-search', handleSearch as EventListener)
})

// 由于现在使用后端搜索，不再需要前端过滤
const filteredBooks = computed(() => {
  return books.value
})

const selectCategory = async (category: string) => {
  selectedCategory.value = category
  // 分类改变时执行搜索
  await performSearch()
}

const handleSearch = async (event: CustomEvent) => {
  searchQuery.value = event.detail.query
  // 搜索关键词改变时执行搜索
  await performSearch()
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

const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  target.src = '/images/book-placeholder.svg'
}

const handleCardClick = (book: Book) => {
  // 跳转到图书详情页
  router.push({ name: 'bookDetail', params: { id: book.id } })
}

const addToCart = (book: Book) => {
  window.dispatchEvent(new CustomEvent('add-to-cart', {
    detail: { book }
  }))
}

// 根据索引返回不同的卡片尺寸类（创建不规则网格效果）
const getCardSizeClass = (index: number) => {
  const patterns = ['small', 'medium', 'large', 'medium', 'small', 'large']
  return patterns[index % patterns.length]
}

// 根据索引返回不同的纯色背景 - 改为纯黑色
const getBookColor = (index: number) => {
  return '#000000'  // 纯黑色
}
</script>

<style scoped>
.card-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.container-header {
  text-align: center;
  margin-bottom: 50px;
  padding: 20px 0;
}

.section-title {
  font-size: 48px;
  font-weight: 900;
  background: linear-gradient(135deg, #10b981, #34d399, #6ee7b7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 15px 0;
  text-shadow: 0 0 30px rgba(16, 185, 129, 0.3);
  letter-spacing: 2px;
}

.section-subtitle {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  font-weight: 300;
  letter-spacing: 1px;
}

/* 加载状态样式 */
.loading-state {
  text-align: center;
  padding: 100px 20px;
  color: rgba(255, 255, 255, 0.8);
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(16, 185, 129, 0.2);
  border-top-color: #10b981;
  border-radius: 50%;
  margin: 0 auto 25px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  font-size: 18px;
  font-weight: 500;
  color: #10b981;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 100px 20px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 20px;
}

/* 瀑布流网格布局 */
.masonry-grid {
  column-count: 4;
  column-gap: 20px;
  margin-top: 40px;
}

.masonry-item {
  break-inside: avoid;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  backdrop-filter: blur(20px);
  position: relative;
}

.masonry-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), transparent);
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
  z-index: 1;
}

.masonry-item:hover::before {
  opacity: 1;
}

.masonry-item:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow:
    0 20px 40px rgba(16, 185, 129, 0.2),
    0 0 0 1px rgba(16, 185, 129, 0.3);
  border-color: rgba(16, 185, 129, 0.4);
}

/* 不同尺寸的卡片 */
.masonry-item.small .book-cover {
  height: 200px;
}

.masonry-item.medium .book-cover {
  height: 280px;
}

.masonry-item.large .book-cover {
  height: 360px;
}

/* 图书封面 */
.book-cover {
  position: relative;
  width: 100%;
  overflow: hidden;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.masonry-item:hover .book-cover {
  filter: brightness(1.15) saturate(1.2);
}

/* 封面遮罩层 */
.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.3) 0%,
    rgba(0, 0, 0, 0.7) 100%
  );
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.4s ease;
  z-index: 2;
}

.masonry-item:hover .cover-overlay {
  opacity: 1;
  backdrop-filter: blur(5px);
}

.overlay-content {
  transform: translateY(20px);
  transition: transform 0.4s ease;
}

.masonry-item:hover .overlay-content {
  transform: translateY(0);
}

/* 快捷操作按钮 */
.quick-actions {
  display: flex;
  gap: 15px;
}

.action-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: 2px solid #10b981;
  background: rgba(0, 0, 0, 0.6);
  color: #10b981;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  font-size: 20px;
}

.action-btn:hover {
  background: #10b981;
  color: #000;
  transform: scale(1.15) rotate(10deg);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.6);
}

.action-btn .el-icon {
  font-size: 20px;
}

/* 分类角标 */
.category-badge {
  position: absolute;
  top: 15px;
  left: 15px;
  padding: 6px 14px;
  background: rgba(16, 185, 129, 0.9);
  color: #000;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  z-index: 3;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
  transition: all 0.3s ease;
}

.masonry-item:hover .category-badge {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6);
}

/* 评分角标 */
.rating-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  padding: 6px 12px;
  background: rgba(0, 0, 0, 0.8);
  color: #10b981;
  font-size: 13px;
  font-weight: 700;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  z-index: 3;
  display: flex;
  align-items: center;
  gap: 4px;
  border: 1px solid rgba(16, 185, 129, 0.3);
  transition: all 0.3s ease;
}

.rating-badge .star-icon {
  color: #fbbf24;
  font-size: 14px;
}

.masonry-item:hover .rating-badge {
  transform: scale(1.1);
  border-color: rgba(16, 185, 129, 0.6);
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
}

/* 图书信息区域 */
.book-info {
  padding: 20px;
  position: relative;
  z-index: 2;
}

.book-title {
  font-size: 18px;
  font-weight: 800;
  color: #fff;
  margin: 0 0 12px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: color 0.3s ease;
}

.masonry-item:hover .book-title {
  color: #10b981;
}

.book-author {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 12px 0;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.author-icon {
  font-size: 14px;
  color: #10b981;
}

.book-description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 16px 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 底部信息栏 */
.info-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid rgba(16, 185, 129, 0.1);
}

.price-tag {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.price-symbol {
  font-size: 16px;
  color: #10b981;
  font-weight: 700;
}

.price-value {
  font-size: 24px;
  font-weight: 900;
  color: #10b981;
  text-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
}

.buy-now-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  border-radius: 20px;
  color: #000;
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.buy-now-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
  background: linear-gradient(135deg, #34d399, #10b981);
}

.buy-now-btn:active {
  transform: translateY(0);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .masonry-grid {
    column-count: 3;
  }
}

@media (max-width: 900px) {
  .masonry-grid {
    column-count: 2;
  }

  .section-title {
    font-size: 36px;
  }

  .section-subtitle {
    font-size: 16px;
  }
}

@media (max-width: 600px) {
  .masonry-grid {
    column-count: 1;
    column-gap: 0;
  }

  .masonry-item {
    margin-bottom: 15px;
  }

  .section-title {
    font-size: 28px;
  }

  .section-subtitle {
    font-size: 14px;
  }

  .book-info {
    padding: 15px;
  }

  .masonry-item.small .book-cover,
  .masonry-item.medium .book-cover,
  .masonry-item.large .book-cover {
    height: 250px;
  }
}
</style>