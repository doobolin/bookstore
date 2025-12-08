<template>
  <PageContainer>
  <div class="order-list">
    <el-card class="order-header-card">
      <div class="header-content">
        <h2 class="order-title">我的订单</h2>
        <div class="status-tabs">
          <button
            v-for="tab in statusTabs"
            :key="tab.value"
            :class="['status-tab', { active: activeStatus === tab.value }]"
            @click="activeStatus = tab.value"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
    </el-card>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else-if="filteredOrders.length === 0" class="empty-orders">
      <el-empty description="暂无订单">
        <el-button type="primary" @click="goToHome">去购物</el-button>
      </el-empty>
    </div>

    <div v-else class="orders-container">
      <el-card
        v-for="order in filteredOrders"
        :key="order.id"
        class="order-card"
        shadow="hover"
      >
        <div class="order-card-header">
          <div class="order-number">
            <span class="label">订单号：</span>
            <span class="value">{{ order.order_number }}</span>
          </div>
          <div class="order-status-badge">
            <el-tag :type="getStatusType(order.status)" size="large">
              {{ getStatusText(order.status) }}
            </el-tag>
          </div>
        </div>

        <div class="order-card-body">
          <!-- 订单商品列表 -->
          <div v-if="order.items && order.items.length > 0" class="order-items-preview">
            <div
              v-for="item in order.items"
              :key="item.book_id"
              class="order-item-preview"
            >
              <div class="item-image">
                <el-image
                  :src="item.book_image"
                  :alt="item.book_title"
                  fit="cover"
                >
                  <template #error>
                    <div class="image-error">
                      <el-icon><Picture /></el-icon>
                    </div>
                  </template>
                </el-image>
              </div>
              <div class="item-info">
                <div class="item-title">{{ item.book_title }}</div>
                <div class="item-author">{{ item.book_author }}</div>
                <div class="item-quantity">x{{ item.quantity }}</div>
              </div>
            </div>
            <div v-if="order.total_items && order.total_items > 3" class="more-items">
              还有{{ order.total_items - 3 }}件商品...
            </div>
          </div>

          <div class="order-info-row">
            <div class="order-time">
              <el-icon><Clock /></el-icon>
              <span>{{ order.created_at }}</span>
            </div>
            <div class="order-total">
              <span class="total-label">订单金额：</span>
              <span class="total-amount">¥{{ order.total_amount.toFixed(2) }}</span>
            </div>
          </div>
        </div>

        <div class="order-card-footer">
          <el-button size="small" @click="viewOrderDetail(order.id)">
            查看详情
          </el-button>
          <el-button
            v-if="order.status === 'pending' || order.status === 'processing'"
            type="danger"
            size="small"
            @click="cancelOrder(order.id)"
          >
            取消订单
          </el-button>
          <el-button
            v-if="order.status === 'shipping'"
            type="success"
            size="small"
            @click="confirmReceipt(order.id)"
          >
            确认收货
          </el-button>
          <el-button
            v-if="order.status === 'cancelled'"
            type="primary"
            size="small"
            @click="reorder(order.id)"
          >
            再次下单
          </el-button>
          <el-button
            v-if="order.status === 'cancelled' || order.status === 'delivered'"
            type="danger"
            size="small"
            @click="deleteOrder(order.id)"
          >
            删除订单
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading, Clock, Picture } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageContainer from './PageContainer.vue'
import { getOrders, cancelOrder as cancelOrderApi, updateOrderStatus, getOrderDetail, deleteOrder as deleteOrderApi, type Order, type OrderStatus } from '../api/orderApi'

const router = useRouter()
const orders = ref<Order[]>([])
const loading = ref(false)
const activeStatus = ref<'all' | 'to_ship' | 'shipping' | 'cancelled' | 'after_sales'>('all')

// 状态标签页配置 - 用户视角：待发货、待收货、已取消、售后
const statusTabs = [
  { label: '全部', value: 'all' as const },
  { label: '待发货', value: 'to_ship' as const },
  { label: '待收货', value: 'shipping' as const },
  { label: '已取消', value: 'cancelled' as const },
  { label: '售后', value: 'after_sales' as const }
]

// 筛选后的订单列表
const filteredOrders = computed(() => {
  if (activeStatus.value === 'all') {
    return orders.value
  }

  // 待发货：pending 和 processing 状态
  if (activeStatus.value === 'to_ship') {
    return orders.value.filter(order =>
      order.status === 'pending' || order.status === 'processing'
    )
  }

  // 待收货：shipping 状态
  if (activeStatus.value === 'shipping') {
    return orders.value.filter(order => order.status === 'shipping')
  }

  // 已取消：cancelled 状态
  if (activeStatus.value === 'cancelled') {
    return orders.value.filter(order => order.status === 'cancelled')
  }

  // 售后：delivered 状态（不包含已取消）
  if (activeStatus.value === 'after_sales') {
    return orders.value.filter(order => order.status === 'delivered')
  }

  return orders.value
})

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

// 加载订单列表
const loadOrders = async () => {
  const userId = getUserId()
  if (!userId || !checkUserLogin()) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    loading.value = true
    orders.value = await getOrders(userId)
  } catch (error) {
    console.error('加载订单失败:', error)
    ElMessage.error('加载订单失败')
  } finally {
    loading.value = false
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

// 查看订单详情
const viewOrderDetail = (orderId: number) => {
  router.push(`/order/${orderId}`)
}

// 跳转到首页
const goToHome = () => {
  router.push('/')
}

// 获取状态文本
const getStatusText = (status?: OrderStatus): string => {
  const statusMap: Record<OrderStatus, string> = {
    pending: '待处理',
    processing: '处理中',
    shipping: '配送中',
    delivered: '已完成',
    cancelled: '已取消'
  }
  return status ? statusMap[status] : '未知状态'
}

// 获取状态标签类型
const getStatusType = (status?: OrderStatus): 'info' | 'warning' | 'success' | 'danger' => {
  const typeMap: Record<OrderStatus, 'info' | 'warning' | 'success' | 'danger'> = {
    pending: 'info',
    processing: 'warning',
    shipping: 'primary' as 'info',
    delivered: 'success',
    cancelled: 'danger'
  }
  return status ? typeMap[status] : 'info'
}

// 确认收货
const confirmReceipt = async (orderId: number) => {
  try {
    await ElMessageBox.confirm(
      '确认已收到商品？',
      '确认收货',
      {
        confirmButtonText: '确认收货',
        cancelButtonText: '取消',
        type: 'success'
      }
    )

    // 调用更新订单状态的API，将状态改为已完成
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

// 再次下单
const reorder = async (orderId: number) => {
  try {
    loading.value = true
    // 获取订单详情
    const orderDetail = await getOrderDetail(orderId)

    if (!orderDetail || !orderDetail.items || orderDetail.items.length === 0) {
      ElMessage.error('无法获取订单详情')
      return
    }

    // 检查用户是否登录
    const userId = getUserId()
    if (!userId) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }

    // 将订单商品数据存入 sessionStorage 供结账页面使用
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
    // 跳转到结账页面
    setTimeout(() => {
      router.push('/checkout')
    }, 500)
  } catch (error) {
    console.error('再次下单失败:', error)
    ElMessage.error('再次下单失败')
  } finally {
    loading.value = false
  }
}

// 删除订单
const deleteOrder = async (orderId: number) => {
  try {
    await ElMessageBox.confirm(
      '确认删除此订单？删除后将无法恢复。',
      '删除订单',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

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

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.order-list {
  max-width: 1000px;
  margin: 0 auto;
  background: #f5f5f7;
  padding: 20px;
  border-radius: 20px;
  position: relative;
  overflow: hidden;
}

/* 渐变波纹背景 */
.order-list::before {
  content: '';
  position: fixed;
  width: 200%;
  height: 200%;
  left: -50%;
  top: -50%;
  background:
    radial-gradient(circle at 30% 40%, rgba(100, 240, 255, 1) 0%, rgba(100, 240, 255, 0.6) 20%, transparent 45%),
    radial-gradient(circle at 70% 30%, rgba(150, 100, 255, 0.9) 0%, rgba(255, 100, 220, 0.5) 25%, transparent 50%),
    radial-gradient(circle at 50% 70%, rgba(50, 120, 220, 0.95) 0%, rgba(100, 20, 150, 0.6) 22%, transparent 48%);
  background-size: 100% 100%;
  animation: flowingWave1 8s ease-in-out infinite;
  filter: blur(40px);
  opacity: 0.3;
  z-index: 0;
  pointer-events: none;
}

.order-list::after {
  content: '';
  position: fixed;
  width: 200%;
  height: 200%;
  left: -50%;
  top: -50%;
  background:
    radial-gradient(circle at 20% 60%, rgba(255, 100, 200, 1) 0%, rgba(255, 150, 180, 0.7) 18%, transparent 42%),
    radial-gradient(circle at 80% 50%, rgba(200, 30, 200, 0.9) 0%, rgba(220, 50, 180, 0.6) 20%, transparent 46%),
    radial-gradient(circle at 45% 25%, rgba(255, 150, 100, 0.85) 0%, rgba(180, 70, 50, 0.5) 24%, transparent 50%);
  background-size: 100% 100%;
  animation: flowingWave2 10s ease-in-out infinite;
  filter: blur(50px);
  opacity: 0.25;
  z-index: 0;
  pointer-events: none;
}

@keyframes flowingWave1 {
  0% {
    transform: translate(0%, 0%) rotate(0deg) scale(1);
  }
  25% {
    transform: translate(-15%, 10%) rotate(90deg) scale(1.1);
  }
  50% {
    transform: translate(-10%, -15%) rotate(180deg) scale(1.05);
  }
  75% {
    transform: translate(15%, -8%) rotate(270deg) scale(1.12);
  }
  100% {
    transform: translate(0%, 0%) rotate(360deg) scale(1);
  }
}

@keyframes flowingWave2 {
  0% {
    transform: translate(0%, 0%) rotate(0deg) scale(1);
  }
  20% {
    transform: translate(12%, -10%) rotate(-72deg) scale(1.08);
  }
  40% {
    transform: translate(-8%, -12%) rotate(-144deg) scale(1.15);
  }
  60% {
    transform: translate(-15%, 8%) rotate(-216deg) scale(1.06);
  }
  80% {
    transform: translate(10%, 15%) rotate(-288deg) scale(1.12);
  }
  100% {
    transform: translate(0%, 0%) rotate(-360deg) scale(1);
  }
}

/* 确保内容在波纹之上 */
.order-list > * {
  position: relative;
  z-index: 1;
}

/* 头部卡片 - 增强毛玻璃 */
.order-header-card {
  margin-bottom: 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: saturate(180%) blur(30px);
  -webkit-backdrop-filter: saturate(180%) blur(30px);
  border: 0.5px solid rgba(255, 255, 255, 0.3);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.08),
    0 2px 8px rgba(0, 0, 0, 0.04),
    inset 0 1px 1px rgba(255, 255, 255, 0.9);
  overflow: hidden;
}

.order-header-card :deep(.el-card__body) {
  padding: 28px 32px;
  background: transparent;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.order-title {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.5px;
}

/* 状态标签页 - iOS风格圆角按钮 */
.status-tabs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.status-tab {
  padding: 8px 18px;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #1d1d1f;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.status-tab:hover {
  background: rgba(0, 0, 0, 0.08);
  transform: scale(1.02);
}

.status-tab.active {
  background: #007aff;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.3);
}

/* 加载状态 */
.loading-container {
  text-align: center;
  padding: 80px 20px;
  color: #6e6e73;
}

.loading-container p {
  margin-top: 16px;
  font-size: 15px;
}

.empty-orders {
  padding: 60px 20px;
}

/* 订单卡片容器 */
.orders-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 订单卡片 - 增强毛玻璃 */
.order-card {
  border-radius: 20px;
  border: 0.5px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.45);
  backdrop-filter: saturate(180%) blur(30px);
  -webkit-backdrop-filter: saturate(180%) blur(30px);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.08),
    0 2px 8px rgba(0, 0, 0, 0.04),
    inset 0 1px 1px rgba(255, 255, 255, 0.8);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.order-card:hover {
  background: rgba(255, 255, 255, 0.55);
  transform: translateY(-2px);
  box-shadow:
    0 12px 48px rgba(0, 0, 0, 0.12),
    0 4px 12px rgba(0, 0, 0, 0.06),
    inset 0 1px 1px rgba(255, 255, 255, 0.9);
}

.order-card :deep(.el-card__body) {
  padding: 24px;
}

/* 订单头部 */
.order-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
}

.order-number {
  display: flex;
  align-items: center;
  gap: 8px;
}

.order-number .label {
  color: #6e6e73;
  font-size: 14px;
  font-weight: 500;
}

.order-number .value {
  color: #007aff;
  font-weight: 600;
  font-size: 15px;
  padding: 4px 12px;
  background: rgba(0, 122, 255, 0.08);
  border-radius: 10px;
}

.order-status-badge {
  display: flex;
  align-items: center;
}

.order-status-badge :deep(.el-tag) {
  padding: 6px 14px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 13px;
  border: none;
}

/* 订单主体 */
.order-card-body {
  margin-bottom: 20px;
}

/* 订单商品预览 */
.order-items-preview {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px 0;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
  margin-bottom: 16px;
}

.order-item-preview {
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.order-item-preview:hover {
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
  color: #c0c4cc;
  font-size: 24px;
}

.item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-title {
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.2px;
}

.item-author {
  font-size: 13px;
  color: #6e6e73;
}

.item-quantity {
  font-size: 13px;
  color: #1d1d1f;
  font-weight: 600;
  padding: 3px 10px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  display: inline-block;
  width: fit-content;
}

.more-items {
  text-align: center;
  font-size: 13px;
  color: #007aff;
  font-weight: 500;
  padding: 10px 0;
  background: rgba(0, 122, 255, 0.05);
  border-radius: 10px;
}

/* 订单信息行 */
.order-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.order-time {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6e6e73;
  font-size: 13px;
  font-weight: 400;
}

.order-total {
  display: flex;
  align-items: center;
  gap: 10px;
}

.total-label {
  color: #6e6e73;
  font-size: 14px;
  font-weight: 500;
}

.total-amount {
  font-size: 22px;
  font-weight: 600;
  color: #ff3b30;
  letter-spacing: -0.5px;
}

/* 订单底部操作 - iOS风格按钮 */
.order-card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 16px;
  border-top: 0.5px solid rgba(0, 0, 0, 0.08);
}

.order-card-footer :deep(.el-button) {
  border-radius: 12px;
  padding: 8px 18px;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.order-card-footer :deep(.el-button--primary) {
  background: #007aff;
  border: none;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.25);
}

.order-card-footer :deep(.el-button--primary:hover) {
  background: #0051d5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
}

.order-card-footer :deep(.el-button--success) {
  background: #34c759;
  border: none;
  color: #fff;
  box-shadow: 0 2px 8px rgba(52, 199, 89, 0.25);
}

.order-card-footer :deep(.el-button--success:hover) {
  background: #28a745;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(52, 199, 89, 0.3);
}

.order-card-footer :deep(.el-button--danger) {
  background: #ff3b30;
  border: none;
  color: #fff;
  box-shadow: 0 2px 8px rgba(255, 59, 48, 0.25);
}

.order-card-footer :deep(.el-button--danger:hover) {
  background: #d32f2f;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 59, 48, 0.3);
}

.order-card-footer :deep(.el-button:not(.el-button--primary):not(.el-button--success):not(.el-button--danger)) {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 0.5px solid rgba(0, 0, 0, 0.1);
  color: #1d1d1f;
}

.order-card-footer :deep(.el-button:not(.el-button--primary):not(.el-button--success):not(.el-button--danger):hover) {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(0, 122, 255, 0.3);
  color: #007aff;
  transform: translateY(-1px);
}
</style>
