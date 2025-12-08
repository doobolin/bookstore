<template>
  <PageContainer>
  <div class="order-detail">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else-if="!order" class="error-container">
      <el-empty description="订单不存在或已被删除">
        <el-button @click="goBack">返回订单列表</el-button>
      </el-empty>
    </div>

    <div v-else class="order-content">
      <!-- 订单头部信息 -->
      <el-card class="order-header-card">
        <div class="order-header">
          <div class="header-left">
            <div class="title-row">
              <h2 class="order-title">订单详情</h2>
              <el-tag :type="getStatusType(order.status)" size="large" class="status-tag">
                {{ getStatusText(order.status) }}
              </el-tag>
            </div>
            <div class="order-meta">
              <div class="meta-item">
                <span class="meta-label">订单号：</span>
                <span class="meta-value">{{ order.order_number }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">用户：</span>
                <span class="meta-value">{{ order.username || '未知用户' }}</span>
              </div>
              <div class="meta-item">
                <el-icon><Clock /></el-icon>
                <span class="meta-value">{{ order.created_at }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 订单商品列表 -->
      <el-card class="items-card">
        <template #header>
          <div class="card-header">
            <span>订单商品</span>
          </div>
        </template>
        <div class="items-container">
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
                @error="handleImageError"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
            </div>
            <div class="item-details">
              <h3 class="item-title">{{ item.book_title }}</h3>
              <p class="item-author">作者：{{ item.book_author }}</p>
              <p class="item-isbn">ISBN：{{ item.book_isbn }}</p>
            </div>
            <div class="item-pricing">
              <div class="pricing-row">
                <span class="pricing-label">单价：</span>
                <span class="pricing-value">¥{{ item.unit_price?.toFixed(2) }}</span>
              </div>
              <div class="pricing-row">
                <span class="pricing-label">数量：</span>
                <span class="pricing-value">{{ item.quantity }}</span>
              </div>
              <div class="pricing-row subtotal-row">
                <span class="pricing-label">小计：</span>
                <span class="subtotal-value">¥{{ item.subtotal?.toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 订单总计 -->
      <el-card class="summary-card">
        <div class="order-summary">
          <div class="summary-row">
            <span class="summary-label">订单总金额：</span>
            <span class="summary-amount">¥{{ order.total_amount.toFixed(2) }}</span>
          </div>
        </div>
      </el-card>

      <!-- 操作按钮 -->
      <div class="order-actions">
        <el-button @click="goBack">返回订单列表</el-button>
        <el-button
          v-if="order.status === 'pending' || order.status === 'processing'"
          type="danger"
          @click="cancelOrder"
        >
          取消订单
        </el-button>
        <el-button
          v-if="order.status === 'shipping'"
          type="success"
          @click="confirmReceipt"
        >
          确认收货
        </el-button>
        <el-button
          v-if="order.status === 'cancelled' || order.status === 'delivered'"
          type="danger"
          @click="deleteOrder"
        >
          删除订单
        </el-button>
      </div>
    </div>
  </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Loading, Clock, Picture } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageContainer from './PageContainer.vue'
import { getOrderDetail, cancelOrder as cancelOrderApi, updateOrderStatus, deleteOrder as deleteOrderApi, type Order, type OrderStatus } from '../api/orderApi'

const router = useRouter()
const route = useRoute()

const order = ref<Order | null>(null)
const loading = ref(false)

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
      '确认取消此订单？取消后将恢复库存，订单状态将变为已取消。',
      '取消订单',
      {
        confirmButtonText: '确认取消',
        cancelButtonText: '我再想想',
        type: 'warning'
      }
    )

    await cancelOrderApi(order.value.id)
    ElMessage.success('订单已取消')
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

// 确认收货
const confirmReceipt = async () => {
  if (!order.value) return

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
    await updateOrderStatus(order.value.id, 'delivered')
    ElMessage.success('收货确认成功')
    await loadOrderDetail()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('确认收货失败:', error)
      ElMessage.error('确认收货失败')
    }
  }
}

// 删除订单
const deleteOrder = async () => {
  if (!order.value) return

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

    await deleteOrderApi(order.value.id)
    ElMessage.success('订单已删除')
    router.push('/orders')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除订单失败:', error)
      ElMessage.error('删除订单失败')
    }
  }
}

onMounted(() => {
  loadOrderDetail()
})
</script>

<style scoped>
.order-detail {
  max-width: 1000px;
  margin: 0 auto;
  background: #f5f5f7;
  padding: 20px;
  border-radius: 20px;
  position: relative;
  overflow: hidden;
}

/* 渐变波纹背景 */
.order-detail::before {
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

.order-detail::after {
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
.order-detail > * {
  position: relative;
  z-index: 1;
}

.loading-container,
.error-container {
  text-align: center;
  padding: 60px 20px;
  color: #6e6e73;
}

.loading-container p {
  margin-top: 16px;
  font-size: 15px;
}

.order-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 订单头部 - 增强毛玻璃 */
.order-header-card {
  border-radius: 20px;
  border: 0.5px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: saturate(180%) blur(30px);
  -webkit-backdrop-filter: saturate(180%) blur(30px);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.08),
    0 2px 8px rgba(0, 0, 0, 0.04),
    inset 0 1px 1px rgba(255, 255, 255, 0.9);
}

.order-header-card :deep(.el-card__body) {
  padding: 28px;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left {
  flex: 1;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.order-title {
  margin: 0;
  font-size: 26px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.5px;
}

.status-tag {
  font-size: 13px;
  font-weight: 600;
  padding: 6px 16px;
  border-radius: 12px;
  border: none;
}

.order-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.meta-label {
  color: #6e6e73;
  font-weight: 500;
}

.meta-value {
  color: #1d1d1f;
  font-weight: 600;
}

/* 商品列表卡片 - 增强毛玻璃 */
.items-card {
  border-radius: 20px;
  border: 0.5px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.45);
  backdrop-filter: saturate(180%) blur(30px);
  -webkit-backdrop-filter: saturate(180%) blur(30px);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.08),
    0 2px 8px rgba(0, 0, 0, 0.04),
    inset 0 1px 1px rgba(255, 255, 255, 0.8);
}

.items-card :deep(.el-card__header) {
  background: rgba(247, 247, 247, 0.6);
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.06);
  padding: 18px 24px;
}

.items-card :deep(.el-card__body) {
  padding: 24px;
}

.card-header {
  font-size: 17px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.3px;
}

.items-container {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.order-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.order-item:hover {
  background: rgba(0, 0, 0, 0.04);
  transform: translateX(2px);
}

.item-image {
  width: 80px;
  height: 100px;
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

.item-details {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.3px;
}

.item-author,
.item-isbn {
  font-size: 13px;
  color: #6e6e73;
  margin: 4px 0;
}

.item-pricing {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
  min-width: 140px;
  text-align: right;
}

.pricing-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.pricing-label {
  color: #6e6e73;
  font-weight: 500;
}

.pricing-value {
  color: #1d1d1f;
  font-weight: 600;
}

.subtotal-row {
  margin-top: 4px;
  padding-top: 8px;
  border-top: 0.5px dashed rgba(0, 0, 0, 0.1);
}

.subtotal-value {
  font-size: 17px;
  font-weight: 600;
  color: #ff3b30;
  letter-spacing: -0.3px;
}

/* 总计卡片 - 增强毛玻璃 */
.summary-card {
  border-radius: 20px;
  border: 0.5px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.45);
  backdrop-filter: saturate(180%) blur(30px);
  -webkit-backdrop-filter: saturate(180%) blur(30px);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.08),
    0 2px 8px rgba(0, 0, 0, 0.04),
    inset 0 1px 1px rgba(255, 255, 255, 0.8);
}

.summary-card :deep(.el-card__body) {
  padding: 24px;
}

.order-summary {
  padding: 20px;
  background: rgba(0, 122, 255, 0.05);
  border-radius: 14px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-label {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.3px;
}

.summary-amount {
  font-size: 26px;
  font-weight: 600;
  color: #ff3b30;
  letter-spacing: -0.5px;
}

/* 操作按钮 - iOS风格 */
.order-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 0;
}

.order-actions :deep(.el-button) {
  border-radius: 12px;
  padding: 10px 20px;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.order-actions :deep(.el-button--primary) {
  background: #007aff;
  border: none;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.25);
}

.order-actions :deep(.el-button--primary:hover) {
  background: #0051d5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
}

.order-actions :deep(.el-button--success) {
  background: #34c759;
  border: none;
  color: #fff;
  box-shadow: 0 2px 8px rgba(52, 199, 89, 0.25);
}

.order-actions :deep(.el-button--success:hover) {
  background: #28a745;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(52, 199, 89, 0.3);
}

.order-actions :deep(.el-button--danger) {
  background: #ff3b30;
  border: none;
  color: #fff;
  box-shadow: 0 2px 8px rgba(255, 59, 48, 0.25);
}

.order-actions :deep(.el-button--danger:hover) {
  background: #d32f2f;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 59, 48, 0.3);
}

.order-actions :deep(.el-button:not(.el-button--primary):not(.el-button--success):not(.el-button--danger)) {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 0.5px solid rgba(0, 0, 0, 0.1);
  color: #1d1d1f;
}

.order-actions :deep(.el-button:not(.el-button--primary):not(.el-button--success):not(.el-button--danger):hover) {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(0, 122, 255, 0.3);
  color: #007aff;
  transform: translateY(-1px);
}

/* 响应式 */
@media (max-width: 768px) {
  .order-item {
    flex-direction: column;
  }

  .item-pricing {
    width: 100%;
    text-align: left;
  }

  .pricing-row {
    justify-content: space-between;
  }

  .order-meta {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
