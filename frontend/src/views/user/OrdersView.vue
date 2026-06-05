<script setup lang="ts">
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import type { OrderItem } from '@/types/order'
import {
  cancelOrder,
  confirmOrder,
  confirmPayment,
  createPayment,
  getOrderList,
  returnOrder,
  updateOrderAddress,
} from '@/api/order'
import {
  addAddress,
  getAddresses,
  getDivisions,
  type AddressForm,
  type AddressItem,
  type DivisionItem,
} from '@/api/address'

const router = useRouter()
const orders = ref<OrderItem[]>([])
const addresses = ref<AddressItem[]>([])
const provinces = ref<DivisionItem[]>([])
const cities = ref<DivisionItem[]>([])
const districts = ref<DivisionItem[]>([])
const loading = ref(false)
const addressLoading = ref(false)
const activeTab = ref('all')
const showAddressModal = ref(false)
const addressMode = ref<'pay' | 'edit'>('pay')
const targetOrder = ref<OrderItem | null>(null)
const selectedAddressId = ref<number | null>(null)
const useNewAddress = ref(false)

const addressForm = reactive<AddressForm>({
  receiver_name: '',
  receiver_phone: '',
  province_code: '',
  city_code: '',
  district_code: '',
  street: '',
  detail: '',
  is_default: false,
})

const tabs = [
  { key: 'all', label: '全部' },
  { key: 'pending_payment', label: '待付款' },
  { key: 'paid', label: '已支付' },
  { key: 'receiving', label: '待收货' },
  { key: 'completed', label: '已完成' },
  { key: 'cancelled', label: '已取消' },
]

const statusMap: Record<string, string> = {
  created: '已创建',
  pending_payment: '待付款',
  paid: '已支付',
  receiving: '待收货',
  completed: '已完成',
  cancelled: '已取消',
  closed: '已关闭',
  refunded: '已退货',
}

const statusClassMap: Record<string, string> = {
  created: 'status-pending',
  pending_payment: 'status-pending',
  paid: 'status-paid',
  receiving: 'status-receiving',
  completed: 'status-completed',
  cancelled: 'status-cancelled',
  closed: 'status-cancelled',
  refunded: 'status-cancelled',
}

const selectedAddress = computed(() => addresses.value.find(item => item.id === selectedAddressId.value) || null)

async function loadOrders() {
  loading.value = true
  try {
    const params: Record<string, any> = { page: 1, page_size: 50 }
    if (activeTab.value === 'paid') {
      params.status = 'paid,receiving'
    } else if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }
    const res = await getOrderList(params)
    if (res.code === 200) {
      orders.value = res.data.results
    }
  } catch (e) {
    console.error('加载订单失败', e)
  } finally {
    loading.value = false
  }
}

async function loadAddresses() {
  const res = await getAddresses()
  if (res.code === 200) {
    addresses.value = res.data
    selectedAddressId.value = res.data.find(item => item.is_default)?.id || res.data[0]?.id || null
  }
}

async function loadProvinces() {
  const res = await getDivisions()
  if (res.code === 200) provinces.value = res.data
}

async function loadCities() {
  addressForm.city_code = ''
  addressForm.district_code = ''
  cities.value = []
  districts.value = []
  if (!addressForm.province_code) return
  const res = await getDivisions(addressForm.province_code)
  if (res.code === 200) cities.value = res.data
}

async function loadDistricts() {
  addressForm.district_code = ''
  districts.value = []
  if (!addressForm.city_code) return
  const res = await getDivisions(addressForm.city_code)
  if (res.code === 200) districts.value = res.data
}

function resetAddressForm() {
  addressForm.receiver_name = ''
  addressForm.receiver_phone = ''
  addressForm.province_code = ''
  addressForm.city_code = ''
  addressForm.district_code = ''
  addressForm.street = ''
  addressForm.detail = ''
  addressForm.is_default = false
  cities.value = []
  districts.value = []
}

async function openAddressModal(order: OrderItem, mode: 'pay' | 'edit') {
  targetOrder.value = order
  addressMode.value = mode
  useNewAddress.value = addresses.value.length === 0
  if (!provinces.value.length) await loadProvinces()
  await loadAddresses()
  if (mode === 'edit' && order.shipping_address_id) {
    selectedAddressId.value = order.shipping_address_id
  }
  resetAddressForm()
  showAddressModal.value = true
}

function closeAddressModal() {
  showAddressModal.value = false
  targetOrder.value = null
  addressLoading.value = false
}

async function ensureAddressId() {
  if (!useNewAddress.value) {
    if (!selectedAddressId.value) {
      ElMessage.warning('请选择收货地址')
      return null
    }
    return selectedAddressId.value
  }

  const res = await addAddress(addressForm)
  if (res.code !== 200) {
    ElMessage.error(res.message || '创建地址失败')
    return null
  }
  await loadAddresses()
  selectedAddressId.value = res.data.id
  return res.data.id
}

async function submitAddressModal() {
  if (!targetOrder.value) return
  addressLoading.value = true
  try {
    const addressId = await ensureAddressId()
    if (!addressId) return

    if (addressMode.value === 'pay') {
      await payWithAddress(targetOrder.value, addressId)
    } else {
      const res = await updateOrderAddress(targetOrder.value.order_id, addressId)
      if (res.code === 200) {
        ElMessage.success('收货地址已修改')
        closeAddressModal()
        loadOrders()
      }
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '操作失败')
  } finally {
    addressLoading.value = false
  }
}

async function payWithAddress(order: OrderItem, addressId: number) {
  const res = await createPayment(order.order_id)
  if (res.code !== 200) {
    ElMessage.error(res.message || '创建支付失败')
    return
  }
  const payRes = await confirmPayment(order.order_id, res.data.payment_id, addressId)
  if (payRes.code === 200) {
    ElMessage.success('支付成功，订单已进入待收货')
    closeAddressModal()
    loadOrders()
  }
}

async function handleConfirm(order: OrderItem) {
  try {
    await ElMessageBox.confirm('确认已经收到商品？确认后订单将进入已完成。', '确认收货', {
      confirmButtonText: '确认收货',
      cancelButtonText: '取消',
      type: 'success',
    })
  } catch {
    return
  }
  try {
    const res = await confirmOrder(order.order_id)
    if (res.code === 200) {
      ElMessage.success('已确认收货')
      loadOrders()
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '确认收货失败')
  }
}

async function handleReturn(order: OrderItem) {
  let reason = ''
  try {
    const result = await ElMessageBox.prompt('退货会扣除 2 分信用分，请填写退货原因。', '申请退货', {
      confirmButtonText: '确认退货',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入退货原因',
      inputValidator: value => !!value?.trim() || '请填写退货原因',
      type: 'warning',
    })
    reason = result.value
  } catch {
    return
  }
  try {
    const res = await returnOrder(order.order_id, reason)
    if (res.code === 200) {
      ElMessage.success('退货成功，已扣除 2 分信用分')
      loadOrders()
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '退货失败')
  }
}

async function handleCancel(order: OrderItem) {
  try {
    await ElMessageBox.confirm('确定取消此订单？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  try {
    const res = await cancelOrder(order.order_id, '用户主动取消')
    if (res.code === 200) {
      ElMessage.success('订单已取消')
      loadOrders()
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '取消失败')
  }
}

function switchTab(tab: string) {
  activeTab.value = tab
  loadOrders()
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

onMounted(() => {
  loadOrders()
  loadAddresses().catch(() => {})
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="hero">
      <div>
        <p class="eyebrow">订单管理</p>
        <h1>我的订单</h1>
        <p>查看和管理您的所有交易订单</p>
      </div>
    </section>

    <section class="order-section">
      <nav class="tabs" aria-label="订单筛选">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          type="button"
          :class="{ active: activeTab === tab.key }"
          @click="switchTab(tab.key)"
        >
          {{ tab.label }}
        </button>
      </nav>

      <div v-if="loading" class="empty-state">
        <strong>加载中...</strong>
      </div>

      <div v-else-if="orders.length === 0" class="empty-state">
        <strong>暂无订单</strong>
        <p>您还没有相关订单记录</p>
      </div>

      <div v-else class="order-list">
        <article v-for="order in orders" :key="order.order_id" class="order-card">
          <div class="order-header">
            <span class="order-id">订单号：{{ order.order_id }}</span>
            <span class="order-date">{{ formatDate(order.created_at) }}</span>
            <span :class="['order-status', statusClassMap[order.status]]">
              {{ statusMap[order.status] }}
            </span>
          </div>
          <div class="order-body">
            <div class="order-info">
              <h3>{{ order.product_name }}</h3>
              <p>数量：{{ order.quantity }}</p>
              <p v-if="order.status === 'receiving'" class="address-line">
                收货地址：{{ order.receiver_name }} {{ order.receiver_phone }}，{{ order.shipping_address_text }}
              </p>
            </div>
            <div class="order-price">
              <strong>¥ {{ Number(order.amount).toFixed(2) }}</strong>
            </div>
          </div>
          <div class="order-footer">
            <button v-if="order.status === 'pending_payment'" class="primary" type="button" @click="openAddressModal(order, 'pay')">去付款</button>
            <button v-if="order.status === 'receiving'" class="primary" type="button" @click="handleConfirm(order)">确认收货</button>
            <button v-if="order.status === 'receiving'" class="secondary" type="button" @click="openAddressModal(order, 'edit')">修改地址</button>
            <button v-if="order.status === 'receiving'" class="danger" type="button" @click="handleReturn(order)">退货</button>
            <button v-if="order.status === 'pending_payment'" class="secondary" type="button" @click="handleCancel(order)">取消订单</button>
            <button class="secondary" type="button" @click="router.push(`/my-orders/${order.order_id}`)">查看详情</button>
          </div>
        </article>
      </div>
    </section>

    <div v-if="showAddressModal" class="modal-overlay" @click.self="closeAddressModal">
      <div class="address-modal">
        <div class="modal-head">
          <h2>{{ addressMode === 'pay' ? '选择收货地址并付款' : '修改收货地址' }}</h2>
          <button class="modal-close" type="button" @click="closeAddressModal">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="addresses.length" class="mode-switch">
            <button type="button" :class="{ active: !useNewAddress }" @click="useNewAddress = false">选择已有地址</button>
            <button type="button" :class="{ active: useNewAddress }" @click="useNewAddress = true">创建新地址</button>
          </div>
          <div v-if="!useNewAddress && addresses.length" class="address-list">
            <label v-for="addr in addresses" :key="addr.id" class="address-option" :class="{ active: selectedAddressId === addr.id }">
              <input v-model="selectedAddressId" type="radio" :value="addr.id">
              <span>
                <strong>{{ addr.receiver_name }} {{ addr.receiver_phone }}</strong>
                <em>{{ addr.province.name }}{{ addr.city.name }}{{ addr.district.name }}{{ addr.street }}{{ addr.detail }}</em>
              </span>
            </label>
          </div>
          <form v-else class="address-form" @submit.prevent>
            <div class="form-row">
              <label><span>收货人 *</span><input v-model="addressForm.receiver_name" type="text" required></label>
              <label><span>手机号 *</span><input v-model="addressForm.receiver_phone" type="tel" required maxlength="11"></label>
            </div>
            <div class="form-row">
              <label>
                <span>省份 *</span>
                <select v-model="addressForm.province_code" required @change="loadCities">
                  <option value="">请选择省份</option>
                  <option v-for="item in provinces" :key="item.code" :value="item.code">{{ item.name }}</option>
                </select>
              </label>
              <label>
                <span>城市 *</span>
                <select v-model="addressForm.city_code" required @change="loadDistricts">
                  <option value="">请选择城市</option>
                  <option v-for="item in cities" :key="item.code" :value="item.code">{{ item.name }}</option>
                </select>
              </label>
            </div>
            <div class="form-row">
              <label>
                <span>区县 *</span>
                <select v-model="addressForm.district_code" required>
                  <option value="">请选择区县</option>
                  <option v-for="item in districts" :key="item.code" :value="item.code">{{ item.name }}</option>
                </select>
              </label>
              <label><span>街道 *</span><input v-model="addressForm.street" type="text" required></label>
            </div>
            <label><span>详细地址 *</span><input v-model="addressForm.detail" type="text" required></label>
            <label class="checkbox-line"><input v-model="addressForm.is_default" type="checkbox"> 设为默认地址</label>
          </form>
          <p v-if="selectedAddress && !useNewAddress" class="selected-tip">
            将使用：{{ selectedAddress.receiver_name }}，{{ selectedAddress.province.name }}{{ selectedAddress.city.name }}{{ selectedAddress.district.name }}{{ selectedAddress.street }}{{ selectedAddress.detail }}
          </p>
        </div>
        <div class="modal-actions">
          <button type="button" class="secondary" @click="closeAddressModal">取消</button>
          <button type="button" class="primary" :disabled="addressLoading" @click="submitAddressModal">
            {{ addressLoading ? '处理中...' : addressMode === 'pay' ? '确认付款' : '保存地址' }}
          </button>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.page { width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.hero {
  display: grid; gap: 28px; align-items: center; padding: 36px; border-radius: 10px; color: #fff;
  background: linear-gradient(rgba(10, 74, 90, 0.88), rgba(10, 74, 90, 0.92)),
    url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80") center/cover;
  box-shadow: var(--shadow);
}
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 42px; line-height: 1.16; }
.hero p:last-child { max-width: 660px; margin-top: 14px; color: rgba(255, 255, 255, 0.84); line-height: 1.8; }
.order-section { margin-top: 20px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 24px; }
.tabs { display: flex; gap: 8px; padding: 6px; border: 1px solid var(--line); border-radius: 8px; background: #f4f8fa; margin-bottom: 20px; }
.tabs button { min-height: 42px; flex: 1; border: 0; border-radius: 6px; color: var(--muted); background: transparent; font-weight: 700; cursor: pointer; font: inherit; }
.tabs button.active { color: #fff; background: var(--accent); box-shadow: 0 10px 24px rgba(15, 93, 114, 0.2); }
.empty-state { min-height: 200px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); }
.empty-state strong { display: block; margin-bottom: 8px; color: var(--ink); font-size: 18px; }
.order-list { display: grid; gap: 16px; }
.order-card { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
.order-header { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 12px 16px; background: var(--soft); border-bottom: 1px solid var(--line); }
.order-id, .order-date { font-size: 13px; color: var(--muted); }
.order-status { padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status-pending { background: #fef3c7; color: #b45309; }
.status-paid { background: #dbeafe; color: #1d4ed8; }
.status-receiving { background: #f1ebff; color: #6d4bc2; }
.status-completed { background: #dcfce7; color: #15803d; }
.status-cancelled { background: #f3f4f6; color: #6b7280; }
.order-body { display: flex; align-items: center; gap: 16px; padding: 16px; }
.order-info { flex: 1; }
.order-info h3 { font-size: 16px; margin-bottom: 8px; }
.order-info p { color: var(--muted); font-size: 14px; }
.address-line { margin-top: 6px; line-height: 1.6; }
.order-price strong { font-size: 20px; color: var(--accent); font-weight: 800; }
.order-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 12px 16px; border-top: 1px solid var(--line); flex-wrap: wrap; }
.primary, .secondary, .danger { min-height: 38px; padding: 0 16px; border-radius: 8px; font-weight: 700; cursor: pointer; font: inherit; }
.primary { border: 0; color: #fff; background: var(--accent); }
.primary:hover { background: var(--accent-dark); }
.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.secondary { color: var(--muted); background: var(--soft); border: 1px solid var(--line); }
.secondary:hover { background: #edf6f8; }
.danger { border: 0; color: #fff; background: #be123c; }
.danger:hover { background: #9f1239; }
.modal-overlay { position: fixed; inset: 0; z-index: 1000; display: grid; place-items: center; padding: 20px; background: rgba(0,0,0,0.45); }
.address-modal { width: min(720px, 100%); max-height: 90vh; overflow-y: auto; border-radius: 12px; background: var(--panel); box-shadow: 0 24px 70px rgba(0,0,0,0.24); }
.modal-head { display: flex; align-items: center; justify-content: space-between; padding: 22px 24px; border-bottom: 1px solid var(--line); }
.modal-head h2 { font-size: 22px; }
.modal-close { width: 38px; height: 38px; border: 0; border-radius: 8px; background: var(--soft); color: var(--muted); font-size: 24px; cursor: pointer; }
.modal-body { display: grid; gap: 16px; padding: 24px; }
.mode-switch { display: flex; gap: 8px; padding: 6px; border-radius: 8px; background: var(--soft); }
.mode-switch button { flex: 1; min-height: 38px; border: 0; border-radius: 6px; background: transparent; cursor: pointer; font: inherit; font-weight: 700; color: var(--muted); }
.mode-switch button.active { color: #fff; background: var(--accent); }
.address-list { display: grid; gap: 10px; }
.address-option { display: flex; gap: 10px; align-items: flex-start; padding: 14px; border: 1px solid var(--line); border-radius: 8px; cursor: pointer; }
.address-option.active { border-color: var(--accent); background: #eef8fa; }
.address-option span { display: grid; gap: 6px; }
.address-option em { color: var(--muted); font-style: normal; line-height: 1.5; }
.address-form { display: grid; gap: 14px; }
.form-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.address-form label { display: grid; gap: 8px; color: var(--muted); font-size: 14px; font-weight: 700; }
.address-form input, .address-form select { width: 100%; height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; font: inherit; box-sizing: border-box; background: #fff; }
.checkbox-line { display: flex !important; align-items: center; gap: 8px !important; }
.checkbox-line input { width: auto; height: auto; }
.selected-tip { padding: 12px 14px; border-radius: 8px; color: var(--accent); background: #eef8fa; line-height: 1.6; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; padding: 18px 24px; border-top: 1px solid var(--line); }
@media (max-width: 620px) {
  .page { width: min(100% - 20px, 1180px); }
  .hero, .order-section { padding: 20px; }
  h1 { font-size: 30px; }
  .tabs { flex-wrap: wrap; }
  .tabs button { flex: none; min-width: calc(50% - 4px); }
  .order-body, .order-footer, .order-header { flex-wrap: wrap; }
  .primary, .secondary, .danger { flex: 1; min-width: 120px; }
  .form-row { grid-template-columns: 1fr; }
}
</style>
