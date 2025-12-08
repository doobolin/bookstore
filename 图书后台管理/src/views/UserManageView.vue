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
/* iOS风格全局样式 */
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

.user-manage-container {
  width: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
  -webkit-font-smoothing: antialiased;
}

.page-header {
  margin-bottom: 24px;

  h2 {
    margin: 0;
    color: #1C1C1E;
    font-weight: 700;
  }
}

/* 标签页 - iOS风格 */
.tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  background: white;
  padding: 6px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
}

.tab-btn {
  background: none;
  border: none;
  padding: 10px 24px;
  color: #8E8E93;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  flex: 1;

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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h3 {
    margin: 0;
    color: #1C1C1E;
    font-weight: 700;
  }

  .tip {
    color: #8E8E93;
    font-size: 13px;
    font-weight: 500;
  }
}

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

/* 用户列表样式 - iOS风格 */
.user-list {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
}

.list-header {
  display: grid;
  grid-template-columns: 80px 150px 1fr 100px 200px 180px;
  background: #F9F9F9;
  padding: 16px 20px;
  font-weight: 700;
  color: #8E8E93;
  border-bottom: 1px solid #E5E5EA;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.5px;
}

.header-item {
  text-align: left;
}

.user-item {
  display: grid;
  grid-template-columns: 80px 150px 1fr 100px 200px 180px;
  padding: 16px 20px;
  border-bottom: 1px solid #F2F2F7;
  transition: all 0.2s ease;

  &:hover {
    background: #F9F9F9;
  }

  &:last-child {
    border-bottom: none;
  }
}

.user-info {
  display: flex;
  align-items: center;
  color: #1C1C1E;
  font-size: 14px;
  font-weight: 500;
}

/* 状态标签 - iOS风格 */
.status-tag {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;

  &.active {
    background: #E6F9ED;
    color: #34C759;
  }

  &.inactive {
    background: #F2F2F7;
    color: #8E8E93;
  }
}

/* 操作按钮 - iOS风格 */
.user-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.edit-btn,
.delete-btn,
.status-btn {
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

.edit-btn {
  background: #007AFF;
  color: white;

  &:hover:not(:disabled) {
    background: #0066d9;
    transform: translateY(-1px);
  }
}

.delete-btn {
  background: #FF3B30;
  color: white;

  &:hover:not(:disabled) {
    background: #d92f24;
    transform: translateY(-1px);
  }
}

.status-btn {
  color: white;

  &.disable {
    background: #FF9500;
  }

  &.enable {
    background: #34C759;
  }

  &:hover:not(:disabled) {
    opacity: 0.9;
    transform: translateY(-1px);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }
}

.loading-message,
.empty-message {
  padding: 60px 40px;
  text-align: center;
  color: #8E8E93;
  font-size: 15px;
  font-weight: 500;
}

/* 模态框样式 - iOS风格 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeInOverlay 0.2s ease;
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
}

/* 表单样式 - iOS风格 */
.user-form {
  padding: 24px;
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

  input,
  select {
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

  &:hover:not(:disabled) {
    background: #E5E5EA;
  }
}

.submit-btn {
  background: #34C759;
  color: white;
  box-shadow: 0 4px 12px rgba(52, 199, 89, 0.3);

  &:hover:not(:disabled) {
    background: #2db34b;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(52, 199, 89, 0.4);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }
}
</style>
