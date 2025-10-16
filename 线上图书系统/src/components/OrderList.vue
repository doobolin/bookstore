<template>
  <div class="order-list">
    <div class="order-header">
      <h3 class="order-title">我的订单</h3>
    </div>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else-if="orders.length === 0" class="empty-orders">
      <div class="empty-icon">
        <el-icon size="48"><Document /></el-icon>
      </div>
      <p class="empty-text">暂无订单</p>
      <p class="empty-subtext">快去挑选心仪的书籍吧！</p>
      <el-button type="primary" @click="goToHome">去购物</el-button>
    </div>

    <div v-else class="orders-container">
      <div
        v-for="order in orders"
        :key="order.id"
        class="order-card"
      >
        <div class="order-card-header">
          <div class="order-number">
            <span class="label">订单号：</span>
            <span class="value">{{ order.order_number }}</span>
          </div>
          <div class="order-time">
            <span class="time-text">{{ order.created_at }}</span>
          </div>
        </div>

        <div class="order-card-body">
          <div class="order-total">
            <span class="total-label">订单金额：</span>
            <span class="total-amount">¥{{ order.total_amount.toFixed(2) }}</span>
          </div>
        </div>

        <div class="order-card-footer">
          <el-button size="small" @click="viewOrderDetail(order.id)">
            查看详情
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="cancelOrder(order.id)"
          >
            取消订单
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading, Document } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrders, cancelOrder as cancelOrderApi, type Order } from '../api/orderApi'

const router = useRouter()
const orders = ref<Order[]>([])
const loading = ref(false)

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
      '确认取消并删除此订单？取消后将恢复库存，订单将被永久删除。',
      '取消订单',
      {
        confirmButtonText: '确认取消',
        cancelButtonText: '我再想想',
        type: 'warning'
      }
    )

    await cancelOrderApi(orderId)
    ElMessage.success('订单已取消并删除')
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

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.order-list {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
  max-width: 900px;
  margin: 20px auto;
}

.order-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 255, 255, 0.2);
}

.order-title {
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(135deg, #00ffff, #ff00ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.loading-container {
  text-align: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.7);
}

.loading-container p {
  margin-top: 10px;
  font-size: 14px;
}

.empty-orders {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 15px;
}

.empty-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 10px 0;
}

.empty-subtext {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin: 0 0 20px 0;
}

.orders-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.order-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 255, 255, 0.15);
  border-radius: 10px;
  padding: 15px;
  transition: all 0.3s ease;
}

.order-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 255, 255, 0.2);
}

.order-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.order-number {
  display: flex;
  align-items: center;
  gap: 5px;
}

.order-number .label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
}

.order-number .value {
  color: #00ffff;
  font-weight: 600;
  font-size: 14px;
}

.order-card-body {
  margin-bottom: 15px;
}

.order-info {
  margin-bottom: 10px;
}

.info-row {
  display: flex;
  gap: 10px;
  margin-bottom: 5px;
  font-size: 14px;
}

.info-row .label {
  color: rgba(255, 255, 255, 0.6);
  min-width: 70px;
}

.info-row .value {
  color: rgba(255, 255, 255, 0.9);
}

.order-total {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.total-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  font-weight: 600;
}

.total-amount {
  font-size: 18px;
  font-weight: 800;
  color: #00ffff;
}

.order-card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
