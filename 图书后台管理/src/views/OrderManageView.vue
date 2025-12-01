<template>
  <div class="order-manage-container">
    <div class="page-header">
      <button class="refresh-btn" @click="fetchOrders" :disabled="loading">
        🔄 刷新
      </button>
    </div>

    <!-- 状态筛选标签 -->
    <div class="status-tabs">
      <button
        v-for="tab in statusTabs"
        :key="tab.value"
        :class="['status-tab', { active: activeStatus === tab.value }]"
        @click="activeStatus = tab.value"
      >
        {{ tab.label }}
        <span v-if="getStatusCount(tab.value) > 0" class="tab-count">{{ getStatusCount(tab.value) }}</span>
      </button>
    </div>

    <!-- 订单列表 -->
    <div class="order-list">
      <div class="list-header">
        <div class="header-item">订单号</div>
        <div class="header-item">用户名</div>
        <div class="header-item">订单金额</div>
        <div class="header-item">订单状态</div>
        <div class="header-item">下单时间</div>
        <div class="header-item">操作</div>
      </div>

      <div v-if="loading" class="loading-message">
        正在加载订单数据...
      </div>

      <div v-else-if="filteredOrders.length === 0" class="empty-message">
        {{ activeStatus === 'all' ? '暂无订单数据' : '该状态下暂无订单' }}
      </div>

      <div v-else>
        <div
          v-for="order in filteredOrders"
          :key="order.id"
          class="order-item"
        >
          <div class="order-info">{{ order.order_number }}</div>
          <div class="order-info">{{ order.username || '未知用户' }}</div>
          <div class="order-info amount">¥{{ order.total_amount.toFixed(2) }}</div>
          <div class="order-info">
            <span :class="['status-badge', getStatusClass(order.status)]">
              {{ getStatusText(order.status) }}
            </span>
          </div>
          <div class="order-info">{{ formatDate(order.created_at) }}</div>
          <div class="order-actions">
            <button class="view-btn" @click="viewOrderDetail(order)">
              👁️ 详情
            </button>
            <button
              v-if="order.status === 'pending' || order.status === 'processing'"
              class="ship-btn"
              @click="quickShip(order)"
            >
              📦 发货
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 订单详情模态框 -->
    <div v-if="detailModalVisible" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>订单详情</h3>
          <button class="close-btn" @click="closeDetailModal">×</button>
        </div>
        <div class="modal-body" v-if="currentOrder">
          <div class="detail-section">
            <h4>订单信息</h4>
            <div class="detail-row">
              <span class="detail-label">订单号：</span>
              <span class="detail-value">{{ currentOrder.order_number }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">用户名：</span>
              <span class="detail-value">{{ currentOrder.username || '未知用户' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">订单状态：</span>
              <span class="detail-value">
                <span :class="['status-badge', getStatusClass(currentOrder.status)]">
                  {{ getStatusText(currentOrder.status) }}
                </span>
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">订单金额：</span>
              <span class="detail-value amount">¥{{ currentOrder.total_amount.toFixed(2) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">下单时间：</span>
              <span class="detail-value">{{ formatDate(currentOrder.created_at) }}</span>
            </div>
          </div>

          <div class="detail-section">
            <h4>订单商品</h4>
            <div class="items-table">
              <div class="items-header">
                <div>书名</div>
                <div>作者</div>
                <div>单价</div>
                <div>数量</div>
                <div>小计</div>
              </div>
              <div
                v-for="(item, index) in currentOrder.items"
                :key="index"
                class="items-row"
              >
                <div>{{ item.book_title || '未知' }}</div>
                <div>{{ item.book_author || '未知' }}</div>
                <div>¥{{ item.unit_price?.toFixed(2) || '0.00' }}</div>
                <div>{{ item.quantity }}</div>
                <div class="amount">¥{{ item.subtotal?.toFixed(2) || '0.00' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getAllOrders, getOrderDetail, updateOrderStatus, deleteOrder } from '../api/orderApi'
import type { Order, OrderStatus } from '../api/orderApi'

const orders = ref<Order[]>([])
const loading = ref(false)
const detailModalVisible = ref(false)
const currentOrder = ref<Order | null>(null)
const activeStatus = ref<'all' | 'to_ship' | OrderStatus>('all')

// 状态标签页配置 - 删除待处理和处理中状态
const statusTabs = [
  { label: '全部订单', value: 'all' as const },
  { label: '待发货', value: 'to_ship' as const },
  { label: '配送中', value: 'shipping' as const },
  { label: '已完成', value: 'delivered' as const },
  { label: '已取消', value: 'cancelled' as const }
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

  return orders.value.filter(order => order.status === activeStatus.value)
})

// 获取各状态的订单数量
const getStatusCount = (status: 'all' | 'to_ship' | OrderStatus): number => {
  if (status === 'all') {
    return orders.value.length
  }

  // 待发货：pending 和 processing 状态的订单数量
  if (status === 'to_ship') {
    return orders.value.filter(order =>
      order.status === 'pending' || order.status === 'processing'
    ).length
  }

  return orders.value.filter(order => order.status === status).length
}

// 获取订单列表
const fetchOrders = async () => {
  loading.value = true
  try {
    const response = await getAllOrders()
    orders.value = response.orders
    // 移除加载成功提示，直接显示订单列表
  } catch (error) {
    console.error('获取订单列表失败:', error)
    showMessage('获取订单列表失败', 'error')
  } finally {
    loading.value = false
  }
}

// 查看订单详情
const viewOrderDetail = async (order: Order) => {
  try {
    const detail = await getOrderDetail(order.id)
    if (detail) {
      currentOrder.value = detail
      detailModalVisible.value = true
    }
  } catch (error) {
    console.error('获取订单详情失败:', error)
    showMessage('获取订单详情失败', 'error')
  }
}

// 关闭详情模态框
const closeDetailModal = () => {
  detailModalVisible.value = false
  currentOrder.value = null
}

// 快速发货（直接将状态改为配送中）
const quickShip = async (order: Order) => {
  try {
    await updateOrderStatus(order.id, 'shipping')
    showMessage('订单已发货，状态更新为配送中', 'success')

    // 刷新订单列表
    await fetchOrders()

    // 自动切换到配送中标签页
    activeStatus.value = 'shipping'
  } catch (error) {
    console.error('发货失败:', error)
    showMessage('发货失败', 'error')
  }
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
  return status ? statusMap[status] : '未知'
}

// 获取状态样式类名
const getStatusClass = (status?: OrderStatus): string => {
  const classMap: Record<OrderStatus, string> = {
    pending: 'status-pending',
    processing: 'status-processing',
    shipping: 'status-shipping',
    delivered: 'status-delivered',
    cancelled: 'status-cancelled'
  }
  return status ? classMap[status] : ''
}

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 显示消息
const showMessage = (message: string, type: 'success' | 'error') => {
  alert(message)
}

onMounted(() => {
  fetchOrders()
})
</script>

<style scoped lang="scss">
.order-manage-container {
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  color: #4caf50;
  font-size: 24px;
}

.refresh-btn {
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

.refresh-btn:hover:not(:disabled) {
  background-color: #45a049;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 状态标签样式 */
.status-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.status-tab {
  position: relative;
  padding: 10px 20px;
  background-color: #2a2a2a;
  color: #b0b0b0;
  border: 1px solid #333;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-tab:hover {
  background-color: #333;
  border-color: #4caf50;
  color: #e0e0e0;
}

.status-tab.active {
  background-color: #4caf50;
  color: white;
  border-color: #4caf50;
}

.tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.status-tab.active .tab-count {
  background-color: rgba(255, 255, 255, 0.3);
}

/* 订单列表样式 */
.order-list {
  background-color: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
}

.list-header {
  display: grid;
  grid-template-columns: 200px 120px 120px 140px 180px 200px;
  background-color: #2a2a2a;
  padding: 16px 20px;
  font-weight: 600;
  color: #4caf50;
  border-bottom: 1px solid #333;
}

.header-item {
  text-align: left;
}

.order-item {
  display: grid;
  grid-template-columns: 200px 120px 120px 140px 180px 200px;
  padding: 16px 20px;
  border-bottom: 1px solid #333;
  transition: background-color 0.2s ease;
  align-items: center;
}

.order-item:hover {
  background-color: #252525;
}

.order-item:last-child {
  border-bottom: none;
}

.order-info {
  color: #e0e0e0;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-info.amount {
  color: #f56c6c;
  font-weight: bold;
}

.order-info.address {
  white-space: normal;
  line-height: 1.4;
}

/* 状态标签 */
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background-color: rgba(100, 181, 246, 0.2);
  color: #64b5f6;
}

.status-processing {
  background-color: rgba(255, 167, 38, 0.2);
  color: #ffa726;
}

.status-shipping {
  background-color: rgba(156, 39, 176, 0.2);
  color: #ab47bc;
}

.status-delivered {
  background-color: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}

.status-cancelled {
  background-color: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

/* 操作按钮 */
.order-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.view-btn,
.ship-btn,
.delete-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s ease;
}

.view-btn {
  background-color: #2196f3;
  color: white;
}

.view-btn:hover {
  background-color: #1976d2;
}

.ship-btn {
  background-color: #4caf50;
  color: white;
}

.ship-btn:hover {
  background-color: #45a049;
}

.delete-btn {
  background-color: #f44336;
  color: white;
}

.delete-btn:hover {
  background-color: #d32f2f;
}

/* 状态下拉菜单 */
.status-dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: #2a2a2a;
  border: 1px solid #333;
  border-radius: 4px;
  margin-top: 4px;
  min-width: 120px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.dropdown-item {
  padding: 10px 16px;
  color: #e0e0e0;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 14px;
}

.dropdown-item:hover {
  background-color: #333;
}

.dropdown-item.danger {
  color: #f44336;
  border-top: 1px solid #333;
}

.loading-message {
  padding: 40px;
  text-align: center;
  color: #4caf50;
  font-weight: 500;
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
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #1e1e1e;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content.small {
  max-width: 500px;
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
  font-size: 20px;
}

.close-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 28px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.close-btn:hover {
  color: #fff;
}

.modal-body {
  padding: 20px;
}

/* 详情部分 */
.detail-section {
  margin-bottom: 30px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  color: #4caf50;
  margin: 0 0 16px 0;
  font-size: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #333;
}

.detail-row {
  display: flex;
  padding: 12px 0;
  border-bottom: 1px solid #2a2a2a;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  flex: 0 0 120px;
  color: #b0b0b0;
  font-weight: 500;
}

.detail-value {
  flex: 1;
  color: #e0e0e0;
}

.detail-value.amount {
  color: #f56c6c;
  font-weight: bold;
}

/* 商品表格 */
.items-table {
  background-color: #2a2a2a;
  border-radius: 4px;
  overflow: hidden;
}

.items-header {
  display: grid;
  grid-template-columns: 2fr 1fr 100px 80px 100px;
  padding: 12px 16px;
  background-color: #333;
  color: #4caf50;
  font-weight: 600;
  font-size: 14px;
}

.items-row {
  display: grid;
  grid-template-columns: 2fr 1fr 100px 80px 100px;
  padding: 12px 16px;
  border-bottom: 1px solid #333;
  color: #e0e0e0;
  font-size: 14px;
}

.items-row:last-child {
  border-bottom: none;
}

.items-row div.amount {
  color: #f56c6c;
  font-weight: bold;
}

/* 滚动条样式 */
.modal-content::-webkit-scrollbar {
  width: 8px;
}

.modal-content::-webkit-scrollbar-track {
  background: #1e1e1e;
}

.modal-content::-webkit-scrollbar-thumb {
  background: #666;
  border-radius: 4px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: #888;
}

</style>
