<template>
  <PageContainer :hideNavbar="true">
    <div id="app" class="min-h-screen pb-32 lg:pb-12">
      <!-- 动态背景光球 -->
      <div class="mesh-gradients">
        <div class="gradient-blob blob-1"></div>
        <div class="gradient-blob blob-2"></div>
        <div class="gradient-blob blob-3"></div>
      </div>

      <!-- 顶部导航 - Cart风格 -->
      <nav class="glass-nav">
        <div class="nav-container">
          <div class="nav-left">
            <a @click="goBack" class="back-button">
              <i class="ri-arrow-left-s-line"></i>
            </a>
            <h1 class="nav-title">确认订单 <span class="item-count">({{ orderItems.length }})</span></h1>
          </div>
        </div>
      </nav>

      <main class="max-w-6xl mx-auto px-4 md:px-6 pt-8 grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-8 items-start">
        <!-- 左侧：主要信息流 -->
        <div class="space-y-6">
          <!-- 收货地址 -->
          <section>
            <div class="flex items-center justify-between mb-3 px-2">
              <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider">收货信息</h3>
              <button @click="showAddressDialog()" class="text-ios-blue text-sm font-medium hover:opacity-70 transition">
                + 新增地址
              </button>
            </div>

            <div v-if="loadingAddresses" class="bg-white rounded-[24px] p-12 shadow-soft text-center">
              <i class="ri-loader-4-line text-2xl animate-spin text-gray-400"></i>
              <p class="mt-2 text-gray-500">加载地址中...</p>
            </div>

            <div v-else-if="addresses.length === 0" class="bg-white rounded-[24px] p-12 shadow-soft text-center">
              <i class="ri-map-pin-line text-4xl text-gray-300 mb-3"></i>
              <p class="text-gray-500 mb-4">暂无收货地址，请先添加地址</p>
              <button @click="showAddressDialog()" class="bg-ios-blue text-white px-6 py-2 rounded-xl hover:opacity-90 transition">
                添加地址
              </button>
            </div>

            <div v-else class="space-y-3">
              <div
                v-for="address in addresses"
                :key="address.id"
                @click="selectAddress(address.id)"
                class="bg-white rounded-[24px] p-5 shadow-soft hover:shadow-float transition cursor-pointer group border-2"
                :class="selectedAddressId === address.id ? 'border-ios-blue bg-blue-50/50' : 'border-transparent hover:border-ios-blue/20'"
              >
                <div class="flex items-center gap-4">
                  <div class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 group-hover:bg-blue-50 group-hover:text-ios-blue transition">
                    <i class="ri-map-pin-2-fill text-xl"></i>
                  </div>
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                      <span class="font-bold text-gray-900">{{ address.receiver_name }}</span>
                      <span v-if="address.is_default" class="bg-gray-100 text-gray-500 text-[10px] px-2 py-0.5 rounded font-bold">默认</span>
                    </div>
                    <p class="text-gray-900 font-medium text-base leading-tight">
                      {{ address.province }} {{ address.city }} {{ address.district }} {{ address.detail_address }}
                    </p>
                    <p class="text-gray-500 text-sm mt-1">{{ address.receiver_phone }}</p>
                  </div>
                  <div class="flex items-center gap-3">
                    <button @click.stop="editAddress(address)" class="text-ios-blue text-sm hover:opacity-70 transition">
                      编辑
                    </button>
                    <div class="radio-circle" :class="{'radio-selected': selectedAddressId === address.id}"></div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- 商品清单 -->
          <section>
            <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3 px-2">商品清单 ({{ orderItems.length }})</h3>

            <div v-if="orderItems.length === 0" class="bg-white rounded-[24px] p-12 shadow-soft text-center">
              <i class="ri-shopping-cart-line text-4xl text-gray-300 mb-3"></i>
              <p class="text-gray-500">购物车为空</p>
            </div>

            <div v-else class="bg-white rounded-[24px] p-5 shadow-soft divide-y divide-gray-100">
              <div v-for="item in orderItems" :key="item.book_id" class="flex gap-4 py-4 first:pt-0 last:pb-0">
                <div class="w-16 h-20 bg-gray-100 rounded-lg overflow-hidden border border-gray-100 flex-shrink-0">
                  <img v-if="item.cover" :src="item.cover" class="w-full h-full object-cover" alt="">
                  <div v-else class="w-full h-full flex items-center justify-center">
                    <i class="ri-book-line text-2xl text-gray-300"></i>
                  </div>
                </div>
                <div class="flex-1 min-w-0 flex flex-col justify-between py-0.5">
                  <div>
                    <h4 class="font-bold text-gray-900 line-clamp-1">{{ item.title }}</h4>
                    <p class="text-xs text-gray-500 mt-0.5">{{ item.author }}</p>
                  </div>
                  <div class="flex justify-between items-end">
                    <span class="text-sm font-medium">¥{{ item.price.toFixed(2) }}</span>
                    <div class="flex items-center gap-2">
                      <button @click="decreaseQuantity(item)" :disabled="item.quantity <= 1" class="w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-30 flex items-center justify-center transition">
                        <i class="ri-subtract-line text-sm"></i>
                      </button>
                      <span class="text-xs text-gray-600 min-w-[20px] text-center">x{{ item.quantity }}</span>
                      <button @click="increaseQuantity(item)" class="w-6 h-6 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition">
                        <i class="ri-add-line text-sm"></i>
                      </button>
                      <button @click="removeItem(item)" class="ml-2 text-red-500 hover:opacity-70 transition">
                        <i class="ri-delete-bin-line text-base"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- 配送方式 -->
          <section>
            <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3 px-2">配送方式</h3>
            <div class="bg-white rounded-[24px] overflow-hidden shadow-soft">
              <div
                v-for="method in deliveryMethods"
                :key="method.id"
                @click="selectedDelivery = method.id"
                class="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition border-b border-gray-100 last:border-0"
              >
                <div class="flex items-center gap-3">
                  <i :class="method.icon" class="text-xl text-gray-400"></i>
                  <div>
                    <p class="font-bold text-sm text-gray-900">{{ method.name }}</p>
                    <p class="text-xs text-gray-500">{{ method.desc }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-3">
                  <span class="text-sm font-medium" :class="method.price === 0 ? 'text-ios-green' : 'text-gray-900'">
                    {{ method.price === 0 ? '免费' : '¥' + method.price.toFixed(2) }}
                  </span>
                  <div class="radio-circle" :class="{'radio-selected': selectedDelivery === method.id}"></div>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- 右侧：支付与结算 -->
        <div class="space-y-6">
          <!-- 支付方式 -->
          <div class="bg-white rounded-[24px] p-5 shadow-soft">
            <h3 class="text-lg font-bold mb-4">支付方式</h3>
            <div class="space-y-3">
              <div
                v-for="pay in paymentMethods"
                :key="pay.id"
                @click="selectedPayment = pay.id"
                :class="selectedPayment === pay.id ? 'border-ios-blue bg-blue-50/50' : 'border-gray-100 hover:border-gray-200'"
                class="flex items-center justify-between p-3 rounded-xl border-2 cursor-pointer transition-all"
              >
                <div class="flex items-center gap-3">
                  <div :class="pay.bg" class="w-10 h-10 rounded-lg flex items-center justify-center text-white text-xl">
                    <i :class="pay.icon"></i>
                  </div>
                  <span class="font-bold text-sm text-gray-900">{{ pay.name }}</span>
                </div>
                <div class="radio-circle" :class="{'radio-selected': selectedPayment === pay.id}"></div>
              </div>
            </div>
          </div>

          <!-- 金额明细 -->
          <div class="bg-white rounded-[24px] p-6 shadow-float border border-gray-100">
            <div class="space-y-3 mb-6">
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">商品小计</span>
                <span class="font-medium">¥{{ subtotalAmount.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-500">运费</span>
                <span class="font-medium" :class="deliveryPrice === 0 ? 'text-ios-green' : ''">
                  {{ deliveryPrice === 0 ? '免费' : '¥' + deliveryPrice.toFixed(2) }}
                </span>
              </div>
            </div>

            <div class="border-t border-dashed border-gray-200 my-4"></div>

            <div class="flex justify-between items-end mb-6">
              <span class="text-gray-900 font-bold">应付总额</span>
              <span class="text-3xl font-bold tracking-tight">¥{{ finalTotal.toFixed(2) }}</span>
            </div>

            <!-- 桌面端支付按钮 -->
            <button
              @click="submitOrder"
              :disabled="!canSubmitOrder"
              class="hidden lg:flex w-full bg-black hover:bg-gray-800 disabled:bg-gray-400 text-white font-bold py-4 rounded-xl shadow-lg shadow-black/20 transition items-center justify-center gap-2 group active:scale-95 duration-200"
            >
              <i class="ri-fingerprint-line text-2xl opacity-50 group-hover:opacity-100 transition-opacity"></i>
              <span>{{ submitting ? '提交中...' : '确认支付' }}</span>
            </button>

            <p class="text-[10px] text-gray-400 text-center mt-3">
              点击支付即表示您同意服务条款
            </p>
          </div>
        </div>
      </main>

      <!-- 移动端底部悬浮支付栏 -->
      <div class="lg:hidden fixed bottom-0 left-0 w-full bg-white/90 backdrop-blur-xl border-t border-gray-200 p-4 pb-8 z-50">
        <div class="flex gap-4">
          <div class="flex-1 flex flex-col justify-center">
            <p class="text-xs text-gray-500">应付总额</p>
            <div class="flex items-baseline gap-1">
              <span class="text-sm font-bold">¥</span>
              <span class="text-2xl font-bold text-gray-900">{{ finalTotal.toFixed(2) }}</span>
            </div>
          </div>
          <button
            @click="submitOrder"
            :disabled="!canSubmitOrder"
            class="flex-[2] bg-black disabled:bg-gray-400 text-white font-bold py-3.5 rounded-xl shadow-lg flex items-center justify-center gap-2 active:scale-95 transition-transform"
          >
            <i class="ri-fingerprint-line text-xl"></i> {{ submitting ? '提交中...' : '确认支付' }}
          </button>
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
  cover?: string
}

const orderItems = ref<OrderItem[]>([])
const submitting = ref(false)

// 配送方式
const selectedDelivery = ref('standard')
const deliveryMethods = [
  { id: 'express', name: '顺丰速运', desc: '预计明天送达', price: 12.00, icon: 'ri-truck-line' },
  { id: 'standard', name: '普通快递', desc: '预计 3-5 天送达', price: 0.00, icon: 'ri-box-3-line' }
]

// 支付方式
const selectedPayment = ref('wechat')
const paymentMethods = [
  { id: 'wechat', name: '微信支付', icon: 'ri-wechat-fill', bg: 'bg-green-500' },
  { id: 'alipay', name: '支付宝', icon: 'ri-alipay-fill', bg: 'bg-blue-500' }
]

// 计算属性
const subtotalAmount = computed(() => {
  return orderItems.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
})

const deliveryPrice = computed(() => {
  const method = deliveryMethods.find(m => m.id === selectedDelivery.value)
  return method ? method.price : 0
})

const finalTotal = computed(() => {
  return subtotalAmount.value + deliveryPrice.value
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
      `确认提交订单？应付金额：¥${finalTotal.value.toFixed(2)}`,
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
/* iOS风格颜色系统 */
.text-ios-blue { color: #007AFF; }
.text-ios-green { color: #34C759; }
.bg-ios-blue { background-color: #007AFF; }
.bg-ios-green { background-color: #34C759; }

/* 玻璃态导航栏 - Cart风格 */
.glass-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  height: 64px;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-button {
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
}

.back-button:hover {
  background: rgba(0, 0, 0, 0.05);
}

.nav-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1D1D1F;
  letter-spacing: -0.02em;
  margin: 0;
}

.item-count {
  color: #86868B;
  font-weight: 400;
  font-size: 1rem;
}

/* 自定义单选框样式 */
.radio-circle {
  width: 20px;
  height: 20px;
  border: 2px solid #D1D1D6;
  border-radius: 50%;
  position: relative;
  transition: all 0.2s;
  flex-shrink: 0;
}

.radio-selected {
  border-color: #007AFF;
  background-color: #007AFF;
}

.radio-selected::after {
  content: '';
  position: absolute;
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 卡片阴影 */
.shadow-soft {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.shadow-float {
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.08);
}

/* 对话框样式 */
:deep(.el-dialog) {
  border-radius: 20px;
}

/* 表单样式 */
:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  border-radius: 12px;
}

:deep(.el-button) {
  border-radius: 12px;
  transition: all 0.2s;
}

:deep(.el-button--primary) {
  background: #007aff;
  border-color: #007aff;
}

:deep(.el-button--primary:hover) {
  background: #0051d5;
  border-color: #0051d5;
}

/* 背景色 */
#app {
  background: #F5F5F7;
  position: relative;
  overflow-x: hidden;
}

/* ========== 动态背景光球 ========== */
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

/* 覆盖PageContainer的样式，让背景延伸到页面两侧 */
:deep(.page-content) {
  max-width: none;
  padding: 0;
  margin: 0;
}
</style>
