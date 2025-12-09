<template>
  <div class="card-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在加载图书数据...</p>
    </div>

    <div v-else-if="books.length === 0" class="empty-state">
      <p>暂无图书数据</p>
    </div>

    <!-- 图书网格布局 -->
    <div v-else class="books-grid">
      <div
        v-for="(book, index) in filteredBooks"
        :key="book.id"
        class="book-card"
      >
        <!-- 卡片头部 -->
        <div class="card-header">
          <span class="category-badge">{{ book.category }}</span>
          <div class="rating-stars">
            <i class="ri-star-fill" v-for="n in Math.floor(book.rating)" :key="n"></i>
            <i class="ri-star-half-fill" v-if="book.rating % 1 !== 0"></i>
          </div>
        </div>

        <!-- 图书封面 -->
        <div class="book-cover" @click="handleCardClick(book)">
          <div class="cover-placeholder"></div>
        </div>

        <!-- 图书信息 -->
        <h3 class="book-title">{{ book.title }}</h3>
        <p class="book-desc">{{ book.description?.substring(0, 30) }}...</p>
        <button class="action-btn" @click="addToCart(book)">立即购买</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
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
  return books.value.slice(0, 10) // 只显示前10本书
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

// 根据索引返回不同的渐变背景
const getBookColor = (index: number) => {
  return '#000000'  // 纯黑色
}
</script>

<style scoped>
/* 引入 Remix Icon */
@import url('https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css');

.card-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
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

/* 图书网格布局 */
.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.book-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  padding: 1.5rem;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
  border: 1px solid white;
  animation: float 6s ease-in-out infinite;
  transition: all 0.3s ease;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.category-badge {
  font-size: 11px;
  font-weight: 700;
  color: #86868B;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.rating-stars {
  display: flex;
  gap: 2px;
  color: #FCD34D;
  font-size: 12px;
}

/* 图书封面 */
.book-cover {
  position: relative;
  width: 100%;
  height: 192px;
  border-radius: 12px;
  margin-bottom: 1rem;
  overflow: hidden;
  cursor: pointer;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
  color: #007AFF;
  transition: transform 0.5s ease;
  background: white;
  border: 1px solid #E5E5E7;
  position: relative;
}

.cover-placeholder::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.05) 0%, rgba(52, 199, 89, 0.05) 100%);
  z-index: 0;
}

.book-cover:hover .cover-placeholder {
  transform: scale(1.05);
}

/* 图书标题 */
.book-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 0.25rem;
  color: #1D1D1F;
}

/* 图书描述 */
.book-desc {
  font-size: 14px;
  color: #6B7280;
  margin-bottom: 1rem;
}

/* 操作按钮 */
.action-btn {
  width: 100%;
  padding: 0.75rem;
  background: #000000;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: #2c2c2e;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

@media (max-width: 900px) {
  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }

  .section-title {
    font-size: 36px;
  }

  .section-subtitle {
    font-size: 16px;
  }
}

@media (max-width: 600px) {
  .books-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
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

  .book-cover {
    height: 250px;
  }
}
</style>