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
        <!-- 图书封面 -->
        <div class="book-cover" @click="handleCardClick(book)">
          <div class="cover-placeholder"></div>
          <!-- 评分标签 -->
          <div class="rating-badge">
            <i class="ri-star-fill"></i>
            {{ book.rating?.toFixed(1) || '4.5' }}
          </div>
        </div>

        <!-- 图书信息 -->
        <div class="book-info">
          <h3 class="book-title">{{ book.title }}</h3>
          <p class="book-author">{{ book.author }}</p>
          <div class="book-footer">
            <span class="book-price">¥{{ typeof book.price === 'number' ? book.price.toFixed(2) : parseFloat(book.price).toFixed(2) }}</span>
            <button class="add-btn" @click="addToCart(book)">
              <i class="ri-add-line"></i>
            </button>
          </div>
        </div>
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
import { getCart, addToCart as addToCartApi } from '../api/cartApi'

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

// 随机选择10本书进行展示
const filteredBooks = computed(() => {
  if (books.value.length === 0) return []

  // 创建图书数组的副本并打乱顺序
  const shuffled = [...books.value].sort(() => Math.random() - 0.5)

  // 返回随机的前10本书
  return shuffled.slice(0, Math.min(10, shuffled.length))
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

// 获取当前用户ID
const getUserId = (): number | null => {
  const userId = localStorage.getItem('user_id')
  return userId ? parseInt(userId) : null
}

// 检查用户是否登录
const checkUserLogin = (): boolean => {
  const isLoggedIn = localStorage.getItem('isLoggedIn')
  return isLoggedIn === 'true'
}

const handleCardClick = (book: Book) => {
  // 跳转到图书详情页
  router.push({ name: 'bookDetail', params: { id: book.id } })
}

// 添加到购物车 - 使用真实API
const addToCart = async (book: Book) => {
  if (!checkUserLogin()) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  const userId = getUserId()
  if (!userId) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    await addToCartApi(userId, book.id, 1)
    ElMessage.success(`《${book.title}》已添加到购物车！`)

    // 更新购物车数量
    const response = await getCart(userId)
    const totalQuantity = response.items.reduce((total, item) => total + item.quantity, 0)

    const event = new CustomEvent('cart-updated', {
      detail: { count: totalQuantity }
    })
    window.dispatchEvent(event)
  } catch (error) {
    console.error('添加到购物车失败:', error)
    ElMessage.error('添加到购物车失败')
  }
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
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.book-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* 图书封面 */
.book-cover {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  overflow: hidden;
  cursor: pointer;
  background: #F5F5F7;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #E5E5E7 0%, #F5F5F7 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}

.book-cover:hover .cover-placeholder {
  transform: scale(1.05);
}

/* 评分标签 */
.rating-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.rating-badge i {
  color: #FCD34D;
  font-size: 12px;
}

/* 图书信息 */
.book-info {
  padding: 16px;
}

/* 图书标题 */
.book-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #1D1D1F;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 作者名 */
.book-author {
  font-size: 13px;
  color: #86868B;
  margin: 0 0 12px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 底部操作区 */
.book-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.book-price {
  font-size: 18px;
  font-weight: 700;
  color: #1D1D1F;
}

.add-btn {
  width: 36px;
  height: 36px;
  background: #000000;
  color: white;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 20px;
}

.add-btn:hover {
  background: #2c2c2e;
  transform: scale(1.1);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
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