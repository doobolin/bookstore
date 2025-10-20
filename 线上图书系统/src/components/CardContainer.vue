<template>
  <div class="card-container">
    <div class="container-header">
      <h3 class="section-title">精选图书大全</h3>
      <p class="section-subtitle">涵盖各类知识的图书海洋</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在加载图书数据...</p>
    </div>

    <div v-else-if="books.length === 0" class="empty-state">
      <p>暂无图书数据</p>
    </div>

    <div v-else class="books-grid">
      <div 
        v-for="book in filteredBooks" 
        :key="book.id"
        class="book-card"
        @click="handleCardClick(book)"
      >
        <div class="card-image">
          <img :src="book.image" :alt="book.title" @error="handleImageError" />
          <div class="card-overlay">
            <span class="view-details">查看详情</span>
          </div>
        </div>
        
        <div class="card-content">
          <div class="book-category">
            <span class="category-tag" :class="getCategoryClass(book.category)">{{ book.category }}</span>
          </div>
          
          <h4 class="book-title">{{ book.title }}</h4>
          <p class="book-author">{{ book.author }}</p>
          <p class="book-description">{{ book.description }}</p>
          
          <div class="card-footer">
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
            
            <div class="book-price">
              <span class="price-symbol">¥</span>
              <span class="price-number">{{ book.price }}</span>
            </div>
          </div>
          
          <div class="card-actions">
            <el-button 
              type="primary" 
              class="add-to-cart-btn"
              @click.stop="addToCart(book)"
            >
              <el-icon><ShoppingCart /></el-icon>
              加入购物车
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ShoppingCart } from '@element-plus/icons-vue'
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
</script>

<style scoped>
.card-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.container-header {
  text-align: center;
  margin-bottom: 40px;
}

.section-title {
  font-size: 36px;
  font-weight: 800;
  color: #10b981;
  margin: 0 0 10px 0;
  text-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

.section-subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  font-weight: 300;
}

/* 加载状态样式 */
.loading-state {
  text-align: center;
  padding: 80px 20px;
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

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 18px;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 30px;
  margin-top: 40px;
}

.book-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 15px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  backdrop-filter: blur(10px);
}

.book-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(16, 185, 129, 0.2);
  border-color: rgba(16, 185, 129, 0.4);
}

.card-image {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: linear-gradient(135deg, #0a0a0a, #1a1a1a);
  border-bottom: 2px solid rgba(16, 185, 129, 0.2);
}

.card-image::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    transparent 0%,
    rgba(16, 185, 129, 0.1) 50%,
    transparent 100%
  );
  opacity: 0;
  transition: opacity 0.4s ease;
  z-index: 2;
  pointer-events: none;
}

.book-card:hover .card-image::before {
  opacity: 1;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.4s ease;
  position: relative;
  z-index: 1;
}

.book-card:hover .card-image img {
  transform: scale(1.08);
  filter: brightness(1.1);
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.9) 0%,
    rgba(0, 0, 0, 0.6) 50%,
    transparent 100%
  );
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 3;
}

.book-card:hover .card-overlay {
  opacity: 1;
}

.view-details {
  color: #10b981;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 8px 16px;
  border: 2px solid #10b981;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
}

.book-card:hover .view-details {
  background: rgba(16, 185, 129, 0.2);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
  transform: scale(1.05);
}

.card-content {
  padding: 20px;
}

.book-category {
  margin-bottom: 10px;
}

.category-tag {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.category-tag.tech {
  background: linear-gradient(135deg, #00ffff, #0080ff);
  color: white;
}

.category-tag.literature {
  background: linear-gradient(135deg, #ff6b6b, #ff8e53);
  color: white;
}

.category-tag.history {
  background: linear-gradient(135deg, #ffa726, #ffcc02);
  color: white;
}

.category-tag.science {
  background: linear-gradient(135deg, #66bb6a, #43a047);
  color: white;
}

.category-tag.art {
  background: linear-gradient(135deg, #ab47bc, #8e24aa);
  color: white;
}

.category-tag.philosophy {
  background: linear-gradient(135deg, #5c6bc0, #3f51b5);
  color: white;
}

.category-tag.psychology {
  background: linear-gradient(135deg, #ec407a, #d81b60);
  color: white;
}

.category-tag.economy {
  background: linear-gradient(135deg, #26c6da, #00acc1);
  color: white;
}

.category-tag.management {
  background: linear-gradient(135deg, #ff7043, #e64a19);
  color: white;
}

.category-tag.lifestyle {
  background: linear-gradient(135deg, #9ccc65, #689f38);
  color: white;
}

.book-title {
  font-size: 18px;
  font-weight: 700;
  color: white;
  margin: 0 0 8px 0;
  line-height: 1.3;
}

.book-author {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 10px 0;
  font-weight: 500;
}

.book-description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 15px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.book-rating {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rating-text {
  font-size: 14px;
  color: #10b981;
  font-weight: 600;
}

.book-price {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.price-symbol {
  font-size: 14px;
  color: #10b981;
  font-weight: 600;
}

.price-number {
  font-size: 20px;
  font-weight: 800;
  color: white;
}

.card-actions {
  margin-top: 15px;
}

.add-to-cart-btn {
  position: relative;
  width: 100%;
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 8px;
  color: white;
  font-weight: 700;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.add-to-cart-btn:hover {
  background: #10b981;
  border-color: #10b981;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.add-to-cart-btn:active {
  transform: translateY(-1px);
}

.add-to-cart-btn .el-icon {
  margin-right: 4px;
  transition: all 0.3s ease;
}

.add-to-cart-btn:hover .el-icon {
  filter: drop-shadow(0 0 3px rgba(255, 255, 255, 0.6));
}

/* 响应式设计 */
@media (max-width: 768px) {
  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }

  .section-title {
    font-size: 28px;
  }

  .section-subtitle {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .books-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .section-title {
    font-size: 24px;
  }

  .book-card {
    margin: 0 10px;
  }
}
</style>