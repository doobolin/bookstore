<template>
  <div class="book-manage-container">
    <!-- 标签页切换 -->
    <div class="tabs-container">
      <button
        :class="['tab-btn', { active: activeTab === 'available' }]"
        @click="activeTab = 'available'"
      >
        已上架图书
        <span class="tab-count">{{ availableBooks.length }}</span>
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'pending' }]"
        @click="activeTab = 'pending'"
      >
        进货图书
        <span class="tab-count">{{ pendingBooks.length }}</span>
      </button>
    </div>

    <!-- 已上架图书 -->
    <div v-if="activeTab === 'available'" class="tab-content">
      <div class="page-header">
        <div class="search-box">
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
      </div>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <div class="filter-group">
          <label class="filter-label">类别筛选：</label>
          <select v-model="selectedCategory" class="filter-select" :disabled="loadingCategories">
            <option value="">全部类别</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">库存状态：</label>
          <select v-model="stockFilter" class="filter-select">
            <option value="">全部</option>
            <option value="low">低库存预警 (< 20)</option>
            <option value="normal">正常库存 (≥ 20)</option>
          </select>
        </div>
        <div class="filter-stats">
          <span v-if="lowStockCount > 0" class="low-stock-warning">
            ⚠️ {{ lowStockCount }} 本图书库存不足
          </span>
        </div>
      </div>

      <!-- 已上架图书列表 -->
      <div class="book-list">
        <div class="list-header available-header">
          <div class="header-item">ID</div>
          <div class="header-item">书名</div>
          <div class="header-item">作者</div>
          <div class="header-item">ISBN</div>
          <div class="header-item">价格</div>
          <div class="header-item">库存</div>
          <div class="header-item">操作</div>
        </div>
        <div v-if="loading" class="loading-message">
          加载中...
        </div>
        <div v-else v-for="book in filteredAvailableBooks" :key="book.id" class="book-item available-item">
          <div class="book-info">{{ book.id }}</div>
          <div class="book-info">{{ book.title }}</div>
          <div class="book-info">{{ book.author }}</div>
          <div class="book-info">{{ book.isbn || '-' }}</div>
          <div class="book-info">¥{{ book.price?.toFixed(2) }}</div>
          <div class="book-info" :class="{ 'low-stock': book.stock && book.stock < 20 }">{{ book.stock }}</div>
          <div class="book-actions">
            <button class="restock-btn" @click="restockBook(book)" :disabled="isProcessing">
              进货
            </button>
            <button class="edit-btn" @click="editBook(book)" :disabled="isProcessing">
              编辑
            </button>
            <button class="delete-btn" @click="deleteBook(book.id)" :disabled="isProcessing">
              下架
            </button>
          </div>
        </div>
        <div v-if="!loading && filteredAvailableBooks.length === 0" class="empty-message">
          {{ searchKeyword ? '未找到匹配的图书' : '暂无已上架图书' }}
        </div>
      </div>
    </div>

    <!-- 进货图书 -->
    <div v-if="activeTab === 'pending'" class="tab-content">
      <div class="page-header">
        <div class="header-title">
          <h3>进货图书列表</h3>
          <p class="subtitle">添加图书信息后，点击"上架"按钮设置价格和库存</p>
        </div>
        <button class="add-btn" @click="handleAddBook" :disabled="loading || isProcessing">
          ➕ 添加图书
        </button>
      </div>

      <!-- 进货图书列表 -->
      <div class="book-list">
        <div class="list-header pending-header">
          <div class="header-item">ID</div>
          <div class="header-item">书名</div>
          <div class="header-item">作者</div>
          <div class="header-item">ISBN</div>
          <div class="header-item">类别</div>
          <div class="header-item">操作</div>
        </div>
        <div v-if="loading" class="loading-message">
          加载中...
        </div>
        <div v-else v-for="book in pendingBooks" :key="book.id" class="book-item pending-item">
          <div class="book-info">{{ book.id }}</div>
          <div class="book-info">{{ book.title }}</div>
          <div class="book-info">{{ book.author }}</div>
          <div class="book-info">{{ book.isbn || '-' }}</div>
          <div class="book-info">{{ book.category || '-' }}</div>
          <div class="book-actions">
            <button class="launch-btn" @click="launchBook(book)" :disabled="isProcessing">
              📦 上架
            </button>
            <button class="edit-btn" @click="editPendingBook(book)" :disabled="isProcessing">
              编辑
            </button>
            <button class="delete-btn" @click="deletePendingBook(book.id)" :disabled="isProcessing">
              删除
            </button>
          </div>
        </div>
        <div v-if="!loading && pendingBooks.length === 0" class="empty-message">
          暂无待上架图书，点击"添加图书"按钮开始进货
        </div>
      </div>
    </div>

    <!-- 添加进货图书表单模态框 -->
    <div v-if="showAddForm" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>添加进货图书</h3>
          <button class="close-btn" @click="closeModal" :disabled="isProcessing">&times;</button>
        </div>
        <form @submit.prevent="submitAddForm" class="book-form">
          <div class="form-group">
            <label for="title">书名 *</label>
            <input
              id="title"
              v-model="formData.title"
              type="text"
              required
              placeholder="请输入书名"
            />
          </div>
          <div class="form-group">
            <label for="author">作者 *</label>
            <input
              id="author"
              v-model="formData.author"
              type="text"
              required
              placeholder="请输入作者"
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
              <option :value="null">请选择图书类别</option>
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
              placeholder="请输入图书描述（选填）"
            ></textarea>
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="closeModal" :disabled="isProcessing">取消</button>
            <button type="submit" class="submit-btn" :disabled="isProcessing">
              {{ isProcessing ? '添加中...' : '添加到进货列表' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 编辑进货图书表单模态框 -->
    <div v-if="showEditPendingForm" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>编辑进货图书</h3>
          <button class="close-btn" @click="closeModal" :disabled="isProcessing">&times;</button>
        </div>
        <form @submit.prevent="submitEditPendingForm" class="book-form">
          <div class="form-group">
            <label for="edit_title">书名 *</label>
            <input
              id="edit_title"
              v-model="editFormData.title"
              type="text"
              required
              placeholder="请输入书名"
            />
          </div>
          <div class="form-group">
            <label for="edit_author">作者 *</label>
            <input
              id="edit_author"
              v-model="editFormData.author"
              type="text"
              required
              placeholder="请输入作者"
            />
          </div>
          <div class="form-group">
            <label for="edit_isbn">ISBN</label>
            <input
              id="edit_isbn"
              v-model="editFormData.isbn"
              type="text"
              placeholder="ISBN"
              readonly
            />
          </div>
          <div class="form-group">
            <label for="edit_category_id">图书类别</label>
            <select
              id="edit_category_id"
              v-model="editFormData.category_id"
              :disabled="loadingCategories"
            >
              <option :value="null">请选择图书类别</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="edit_description">图书描述</label>
            <textarea
              id="edit_description"
              v-model="editFormData.description"
              rows="4"
              placeholder="请输入图书描述（选填）"
            ></textarea>
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="closeModal" :disabled="isProcessing">取消</button>
            <button type="submit" class="submit-btn" :disabled="isProcessing">
              {{ isProcessing ? '保存中...' : '保存修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 上架图书表单模态框 -->
    <div v-if="showLaunchForm" class="modal-overlay" @click="closeModal">
      <div class="modal-content launch-modal" @click.stop>
        <div class="modal-header">
          <h3>图书上架</h3>
          <button class="close-btn" @click="closeModal" :disabled="isProcessing">&times;</button>
        </div>
        <form @submit.prevent="submitLaunchForm" class="book-form">
          <div class="book-preview">
            <h4>图书信息</h4>
            <div class="preview-item">
              <span class="preview-label">书名：</span>
              <span class="preview-value">{{ launchFormData.title }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">作者：</span>
              <span class="preview-value">{{ launchFormData.author }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">ISBN：</span>
              <span class="preview-value">{{ launchFormData.isbn || '-' }}</span>
            </div>
            <div class="preview-item">
              <span class="preview-label">类别：</span>
              <span class="preview-value">{{ launchFormData.category || '-' }}</span>
            </div>
          </div>
          <div class="divider"></div>
          <h4 class="section-title">设置上架信息</h4>
          <div class="form-group">
            <label for="launch_price">上架价格（元）*</label>
            <input
              id="launch_price"
              v-model.number="launchFormData.price"
              type="number"
              step="0.01"
              min="0"
              required
              placeholder="请输入上架价格"
            />
          </div>
          <div class="form-group">
            <label for="launch_stock">库存数量 *</label>
            <input
              id="launch_stock"
              v-model.number="launchFormData.stock"
              type="number"
              min="0"
              required
              placeholder="请输入库存数量"
            />
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="closeModal" :disabled="isProcessing">取消</button>
            <button type="submit" class="submit-btn launch-submit-btn" :disabled="isProcessing">
              {{ isProcessing ? '上架中...' : '✓ 确认上架' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 编辑已上架图书表单模态框 -->
    <div v-if="showEditForm" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>编辑图书</h3>
          <button class="close-btn" @click="closeModal" :disabled="isProcessing">&times;</button>
        </div>
        <form @submit.prevent="submitEditForm" class="book-form">
          <div class="form-group">
            <label for="edit_available_title">书名 *</label>
            <input
              id="edit_available_title"
              v-model="editAvailableFormData.title"
              type="text"
              required
              placeholder="请输入书名"
            />
          </div>
          <div class="form-group">
            <label for="edit_available_author">作者 *</label>
            <input
              id="edit_available_author"
              v-model="editAvailableFormData.author"
              type="text"
              required
              placeholder="请输入作者"
            />
          </div>
          <div class="form-group">
            <label for="edit_available_price">价格（元）*</label>
            <input
              id="edit_available_price"
              v-model.number="editAvailableFormData.price"
              type="number"
              step="0.01"
              min="0"
              required
              placeholder="请输入价格"
            />
          </div>
          <div class="form-group">
            <label for="edit_available_stock">库存</label>
            <input
              id="edit_available_stock"
              v-model.number="editAvailableFormData.stock"
              type="number"
              min="0"
              readonly
              disabled
              placeholder="库存不可编辑，请使用进货功能"
            />
            <p class="field-hint">💡 库存数量不可直接编辑，请使用"进货"功能增加库存</p>
          </div>
          <div class="form-group">
            <label for="edit_available_category_id">图书类别</label>
            <select
              id="edit_available_category_id"
              v-model="editAvailableFormData.category_id"
              :disabled="loadingCategories"
            >
              <option :value="null">请选择图书类别</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="edit_available_description">图书描述</label>
            <textarea
              id="edit_available_description"
              v-model="editAvailableFormData.description"
              rows="4"
              placeholder="请输入图书描述"
            ></textarea>
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="closeModal" :disabled="isProcessing">取消</button>
            <button type="submit" class="submit-btn" :disabled="isProcessing">
              {{ isProcessing ? '保存中...' : '保存修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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
  price?: number
  stock?: number
  isbn?: string
  category?: string
  category_id?: number
  description?: string
  status?: 'available' | 'pending'
}

// 状态变量
const books = ref<Book[]>([])
const categories = ref<Category[]>([])
const activeTab = ref<'available' | 'pending'>('available')
const showAddForm = ref(false)
const showEditForm = ref(false)
const showEditPendingForm = ref(false)
const showLaunchForm = ref(false)
const currentBookId = ref<number | null>(null)
const loading = ref(false)
const isProcessing = ref(false)
const loadingCategories = ref(false)
const searchKeyword = ref('')
const selectedCategory = ref<number | string>('')
const stockFilter = ref('')

// 添加进货图书表单数据
const formData = reactive({
  title: '',
  author: '',
  isbn: '',
  category_id: null as number | null,
  description: '',
  status: 'pending' as 'pending'
})

// 编辑进货图书表单数据
const editFormData = reactive({
  title: '',
  author: '',
  isbn: '',
  category_id: null as number | null,
  description: ''
})

// 上架表单数据
const launchFormData = reactive({
  id: 0,
  title: '',
  author: '',
  isbn: '',
  category: '',
  price: 0,
  stock: 0
})

// 编辑已上架图书表单数据
const editAvailableFormData = reactive({
  title: '',
  author: '',
  price: 0,
  stock: 0,
  category_id: null as number | null,
  description: ''
})

// 计算属性：已上架图书
const availableBooks = computed(() => {
  return books.value.filter(book => book.status === 'available')
})

// 计算属性：进货图书
const pendingBooks = computed(() => {
  return books.value.filter(book => book.status === 'pending')
})

// 低库存图书数量
const lowStockCount = computed(() => {
  return availableBooks.value.filter(book => (book.stock || 0) < 20).length
})

// 过滤后的已上架图书列表
const filteredAvailableBooks = computed(() => {
  let result = availableBooks.value

  // 搜索关键词过滤
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(book =>
      book.title.toLowerCase().includes(keyword) ||
      book.author.toLowerCase().includes(keyword) ||
      (book.isbn && book.isbn.toLowerCase().includes(keyword))
    )
  }

  // 类别过滤
  if (selectedCategory.value) {
    result = result.filter(book => book.category_id === Number(selectedCategory.value))
  }

  // 库存状态过滤
  if (stockFilter.value === 'low') {
    result = result.filter(book => (book.stock || 0) < 20)
  } else if (stockFilter.value === 'normal') {
    result = result.filter(book => (book.stock || 0) >= 20)
  }

  return result
})

// 生命周期钩子
onMounted(() => {
  loadBooks()
  loadCategories()
})

// 处理添加图书
const handleAddBook = () => {
  resetForm()
  formData.isbn = generateISBN()
  showAddForm.value = true
}

// 加载图书数据
const loadBooks = async () => {
  loading.value = true
  try {
    const data = await getAllBooks()
    books.value = data
  } catch (error) {
    ElMessage.error('加载图书列表失败')
    console.error('加载图书列表失败:', error)
    books.value = []
  } finally {
    loading.value = false
  }
}

// 加载图书分类
const loadCategories = async () => {
  loadingCategories.value = true
  try {
    const data = await getAllCategories()
    categories.value = data
  } catch (error) {
    ElMessage.error('加载图书分类失败')
    console.error('加载图书分类失败:', error)
    categories.value = []
  } finally {
    loadingCategories.value = false
  }
}

// 提交添加进货图书表单
const submitAddForm = async () => {
  isProcessing.value = true
  try {
    // 添加进货图书，status设为pending，不需要价格和库存
    await addBook({
      ...formData,
      price: 0,
      stock: 0,
      status: 'pending'
    })
    ElMessage.success('图书已添加到进货列表')
    closeModal()
    await loadBooks()
    // 切换到进货图书标签
    activeTab.value = 'pending'
  } catch (error) {
    ElMessage.error('添加图书失败')
    console.error('添加图书失败:', error)
  } finally {
    isProcessing.value = false
  }
}

// 编辑进货图书
const editPendingBook = (book: Book) => {
  currentBookId.value = book.id
  editFormData.title = book.title
  editFormData.author = book.author
  editFormData.isbn = book.isbn || ''
  editFormData.category_id = book.category_id || null
  editFormData.description = book.description || ''
  showEditPendingForm.value = true
}

// 提交编辑进货图书表单
const submitEditPendingForm = async () => {
  if (currentBookId.value === null) return

  isProcessing.value = true
  try {
    await updateBook(currentBookId.value, {
      ...editFormData,
      status: 'pending'
    })
    ElMessage.success('图书信息已更新')
    closeModal()
    await loadBooks()
  } catch (error) {
    ElMessage.error('更新图书失败')
    console.error('更新图书失败:', error)
  } finally {
    isProcessing.value = false
  }
}

// 上架图书
const launchBook = (book: Book) => {
  launchFormData.id = book.id
  launchFormData.title = book.title
  launchFormData.author = book.author
  launchFormData.isbn = book.isbn || ''
  launchFormData.category = book.category || ''
  launchFormData.price = 0
  launchFormData.stock = 0
  showLaunchForm.value = true
}

// 提交上架表单
const submitLaunchForm = async () => {
  isProcessing.value = true
  try {
    await updateBook(launchFormData.id, {
      price: launchFormData.price,
      stock: launchFormData.stock,
      status: 'available'
    })
    ElMessage.success('图书已成功上架')

    // 触发新书上架事件
    eventBus.emit(EventTypes.NEW_BOOK_ADDED, {
      title: launchFormData.title,
      author: launchFormData.author,
      time: new Date()
    })

    closeModal()
    await loadBooks()
    // 切换到已上架图书标签
    activeTab.value = 'available'
  } catch (error) {
    ElMessage.error('上架失败')
    console.error('上架失败:', error)
  } finally {
    isProcessing.value = false
  }
}

// 编辑已上架图书
const editBook = (book: Book) => {
  currentBookId.value = book.id
  editAvailableFormData.title = book.title
  editAvailableFormData.author = book.author
  editAvailableFormData.price = book.price || 0
  editAvailableFormData.stock = book.stock || 0
  editAvailableFormData.category_id = book.category_id || null
  editAvailableFormData.description = book.description || ''
  showEditForm.value = true
}

// 提交编辑已上架图书表单
const submitEditForm = async () => {
  if (currentBookId.value === null) return

  isProcessing.value = true
  try {
    // 编辑已上架图书时，不更新库存字段
    const { stock, ...updateData } = editAvailableFormData
    await updateBook(currentBookId.value, {
      ...updateData,
      status: 'available'
    })
    ElMessage.success('图书信息已更新')
    closeModal()
    await loadBooks()
  } catch (error) {
    ElMessage.error('更新图书失败')
    console.error('更新图书失败:', error)
  } finally {
    isProcessing.value = false
  }
}

// 进货功能 - 创建新的进货记录
const restockBook = async (book: Book) => {
  if (!confirm(`确定要为《${book.title}》创建进货记录吗？`)) {
    return
  }

  isProcessing.value = true
  try {
    // 创建新的进货记录，保留原有图书信息
    // 生成新的ISBN以避免唯一性冲突
    const newISBN = generateISBN()

    await addBook({
      title: book.title,
      author: book.author,
      isbn: newISBN,
      category_id: book.category_id || null,
      description: book.description || '',
      price: 0,
      stock: 0,
      status: 'pending'
    })
    ElMessage.success('进货记录已创建')
    await loadBooks()
    // 切换到进货图书标签
    activeTab.value = 'pending'
  } catch (error) {
    ElMessage.error('创建进货记录失败')
    console.error('进货操作失败:', error)
  } finally {
    isProcessing.value = false
  }
}

// 删除已上架图书（下架）
const deleteBook = async (id: number) => {
  if (!confirm('确定要下架这本图书吗？下架后图书将从商城中移除。')) {
    return
  }

  const bookToDelete = books.value.find(book => book.id === id)

  isProcessing.value = true
  try {
    await deleteBookApi(id)
    ElMessage.success('图书已下架')

    if (bookToDelete) {
      eventBus.emit(EventTypes.BOOK_REMOVED, {
        title: bookToDelete.title,
        author: bookToDelete.author,
        time: new Date()
      })
    }

    await loadBooks()
  } catch (error) {
    ElMessage.error('下架失败')
    console.error('下架失败:', error)
  } finally {
    isProcessing.value = false
  }
}

// 删除进货图书
const deletePendingBook = async (id: number) => {
  if (!confirm('确定要删除这本进货图书吗？')) {
    return
  }

  isProcessing.value = true
  try {
    await deleteBookApi(id)
    ElMessage.success('图书已删除')
    await loadBooks()
  } catch (error) {
    ElMessage.error('删除失败')
    console.error('删除失败:', error)
  } finally {
    isProcessing.value = false
  }
}

// 关闭所有模态框
const closeModal = () => {
  showAddForm.value = false
  showEditForm.value = false
  showEditPendingForm.value = false
  showLaunchForm.value = false
  resetForm()
}

// 生成随机ISBN编号（格式：978-7115531291）
const generateISBN = () => {
  const prefix = Math.random() > 0.5 ? '978' : '979'

  // 生成10位数字（ISBN-13去掉前缀978/979后的部分，包含校验位）
  let digits = ''
  for (let i = 0; i < 9; i++) {
    digits += Math.floor(Math.random() * 10).toString()
  }

  // 计算校验位（基于前缀+9位数字）
  const allDigits = (prefix + digits).split('')
  let sum = 0

  for (let i = 0; i < allDigits.length; i++) {
    const digit = parseInt(allDigits[i])
    sum += i % 2 === 0 ? digit : digit * 3
  }

  const checkDigit = (10 - (sum % 10)) % 10

  // 返回格式：978-7115531291（只有前缀后面有连字符）
  return `${prefix}-${digits}${checkDigit}`
}

// 重置表单
const resetForm = () => {
  formData.title = ''
  formData.author = ''
  formData.isbn = ''
  formData.category_id = null
  formData.description = ''

  editFormData.title = ''
  editFormData.author = ''
  editFormData.isbn = ''
  editFormData.category_id = null
  editFormData.description = ''

  editAvailableFormData.title = ''
  editAvailableFormData.author = ''
  editAvailableFormData.price = 0
  editAvailableFormData.stock = 0
  editAvailableFormData.category_id = null
  editAvailableFormData.description = ''

  currentBookId.value = null
}
</script>

<style scoped lang="scss">
/* iOS 风格全局样式 */
* {
  scrollbar-width: thin;
  scrollbar-color: #C7C7CC #f2f2f7;
}

*::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

*::-webkit-scrollbar-track {
  background: transparent;
}

*::-webkit-scrollbar-thumb {
  background: #C7C7CC;
  border-radius: 10px;

  &:hover {
    background: #8E8E93;
  }
}

/* iOS 风格容器 */
.book-manage-container {
  width: 100%;
  position: relative;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
  -webkit-font-smoothing: antialiased;
  background: #F2F2F7;
  min-height: 100vh;
  padding: 24px;
}

/* 标签页样式 - iOS风格 */
.tabs-container {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  background: white;
  padding: 6px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
}

.tab-btn {
  padding: 10px 20px;
  background: none;
  border: none;
  color: #8E8E93;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  position: relative;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 8px;
  flex: 1;
  justify-content: center;

  &:hover {
    color: #34C759;
    background: rgba(52, 199, 89, 0.05);
  }

  &.active {
    color: white;
    background: #34C759;
    box-shadow: 0 4px 12px rgba(52, 199, 89, 0.3);
  }
}

.tab-count {
  background: rgba(0, 0, 0, 0.1);
  color: inherit;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  min-width: 24px;
  text-align: center;
}

.tab-btn.active .tab-count {
  background: rgba(255, 255, 255, 0.25);
  color: white;
}

/* 页面头部 */
.tab-content {
  animation: fadeIn 0.4s ease;
}

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

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
}

.header-title {
  flex: 1;

  h3 {
    margin: 0 0 4px 0;
    color: #1C1C1E;
    font-size: 22px;
    font-weight: 700;
  }

  .subtitle {
    margin: 0;
    color: #8E8E93;
    font-size: 13px;
    font-weight: 500;
  }
}

/* 搜索框 - iOS风格 */
.search-box {
  position: relative;
  flex: 1;
  max-width: 500px;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 14px;
  font-size: 16px;
  pointer-events: none;
  z-index: 1;
  color: #8E8E93;
}

.search-input {
  width: 100%;
  padding: 10px 40px 10px 40px;
  background: white;
  border: 1px solid #E5E5EA;
  border-radius: 12px;
  color: #1C1C1E;
  font-size: 15px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);

  &::placeholder {
    color: #8E8E93;
  }

  &:focus {
    outline: none;
    border-color: #34C759;
    box-shadow: 0 0 0 3px rgba(52, 199, 89, 0.1), 0 8px 16px rgba(0, 0, 0, 0.04);
  }

  &:hover {
    border-color: #C7C7CC;
  }
}

.clear-btn {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  color: #8E8E93;
  font-size: 20px;
  cursor: pointer;
  padding: 4px 8px;
  line-height: 1;
  transition: color 0.2s ease;
  border-radius: 6px;

  &:hover {
    color: #34C759;
    background: rgba(52, 199, 89, 0.1);
  }
}

/* 按钮 - iOS风格 */
.add-btn {
  background: #34C759;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(52, 199, 89, 0.3);

  &:hover {
    background: #2db34b;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(52, 199, 89, 0.4);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px 20px;
  background: white;
  border-radius: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-label {
  color: #8E8E93;
  font-size: 14px;
  white-space: nowrap;
  font-weight: 600;
}

.filter-select {
  padding: 8px 12px;
  background: #F2F2F7;
  border: 1px solid transparent;
  border-radius: 10px;
  color: #1C1C1E;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 150px;
  font-weight: 500;

  &:hover {
    background: #E5E5EA;
  }

  &:focus {
    outline: none;
    border-color: #34C759;
    box-shadow: 0 0 0 3px rgba(52, 199, 89, 0.1);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  option {
    background: white;
    color: #1C1C1E;
  }
}

.filter-stats {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 16px;
}

.low-stock-warning {
  color: #FF9500;
  font-size: 13px;
  font-weight: 700;
  padding: 8px 12px;
  background: #FFF4E6;
  border: 1px solid #FFE5CC;
  border-radius: 10px;
}

/* 图书列表 - iOS风格 */
.book-list {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
}

.list-header {
  display: grid;
  background: #F9F9F9;
  padding: 16px 20px;
  font-weight: 700;
  color: #8E8E93;
  border-bottom: 1px solid #E5E5EA;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.5px;

  &.available-header {
    grid-template-columns: 80px 1fr 1fr 140px 120px 100px 260px;
  }

  &.pending-header {
    grid-template-columns: 80px 1fr 1fr 140px 1fr 220px;
  }
}

.header-item {
  text-align: left;
}

.book-item {
  display: grid;
  padding: 16px 20px;
  border-bottom: 1px solid #F2F2F7;
  transition: all 0.2s ease;

  &.available-item {
    grid-template-columns: 80px 1fr 1fr 140px 120px 100px 260px;
  }

  &.pending-item {
    grid-template-columns: 80px 1fr 1fr 140px 1fr 220px;
  }

  &:hover {
    background: #F9F9F9;
  }

  &:last-child {
    border-bottom: none;
  }
}

.book-info {
  display: flex;
  align-items: center;
  color: #1C1C1E;
  font-size: 14px;
  font-weight: 500;

  &.low-stock {
    color: #FF3B30;
    font-weight: 700;
  }
}

.book-actions {
  display: flex;
  gap: 8px;
}

/* 操作按钮 - iOS风格 */
.edit-btn,
.delete-btn,
.launch-btn,
.restock-btn {
  padding: 6px 14px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s ease;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.launch-btn {
  background: #34C759;
  color: white;

  &:hover {
    background: #2db34b;
    transform: translateY(-1px);
  }
}

.restock-btn {
  background: #FF9500;
  color: white;

  &:hover {
    background: #e68600;
    transform: translateY(-1px);
  }
}

.edit-btn {
  background: #007AFF;
  color: white;

  &:hover {
    background: #0066d9;
    transform: translateY(-1px);
  }
}

.delete-btn {
  background: #FF3B30;
  color: white;

  &:hover {
    background: #d92f24;
    transform: translateY(-1px);
  }
}

/* 加载和空状态 */
.loading-message {
  padding: 60px 40px;
  text-align: center;
  color: #34C759;
  font-weight: 600;
  font-size: 15px;
}

.empty-message {
  padding: 60px 40px;
  text-align: center;
  color: #8E8E93;
  font-size: 15px;
  font-weight: 500;
}

/* 模态框 - iOS风格 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeInOverlay 0.2s ease;
  backdrop-filter: blur(10px);
}

@keyframes fadeInOverlay {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);

  &.launch-modal {
    max-width: 600px;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 16px;
  border-bottom: 1px solid #F2F2F7;

  h3 {
    margin: 0;
    color: #1C1C1E;
    font-size: 20px;
    font-weight: 700;
  }
}

.close-btn {
  background: #F2F2F7;
  border: none;
  color: #8E8E93;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s ease;

  &:hover {
    background: #E5E5EA;
    color: #1C1C1E;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

/* 表单样式 - iOS风格 */
.book-form {
  padding: 24px;
}

.book-preview {
  padding: 20px;
  background: #F9F9F9;
  border-radius: 12px;
  margin-bottom: 20px;

  h4 {
    margin: 0 0 16px 0;
    color: #1C1C1E;
    font-size: 15px;
    font-weight: 700;
  }
}

.preview-item {
  display: flex;
  margin-bottom: 10px;
  font-size: 14px;

  &:last-child {
    margin-bottom: 0;
  }
}

.preview-label {
  color: #8E8E93;
  min-width: 80px;
  font-weight: 600;
}

.preview-value {
  color: #1C1C1E;
  flex: 1;
  font-weight: 500;

  &.cost-value {
    color: #FF9500;
    font-weight: 700;
  }
}

.divider {
  height: 1px;
  background: #E5E5EA;
  margin: 24px 0;
}

.section-title {
  margin: 0 0 16px 0;
  color: #1C1C1E;
  font-size: 17px;
  font-weight: 700;
}

.form-group {
  margin-bottom: 20px;

  label {
    display: block;
    margin-bottom: 8px;
    color: #1C1C1E;
    font-weight: 600;
    font-size: 14px;
  }

  .field-hint {
    margin-top: 6px;
    font-size: 12px;
    color: #8E8E93;
    line-height: 1.4;
  }

  input,
  select,
  textarea {
    width: 100%;
    padding: 12px;
    background: #F9F9F9;
    border: 1px solid #E5E5EA;
    border-radius: 10px;
    color: #1C1C1E;
    font-size: 15px;
    transition: all 0.3s ease;

    &:focus {
      outline: none;
      border-color: #34C759;
      background: white;
      box-shadow: 0 0 0 3px rgba(52, 199, 89, 0.1);
    }

    &:hover {
      border-color: #C7C7CC;
    }

    &::placeholder {
      color: #8E8E93;
    }

    &:disabled,
    &[readonly] {
      opacity: 0.6;
      cursor: not-allowed;
      background: #F2F2F7;
    }
  }

  textarea {
    resize: vertical;
    min-height: 100px;
    line-height: 1.5;
  }

  select {
    cursor: pointer;
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
}

/* 表单按钮 - iOS风格 */
.cancel-btn,
.submit-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
}

.cancel-btn {
  background: #F2F2F7;
  color: #1C1C1E;

  &:hover {
    background: #E5E5EA;
  }
}

.submit-btn {
  background: #34C759;
  color: white;
  box-shadow: 0 4px 12px rgba(52, 199, 89, 0.3);

  &:hover {
    background: #2db34b;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(52, 199, 89, 0.4);
  }

  &.launch-submit-btn {
    background: #007AFF;
    box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);

    &:hover {
      background: #0066d9;
      box-shadow: 0 6px 16px rgba(0, 122, 255, 0.4);
    }
  }
}
</style>
