<template>
  <div class="user-manage-container">
    <!-- 标签页切换 -->
    <div class="tabs">
      <button
        :class="['tab-btn', { active: activeTab === 'users' }]"
        @click="activeTab = 'users'"
      >
        普通用户管理
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'admins' }]"
        @click="activeTab = 'admins'"
      >
        管理员管理
      </button>
    </div>

    <!-- 普通用户管理 -->
    <div v-show="activeTab === 'users'" class="tab-content">
      <div class="user-list">
        <div class="list-header">
          <div class="header-item">ID</div>
          <div class="header-item">用户名</div>
          <div class="header-item">邮箱</div>
          <div class="header-item">状态</div>
          <div class="header-item">创建时间</div>
          <div class="header-item">操作</div>
        </div>
        <div v-if="loading" class="loading-message">
          加载中...
        </div>
        <div v-else v-for="user in normalUsers" :key="user.id" class="user-item">
          <div class="user-info">{{ user.id }}</div>
          <div class="user-info">{{ user.username }}</div>
          <div class="user-info">{{ user.email }}</div>
          <div class="user-info">
            <span :class="['status-tag', user.status]">
              {{ user.status === 'active' ? '活跃' : '禁用' }}
            </span>
          </div>
          <div class="user-info">{{ formatDate(user.created_at) }}</div>
          <div class="user-actions">
            <button
              class="status-btn"
              :class="user.status === 'active' ? 'disable' : 'enable'"
              @click="toggleUserStatus(user.id, user.status)"
              :disabled="isProcessing"
            >
              {{ user.status === 'active' ? '禁用' : '启用' }}
            </button>
          </div>
        </div>
        <div v-if="!loading && normalUsers.length === 0" class="empty-message">
          暂无普通用户数据
        </div>
      </div>
    </div>

    <!-- 管理员管理 -->
    <div v-show="activeTab === 'admins'" class="tab-content">
      <div class="section-header">
        <button class="add-btn" @click="showAddForm = true" :disabled="loading">
          添加管理员
        </button>
      </div>

      <div class="user-list">
        <div class="list-header">
          <div class="header-item">ID</div>
          <div class="header-item">用户名</div>
          <div class="header-item">邮箱</div>
          <div class="header-item">状态</div>
          <div class="header-item">创建时间</div>
          <div class="header-item">操作</div>
        </div>
        <div v-if="loading" class="loading-message">
          加载中...
        </div>
        <div v-else v-for="user in adminUsers" :key="user.id" class="user-item">
          <div class="user-info">{{ user.id }}</div>
          <div class="user-info">{{ user.username }}</div>
          <div class="user-info">{{ user.email }}</div>
          <div class="user-info">
            <span :class="['status-tag', user.status]">
              {{ user.status === 'active' ? '活跃' : '禁用' }}
            </span>
          </div>
          <div class="user-info">{{ formatDate(user.created_at) }}</div>
          <div class="user-actions">
            <button class="edit-btn" @click="editUser(user)" :disabled="isProcessing">
              编辑
            </button>
            <button class="delete-btn" @click="deleteUser(user.id)" :disabled="isProcessing">
              删除
            </button>
            <button
              class="status-btn"
              :class="user.status === 'active' ? 'disable' : 'enable'"
              @click="toggleUserStatus(user.id, user.status)"
              :disabled="isProcessing"
            >
              {{ user.status === 'active' ? '禁用' : '启用' }}
            </button>
          </div>
        </div>
        <div v-if="!loading && adminUsers.length === 0" class="empty-message">
          暂无管理员数据
        </div>
      </div>
    </div>

    <!-- 添加/编辑管理员表单 -->
    <div v-if="showAddForm || showEditForm" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ showEditForm ? '编辑管理员' : '添加管理员' }}</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <form @submit.prevent="submitForm" class="user-form">
          <div class="form-group">
            <label for="username">用户名</label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              required
              placeholder="请输入用户名"
            />
          </div>
          <div class="form-group">
            <label for="email">邮箱</label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              required
              placeholder="请输入邮箱"
            />
          </div>
          <div class="form-group">
            <label for="password">{{ showEditForm ? '新密码（留空表示不修改）' : '密码' }}</label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              :required="!showEditForm"
              placeholder="请输入密码"
            />
          </div>
          <div class="form-group" v-if="showEditForm">
            <label for="status">状态</label>
            <select id="status" v-model="formData.status" required>
              <option value="active">活跃</option>
              <option value="inactive">禁用</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="closeModal" :disabled="formLoading">
              取消
            </button>
            <button type="submit" class="submit-btn" :disabled="formLoading">
              <span v-if="formLoading">处理中...</span>
              <span v-else>{{ showEditForm ? '保存' : '添加' }}</span>
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
  getAllUsers,
  addUser,
  updateUser,
  deleteUser as deleteUserApi,
  toggleUserStatus as toggleUserStatusApi
} from '../api/userApi'

// 定义用户接口
interface User {
  id: number
  username: string
  email: string
  password?: string
  role: 'admin' | 'user'
  status: 'active' | 'inactive'
  created_at?: string
}

// 状态变量
const activeTab = ref<'users' | 'admins'>('users')
const users = ref<User[]>([])
const showAddForm = ref(false)
const showEditForm = ref(false)
const currentUserId = ref<number | null>(null)
const loading = ref(false)
const isProcessing = ref(false)
const formLoading = ref(false)

// 表单数据
const formData = reactive({
  username: '',
  email: '',
  password: '',
  role: 'admin' as 'admin' | 'user',
  status: 'active' as 'active' | 'inactive'
})

// 计算属性：普通用户列表
const normalUsers = computed(() => {
  return users.value.filter(user => user.role === 'user')
})

// 计算属性：管理员列表
const adminUsers = computed(() => {
  return users.value.filter(user => user.role === 'admin')
})

// 组件挂载时加载数据
onMounted(() => {
  loadUsers()
})

// 加载用户数据
const loadUsers = async () => {
  loading.value = true
  try {
    const data = await getAllUsers()
    users.value = data
  } catch (error) {
    ElMessage.error('加载用户列表失败，请检查后端服务是否正常运行')
    console.error('加载用户列表失败:', error)
    users.value = []
  } finally {
    loading.value = false
  }
}

// 编辑用户（仅限管理员）
const editUser = (user: User) => {
  if (user.role !== 'admin') {
    ElMessage.warning('只能编辑管理员信息')
    return
  }
  currentUserId.value = user.id
  formData.username = user.username
  formData.email = user.email
  formData.password = ''
  formData.role = 'admin'
  formData.status = user.status
  showEditForm.value = true
}

// 重置表单
const resetForm = () => {
  formData.username = ''
  formData.email = ''
  formData.password = ''
  formData.role = 'admin'
  formData.status = 'active'
  currentUserId.value = null
}

// 关闭模态框
const closeModal = () => {
  showAddForm.value = false
  showEditForm.value = false
  resetForm()
}

// 提交表单（添加或编辑管理员）
const submitForm = async () => {
  formLoading.value = true
  try {
    if (showEditForm.value && currentUserId.value) {
      // 编辑管理员
      const updateData: any = {
        username: formData.username,
        email: formData.email,
        role: 'admin',
        status: formData.status
      }
      if (formData.password) {
        updateData.password = formData.password
      }

      await updateUser(currentUserId.value, updateData)
      ElMessage.success('管理员更新成功')
    } else {
      // 添加管理员
      await addUser({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        role: 'admin'
      })
      ElMessage.success('管理员添加成功')
    }

    closeModal()
    await loadUsers()
  } catch (error) {
    ElMessage.error(showEditForm.value ? '管理员更新失败' : '管理员添加失败')
    console.error(showEditForm.value ? '更新管理员失败:' : '添加管理员失败:', error)
  } finally {
    formLoading.value = false
  }
}

// 删除用户（仅限管理员）
const deleteUser = async (id: number) => {
  const user = users.value.find(u => u.id === id)
  if (user && user.role !== 'admin') {
    ElMessage.warning('只能删除管理员账号')
    return
  }

  if (!confirm('确定要删除这个管理员吗？')) {
    return
  }

  isProcessing.value = true
  try {
    await deleteUserApi(id)
    ElMessage.success('管理员删除成功')
    await loadUsers()
  } catch (error) {
    ElMessage.error('管理员删除失败')
    console.error('删除管理员失败:', error)
  } finally {
    isProcessing.value = false
  }
}

// 切换用户状态
const toggleUserStatus = async (id: number, currentStatus: 'active' | 'inactive') => {
  isProcessing.value = true
  try {
    const newStatus = currentStatus === 'active' ? 'inactive' : 'active'
    await toggleUserStatusApi(id, newStatus)
    ElMessage.success(`用户已${newStatus === 'active' ? '启用' : '禁用'}`)
    await loadUsers()
  } catch (error) {
    ElMessage.error(`用户${currentStatus === 'active' ? '禁用' : '启用'}失败`)
    console.error('切换用户状态失败:', error)
  } finally {
    isProcessing.value = false
  }
}

// 格式化日期
const formatDate = (dateString?: string) => {
  if (!dateString) return '-'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}
</script>

<style scoped lang="scss">
.user-manage-container {
  width: 100%;
}

.page-header {
  margin-bottom: 24px;

  h2 {
    margin: 0;
    color: #4caf50;
  }
}

/* 标签页 */
.tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  border-bottom: 2px solid #333;
}

.tab-btn {
  background: none;
  border: none;
  padding: 12px 24px;
  color: #999;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
  position: relative;
  top: 2px;

  &:hover {
    color: #4caf50;
  }

  &.active {
    color: #4caf50;
    border-bottom-color: #4caf50;
  }
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h3 {
    margin: 0;
    color: #e0e0e0;
  }

  .tip {
    color: #999;
    font-size: 13px;
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

  &:hover {
    background-color: #45a049;
  }

  &:disabled {
    background-color: #666;
    cursor: not-allowed;
  }
}

/* 用户列表样式 */
.user-list {
  background-color: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
}

.list-header {
  display: grid;
  grid-template-columns: 80px 150px 1fr 100px 200px 180px;
  background-color: #2a2a2a;
  padding: 16px 20px;
  font-weight: 600;
  color: #4caf50;
  border-bottom: 1px solid #333;
}

.header-item {
  text-align: left;
}

.user-item {
  display: grid;
  grid-template-columns: 80px 150px 1fr 100px 200px 180px;
  padding: 16px 20px;
  border-bottom: 1px solid #333;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #252525;
  }

  &:last-child {
    border-bottom: none;
  }
}

.user-info {
  display: flex;
  align-items: center;
  color: #e0e0e0;
}

/* 状态标签 */
.status-tag {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;

  &.active {
    background-color: #4caf50;
    color: white;
  }

  &.inactive {
    background-color: #9e9e9e;
    color: white;
  }
}

/* 操作按钮 */
.user-actions {
  display: flex;
  gap: 6px;
  align-items: center;
}

.edit-btn,
.delete-btn,
.status-btn {
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s ease;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.edit-btn {
  background-color: #2196f3;
  color: white;

  &:hover:not(:disabled) {
    background-color: #1976d2;
  }
}

.delete-btn {
  background-color: #f44336;
  color: white;

  &:hover:not(:disabled) {
    background-color: #d32f2f;
  }
}

.status-btn {
  color: white;

  &.disable {
    background-color: #ff5722;
  }

  &.enable {
    background-color: #4caf50;
  }

  &:hover:not(:disabled) {
    opacity: 0.9;
  }
}

.loading-message,
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

  h3 {
    margin: 0;
    color: #4caf50;
  }
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

  &:hover {
    color: #fff;
  }
}

/* 表单样式 */
.user-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;

  label {
    display: block;
    margin-bottom: 8px;
    color: #e0e0e0;
    font-weight: 500;
  }

  input,
  select {
    width: 100%;
    padding: 10px;
    background-color: #2a2a2a;
    border: 1px solid #333;
    border-radius: 4px;
    color: #e0e0e0;
    font-size: 14px;

    &:focus {
      outline: none;
      border-color: #4caf50;
    }
  }
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

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.cancel-btn {
  background-color: #666;
  color: white;

  &:hover:not(:disabled) {
    background-color: #555;
  }
}

.submit-btn {
  background-color: #4caf50;
  color: white;

  &:hover:not(:disabled) {
    background-color: #45a049;
  }
}
</style>
