<template>
  <div class="min-h-screen pb-12 bg-[#F5F5F7]">
    <!-- 磨砂玻璃导航栏 -->
    <nav class="glass-navbar">
      <div class="nav-content">
        <button @click="goBack" class="back-btn">
          <i class="ri-arrow-left-s-line"></i>
        </button>
        <div class="nav-title">
          <span class="title">订单详情</span>
          <span class="order-number" v-if="order">#{{ order.order_number?.slice(-6) }}</span>
        </div>
        <div class="placeholder"></div>
      </div>
    </nav>

    <!-- 主要内容 -->
    <main class="main-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner-ios">
          <div class="spinner-blade" v-for="n in 12" :key="n"></div>
        </div>
        <p class="loading-text">正在加载订单数据</p>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!order" class="empty-state">
        <i class="ri-file-list-3-line"></i>
        <p>订单不存在或已被删除</p>
        <button @click="goBack" class="empty-btn">返回订单列表</button>
      </div>

      <!-- 订单内容 -->
      <div v-else class="order-content">
        <!-- 左侧:主要内容 -->
        <div class="content-left">
          <!-- A. 状态进度条 -->
          <div class="status-card">
            <!-- 正常流程进度条 -->
            <div v-if="order.status !== 'cancelled'" class="progress-container">
              <!-- Step 1: 待处理 -->
              <div class="progress-step">
                <div class="step-circle" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
                  <i v-if="currentStep > 1" class="ri-check-line"></i>
                  <i v-else class="ri-file-list-3-line"></i>
                </div>
                <span class="step-label" :class="{ active: currentStep >= 1 }">待处理</span>
              </div>

              <!-- Step 2: 已发货 -->
              <div class="progress-step">
                <div class="step-circle" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
                  <i v-if="currentStep > 2" class="ri-check-line"></i>
                  <i v-else class="ri-truck-line"></i>
                </div>
                <span class="step-label" :class="{ active: currentStep >= 2 }">已发货</span>
              </div>

              <!-- Step 3: 已完成 -->
              <div class="progress-step">
                <div class="step-circle" :class="{ active: currentStep >= 3, completed: currentStep >= 3 }">
                  <i v-if="currentStep >= 3" class="ri-check-line"></i>
                  <i v-else class="ri-record-circle-line"></i>
                </div>
                <span class="step-label" :class="{ active: currentStep >= 3 }">已完成</span>
              </div>

              <!-- 进度线 -->
              <div class="progress-line"></div>
              <div class="progress-active" :style="{ width: progressWidth }"></div>
            </div>

            <!-- 已取消状态 -->
            <div v-else class="cancelled-container">
              <div class="cancelled-icon">
                <i class="ri-close-circle-fill"></i>
              </div>
              <div class="cancelled-text">
                <p class="cancelled-title">订单已取消</p>
                <p class="cancelled-desc">此订单已被取消</p>
              </div>
            </div>

            <!-- 当前状态提示 -->
            <div v-if="order.status === 'pending'" class="status-tip">
              <i class="ri-time-fill"></i>
              <div>
                <p class="tip-title">订单等待处理</p>
                <p class="tip-desc">订单已提交,等待处理中。</p>
              </div>
            </div>
            <div v-else-if="order.status === 'shipping'" class="status-tip shipping">
              <i class="ri-truck-line"></i>
              <div>
                <p class="tip-title">商品配送中</p>
                <p class="tip-desc">您的订单正在配送途中,请耐心等待。</p>
              </div>
            </div>
            <div v-else-if="order.status === 'delivered'" class="status-tip success">
              <i class="ri-checkbox-circle-fill"></i>
              <div>
                <p class="tip-title">订单已完成</p>
                <p class="tip-desc">感谢您的购买,期待下次光临。</p>
              </div>
            </div>
          </div>

          <!-- B. 商品列表 -->
          <div class="items-card">
            <div class="card-header">
              <h3>订单商品 ({{ order.items?.length || 0 }})</h3>
            </div>
            <div class="items-list">
              <div v-for="item in order.items" :key="item.book_id" class="item-row">
                <!-- 封面 -->
                <div class="item-cover">
                  <div v-if="!item.book_image" class="cover-placeholder"></div>
                  <img v-else :src="item.book_image" :alt="item.book_title" class="cover-img">
                </div>

                <!-- 信息 -->
                <div class="item-info">
                  <div class="info-top">
                    <h4 class="item-title">{{ item.book_title }}</h4>
                    <p class="item-author">{{ item.book_author }}</p>
                    <p class="item-isbn" v-if="item.book_isbn">ISBN: {{ item.book_isbn }}</p>
                  </div>
                  <div class="info-bottom">
                    <span class="item-quantity">x{{ item.quantity }}</span>
                    <span class="item-price">¥{{ parseFloat(item.unit_price || 0).toFixed(2) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- 右侧:信息汇总 & 操作 -->
        <div class="content-right">
          <!-- 订单信息卡片 -->
          <div class="info-card">
            <div class="info-row">
              <span class="info-label">订单号</span>
              <span class="info-value order-id">{{ order.order_number }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">下单时间</span>
              <span class="info-value time">{{ order.created_at }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">用户</span>
              <div class="user-info">
                <div class="user-avatar">
                  <i class="ri-user-line"></i>
                </div>
                <span class="user-name">{{ order.username || '未知用户' }}</span>
              </div>
            </div>
          </div>

          <!-- 费用明细 -->
          <div class="receipt-card">
            <div class="receipt-teeth"></div>
            <h3>费用明细</h3>

            <div class="fee-list">
              <div class="fee-row">
                <span class="fee-label">商品总额</span>
                <span class="fee-value">¥{{ parseFloat(order.total_amount).toFixed(2) }}</span>
              </div>
              <div class="fee-row">
                <span class="fee-label">运费</span>
                <span class="fee-value">¥0.00</span>
              </div>
              <div class="fee-row discount">
                <span class="fee-label">优惠</span>
                <span class="fee-value">-¥0.00</span>
              </div>
            </div>

            <div class="divider"></div>

            <div class="total-row">
              <span class="total-label">实付款</span>
              <span class="total-amount">¥{{ parseFloat(order.total_amount).toFixed(2) }}</span>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <button
                v-if="order.status === 'pending' || order.status === 'processing'"
                @click="handleCancelOrder"
                class="cancel-btn">
                取消订单
              </button>
              <button
                v-if="order.status === 'shipping'"
                @click="handleConfirmReceipt"
                class="pay-btn">
                确认收货
              </button>
              <button
                v-if="order.status === 'cancelled' || order.status === 'delivered'"
                @click="handleDeleteOrder"
                class="cancel-btn">
                删除订单
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrderDetail, cancelOrder as cancelOrderApi, updateOrderStatus, deleteOrder as deleteOrderApi, type Order } from '../api/orderApi'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const order = ref<Order | null>(null)
const currentStep = ref(1)

// 计算进度条宽度
const progressWidth = computed(() => {
  if (!order.value) return '0%'

  const statusMap: Record<string, number> = {
    'pending': 0,
    'processing': 50,
    'shipping': 50,
    'delivered': 100
  }

  return `${statusMap[order.value.status || 'pending'] || 0}%`
})

// 加载订单详情
const loadOrderDetail = async () => {
  const orderId = route.params.id as string

  try {
    const response = await getOrderDetail(Number(orderId))

    if (response) {
      order.value = response

      // 设置进度步骤
      if (response.status === 'pending' || response.status === 'processing') {
        currentStep.value = 1
      } else if (response.status === 'shipping') {
        currentStep.value = 2
      } else if (response.status === 'delivered') {
        currentStep.value = 3
      }
    } else {
      ElMessage.error('订单不存在')
    }

    loading.value = false
  } catch (error) {
    console.error('加载订单详情失败:', error)
    ElMessage.error('加载订单详情失败')
    loading.value = false
  }
}

const goBack = () => {
  router.push('/profile')
}

// 取消订单
const handleCancelOrder = async () => {
  if (!order.value) return

  try {
    await ElMessageBox.confirm(
      '确认取消此订单?取消后将恢复库存,订单状态将变为已取消。',
      '取消订单',
      {
        confirmButtonText: '确认取消',
        cancelButtonText: '我再想想',
        type: 'warning'
      }
    )

    await cancelOrderApi(order.value.id)
    ElMessage.success('订单已取消')
    router.push('/profile')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('取消订单失败')
    }
  }
}

// 确认收货
const handleConfirmReceipt = async () => {
  if (!order.value) return

  try {
    await ElMessageBox.confirm(
      '确认已收到商品?',
      '确认收货',
      {
        confirmButtonText: '确认收货',
        cancelButtonText: '取消',
        type: 'success'
      }
    )

    await updateOrderStatus(order.value.id, 'delivered')
    ElMessage.success('收货确认成功')
    await loadOrderDetail()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('确认收货失败')
    }
  }
}

// 删除订单
const handleDeleteOrder = async () => {
  if (!order.value) return

  try {
    await ElMessageBox.confirm(
      '确认删除此订单?删除后将无法恢复。',
      '删除订单',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteOrderApi(order.value.id)
    ElMessage.success('订单已删除')
    router.push('/profile')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除订单失败')
    }
  }
}

onMounted(() => {
  loadOrderDetail()
})
</script>

<style scoped>
/* 引入 Remix Icon */
@import url('https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css');

/* ========== 全局样式 ========== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* ========== 导航栏 ========== */
.glass-navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  height: 56px;
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 1.5rem;
}

.back-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.3s;
  font-size: 20px;
  color: #1D1D1F;
  background: none;
  border: none;
}

.back-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.back-btn i {
  font-size: 20px;
}

.nav-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-title .title {
  font-weight: 700;
  font-size: 14px;
  color: #1D1D1F;
}

.nav-title .order-number {
  font-size: 13px;
  font-weight: 500;
  color: #86868B;
}

.placeholder {
  width: 80px;
}

/* ========== iOS 加载动画 ========== */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 100px 20px;
}

.loading-spinner-ios {
  position: relative;
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
}

.spinner-blade {
  position: absolute;
  left: 50%;
  top: 0;
  width: 3px;
  height: 12px;
  margin-left: -1.5px;
  background: #8E8E93;
  border-radius: 3px;
  transform-origin: 50% 20px;
  opacity: 0.25;
}

.spinner-blade:nth-child(1) { transform: rotate(0deg); animation: ios-spinner-fade 1s linear infinite 0s; }
.spinner-blade:nth-child(2) { transform: rotate(30deg); animation: ios-spinner-fade 1s linear infinite 0.083s; }
.spinner-blade:nth-child(3) { transform: rotate(60deg); animation: ios-spinner-fade 1s linear infinite 0.166s; }
.spinner-blade:nth-child(4) { transform: rotate(90deg); animation: ios-spinner-fade 1s linear infinite 0.249s; }
.spinner-blade:nth-child(5) { transform: rotate(120deg); animation: ios-spinner-fade 1s linear infinite 0.332s; }
.spinner-blade:nth-child(6) { transform: rotate(150deg); animation: ios-spinner-fade 1s linear infinite 0.415s; }
.spinner-blade:nth-child(7) { transform: rotate(180deg); animation: ios-spinner-fade 1s linear infinite 0.498s; }
.spinner-blade:nth-child(8) { transform: rotate(210deg); animation: ios-spinner-fade 1s linear infinite 0.581s; }
.spinner-blade:nth-child(9) { transform: rotate(240deg); animation: ios-spinner-fade 1s linear infinite 0.664s; }
.spinner-blade:nth-child(10) { transform: rotate(270deg); animation: ios-spinner-fade 1s linear infinite 0.747s; }
.spinner-blade:nth-child(11) { transform: rotate(300deg); animation: ios-spinner-fade 1s linear infinite 0.830s; }
.spinner-blade:nth-child(12) { transform: rotate(330deg); animation: ios-spinner-fade 1s linear infinite 0.913s; }

@keyframes ios-spinner-fade {
  0% { opacity: 1; }
  100% { opacity: 0.25; }
}

.loading-text {
  font-size: 17px;
  font-weight: 400;
  color: #86868B;
  margin: 0;
}

/* ========== 空状态 ========== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 100px 20px;
  color: #86868B;
}

.empty-state i {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 18px;
  margin-bottom: 20px;
}

.empty-btn {
  background: #000;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.empty-btn:hover {
  background: #2c2c2e;
  transform: translateY(-1px);
}

/* ========== 主要内容 ========== */
.main-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.order-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  align-items: start;
}

@media (min-width: 1024px) {
  .order-content {
    grid-template-columns: 1fr 360px;
  }

  .content-right {
    position: sticky;
    top: 80px;
  }
}

.content-left,
.content-right {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ========== 状态进度卡片 ========== */
.status-card {
  background: white;
  border-radius: 24px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  position: relative;
  overflow: hidden;
}

.progress-container {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  z-index: 10;
}

.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  background: #F5F5F7;
  color: #86868B;
  transition: all 0.5s;
}

.step-circle.active {
  background: #007AFF;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
}

.step-circle.completed {
  background: #34C759;
  color: white;
  box-shadow: 0 4px 12px rgba(52, 199, 89, 0.3);
}

.step-label {
  font-size: 12px;
  font-weight: 500;
  color: #86868B;
  transition: color 0.3s;
}

.step-label.active {
  color: #1D1D1F;
}

.progress-line {
  position: absolute;
  top: 16px;
  left: 0;
  right: 0;
  height: 2px;
  background: #F5F5F7;
  z-index: 0;
  margin: 0 16px;
}

.progress-active {
  position: absolute;
  top: 16px;
  left: 16px;
  height: 2px;
  background: #007AFF;
  z-index: 1;
  transition: width 1s ease-out;
  max-width: calc(100% - 32px);
}

.status-tip {
  display: flex;
  align-items: start;
  gap: 0.75rem;
  padding: 1rem;
  background: #FFF5E6;
  border-radius: 12px;
  border: 1px solid #FFE8CC;
}

.status-tip i {
  color: #FF9500;
  font-size: 20px;
  margin-top: 2px;
}

.status-tip.shipping {
  background: #E6F3FF;
  border-color: #CCE5FF;
}

.status-tip.shipping i {
  color: #007AFF;
}

.status-tip.success {
  background: #E6F9ED;
  border-color: #CCF2DD;
}

.status-tip.success i {
  color: #34C759;
}

.tip-title {
  font-size: 14px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0 0 4px 0;
}

.tip-desc {
  font-size: 12px;
  color: #86868B;
  margin: 0;
}

/* ========== 已取消状态 ========== */
.cancelled-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  background: linear-gradient(135deg, #FFE5E5 0%, #FFF0F0 100%);
  border-radius: 16px;
  border: 2px solid #FFD1D1;
}

.cancelled-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(255, 59, 48, 0.2);
}

.cancelled-icon i {
  font-size: 36px;
  color: #FF3B30;
}

.cancelled-text {
  flex: 1;
}

.cancelled-title {
  font-size: 18px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0 0 4px 0;
}

.cancelled-desc {
  font-size: 14px;
  color: #86868B;
  margin: 0;
}

/* ========== 商品列表卡片 ========== */
.items-card {
  background: white;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.card-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #F5F5F7;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0;
}

.items-list {
  display: flex;
  flex-direction: column;
}

.item-row {
  display: flex;
  gap: 1.25rem;
  padding: 1.5rem;
  border-bottom: 1px solid #F5F5F7;
  transition: background 0.3s;
}

.item-row:last-child {
  border-bottom: none;
}

.item-row:hover {
  background: rgba(0, 0, 0, 0.02);
}

.item-cover {
  width: 80px;
  height: 112px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: #F5F5F7;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border: 1px solid #E5E5E7;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #E5E5E7 0%, #F5F5F7 100%);
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.info-top {
  flex: 1;
}

.item-title {
  font-size: 16px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 0 0 4px 0;
}

.item-author {
  font-size: 14px;
  color: #86868B;
  margin: 0;
}

.item-isbn {
  font-size: 12px;
  font-family: 'SF Mono', monospace;
  color: #C7C7CC;
  margin: 4px 0 0 0;
}

.info-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.item-quantity {
  font-size: 14px;
  font-weight: 500;
  background: #F5F5F7;
  padding: 4px 8px;
  border-radius: 6px;
  color: #86868B;
}

.item-price {
  font-size: 18px;
  font-weight: 700;
  color: #1D1D1F;
}

/* ========== 订单信息卡片 ========== */
.info-card {
  background: white;
  border-radius: 24px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.info-label {
  color: #86868B;
}

.info-value {
  color: #1D1D1F;
  font-weight: 500;
}

.info-value.order-id {
  font-size: 13px;
  font-weight: 600;
  color: #1D1D1F;
  user-select: all;
  letter-spacing: 0.02em;
}

.info-value.time {
  font-size: 13px;
  font-weight: 500;
  color: #1D1D1F;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #F5F5F7;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #86868B;
}

.user-name {
  font-weight: 700;
  color: #1D1D1F;
}

/* ========== 费用明细卡片 ========== */
.receipt-card {
  background: white;
  border-radius: 24px;
  padding: 1.5rem;
  box-shadow: 0 10px 30px -10px rgba(0,0,0,0.08);
  border: 1px solid #F5F5F7;
  position: relative;
  overflow: hidden;
}

.receipt-teeth {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(45deg,transparent 33.333%,#F5F5F7 33.333%,#F5F5F7 66.667%,transparent 66.667%),linear-gradient(-45deg,transparent 33.333%,#F5F5F7 33.333%,#F5F5F7 66.667%,transparent 66.667%);
  background-size: 12px 20px;
}

.receipt-card h3 {
  font-size: 16px;
  font-weight: 700;
  color: #1D1D1F;
  margin: 8px 0 1.5rem 0;
}

.fee-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.fee-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.fee-label {
  color: #86868B;
}

.fee-value {
  font-weight: 500;
  color: #1D1D1F;
}

.fee-row.discount .fee-value {
  color: #FF9500;
}

.divider {
  height: 1px;
  background: linear-gradient(to right, transparent, #E5E5E7, transparent);
  margin: 1rem 0;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: end;
  margin-bottom: 1.5rem;
}

.total-label {
  font-size: 16px;
  font-weight: 700;
  color: #1D1D1F;
}

.total-amount {
  font-size: 32px;
  font-weight: 700;
  color: #FF3B30;
  letter-spacing: -0.02em;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
}

.cancel-btn,
.pay-btn {
  flex: 1;
  padding: 14px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn {
  background: white;
  border: 1px solid #E5E5E7;
  color: #86868B;
}

.cancel-btn:hover {
  background: #F5F5F7;
  color: #FF3B30;
}

.pay-btn {
  flex: 2;
  background: #000;
  color: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.pay-btn:hover {
  background: #2c2c2e;
}

/* ========== 响应式设计 ========== */
@media (max-width: 768px) {
  .main-container {
    padding: 1rem;
  }

  .status-card {
    padding: 1.5rem 1rem;
  }

  .progress-container {
    margin-bottom: 1.5rem;
  }

  .step-circle {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }

  .progress-line,
  .progress-active {
    top: 14px;
  }

  .item-cover {
    width: 60px;
    height: 84px;
  }

  .item-title {
    font-size: 14px;
  }

  .total-amount {
    font-size: 28px;
  }
}
</style>
