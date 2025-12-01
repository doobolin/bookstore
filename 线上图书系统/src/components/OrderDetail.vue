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
}

.loading-container,
.error-container {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.loading-container p {
  margin-top: 16px;
  font-size: 14px;
}

.order-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 订单头部 */
.order-header-card {
  background: #fff;
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
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.status-tag {
  font-size: 14px;
  padding: 6px 16px;
}

.order-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.meta-label {
  color: #909399;
}

.meta-value {
  color: #606266;
  font-weight: 500;
}

/* 商品列表卡片 */
.items-card {
  background: #fff;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.items-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.order-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  transition: all 0.3s;
}

.order-item:hover {
  background: #ecf5ff;
}

.item-image {
  width: 80px;
  height: 100px;
  flex-shrink: 0;
  border-radius: 6px;
  overflow: hidden;
  background: #fff;
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
  color: #303133;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-author,
.item-isbn {
  font-size: 13px;
  color: #909399;
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
  color: #909399;
}

.pricing-value {
  color: #606266;
  font-weight: 500;
}

.subtotal-row {
  margin-top: 4px;
  padding-top: 8px;
  border-top: 1px dashed #dcdfe6;
}

.subtotal-value {
  font-size: 16px;
  font-weight: 600;
  color: #f56c6c;
}

/* 总计卡片 */
.summary-card {
  background: #fff;
}

.order-summary {
  padding: 16px;
  background: #f0f9ff;
  border-radius: 8px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-label {
  font-size: 16px;
  font-weight: 500;
  color: #606266;
}

.summary-amount {
  font-size: 24px;
  font-weight: 600;
  color: #f56c6c;
}

/* 操作按钮 */
.order-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 0;
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
