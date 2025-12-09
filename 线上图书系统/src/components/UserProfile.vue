<template>
  <PageContainer :hide-navbar="true">
  <!-- 动态背景光球 -->
  <div class="mesh-gradients">
    <div class="gradient-blob blob-1"></div>
    <div class="gradient-blob blob-2"></div>
    <div class="gradient-blob blob-3"></div>
  </div>

  <div class="user-profile-container">
    <!-- 左侧：个人概览与导航 -->
    <aside class="sidebar">
      <!-- 用户名片 -->
      <div class="user-card">
        <!-- 动态背景光 -->
        <div class="user-card-bg"></div>

        <div class="avatar-wrapper">
          <el-avatar :size="96" :src="userProfile?.avatar || '/images/default-avatar.png'">
            {{ userProfile?.nickname?.[0] || userProfile?.username?.[0] }}
          </el-avatar>
        </div>

        <h2 class="user-name">{{ userProfile?.nickname || userProfile?.username }}</h2>
        <p class="user-email">{{ userProfile?.email || '@' + userProfile?.username }}</p>

        <button class="edit-profile-btn" @click="showEditProfile">编辑资料</button>
      </div>

      <!-- 导航菜单 -->
      <nav class="nav-menu">
        <a
          v-for="item in navItems"
          :key="item.id"
          @click="activeTab = item.id"
          :class="['nav-item', { active: activeTab === item.id }]"
        >
          <div :class="['nav-icon', item.color]">
            <i :class="item.icon"></i>
          </div>
          <span>{{ item.label }}</span>
          <i class="ri-arrow-right-s-line nav-arrow"></i>
        </a>
      </nav>

      <!-- 回到首页按钮 -->
      <button class="back-home-btn" @click="goToHome">
        <i class="ri-home-4-line"></i>
        <span>回到首页</span>
      </button>
    </aside>

    <!-- 右侧：主要内容区 -->
    <main class="main-content">
      <!-- 顶部：Bento 数据仪表盘 -->
      <section class="stats-dashboard">
        <div class="stat-item stat-primary">
          <div class="stat-icon">
            <i class="ri-shopping-bag-line"></i>
          </div>
          <div>
            <div class="stat-value">{{ userProfile?.stats?.total_orders || 0 }}</div>
            <div class="stat-label">总订单数</div>
          </div>
        </div>
        <div class="stat-item stat-success">
          <div class="stat-icon">
            <i class="ri-check-double-line"></i>
          </div>
          <div>
            <div class="stat-value">{{ userProfile?.stats?.completed_orders || 0 }}</div>
            <div class="stat-label">已完成订单</div>
          </div>
        </div>
        <div class="stat-item stat-featured">
          <div class="stat-icon-white">
            <i class="ri-vip-diamond-line"></i>
          </div>
          <div>
            <div class="stat-value-white">¥{{ (userProfile?.stats?.total_spent || 0).toFixed(2) }}</div>
            <div class="stat-label-white">累计消费</div>
          </div>
        </div>
      </section>

      <!-- 我的订单区域 -->
      <section v-if="activeTab === 'orders'">
        <div class="section-header">
          <h2 class="section-title">我的订单</h2>
        </div>

        <!-- iOS 分段控制器 (Filter Tabs) -->
        <div class="filter-tabs">
          <button
            v-for="tab in orderTabs"
            :key="tab.id"
            @click="orderFilter = tab.id"
            :class="['filter-tab', { active: orderFilter === tab.id }]"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- 加载状态 -->
        <div v-if="loadingOrders" class="loading-container">
          <el-icon class="is-loading" size="32"><Loading /></el-icon>
          <p>加载中...</p>
        </div>

        <!-- 空状态 -->
        <div v-else-if="filteredOrders.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="ri-file-list-3-line"></i>
          </div>
          <p>暂无相关订单</p>
        </div>

        <!-- 订单列表 -->
        <div v-else class="orders-list">
          <div
            v-for="order in filteredOrders"
            :key="order.id"
            class="order-card"
          >
            <!-- 订单头部 -->
            <div class="order-card-header">
              <div class="order-header-left">
                <div class="order-number-row">
                  <span class="order-label">订单号</span>
                  <span class="order-number">{{ order.order_number }}</span>
                </div>
                <div class="order-date">{{ order.created_at }}</div>
              </div>
              <span :class="['status-badge', getStatusClass(order.status)]">
                {{ getStatusText(order.status) }}
              </span>
            </div>

            <!-- 订单商品 -->
            <div class="order-items">
              <div
                v-for="item in order.items"
                :key="item.book_id"
                class="order-item"
              >
                <div class="item-image">
                  <el-image
                    :src="item.book_image"
                    :alt="item.book_title"
                    fit="cover"
                  >
                    <template #error>
                      <div class="image-error">
                        <i class="ri-book-2-line"></i>
                      </div>
                    </template>
                  </el-image>
                </div>
                <div class="item-info">
                  <h4 class="item-title">{{ item.book_title }}</h4>
                  <p class="item-author">{{ item.book_author }}</p>
                </div>
                <div class="item-price-info">
                  <div class="price-row">
                    <span class="price">¥{{ (item.unit_price || 0).toFixed(2) }}</span>
                    <span class="quantity">x{{ item.quantity }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 订单底部 & 操作 -->
            <div class="order-card-footer">
              <div class="order-total">
                <span class="total-label">总计:</span>
                <span class="total-amount">¥{{ order.total_amount.toFixed(2) }}</span>
              </div>

              <div class="order-actions">
                <button class="btn-secondary" @click="viewOrderDetail(order.id)">
                  查看详情
                </button>
                <button
                  v-if="order.status === 'delivered'"
                  class="btn-secondary"
                >
                  申请售后
                </button>
                <button
                  v-if="order.status === 'shipping'"
                  class="btn-primary"
                  @click="confirmReceipt(order.id)"
                >
                  确认收货
                </button>
                <button
                  v-if="order.status === 'pending' || order.status === 'processing'"
                  class="btn-secondary"
                  @click="cancelOrder(order.id)"
                >
                  取消订单
                </button>
                <button
                  v-if="order.status === 'cancelled'"
                  class="btn-primary"
                  @click="reorder(order.id)"
                >
                  再次购买
                </button>
                <button
                  v-if="order.status === 'cancelled' || order.status === 'delivered'"
                  class="btn-secondary"
                  @click="deleteOrder(order.id)"
                >
                  删除订单
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 收货地址标签页 -->
      <section v-if="activeTab === 'address'">
        <div class="section-header">
          <h2 class="section-title">收货地址</h2>
          <button class="btn-primary" @click="showAddressDialog()">新增地址</button>
        </div>

        <div v-if="addresses.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="ri-map-pin-line"></i>
          </div>
          <p>暂无收货地址</p>
        </div>

        <div v-else class="address-list">
          <div
            v-for="address in addresses"
            :key="address.id"
            class="address-card"
          >
            <div class="address-card-header">
              <div class="address-info">
                <span class="receiver-name">{{ address.receiver_name }}</span>
                <span class="receiver-phone">{{ address.receiver_phone }}</span>
              </div>
              <el-tag v-if="address.is_default" type="success" size="small">默认</el-tag>
            </div>
            <div class="address-detail">
              {{ address.full_address }}
            </div>
            <div class="address-card-footer">
              <div class="address-actions">
                <button class="btn-secondary" @click="showAddressDialog(address)">编辑</button>
                <button v-if="!address.is_default" class="btn-secondary" @click="setDefault(address.id)">
                  设为默认
                </button>
                <button class="btn-secondary" @click="deleteAddress(address.id)">删除</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 设置标签页 -->
      <section v-if="activeTab === 'settings'">
        <h2 class="section-title">账号设置</h2>

        <div class="settings-card">
          <div class="settings-item" @click="showPasswordDialog">
            <span>修改密码</span>
            <i class="ri-arrow-right-s-line"></i>
          </div>
          <div class="settings-item settings-item-danger" @click="logout">
            <span>退出登录</span>
          </div>
        </div>
      </section>

      <!-- 个人信息标签页 -->
      <section v-if="activeTab === 'info'">
        <h2 class="section-title">个人资料</h2>

        <div class="info-card">
          <div class="info-card-header">
            <span>基本信息</span>
            <button v-if="!editingProfile" class="btn-primary" @click="editingProfile = true">
              编辑资料
            </button>
            <div v-else class="edit-actions">
              <button class="btn-secondary" @click="cancelEditProfile">取消</button>
              <button class="btn-primary" @click="saveProfile">保存</button>
            </div>
          </div>

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
        </div>
      </section>
    </main>

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
        <button class="btn-secondary" @click="addressDialogVisible = false">取消</button>
        <button class="btn-primary" @click="saveAddress">保存</button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="500px"
    >
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
      </el-form>
      <template #footer>
        <button class="btn-secondary" @click="passwordDialogVisible = false">取消</button>
        <button class="btn-primary" @click="changePassword">确认修改</button>
      </template>
    </el-dialog>
  </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import PageContainer from './PageContainer.vue'
import { getUserProfile, updateUserProfile, changePassword as changePasswordApi, type UserProfile, type UserProfileUpdate, type PasswordChange } from '../api/userApi'
import { getAddresses, addAddress, updateAddress, deleteAddress as deleteAddressApi, setDefaultAddress, type Address } from '../api/addressApi'
import { getOrders, cancelOrder as cancelOrderApi, updateOrderStatus, getOrderDetail, deleteOrder as deleteOrderApi, type Order, type OrderStatus } from '../api/orderApi'

const router = useRouter()

// 当前标签页
const activeTab = ref('orders')

// 订单筛选
const orderFilter = ref('all')

// 导航菜单项
const navItems = [
  { id: 'orders', label: '我的订单', icon: 'ri-file-list-line', color: 'bg-blue' },
  { id: 'address', label: '收货地址', icon: 'ri-map-pin-line', color: 'bg-green' },
  { id: 'settings', label: '账号设置', icon: 'ri-settings-3-line', color: 'bg-gray' },
]

// 订单筛选标签
const orderTabs = [
  { id: 'all', label: '全部' },
  { id: 'pending', label: '待付款' },
  { id: 'shipping', label: '运输中' },
  { id: 'completed', label: '已完成' },
]

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

// 密码对话框
const passwordDialogVisible = ref(false)

// 收货地址列表
const addresses = ref<Address[]>([])

// 地址对话框
const addressDialogVisible = ref(false)

// 订单列表
const orders = ref<Order[]>([])
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

// 筛选后的订单列表
const filteredOrders = computed(() => {
  if (orderFilter.value === 'all') {
    return orders.value
  }
  if (orderFilter.value === 'pending') {
    return orders.value.filter(o => o.status === 'pending' || o.status === 'processing')
  }
  if (orderFilter.value === 'shipping') {
    return orders.value.filter(o => o.status === 'shipping')
  }
  if (orderFilter.value === 'completed') {
    return orders.value.filter(o => o.status === 'delivered')
  }
  return orders.value
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

// 加载订单列表
const loadOrders = async () => {
  const userId = Number(localStorage.getItem('user_id'))
  if (!userId) {
    return
  }

  try {
    loadingOrders.value = true
    orders.value = await getOrders(userId)
  } catch (error) {
    console.error('加载订单失败:', error)
  } finally {
    loadingOrders.value = false
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

// 显示编辑资料
const showEditProfile = () => {
  activeTab.value = 'info'
  editingProfile.value = true
}

// 显示密码对话框
const showPasswordDialog = () => {
  passwordDialogVisible.value = true
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
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
    passwordDialogVisible.value = false

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
  if (!currentAddress.receiver_name || !currentAddress.receiver_phone ||
      !currentAddress.province || !currentAddress.city ||
      !currentAddress.district || !currentAddress.detail_address) {
    ElMessage.warning('请填写完整的地址信息')
    return
  }

  try {
    const userId = Number(localStorage.getItem('user_id'))

    if (currentAddress.id) {
      await updateAddress(currentAddress.id, currentAddress)
      ElMessage.success('地址更新成功')
    } else {
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

// 获取状态文本
const getStatusText = (status?: OrderStatus): string => {
  const statusMap: Record<OrderStatus, string> = {
    pending: '待付款',
    processing: '处理中',
    shipping: '运输中',
    delivered: '已完成',
    cancelled: '已取消'
  }
  return status ? statusMap[status] : '未知状态'
}

// 获取状态标签类型
const getStatusClass = (status?: OrderStatus): string => {
  const classMap: Record<OrderStatus, string> = {
    pending: 'status-pending',
    processing: 'status-processing',
    shipping: 'status-shipping',
    delivered: 'status-completed',
    cancelled: 'status-cancelled'
  }
  return status ? classMap[status] : 'status-pending'
}

// 查看订单详情
const viewOrderDetail = (orderId: number) => {
  router.push(`/order/${orderId}`)
}

// 确认收货
const confirmReceipt = async (orderId: number) => {
  try {
    await ElMessageBox.confirm('确认已收到商品？', '确认收货', {
      confirmButtonText: '确认收货',
      cancelButtonText: '取消',
      type: 'success'
    })

    await updateOrderStatus(orderId, 'delivered')
    ElMessage.success('收货确认成功')
    await loadOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('确认收货失败:', error)
      ElMessage.error('确认收货失败')
    }
  }
}

// 取消订单
const cancelOrder = async (orderId: number) => {
  try {
    await ElMessageBox.confirm(
      '确认取消此订单？取消后将恢复库存，订单状态将变为已取消。',
      '取消订单',
      {
        confirmButtonText: '确认取消',
        cancelButtonText: '我再想想',
        type: 'warning'
      }
    )

    await cancelOrderApi(orderId)
    ElMessage.success('订单已取消')
    await loadOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('取消订单失败:', error)
      ElMessage.error('取消订单失败')
    }
  }
}

// 再次下单
const reorder = async (orderId: number) => {
  try {
    loadingOrders.value = true
    const orderDetail = await getOrderDetail(orderId)

    if (!orderDetail || !orderDetail.items || orderDetail.items.length === 0) {
      ElMessage.error('无法获取订单详情')
      return
    }

    const userId = Number(localStorage.getItem('user_id'))
    if (!userId) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }

    const checkoutItems = orderDetail.items.map(item => ({
      book_id: item.book_id,
      title: item.book_title || '未知商品',
      author: item.book_author || '未知作者',
      price: item.unit_price || 0,
      quantity: item.quantity
    }))

    sessionStorage.setItem('checkoutCart', JSON.stringify({
      items: checkoutItems
    }))

    ElMessage.success('正在为您准备订单...')
    setTimeout(() => {
      router.push('/checkout')
    }, 500)
  } catch (error) {
    console.error('再次下单失败:', error)
    ElMessage.error('再次下单失败')
  } finally {
    loadingOrders.value = false
  }
}

// 删除订单
const deleteOrder = async (orderId: number) => {
  try {
    await ElMessageBox.confirm('确认删除此订单？删除后将无法恢复。', '删除订单', {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteOrderApi(orderId)
    ElMessage.success('订单已删除')
    await loadOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除订单失败:', error)
      ElMessage.error('删除订单失败')
    }
  }
}

// 退出登录
const logout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '退出登录', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    localStorage.clear()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (error: any) {
    // 用户取消
  }
}

// 回到首页
const goToHome = () => {
  router.push('/')
}

// 页面加载时
onMounted(() => {
  loadUserProfile()
  loadAddresses()
  loadOrders()
})
</script>

<style scoped>
/* 引入RemixIcon字体 */
@import url('https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css');

/* 动态背景光球 */
.mesh-gradients {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
  pointer-events: none;
}

.gradient-blob {
  position: absolute;
  width: 384px;
  height: 384px;
  border-radius: 50%;
  mix-blend-mode: multiply;
  filter: blur(64px);
  opacity: 0.3;
}

.blob-1 {
  top: 0;
  left: 25%;
  background: #BFDBFE;
  animation: blob 10s infinite;
}

.blob-2 {
  top: 0;
  right: 25%;
  background: #BBF7D0;
  animation: blob 10s infinite 2s;
}

.blob-3 {
  bottom: -128px;
  left: 33%;
  background: #DDD6FE;
  animation: blob 10s infinite 4s;
}

@keyframes blob {
  0%, 100% {
    transform: translate(0px, 0px) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

.user-profile-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px;
  display: flex;
  gap: 32px;
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

/* ========== 左侧边栏 ========== */
.sidebar {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: fixed;
  top: 40px;
  left: calc((100vw - 1400px) / 2 + 20px);
  height: calc(100vh - 80px);
  overflow-y: auto;
}

/* 用户名片 */
.user-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.user-card-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 96px;
  background: linear-gradient(to bottom, #E0F2FE, white);
  z-index: 0;
}

.avatar-wrapper {
  position: relative;
  z-index: 10;
  margin-bottom: 12px;
  padding: 4px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.avatar-wrapper:hover {
  transform: scale(1.05);
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  color: #1D1D1F;
  margin: 0 0 8px 0;
  z-index: 10;
  position: relative;
}

.user-email {
  font-size: 14px;
  color: #86868B;
  margin: 0 0 16px 0;
  z-index: 10;
  position: relative;
}

.edit-profile-btn {
  width: 100%;
  padding: 8px 16px;
  border-radius: 12px;
  border: 1px solid #E5E5EA;
  background: white;
  color: #1D1D1F;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  z-index: 10;
  position: relative;
}

.edit-profile-btn:hover {
  background: #F5F5F7;
}

/* 导航菜单 */
.nav-menu {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  color: #6E6E73;
  text-decoration: none;
}

.nav-item:hover {
  background: #F5F5F7;
}

.nav-item.active {
  background: #E5E5EA;
  color: #000;
  font-weight: 600;
}

.nav-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.bg-blue { background: #007AFF; }
.bg-red { background: #FF3B30; }
.bg-green { background: #34C759; }
.bg-orange { background: #FF9500; }
.bg-gray { background: #8E8E93; }

.nav-arrow {
  margin-left: auto;
  color: #C7C7CC;
  font-size: 16px;
}

/* 回到首页按钮 */
.back-home-btn {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  width: 100%;
  color: #007AFF;
  font-size: 14px;
  font-weight: 500;
}

.back-home-btn:hover {
  background: rgba(0, 122, 255, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.15);
}

.back-home-btn i {
  font-size: 18px;
}

/* ========== 主内容区 ========== */
.main-content {
  flex: 1;
  min-width: 0;
  margin-left: 352px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* 数据仪表盘 */
.stats-dashboard {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-item {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 20px;
  border-radius: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 128px;
  transition: all 0.3s;
  cursor: pointer;
}

.stat-item:hover {
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}

.stat-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  margin-bottom: 12px;
}

.stat-primary .stat-icon {
  background: #E0F2FE;
  color: #007AFF;
}

.stat-success .stat-icon {
  background: #FEF3C7;
  color: #FF9500;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1D1D1F;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #86868B;
  font-weight: 500;
  margin-top: 4px;
}

/* 特色统计卡片（黑色背景） */
.stat-featured {
  grid-column: span 2;
  background: black;
  color: white;
  position: relative;
  overflow: hidden;
}

.stat-featured::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 128px;
  height: 128px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  filter: blur(40px);
  transform: translate(50%, -50%);
}

.stat-icon-white {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  margin-bottom: 12px;
}

.stat-value-white {
  font-size: 28px;
  font-weight: 600;
  line-height: 1;
  position: relative;
  z-index: 10;
}

.stat-label-white {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 4px;
  position: relative;
  z-index: 10;
}

/* ========== 内容区域 ========== */
.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #1D1D1F;
  margin: 0 0 24px 0;
  letter-spacing: -0.5px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

/* iOS 分段控制器 */
.filter-tabs {
  background: rgba(0, 0, 0, 0.05);
  padding: 4px;
  border-radius: 12px;
  display: flex;
  gap: 4px;
  margin-bottom: 32px;
  overflow-x: auto;
}

.filter-tab {
  flex: 1;
  min-width: 80px;
  padding: 8px 20px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #6E6E73;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.filter-tab:hover {
  color: #1D1D1F;
}

.filter-tab.active {
  background: white;
  color: #000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
}

/* 信息卡片 */
.info-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid rgba(255, 255, 255, 0.8);
  margin-bottom: 20px;
}

.info-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #F5F5F7;
}

.info-card-header span {
  font-size: 17px;
  font-weight: 600;
  color: #1D1D1F;
}

.edit-actions {
  display: flex;
  gap: 8px;
}

/* 地址列表 */
.address-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.address-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid rgba(255, 255, 255, 0.8);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.address-card:hover {
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.08);
  transform: translateY(-2px);
  border-color: rgba(0, 122, 255, 0.1);
}

.address-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  margin-bottom: 20px;
  border-bottom: 1px solid #F5F5F7;
}

.address-info {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.receiver-name {
  font-weight: 600;
  font-size: 17px;
  color: #1D1D1F;
}

.receiver-phone {
  color: #6E6E73;
  font-size: 15px;
}

.address-detail {
  color: #6E6E73;
  line-height: 1.6;
  font-size: 14px;
  padding: 20px 0;
  border-bottom: 1px solid #F5F5F7;
  margin-bottom: 16px;
}

.address-card-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.address-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 订单列表 */
.orders-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.order-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid rgba(255, 255, 255, 0.8);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.order-card:hover {
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.08);
  transform: translateY(-2px);
  border-color: rgba(0, 122, 255, 0.1);
}

.order-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid #F5F5F7;
}

.order-header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.order-number-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.order-label {
  color: #1D1D1F;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: -0.2px;
}

.order-number {
  color: #1D1D1F;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: -0.2px;
}

.order-date {
  color: #86868B;
  font-size: 12px;
  font-weight: 400;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-completed {
  background: #E6F9ED;
  color: #34C759;
}

.status-shipping {
  background: #FFF4E5;
  color: #FF9500;
}

.status-processing {
  background: #E0F2FE;
  color: #007AFF;
}

.status-pending {
  background: #F2F2F7;
  color: #86868B;
}

.status-cancelled {
  background: #FFE5E5;
  color: #FF3B30;
}

.order-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px 0;
  border-bottom: 1px solid #F5F5F7;
  margin-bottom: 16px;
}

.order-item {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.order-item:hover {
  background: rgba(0, 0, 0, 0.04);
  transform: translateX(2px);
}

.item-image {
  width: 64px;
  height: 80px;
  flex-shrink: 0;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.item-image :deep(.el-image) {
  width: 100%;
  height: 100%;
}

.image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.03);
  color: #C0C4CC;
  font-size: 24px;
}

.item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
}

.item-title {
  font-size: 15px;
  font-weight: 600;
  color: #1D1D1F;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.2px;
}

.item-author {
  font-size: 13px;
  color: #6E6E73;
  margin: 0;
}

.item-price-info {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  min-width: 120px;
}

.price-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.price {
  font-weight: 600;
  font-size: 15px;
  color: #1D1D1F;
}

.quantity {
  font-size: 13px;
  color: #86868B;
  font-weight: 500;
}

.order-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.order-total {
  display: flex;
  align-items: center;
  gap: 10px;
}

.total-label {
  color: #6E6E73;
  font-size: 14px;
  font-weight: 500;
}

.total-amount {
  font-size: 22px;
  font-weight: 600;
  color: #1D1D1F;
  letter-spacing: -0.5px;
}

.order-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 设置卡片 */
.settings-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid rgba(255, 255, 255, 0.8);
  overflow: hidden;
}

.settings-item {
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #F5F5F7;
  cursor: pointer;
  transition: all 0.3s;
}

.settings-item:hover {
  background: #F5F5F7;
}

.settings-item:last-child {
  border-bottom: none;
}

.settings-item-danger {
  color: #FF3B30;
}

/* 空状态 */
.empty-state {
  padding: 80px 20px;
  text-align: center;
  color: #6E6E73;
}

.empty-icon {
  width: 80px;
  height: 80px;
  background: #F5F5F7;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  font-size: 32px;
  color: #C7C7CC;
}

/* 加载状态 */
.loading-container {
  text-align: center;
  padding: 80px 20px;
  color: #6E6E73;
}

.loading-container p {
  margin-top: 16px;
  font-size: 15px;
}

/* 按钮样式 - 学习HTML文件 */
.btn-primary {
  padding: 8px 24px;
  border-radius: 12px;
  background: #000;
  color: white;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.btn-primary:hover {
  background: #333;
  transform: translateY(-1px);
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  padding: 8px 16px;
  border-radius: 12px;
  background: #F5F5F7;
  color: #6E6E73;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: #E5E5EA;
  color: #1D1D1F;
}

.btn-link {
  padding: 0;
  background: none;
  border: none;
  color: #007AFF;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-link:hover {
  color: #0051D5;
  text-decoration: underline;
}

.btn-link-danger {
  padding: 0;
  background: none;
  border: none;
  color: #FF3B30;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-link-danger:hover {
  color: #D32F2F;
  text-decoration: underline;
}

/* Element Plus 按钮优化 */
:deep(.el-button--primary) {
  background: #000;
  border: none;
  border-radius: 12px;
  font-weight: 500;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

:deep(.el-button--primary:hover) {
  background: #333;
  transform: translateY(-1px);
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.2);
}

:deep(.el-button) {
  border-radius: 12px;
  font-weight: 500;
  transition: all 0.3s;
}

:deep(.el-button:not(.el-button--primary)) {
  background: #F5F5F7;
  border: none;
  color: #6E6E73;
}

:deep(.el-button:not(.el-button--primary):hover) {
  background: #E5E5EA;
  color: #1D1D1F;
}

/* 表单优化 */
:deep(.el-input__wrapper) {
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #E5E5EA;
  box-shadow: none;
  transition: all 0.3s;
}

:deep(.el-input__wrapper:hover) {
  border-color: rgba(0, 122, 255, 0.3);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #007AFF;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

:deep(.el-textarea__inner) {
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #E5E5EA;
}

:deep(.el-textarea__inner:focus) {
  border-color: #007AFF;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

/* 对话框优化 */
:deep(.el-dialog) {
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

:deep(.el-dialog__header) {
  padding: 24px 24px 16px;
  border-bottom: 1px solid #F5F5F7;
}

:deep(.el-dialog__title) {
  font-size: 20px;
  font-weight: 600;
  color: #1D1D1F;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-dialog__footer) {
  padding: 16px 24px 24px;
  border-top: 1px solid #F5F5F7;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* 响应式 */
@media (max-width: 1024px) {
  .user-profile-container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    position: relative;
    top: 0;
  }

  .stats-dashboard {
    grid-template-columns: 1fr;
  }

  .stat-featured {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .user-profile-container {
    padding: 20px 16px;
  }

  .order-card {
    padding: 20px;
  }

  .order-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .order-card-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .order-actions {
    width: 100%;
  }

  .order-actions :deep(.el-button) {
    flex: 1;
  }
}
</style>
