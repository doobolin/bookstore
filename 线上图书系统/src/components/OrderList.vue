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
}

.order-header-card {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.order-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.status-tabs {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.status-tab {
  padding: 8px 20px;
  border: 1px solid #dcdfe6;
  background: #fff;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: all 0.3s;
}

.status-tab:hover {
  border-color: #409eff;
  color: #409eff;
}

.status-tab.active {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
}

.loading-container {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.loading-container p {
  margin-top: 16px;
  font-size: 14px;
}

.empty-orders {
  padding: 40px 20px;
}

.orders-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-card {
  transition: all 0.3s;
}

.order-card:hover {
  transform: translateY(-2px);
}

.order-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.order-number {
  display: flex;
  align-items: center;
  gap: 8px;
}

.order-number .label {
  color: #909399;
  font-size: 14px;
}

.order-number .value {
  color: #409eff;
  font-weight: 600;
  font-size: 14px;
}

.order-status-badge {
  display: flex;
  align-items: center;
}

.order-card-body {
  margin-bottom: 16px;
}

/* 订单商品预览 */
.order-items-preview {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 12px;
}

.order-item-preview {
  display: flex;
  gap: 12px;
  align-items: center;
}

.item-image {
  width: 60px;
  height: 75px;
  flex-shrink: 0;
  border-radius: 6px;
  overflow: hidden;
  background: #f5f7fa;
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
  background: #f5f7fa;
  color: #c0c4cc;
  font-size: 20px;
}

.item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-author {
  font-size: 12px;
  color: #909399;
}

.item-quantity {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.more-items {
  text-align: center;
  font-size: 13px;
  color: #909399;
  padding: 8px 0;
  background: #f5f7fa;
  border-radius: 4px;
}

.order-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}

.order-time {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 13px;
}

.order-total {
  display: flex;
  align-items: center;
  gap: 12px;
}

.total-label {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.total-amount {
  font-size: 20px;
  font-weight: 600;
  color: #f56c6c;
}

.order-card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}
</style>
