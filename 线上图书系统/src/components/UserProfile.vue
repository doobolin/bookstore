<template>
  <PageContainer>
  <div class="user-profile-container">
    <el-card class="profile-header">
      <div class="header-content">
        <el-avatar :size="80" :src="userProfile?.avatar || '/images/default-avatar.png'">
          {{ userProfile?.nickname?.[0] || userProfile?.username?.[0] }}
        </el-avatar>
        <div class="user-info">
          <h2>{{ userProfile?.nickname || userProfile?.username }}</h2>
          <p class="username">@{{ userProfile?.username }}</p>
          <el-tag :type="userProfile?.role === 'admin' ? 'danger' : 'primary'" size="small">
            {{ userProfile?.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </div>
      </div>
    </el-card>

    <el-tabs v-model="activeTab" class="profile-tabs">
      <!-- 个人信息标签页 -->
      <el-tab-pane label="个人信息" name="info">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-button v-if="!editingProfile" type="primary" @click="editingProfile = true">
                编辑资料
              </el-button>
              <div v-else>
                <el-button @click="cancelEditProfile">取消</el-button>
                <el-button type="primary" @click="saveProfile">保存</el-button>
              </div>
            </div>
          </template>

          <el-form :model="profileForm" label-width="100px" :disabled="!editingProfile">
            <el-form-item label="用户名">
              <el-input v-model="userProfile.username" disabled />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="profileForm.nickname" placeholder="请输入昵称" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
            </el-form-item>
            <el-form-item label="性别">
              <el-radio-group v-model="profileForm.gender">
                <el-radio label="male">男</el-radio>
                <el-radio label="female">女</el-radio>
                <el-radio label="other">保密</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="生日">
              <el-date-picker
                v-model="profileForm.birthday"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 修改密码 -->
        <el-card class="password-card">
          <template #header>
            <span>修改密码</span>
          </template>
          <el-form :model="passwordForm" label-width="100px">
            <el-form-item label="旧密码">
              <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入旧密码" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码" show-password />
            </el-form-item>
            <el-form-item label="确认密码">
              <el-input v-model="passwordForm.confirm_password" type="password" placeholder="再次输入新密码" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 收货地址标签页 -->
      <el-tab-pane label="收货地址" name="address">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>收货地址管理</span>
              <el-button type="primary" @click="showAddressDialog()">新增地址</el-button>
            </div>
          </template>

          <div v-if="addresses.length === 0" class="empty-state">
            <el-empty description="暂无收货地址" />
          </div>

          <div v-else class="address-list">
            <el-card
              v-for="address in addresses"
              :key="address.id"
              class="address-item"
              :class="{ 'default-address': address.is_default }"
            >
              <div class="address-content">
                <div class="address-header">
                  <span class="receiver-name">{{ address.receiver_name }}</span>
                  <span class="receiver-phone">{{ address.receiver_phone }}</span>
                  <el-tag v-if="address.is_default" type="success" size="small">默认</el-tag>
                </div>
                <div class="address-detail">
                  {{ address.full_address }}
                </div>
                <div class="address-actions">
                  <el-button link type="primary" @click="showAddressDialog(address)">编辑</el-button>
                  <el-button v-if="!address.is_default" link type="primary" @click="setDefault(address.id)">
                    设为默认
                  </el-button>
                  <el-button link type="danger" @click="deleteAddress(address.id)">删除</el-button>
                </div>
              </div>
            </el-card>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 交易信息标签页 -->
      <el-tab-pane label="交易信息" name="transactions">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="stat-card">
              <el-statistic title="总订单数" :value="userProfile?.stats?.total_orders || 0">
                <template #suffix>
                  <span>单</span>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="stat-card">
              <el-statistic title="已完成订单" :value="userProfile?.stats?.completed_orders || 0">
                <template #suffix>
                  <span>单</span>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="stat-card">
              <el-statistic title="累计消费" :value="userProfile?.stats?.total_spent || 0" :precision="2">
                <template #prefix>
                  <span>¥</span>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
        </el-row>

        <!-- 最近订单 -->
        <el-card class="recent-orders">
          <template #header>
            <div class="card-header">
              <span>最近订单</span>
              <el-button type="primary" link @click="goToOrders">查看全部</el-button>
            </div>
          </template>

          <div v-if="loadingOrders" class="loading-orders">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>

          <div v-else-if="recentOrders.length === 0" class="empty-orders">
            <el-empty description="暂无订单记录" :image-size="80" />
          </div>

          <div v-else class="orders-list">
            <div
              v-for="order in recentOrders"
              :key="order.id"
              class="order-item"
              @click="goToOrderDetail(order.id)"
            >
              <div class="order-item-header">
                <span class="order-number">{{ order.order_number }}</span>
                <span class="order-amount">¥{{ order.total_amount.toFixed(2) }}</span>
              </div>
              <div class="order-item-footer">
                <span class="order-time">
                  <el-icon><Clock /></el-icon>
                  {{ order.created_at }}
                </span>
              </div>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 地址编辑对话框 -->
    <el-dialog
      v-model="addressDialogVisible"
      :title="currentAddress.id ? '编辑地址' : '新增地址'"
      width="600px"
    >
      <el-form :model="currentAddress" label-width="100px">
        <el-form-item label="收货人" required>
          <el-input v-model="currentAddress.receiver_name" placeholder="请输入收货人姓名" />
        </el-form-item>
        <el-form-item label="手机号" required>
          <el-input v-model="currentAddress.receiver_phone" placeholder="请输入收货人手机号" />
        </el-form-item>
        <el-form-item label="省份" required>
          <el-input v-model="currentAddress.province" placeholder="请输入省份" />
        </el-form-item>
        <el-form-item label="城市" required>
          <el-input v-model="currentAddress.city" placeholder="请输入城市" />
        </el-form-item>
        <el-form-item label="区/县" required>
          <el-input v-model="currentAddress.district" placeholder="请输入区/县" />
        </el-form-item>
        <el-form-item label="详细地址" required>
          <el-input
            v-model="currentAddress.detail_address"
            type="textarea"
            :rows="3"
            placeholder="请输入详细地址"
          />
        </el-form-item>
        <el-form-item label="邮政编码">
          <el-input v-model="currentAddress.postal_code" placeholder="请输入邮政编码（可选）" />
        </el-form-item>
        <el-form-item label="默认地址">
          <el-switch v-model="currentAddress.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addressDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAddress">保存</el-button>
      </template>
    </el-dialog>
  </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, Clock } from '@element-plus/icons-vue'
import PageContainer from './PageContainer.vue'
import { getUserProfile, updateUserProfile, changePassword as changePasswordApi, type UserProfile, type UserProfileUpdate, type PasswordChange } from '../api/userApi'
import { getAddresses, addAddress, updateAddress, deleteAddress as deleteAddressApi, setDefaultAddress, type Address } from '../api/addressApi'
import { getOrders, type Order } from '../api/orderApi'

const router = useRouter()

// 当前标签页
const activeTab = ref('info')

// 用户资料
const userProfile = ref<UserProfile>({
  id: 0,
  username: '',
  email: '',
  role: 'user',
  status: 'active'
})

// 编辑状态
const editingProfile = ref(false)

// 资料表单
const profileForm = reactive<UserProfileUpdate>({
  nickname: '',
  email: '',
  phone: '',
  gender: 'other',
  birthday: ''
})

// 密码表单
const passwordForm = reactive<PasswordChange & { confirm_password?: string }>({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 收货地址列表
const addresses = ref<Address[]>([])

// 地址对话框
const addressDialogVisible = ref(false)

// 最近订单
const recentOrders = ref<Order[]>([])
const loadingOrders = ref(false)
const currentAddress = reactive<Address>({
  receiver_name: '',
  receiver_phone: '',
  province: '',
  city: '',
  district: '',
  detail_address: '',
  postal_code: '',
  is_default: false
})

// 加载用户资料
const loadUserProfile = async () => {
  try {
    const userId = Number(localStorage.getItem('user_id'))
    if (!userId) {
      ElMessage.error('请先登录')
      router.push('/login')
      return
    }

    const data = await getUserProfile(userId)
    userProfile.value = data

    // 初始化编辑表单
    profileForm.nickname = data.nickname || ''
    profileForm.email = data.email
    profileForm.phone = data.phone || ''
    profileForm.gender = data.gender || 'other'
    profileForm.birthday = data.birthday || ''
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '加载用户资料失败')
  }
}

// 加载收货地址
const loadAddresses = async () => {
  try {
    const userId = Number(localStorage.getItem('user_id'))
    const response = await getAddresses(userId)
    addresses.value = response.data.addresses || []
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '加载收货地址失败')
  }
}

// 保存资料
const saveProfile = async () => {
  try {
    const userId = Number(localStorage.getItem('user_id'))
    await updateUserProfile(userId, profileForm)
    ElMessage.success('资料更新成功')
    editingProfile.value = false
    await loadUserProfile()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '资料更新失败')
  }
}

// 取消编辑
const cancelEditProfile = () => {
  editingProfile.value = false
  // 恢复原始数据
  profileForm.nickname = userProfile.value.nickname || ''
  profileForm.email = userProfile.value.email
  profileForm.phone = userProfile.value.phone || ''
  profileForm.gender = userProfile.value.gender || 'other'
  profileForm.birthday = userProfile.value.birthday || ''
}

// 修改密码
const changePassword = async () => {
  if (!passwordForm.old_password || !passwordForm.new_password) {
    ElMessage.warning('请填写完整的密码信息')
    return
  }

  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }

  if (passwordForm.new_password.length < 6) {
    ElMessage.warning('新密码长度不能少于6位')
    return
  }

  try {
    const userId = Number(localStorage.getItem('user_id'))
    await changePasswordApi(userId, {
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    ElMessage.success('密码修改成功，请重新登录')

    // 清空密码表单
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''

    // 跳转到登录页
    setTimeout(() => {
      localStorage.clear()
      router.push('/login')
    }, 1500)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '密码修改失败')
  }
}

// 显示地址对话框
const showAddressDialog = (address?: Address) => {
  if (address) {
    Object.assign(currentAddress, address)
  } else {
    // 重置表单（包括清除id）
    Object.assign(currentAddress, {
      id: undefined,
      receiver_name: '',
      receiver_phone: '',
      province: '',
      city: '',
      district: '',
      detail_address: '',
      postal_code: '',
      is_default: false
    })
  }
  addressDialogVisible.value = true
}

// 保存地址
const saveAddress = async () => {
  // 表单验证
  if (!currentAddress.receiver_name || !currentAddress.receiver_phone ||
      !currentAddress.province || !currentAddress.city ||
      !currentAddress.district || !currentAddress.detail_address) {
    ElMessage.warning('请填写完整的地址信息')
    return
  }

  try {
    const userId = Number(localStorage.getItem('user_id'))

    if (currentAddress.id) {
      // 更新地址
      await updateAddress(currentAddress.id, currentAddress)
      ElMessage.success('地址更新成功')
    } else {
      // 新增地址
      await addAddress({ ...currentAddress, user_id: userId })
      ElMessage.success('地址添加成功')
    }

    addressDialogVisible.value = false
    await loadAddresses()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '保存地址失败')
  }
}

// 设置默认地址
const setDefault = async (addressId: number) => {
  try {
    await setDefaultAddress(addressId)
    ElMessage.success('默认地址设置成功')
    await loadAddresses()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '设置默认地址失败')
  }
}

// 删除地址
const deleteAddress = async (addressId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个地址吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteAddressApi(addressId)
    ElMessage.success('地址删除成功')
    await loadAddresses()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '删除地址失败')
    }
  }
}

// 加载最近订单
const loadRecentOrders = async () => {
  try {
    loadingOrders.value = true
    const userId = Number(localStorage.getItem('user_id'))
    const allOrders = await getOrders(userId)

    // 获取最近的3个订单
    recentOrders.value = allOrders.slice(0, 3)
  } catch (error: any) {
    console.error('加载最近订单失败:', error)
  } finally {
    loadingOrders.value = false
  }
}

// 跳转到订单页
const goToOrders = () => {
  router.push('/orders')
}

// 跳转到订单详情
const goToOrderDetail = (orderId: number) => {
  router.push(`/order/${orderId}`)
}

// 页面加载时
onMounted(() => {
  loadUserProfile()
  loadAddresses()
  loadRecentOrders()
})
</script>

<style scoped>
.user-profile-container {
  max-width: 1200px;
  margin: 0 auto;
}

.profile-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.user-info .username {
  margin: 0 0 8px 0;
  color: #909399;
  font-size: 14px;
}

.profile-tabs {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.password-card {
  margin-top: 20px;
}

.address-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.address-item {
  transition: all 0.3s;
}

.address-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.default-address {
  border: 2px solid #67c23a;
}

.address-content {
  padding: 10px;
}

.address-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.receiver-name {
  font-weight: bold;
  font-size: 16px;
}

.receiver-phone {
  color: #606266;
}

.address-detail {
  color: #606266;
  margin-bottom: 10px;
  line-height: 1.6;
}

.address-actions {
  display: flex;
  gap: 10px;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.stat-card {
  text-align: center;
}

.recent-orders {
  margin-top: 20px;
}

.loading-orders {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px 0;
  color: #909399;
  font-size: 14px;
}

.empty-orders {
  padding: 20px 0;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-item {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.order-item:hover {
  background: #ecf5ff;
  transform: translateX(4px);
}

.order-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.order-number {
  font-size: 14px;
  color: #409eff;
  font-weight: 500;
}

.order-amount {
  font-size: 16px;
  font-weight: 600;
  color: #f56c6c;
}

.order-item-footer {
  display: flex;
  align-items: center;
  gap: 8px;
}

.order-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}
</style>
