<template>
  <div class="book-manage-container">
    <div class="page-header">
      <h2>图书管理</h2>
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索书名、作者或ISBN..."
          class="search-input"
        />
        <button
          v-if="searchKeyword"
          class="clear-btn"
          @click="searchKeyword = ''"
          title="清除搜索"
        >
          ×
        </button>
      </div>
      <button class="add-btn" @click="handleAddBook" :disabled="loading || isProcessing">
        添加图书
      </button>
    </div>

    <!-- 图书列表 -->
    <div class="book-list">
      <div class="list-header">
        <div class="header-item">ID</div>
        <div class="header-item">书名</div>
        <div class="header-item">作者</div>
        <div class="header-item">价格</div>
        <div class="header-item">库存</div>
        <div class="header-item">操作</div>
      </div>
      <div v-if="loading" class="loading-message">
        加载中...
      </div>
      <div v-else v-for="book in filteredBooks" :key="book.id" class="book-item">
        <div class="book-info">{{ book.id }}</div>
        <div class="book-info">{{ book.title }}</div>
        <div class="book-info">{{ book.author }}</div>
        <div class="book-info">¥{{ book.price.toFixed(2) }}</div>
        <div class="book-info" :class="{ 'low-stock': book.stock < 20 }">{{ book.stock }}</div>
        <div class="book-actions">
          <button class="edit-btn" @click="editBook(book)" :disabled="isProcessing">
            编辑
          </button>
          <button class="delete-btn" @click="deleteBook(book.id)" :disabled="isProcessing">
            删除
          </button>
        </div>
      </div>
      <div v-if="!loading && filteredBooks.length === 0" class="empty-message">
        {{ searchKeyword ? '未找到匹配的图书' : '暂无图书数据' }}
      </div>
    </div>

    <!-- 添加/编辑图书表单 -->
    <div v-if="showAddForm || showEditForm" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ showEditForm ? '编辑图书' : '添加图书' }}</h3>
          <button class="close-btn" @click="closeModal" :disabled="isProcessing">&times;</button>
        </div>
        <form @submit.prevent="submitForm" class="book-form">
          <div class="form-group">
            <label for="title">书名</label>
            <input
              id="title"
              v-model="formData.title"
              type="text"
              required
              placeholder="请输入书名"
            />
          </div>
          <div class="form-group">
            <label for="author">作者</label>
            <input
              id="author"
              v-model="formData.author"
              type="text"
              required
              placeholder="请输入作者"
            />
          </div>
          <div class="form-group">
            <label for="price">价格</label>
            <input
              id="price"
              v-model.number="formData.price"
              type="number"
              step="0.01"
              min="0"
              required
              placeholder="请输入价格"
            />
          </div>
          <div class="form-group">
            <label for="stock">库存</label>
            <input
              id="stock"
              v-model.number="formData.stock"
              type="number"
              min="0"
              required
              placeholder="请输入库存"
            />
          </div>
          <div class="form-group">
            <label for="isbn">ISBN</label>
            <input
              id="isbn"
              v-model="formData.isbn"
              type="text"
              placeholder="系统自动生成"
              readonly
            />
          </div>
          <div class="form-group">
            <label for="category_id">图书类别</label>
            <select
              id="category_id"
              v-model="formData.category_id"
              :disabled="loadingCategories"
            >
              <option value="">请选择图书类别</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="description">图书描述</label>
            <textarea
              id="description"
              v-model="formData.description"
              rows="4"
              placeholder="请输入图书描述"
            ></textarea>
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="closeModal">取消</button>
            <button type="submit" class="submit-btn">
              {{ showEditForm ? '保存' : '添加' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 导入接口
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getAllBooks,
  addBook,
  updateBook,
  deleteBook as deleteBookApi,
  getAllCategories,
  type Category
} from '../api/bookApi'
import { eventBus, EventTypes } from '../utils/eventBus'

// 定义图书接口
interface Book {
  id: number
  title: string
  author: string
  price: number
  stock: number
  isbn?: string
  category?: string
  category_id?: number
  description?: string
}

// 定义图书分类接口
// 现在从 bookApi 导入 Category 接口

// 状态变量
const books = ref<Book[]>([])
const categories = ref<Category[]>([])
const showAddForm = ref(false)
const showEditForm = ref(false)
const currentBookId = ref<number | null>(null)
const loading = ref(false)
const isProcessing = ref(false)
const loadingCategories = ref(false)
const searchKeyword = ref('')

// 表单数据
const formData = reactive({
  title: '',
  author: '',
  price: 0,
  stock: 0,
  isbn: '',
  category_id: null as number | null,
  description: ''
})

// 过滤后的图书列表
const filteredBooks = computed(() => {
  if (!searchKeyword.value.trim()) {
    return books.value
  }

  const keyword = searchKeyword.value.toLowerCase()
  return books.value.filter(book =>
    book.title.toLowerCase().includes(keyword) ||
    book.author.toLowerCase().includes(keyword) ||
    (book.isbn && book.isbn.toLowerCase().includes(keyword))
  )
})

// 生命周期钩子
onMounted(() => {
  loadBooks()
  loadCategories()
})

// 处理添加图书
const handleAddBook = () => {
  // 重置表单
  resetForm()
  // 生成随机ISBN
  formData.isbn = generateISBN()
  // 显示添加表单
  showAddForm.value = true
}

// 加载图书数据
const loadBooks = async () => {
  loading.value = true
  try {
    const data = await getAllBooks()
    books.value = data
  } catch (error) {
    ElMessage.error('加载图书列表失败，请检查后端服务是否正常运行')
    console.error('加载图书列表失败:', error)
    // 不使用模拟数据，保持列表为空
    books.value = []
  } finally {
    loading.value = false
  }
}

// 加载图书分类
const loadCategories = async () => {
  loadingCategories.value = true
  try {
    // 从后端API获取分类数据
    const data = await getAllCategories()
    categories.value = data
  } catch (error) {
    ElMessage.error('加载图书分类失败')
    console.error('加载图书分类失败:', error)
    // 失败时保持列表为空
    categories.value = []
  } finally {
    loadingCategories.value = false
  }
}

// 编辑图书
const editBook = (book: Book) => {
  currentBookId.value = book.id
  formData.title = book.title
  formData.author = book.author
  formData.price = book.price
  formData.stock = book.stock
  formData.isbn = book.isbn || ''
  formData.category_id = book.category_id || null
  formData.description = book.description || ''
  showEditForm.value = true
}

// 删除图书
const deleteBook = async (id: number) => {
  if (!confirm('确定要删除这本书吗？')) {
    return
  }
  
  // 查找要删除的图书信息
  const bookToDelete = books.value.find(book => book.id === id)
  
  isProcessing.value = true
  try {
    await deleteBookApi(id)
    ElMessage.success('图书删除成功')
    
    // 如果找到了图书信息，触发图书下架事件
    if (bookToDelete) {
      eventBus.emit(EventTypes.BOOK_REMOVED, {
        title: bookToDelete.title,
        author: bookToDelete.author,
        time: new Date()
      })
    }
    
    await loadBooks()
  } catch (error) {
    ElMessage.error('图书删除失败')
    console.error('删除图书失败:', error)
  } finally {
    isProcessing.value = false
  }
}

// 提交表单
const submitForm = async () => {
  isProcessing.value = true
  try {
    if (showEditForm.value && currentBookId.value !== null) {
      // 编辑现有图书
      await updateBook(currentBookId.value, formData)
      ElMessage.success('图书更新成功')
    } else {
      // 添加新图书
      await addBook(formData)
      ElMessage.success('图书添加成功')
      
      // 触发新书上架事件通知
      eventBus.emit(EventTypes.NEW_BOOK_ADDED, {
        title: formData.title,
        author: formData.author,
        time: new Date()
      })
    }
    
    // 关闭模态框并重新加载数据
    closeModal()
    await loadBooks()
  } catch (error) {
    ElMessage.error(showEditForm.value ? '图书更新失败' : '图书添加失败')
    console.error(showEditForm.value ? '更新图书失败:' : '添加图书失败:', error)
  } finally {
    isProcessing.value = false
  }
}

// 关闭模态框
const closeModal = () => {
  showAddForm.value = false
  showEditForm.value = false
  resetForm()
}

// 生成随机ISBN编号
const generateISBN = () => {
  // ISBN-13格式: 978-XXX-XXXX-XX-X 或 979-XXX-XXXX-XX-X
  const prefix = Math.random() > 0.5 ? '978' : '979';
  const parts = [prefix];
  
  // 生成其他部分
  parts.push(Math.floor(100 + Math.random() * 900).toString()); // 3位
  parts.push(Math.floor(1000 + Math.random() * 9000).toString()); // 4位
  parts.push(Math.floor(10 + Math.random() * 90).toString()); // 2位
  
  // 计算校验位
  const digits = parts.join('').split('');
  let sum = 0;
  
  for (let i = 0; i < digits.length; i++) {
    const digit = parseInt(digits[i]);
    sum += i % 2 === 0 ? digit : digit * 3;
  }
  
  const checkDigit = (10 - (sum % 10)) % 10;
  parts.push(checkDigit.toString());
  
  // 组合并返回不包含连字符的ISBN
  return parts.join('');
}

// 重置表单
const resetForm = () => {
  formData.title = ''
  formData.author = ''
  formData.price = 0
  formData.stock = 0
  formData.isbn = ''
  formData.category_id = null
  formData.description = ''
  currentBookId.value = null
}
</script>

<style scoped lang="scss">
.book-manage-container {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  font-size: 16px;
  pointer-events: none;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding: 10px 40px 10px 36px;
  background-color: #1e1e1e;
  border: 1px solid #333;
  border-radius: 4px;
  color: #fff;
  font-size: 14px;
  transition: all 0.3s ease;

  &::placeholder {
    color: #666;
  }

  &:focus {
    outline: none;
    border-color: #4caf50;
    box-shadow: 0 0 8px rgba(76, 175, 80, 0.3);
  }
}

.clear-btn {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  color: #999;
  font-size: 24px;
  cursor: pointer;
  padding: 0 8px;
  line-height: 1;
  transition: color 0.2s ease;

  &:hover {
    color: #4caf50;
  }
}

.add-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.3s ease;
  white-space: nowrap;
}

.add-btn:hover {
  background-color: #45a049;
}

/* 图书列表样式 */
.book-list {
  background-color: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
}

.list-header {
  display: grid;
  grid-template-columns: 80px 1fr 1fr 100px 100px 160px;
  background-color: #2a2a2a;
  padding: 16px 20px;
  font-weight: 600;
  color: #4caf50;
  border-bottom: 1px solid #333;
}

.header-item {
  text-align: left;
}

.book-item {
  display: grid;
  grid-template-columns: 80px 1fr 1fr 100px 100px 160px;
  padding: 16px 20px;
  border-bottom: 1px solid #333;
  transition: background-color 0.2s ease;
}

.book-item:hover {
  background-color: #252525;
}

.book-item:last-child {
  border-bottom: none;
}

.book-info {
  display: flex;
  align-items: center;
  color: #e0e0e0;
}

.book-info.low-stock {
  color: #ff4444;
  font-weight: bold;
}

.book-actions {
  display: flex;
  gap: 8px;
}

.edit-btn,
.delete-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s ease;
}

.edit-btn {
  background-color: #2196f3;
  color: white;
}

.edit-btn:hover {
  background-color: #1976d2;
}

.delete-btn {
  background-color: #f44336;
  color: white;
}

.delete-btn:hover {
  background-color: #d32f2f;
}

.loading-message {
  padding: 40px;
  text-align: center;
  color: #4caf50;
  font-weight: 500;
}

.empty-message {
  padding: 40px;
  text-align: center;
  color: #666;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #1e1e1e;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #333;
}

.modal-header h3 {
  margin: 0;
  color: #4caf50;
}

.close-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #fff;
}

/* 表单样式 */
.book-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #e0e0e0;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  background-color: #2a2a2a;
  border: 1px solid #333;
  border-radius: 4px;
  color: #e0e0e0;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4caf50;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.form-group select {
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
}

.cancel-btn,
.submit-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.cancel-btn {
  background-color: #666;
  color: white;
}

.cancel-btn:hover {
  background-color: #555;
}

.submit-btn {
  background-color: #4caf50;
  color: white;
}

.submit-btn:hover {
  background-color: #45a049;
}


</style>