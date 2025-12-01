<template>
  <PageContainer>
    <div class="checkout-container">
      <el-card class="checkout-header">
        <h2>确认订单</h2>
      </el-card>

      <!-- 收货地址 -->
      <el-card class="address-section">
        <template #header>
          <div class="section-header">
            <span class="section-title">收货地址</span>
            <el-button type="primary" size="small" @click="showAddressDialog()">
              新增地址
            </el-button>
          </div>
        </template>

        <div v-if="loadingAddresses" class="loading-state">
          <el-icon class="is-loading"><Loading /></el-icon>
          加载地址中...
        </div>

        <div v-else-if="addresses.length === 0" class="empty-addresses">
          <el-empty description="暂无收货地址，请先添加地址">
            <el-button type="primary" @click="showAddressDialog()">添加地址</el-button>
          </el-empty>
        </div>

        <div v-else class="address-list">
          <div
            v-for="address in addresses"
            :key="address.id"
            class="address-item"
            :class="{ selected: selectedAddressId === address.id }"
            @click="selectAddress(address.id)"
          >
            <div class="address-radio">
              <div class="radio-icon" :class="{ checked: selectedAddressId === address.id }">
                <div v-if="selectedAddressId === address.id" class="radio-dot"></div>
              </div>
            </div>
            <div class="address-content">
              <div class="address-header">
                <span class="receiver-name">{{ address.receiver_name }}</span>
                <span class="receiver-phone">{{ address.receiver_phone }}</span>
                <el-tag v-if="address.is_default" type="success" size="small">默认</el-tag>
              </div>
              <div class="address-detail">
                {{ address.province }} {{ address.city }} {{ address.district }} {{ address.detail_address }}
              </div>
            </div>
            <div class="address-actions">
              <el-button link type="primary" @click.stop="editAddress(address)">编辑</el-button>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 订单信息 -->
      <el-card class="order-section">
        <template #header>
          <span class="section-title">订单信息</span>
        </template>

        <div v-if="orderItems.length === 0" class="empty-order">
          <el-empty description="购物车为空" />
        </div>

        <div v-else class="order-items">
          <div v-for="item in orderItems" :key="item.book_id" class="order-item">
            <div class="item-info">
              <div class="item-title">{{ item.title }}</div>
              <div class="item-author">{{ item.author }}</div>
            </div>
            <div class="item-price">
              <span class="unit-price">¥{{ item.price.toFixed(2) }}</span>
            </div>
            <div class="item-quantity">
              <el-button
                size="small"
                @click="decreaseQuantity(item)"
                :disabled="item.quantity <= 1"
                class="quantity-btn"
              >
                <el-icon><Minus /></el-icon>
              </el-button>
              <span class="quantity-display">{{ item.quantity }}</span>
              <el-button
                size="small"
                @click="increaseQuantity(item)"
                class="quantity-btn"
              >
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
            <div class="item-subtotal">¥{{ (item.price * item.quantity).toFixed(2) }}</div>
            <div class="item-remove">
              <el-button
                link
                type="danger"
                @click="removeItem(item)"
                size="small"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 付款详情 -->
      <el-card class="payment-section">
        <template #header>
          <span class="section-title">付款详情</span>
        </template>

        <div class="payment-details">
          <div class="detail-row">
            <span class="detail-label">商品总额：</span>
            <span class="detail-value">¥{{ totalAmount.toFixed(2) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">运费：</span>
            <span class="detail-value shipping-free">免运费</span>
          </div>
          <div class="detail-row total-row">
            <span class="detail-label">应付总额：</span>
            <span class="detail-total">¥{{ totalAmount.toFixed(2) }}</span>
          </div>
        </div>
      </el-card>

      <!-- 底部操作栏 -->
      <div class="checkout-footer">
        <div class="footer-summary">
          <span class="summary-text">共 {{ totalQuantity }} 件商品，总计：</span>
          <span class="summary-amount">¥{{ totalAmount.toFixed(2) }}</span>
        </div>
        <div class="footer-actions">
          <el-button size="large" @click="goBack">返回购物车</el-button>
          <el-button
            type="primary"
            size="large"
            :disabled="!canSubmitOrder"
            :loading="submitting"
            @click="submitOrder"
          >
            提交订单
          </el-button>
        </div>
      </div>

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
          <el-form-item label="设为默认">
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, Minus, Plus, Delete } from '@element-plus/icons-vue'
import PageContainer from './PageContainer.vue'
import { getAddresses, addAddress, updateAddress, type Address } from '../api/addressApi'
import { createOrder } from '../api/orderApi'
import { clearCart } from '../api/cartApi'

const router = useRouter()

// 收货地址相关
const addresses = ref<Address[]>([])
const selectedAddressId = ref<number | null>(null)
const loadingAddresses = ref(false)
const addressDialogVisible = ref(false)
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

// 订单相关
interface OrderItem {
  book_id: number
  title: string
  author: string
  price: number
  quantity: number
}

const orderItems = ref<OrderItem[]>([])
const submitting = ref(false)

// 计算属性
const totalAmount = computed(() => {
  return orderItems.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
})

const totalQuantity = computed(() => {
  return orderItems.value.reduce((sum, item) => sum + item.quantity, 0)
})

const canSubmitOrder = computed(() => {
  return selectedAddressId.value !== null && orderItems.value.length > 0 && !submitting.value
})

// 加载收货地址
const loadAddresses = async () => {
  try {
    loadingAddresses.value = true
    const userId = Number(localStorage.getItem('user_id'))
    const response = await getAddresses(userId)
    addresses.value = response.data.addresses || []

    // 自动选择默认地址
    const defaultAddress = addresses.value.find(addr => addr.is_default)
    if (defaultAddress) {
      selectedAddressId.value = defaultAddress.id || null
    } else if (addresses.value.length > 0) {
      selectedAddressId.value = addresses.value[0].id || null
    }
  } catch (error: any) {
    ElMessage.error('加载收货地址失败')
    console.error('加载收货地址失败:', error)
  } finally {
    loadingAddresses.value = false
  }
}

// 选择地址
const selectAddress = (addressId: number | undefined) => {
  if (addressId) {
    selectedAddressId.value = addressId
  }
}

// 显示地址对话框
const showAddressDialog = (address?: Address) => {
  if (address) {
    Object.assign(currentAddress, address)
  } else {
    // 重置表单
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

// 编辑地址
const editAddress = (address: Address) => {
  showAddressDialog(address)
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

// 加载订单商品
const loadOrderItems = () => {
  // 从 sessionStorage 或 localStorage 获取购物车数据
  const cartData = sessionStorage.getItem('checkoutCart')
  if (cartData) {
    try {
      const cart = JSON.parse(cartData)
      orderItems.value = cart.items || []
    } catch (error) {
      console.error('解析购物车数据失败:', error)
      ElMessage.error('加载订单信息失败')
      router.push('/')
    }
  } else {
    ElMessage.warning('购物车为空，请先添加商品')
    router.push('/')
  }
}

// 返回购物车
const goBack = () => {
  router.go(-1)
}

// 增加数量
const increaseQuantity = (item: OrderItem) => {
  item.quantity++
  updateSessionStorage()
}

// 减少数量
const decreaseQuantity = (item: OrderItem) => {
  if (item.quantity > 1) {
    item.quantity--
    updateSessionStorage()
  }
}

// 移除商品
const removeItem = (item: OrderItem) => {
  const index = orderItems.value.findIndex(i => i.book_id === item.book_id)
  if (index > -1) {
    orderItems.value.splice(index, 1)
    updateSessionStorage()

    if (orderItems.value.length === 0) {
      ElMessage.warning('订单中没有商品了')
      router.push('/')
    }
  }
}

// 更新 sessionStorage
const updateSessionStorage = () => {
  const checkoutData = {
    items: orderItems.value
  }
  sessionStorage.setItem('checkoutCart', JSON.stringify(checkoutData))
}

// 提交订单
const submitOrder = async () => {
  if (!selectedAddressId.value) {
    ElMessage.warning('请选择收货地址')
    return
  }

  if (orderItems.value.length === 0) {
    ElMessage.warning('订单中没有商品')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认提交订单？应付金额：¥${totalAmount.value.toFixed(2)}`,
      '确认订单',
      {
        confirmButtonText: '确认支付',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    submitting.value = true
    const userId = Number(localStorage.getItem('user_id'))

    // 创建订单
    const orderData = {
      user_id: userId,
      items: orderItems.value.map(item => ({
        book_id: item.book_id,
        quantity: item.quantity
      }))
    }

    const result = await createOrder(orderData)

    // 清空购物车
    await clearCart(userId)

    // 清除临时数据
    sessionStorage.removeItem('checkoutCart')

    ElMessage.success('订单提交成功！')

    // 跳转到订单详情页
    router.push(`/order/${result.order_id}`)
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '订单提交失败')
      console.error('订单提交失败:', error)
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadAddresses()
  loadOrderItems()
})
</script>

<style scoped>
.checkout-container {
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 100px;
}

.checkout-header {
  margin-bottom: 20px;
}

.checkout-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

/* 区块标题 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 收货地址部分 */
.address-section {
  margin-bottom: 20px;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: #909399;
}

.empty-addresses {
  padding: 20px 0;
}

.address-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.address-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  border: 2px solid #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.address-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.address-item.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.address-radio {
  display: flex;
  align-items: flex-start;
  padding-top: 2px;
}

.radio-icon {
  width: 18px;
  height: 18px;
  border: 2px solid #dcdfe6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.radio-icon.checked {
  border-color: #409eff;
}

.radio-dot {
  width: 10px;
  height: 10px;
  background: #409eff;
  border-radius: 50%;
}

.address-content {
  flex: 1;
}

.address-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.receiver-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.receiver-phone {
  color: #606266;
}

.address-detail {
  color: #606266;
  line-height: 1.6;
}

.address-actions {
  display: flex;
  align-items: center;
}

/* 订单信息部分 */
.order-section {
  margin-bottom: 20px;
}

.empty-order {
  padding: 20px 0;
}

.order-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.item-author {
  font-size: 14px;
  color: #909399;
}

.item-price {
  display: flex;
  align-items: center;
  min-width: 100px;
  justify-content: flex-end;
}

.unit-price {
  color: #606266;
  font-size: 15px;
}

.item-quantity {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
  justify-content: center;
}

.quantity-btn {
  width: 28px;
  height: 28px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quantity-display {
  min-width: 32px;
  text-align: center;
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

.item-subtotal {
  min-width: 100px;
  text-align: right;
  font-size: 16px;
  font-weight: 600;
  color: #f56c6c;
}

.item-remove {
  display: flex;
  align-items: center;
  min-width: 40px;
  justify-content: center;
}

/* 付款详情部分 */
.payment-section {
  margin-bottom: 20px;
}

.payment-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.detail-label {
  color: #606266;
}

.detail-value {
  color: #303133;
}

.shipping-free {
  color: #67c23a;
}

.total-row {
  border-top: 1px dashed #dcdfe6;
  padding-top: 16px;
  margin-top: 8px;
}

.total-row .detail-label {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.detail-total {
  font-size: 20px;
  font-weight: 600;
  color: #f56c6c;
}

/* 底部操作栏 */
.checkout-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-top: 1px solid #dcdfe6;
  padding: 16px 20px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
  z-index: 100;
}

.checkout-footer > div {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-summary {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.summary-text {
  color: #606266;
  font-size: 14px;
}

.summary-amount {
  font-size: 24px;
  font-weight: 600;
  color: #f56c6c;
}

.footer-actions {
  display: flex;
  gap: 12px;
}

/* 响应式 */
@media (max-width: 768px) {
  .order-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .item-info {
    width: 100%;
  }

  .item-price,
  .item-quantity,
  .item-subtotal {
    width: 100%;
    justify-content: space-between;
  }

  .item-remove {
    width: 100%;
    justify-content: flex-end;
  }

  .checkout-footer > div {
    flex-direction: column;
    gap: 12px;
  }

  .footer-summary,
  .footer-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
