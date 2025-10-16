<template>
  <div class="order-detail">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else-if="!order" class="error-container">
      <el-icon size="48"><WarningFilled /></el-icon>
      <p>订单不存在或已被删除</p>
      <el-button @click="goBack">返回订单列表</el-button>
    </div>

    <div v-else class="order-content">
      <div class="order-header">
        <div class="header-left">
          <h3 class="order-title">订单详情</h3>
          <div class="order-number">订单号：{{ order.order_number }}</div>
        </div>
        <div class="header-right">
          <div class="order-time">{{ order.created_at }}</div>
        </div>
      </div>

      <div class="order-section">
        <h4 class="section-title">订单商品</h4>
        <div class="items-container">
          <div
            v-for="item in order.items"
            :key="item.book_id"
            class="order-item"
          >
            <div class="item-image">
              <img :src="item.book_image" :alt="item.book_title" @error="handleImageError" />
            </div>
            <div class="item-details">
              <h5 class="item-title">{{ item.book_title }}</h5>
              <p class="item-author">作者：{{ item.book_author }}</p>
              <p class="item-isbn">ISBN：{{ item.book_isbn }}</p>
            </div>
            <div class="item-pricing">
              <div class="unit-price">单价：¥{{ item.unit_price?.toFixed(2) }}</div>
              <div class="quantity">数量：{{ item.quantity }}</div>
              <div class="subtotal">小计：¥{{ item.subtotal?.toFixed(2) }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="order-summary">
        <div class="summary-row">
          <span class="summary-label">订单总金额：</span>
          <span class="summary-amount">¥{{ order.total_amount.toFixed(2) }}</span>
        </div>
      </div>

      <div class="order-actions">
        <el-button @click="goBack">返回订单列表</el-button>
        <el-button type="danger" @click="cancelOrder">
          取消订单
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Loading, WarningFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrderDetail, cancelOrder as cancelOrderApi, type Order } from '../api/orderApi'

const router = useRouter()
const route = useRoute()

const order = ref<Order | null>(null)
const loading = ref(false)

// 加载订单详情
const loadOrderDetail = async () => {
  const orderId = parseInt(route.params.id as string)
  if (!orderId || isNaN(orderId)) {
    ElMessage.error('无效的订单ID')
    router.push('/orders')
    return
  }

  try {
    loading.value = true
    order.value = await getOrderDetail(orderId)
  } catch (error) {
    console.error('加载订单详情失败:', error)
    ElMessage.error('加载订单详情失败')
  } finally {
    loading.value = false
  }
}

// 图片加载失败处理
const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  target.src = '/images/book-placeholder.svg'
}

// 取消订单
const cancelOrder = async () => {
  if (!order.value) return

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

    await cancelOrderApi(order.value.id)
    ElMessage.success('订单已取消并删除')
    router.push('/orders')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('取消订单失败:', error)
      ElMessage.error('取消订单失败')
    }
  }
}

// 返回订单列表
const goBack = () => {
  router.push('/orders')
}

onMounted(() => {
  loadOrderDetail()
})
</script>

<style scoped>
.order-detail {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
  max-width: 900px;
  margin: 20px auto;
}

.loading-container,
.error-container {
  text-align: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.7);
}

.loading-container p,
.error-container p {
  margin: 15px 0;
  font-size: 14px;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid rgba(0, 255, 255, 0.2);
}

.header-left {
  flex: 1;
}

.order-title {
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(135deg, #00ffff, #ff00ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 10px 0;
}

.order-number {
  color: #00ffff;
  font-size: 14px;
  font-weight: 600;
}

.order-section {
  margin-bottom: 25px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 255, 255, 0.1);
  border-radius: 10px;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #00ffff;
  margin: 0 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.section-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-row {
  display: flex;
  gap: 10px;
  font-size: 14px;
}

.info-row .label {
  color: rgba(255, 255, 255, 0.6);
  min-width: 80px;
  flex-shrink: 0;
}

.info-row .value {
  color: rgba(255, 255, 255, 0.9);
  flex: 1;
}

.items-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.order-item {
  display: flex;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.order-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(0, 255, 255, 0.2);
}

.item-image {
  width: 80px;
  height: 100px;
  flex-shrink: 0;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
}

.item-details {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin: 0 0 8px 0;
}

.item-author,
.item-isbn {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin: 4px 0;
}

.item-pricing {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
  min-width: 120px;
}

.unit-price,
.quantity {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.subtotal {
  font-size: 16px;
  font-weight: 700;
  color: #00ffff;
}

.order-summary {
  margin: 30px 0;
  padding: 20px;
  background: rgba(0, 255, 255, 0.05);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 10px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-label {
  font-size: 18px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.summary-amount {
  font-size: 24px;
  font-weight: 800;
  color: #00ffff;
}

.order-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
