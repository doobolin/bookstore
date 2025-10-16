<template>
  <div class="user-manage-container">
    <div class="page-header">
      <h2>用户管理</h2>
      <button class="add-btn" @click="showAddForm = true" :disabled="loading">
            添加用户
          </button>
    </div>

    <!-- 用户列表 -->
    <div class="user-list">
      <div class="list-header">
        <div class="header-item">ID</div>
        <div class="header-item">用户名</div>
        <div class="header-item">邮箱</div>
        <div class="header-item">角色</div>
        <div class="header-item">状态</div>
        <div class="header-item">创建时间</div>
        <div class="header-item">操作</div>
      </div>
      <div v-if="loading" class="loading-message">
        加载中...
      </div>
      <div v-else v-for="user in users" :key="user.id" class="user-item">
        <div class="user-info">{{ user.id }}</div>
        <div class="user-info">{{ user.username }}</div>
        <div class="user-info">{{ user.email }}</div>
        <div class="user-info">
          <span :class="['role-tag', user.role]">{{ user.role === 'admin' ? '管理员' : '普通用户' }}</span>
        </div>
        <div class="user-info">
          <span :class="['status-tag', user.status]">{{ user.status === 'active' ? '活跃' : '禁用' }}</span>
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
      <div v-if="!loading && users.length === 0" class="empty-message">
        暂无用户数据
      </div>
    </div>

    <!-- 添加/编辑用户表单 -->
    <div v-if="showAddForm || showEditForm" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ showEditForm ? '编辑用户' : '添加用户' }}</h3>
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
          <div class="form-group">
            <label for="role">角色</label>
            <select id="role" v-model="formData.role" required>
              <option value="user">普通用户</option>
              <option value="admin">管理员</option>
            </select>
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
              <i class="icon-cancel"></i> 取消
            </button>
            <button type="submit" class="submit-btn" :disabled="formLoading">
              <span v-if="formLoading">处理中...</span>
              <span v-else>
                <i v-if="showEditForm" class="icon-save"></i>
                <i v-else class="icon-add"></i>
                {{ showEditForm ? '保存' : '添加' }}
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
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
const users = ref<User[]>([])
const showAddForm = ref(false)
const showEditForm = ref(false)
const currentUserId = ref<number | null>(null)
const loading = ref(false) // 列表加载状态
const isProcessing = ref(false) // 操作处理状态
const formLoading = ref(false) // 表单处理状态

// 表单数据
const formData = reactive({
  username: '',
  email: '',
  password: '',
  role: 'user' as 'admin' | 'user',
  status: 'active' as 'active' | 'inactive'
})

// 组件挂载时加载数据
onMounted(() => {
  loadUsers()
})

// 加载用户数据（从后端API）
  const loadUsers = async () => {
    loading.value = true
    try {
      console.log('开始加载用户数据')
      const data = await getAllUsers()
      console.log('getAllUsers返回的数据:', data)
      users.value = data
      console.log('users.value赋值后:', users.value)
    } catch (error) {
      ElMessage.error('加载用户列表失败，请检查后端服务是否正常运行')
      console.error('加载用户列表失败:', error)
      // 不使用模拟数据，保持列表为空
      users.value = []
    } finally {
      loading.value = false
      console.log('加载完成，loading状态变为false')
    }
  }

// 编辑用户
const editUser = (user: User) => {
  currentUserId.value = user.id
  formData.username = user.username
  formData.email = user.email
  formData.password = '' // 编辑时不显示密码
  formData.role = user.role
  formData.status = user.status
  showEditForm.value = true
}

// 重置表单
const resetForm = () => {
  formData.username = ''
  formData.email = ''
  formData.password = ''
  formData.role = 'user'
  formData.status = 'active'
  currentUserId.value = null
}

// 关闭模态框
const closeModal = () => {
  showAddForm.value = false
  showEditForm.value = false
  resetForm()
}

// 提交表单（添加或编辑用户）
const submitForm = async () => {
  formLoading.value = true
  try {
    if (showEditForm.value && currentUserId.value) {
      // 编辑用户
      const updateData = {
        username: formData.username,
        email: formData.email,
        role: formData.role,
        status: formData.status
      }
      // 只有在填写了新密码时才更新密码
      if (formData.password) {
        updateData.password = formData.password
      }
      
      await updateUser(currentUserId.value, updateData)
      ElMessage.success('用户更新成功')
    } else {
      // 添加用户
      await addUser({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        role: formData.role
      })
      ElMessage.success('用户添加成功')
    }
    
    // 关闭模态框并重新加载数据
    closeModal()
    await loadUsers()
  } catch (error) {
    ElMessage.error(showEditForm.value ? '用户更新失败' : '用户添加失败')
    console.error(showEditForm.value ? '更新用户失败:' : '添加用户失败:', error)
  } finally {
    formLoading.value = false
  }
}

// 删除用户
const deleteUser = async (id: number) => {
  if (!confirm('确定要删除这个用户吗？')) {
    return
  }
  
  isProcessing.value = true
  try {
    await deleteUserApi(id)
    ElMessage.success('用户删除成功')
    await loadUsers()
  } catch (error) {
    ElMessage.error('用户删除失败')
    console.error('删除用户失败:', error)
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
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
}

.add-btn:hover {
  background-color: #45a049;
}

/* 用户列表样式 */
.user-list {
  background-color: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
}

.list-header {
  display: grid;
  grid-template-columns: 80px 150px 1fr 100px 100px 200px 180px;
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
  grid-template-columns: 80px 150px 1fr 100px 100px 200px 180px;
  padding: 16px 20px;
  border-bottom: 1px solid #333;
  transition: background-color 0.2s ease;
}

.user-item:hover {
  background-color: #252525;
}

.user-item:last-child {
  border-bottom: none;
}

.user-info {
  display: flex;
  align-items: center;
  color: #e0e0e0;
}

/* 角色和状态标签 */
.role-tag,
.status-tag {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.role-tag.admin {
  background-color: #2196f3;
  color: white;
}

.role-tag.user {
  background-color: #673ab7;
  color: white;
}

.status-tag.active {
  background-color: #4caf50;
  color: white;
}

.status-tag.inactive {
  background-color: #9e9e9e;
  color: white;
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

.status-btn {
  background-color: #ff9800;
  color: white;
}

.status-btn.disable {
  background-color: #ff5722;
}

.status-btn.enable {
  background-color: #4caf50;
}

.status-btn:hover {
  opacity: 0.9;
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
.user-form {
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
.form-group select {
  width: 100%;
  padding: 10px;
  background-color: #2a2a2a;
  border: 1px solid #333;
  border-radius: 4px;
  color: #e0e0e0;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #4caf50;
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