<script setup lang="ts">
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import {
  cancelOrder,
  confirmOrder,
  confirmPayment,
  createPayment,
  getOrderDetail,
  returnOrder,
  updateOrderAddress,
} from '@/api/order'
import { addAddress, getAddresses, getDivisions, type AddressForm, type AddressItem, type DivisionItem } from '@/api/address'
import { useUserStore } from '@/stores/user'
import type { OrderItem } from '@/types/order'

const route = useRoute()
const router = useRouter()
const order = ref<OrderItem | null>(null)
const addresses = ref<AddressItem[]>([])
const provinces = ref<DivisionItem[]>([])
const cities = ref<DivisionItem[]>([])
const districts = ref<DivisionItem[]>([])
const loading = ref(false)
const actionLoading = ref(false)
const forbidden = ref(false)
const showAddressModal = ref(false)
const addressMode = ref<'pay' | 'edit'>('pay')
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

const statusMap: Record<string, { text: string; cls: string }> = {
  created: { text: '已创建', cls: 'status-pending' },
  pending_payment: { text: '待付款', cls: 'status-pending' },
  paid: { text: '已支付', cls: 'status-active' },
  receiving: { text: '待收货', cls: 'status-receiving' },
  completed: { text: '已完成', cls: 'status-done' },
  cancelled: { text: '已取消', cls: 'status-cancelled' },
  closed: { text: '已关闭', cls: 'status-cancelled' },
  pending_return: { text: '退货审核中', cls: 'status-pending' },
  refunded: { text: '已退货', cls: 'status-cancelled' },
}

const selectedAddress = computed(() => addresses.value.find(item => item.id === selectedAddressId.value) || null)

async function loadOrder() {
  loading.value = true
  try {
    const id = route.params.id as string
    const res = await getOrderDetail(id)
    if (res.code === 200) {
      order.value = res.data
    }
  } catch (e: any) {
    const status = e?.response?.status
    if (status === 403) {
      forbidden.value = true
      setTimeout(() => router.replace('/my-orders'), 1500)
      return
    }
    console.error('加载订单详情失败', e)
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
}

async function openAddressModal(mode: 'pay' | 'edit') {
  addressMode.value = mode
  useNewAddress.value = addresses.value.length === 0
  if (!provinces.value.length) await loadProvinces()
  await loadAddresses()
  if (mode === 'edit' && order.value?.shipping_address_id) {
    selectedAddressId.value = order.value.shipping_address_id
  }
  resetAddressForm()
  showAddressModal.value = true
}

function closeAddressModal() {
  showAddressModal.value = false
  actionLoading.value = false
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
  if (!order.value) return
  actionLoading.value = true
  try {
    const addressId = await ensureAddressId()
    if (!addressId) return
    if (addressMode.value === 'pay') {
      const payRes = await createPayment(order.value.order_id)
      if (payRes.code === 200) {
        const confirmRes = await confirmPayment(order.value.order_id, payRes.data.payment_id, addressId)
        if (confirmRes.code === 200) {
          ElMessage.success('支付成功，订单已进入待收货')
          closeAddressModal()
          loadOrder()
        }
      }
    } else {
      const res = await updateOrderAddress(order.value.order_id, addressId)
      if (res.code === 200) {
        ElMessage.success('收货地址已修改')
        closeAddressModal()
        order.value = res.data
      }
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '操作失败')
  } finally {
    actionLoading.value = false
  }
}

async function handleConfirm() {
  if (!order.value) return
  try {
    await ElMessageBox.confirm('确认已经收到商品？确认后订单将进入已完成。', '确认收货', {
      confirmButtonText: '确认收货',
      cancelButtonText: '取消',
      type: 'success',
    })
  } catch {
    return
  }
  actionLoading.value = true
  try {
    const res = await confirmOrder(order.value.order_id)
    if (res.code === 200) {
      ElMessage.success('已确认收货')
      loadOrder()
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '确认收货失败')
  } finally {
    actionLoading.value = false
  }
}

async function handleReturn() {
  if (!order.value) return
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
  actionLoading.value = true
  try {
    const res = await returnOrder(order.value.order_id, reason)
    if (res.code === 200) {
      ElMessage.success('退货申请已提交，等待管理员审核')
      loadOrder()
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '退货失败')
  } finally {
    actionLoading.value = false
  }
}

async function handleCancel() {
  if (!order.value) return
  try {
    await ElMessageBox.confirm('确定取消此订单？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  actionLoading.value = true
  try {
    const res = await cancelOrder(order.value.order_id)
    if (res.code === 200) {
      ElMessage.success('订单已取消')
      loadOrder()
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '取消失败')
  } finally {
    actionLoading.value = false
  }
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  const userStore = useUserStore()
  if (!userStore.isLoggedIn) {
    router.replace('/login')
    return
  }
  loadOrder()
  loadAddresses().catch(() => {})
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">订单管理</p>
        <h1>订单详情</h1>
      </div>
      <button class="secondary" type="button" @click="router.push('/my-orders')">返回订单列表</button>
    </section>

    <div v-if="loading" class="empty-state"><strong>加载中...</strong></div>
    <div v-else-if="forbidden" class="empty-state"><strong>无权查看此订单</strong><p>即将返回订单列表...</p></div>
    <div v-else-if="!order" class="empty-state"><strong>订单不存在</strong></div>
    <section v-else class="detail-layout">
      <article class="detail-main">
        <div class="detail-header">
          <div>
            <p class="code">订单 {{ order.order_id }}</p>
            <h2>{{ order.product_name }}</h2>
          </div>
          <span :class="['status', statusMap[order.status]?.cls]">{{ statusMap[order.status]?.text }}</span>
        </div>

        <div class="info-grid">
          <div><span>买家</span><strong>{{ order.buyer_name }}</strong></div>
          <div><span>卖家</span><strong>{{ order.seller_name }}</strong></div>
          <div><span>数量</span><strong>{{ order.quantity }}</strong></div>
          <div><span>订单金额</span><strong class="price">¥{{ Number(order.amount).toFixed(2) }}</strong></div>
          <div><span>下单时间</span><strong>{{ formatDate(order.created_at) }}</strong></div>
          <div><span>支付时间</span><strong>{{ formatDate(order.paid_at) }}</strong></div>
          <div><span>完成时间</span><strong>{{ formatDate(order.completed_at) }}</strong></div>
        </div>

        <section v-if="order.status === 'receiving' || order.shipping_address_text" class="address-panel">
          <h3>收货地址</h3>
          <p v-if="order.shipping_address_text">
            {{ order.receiver_name }} {{ order.receiver_phone }}，{{ order.shipping_address_text }}
          </p>
          <p v-else class="muted">尚未选择收货地址</p>
        </section>
      </article>

      <aside class="detail-side">
        <section class="action-card">
          <h3>订单操作</h3>
          <div class="action-list">
            <button v-if="order.status === 'pending_payment'" class="primary full" type="button" :disabled="actionLoading" @click="openAddressModal('pay')">
              {{ actionLoading ? '处理中...' : '去支付' }}
            </button>
            <button v-if="order.status === 'receiving'" class="primary full" type="button" :disabled="actionLoading" @click="handleConfirm">
              {{ actionLoading ? '处理中...' : '确认收货' }}
            </button>
            <button v-if="order.status === 'receiving'" class="secondary full" type="button" :disabled="actionLoading" @click="openAddressModal('edit')">
              修改地址
            </button>
            <button v-if="order.status === 'receiving'" class="danger full" type="button" :disabled="actionLoading" @click="handleReturn">
              退货
            </button>
            <span v-if="order.status === 'pending_return'" class="creator-hint">退货审核中，请耐心等待管理员处理</span>
            <button v-if="order.status === 'pending_payment'" class="danger full" type="button" :disabled="actionLoading" @click="handleCancel">
              {{ actionLoading ? '处理中...' : '取消订单' }}
            </button>
            <button class="secondary full" type="button" @click="router.push('/my-orders')">返回列表</button>
          </div>
        </section>
      </aside>
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
          <button type="button" class="primary" :disabled="actionLoading" @click="submitAddressModal">
            {{ actionLoading ? '处理中...' : addressMode === 'pay' ? '确认付款' : '保存地址' }}
          </button>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.page { width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 20px; }
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 32px; }
.detail-layout { display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 20px; align-items: start; }
.detail-main, .action-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.detail-main { padding: 24px; }
.detail-header { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 20px; }
.code { margin-bottom: 8px; color: var(--accent); font-size: 13px; font-weight: 800; }
.detail-header h2 { font-size: 26px; }
.status { display: inline-flex; align-items: center; height: 28px; padding: 0 10px; border-radius: 999px; font-size: 13px; font-weight: 700; }
.status-pending { background: #fef3c7; color: #b45309; }
.status-active { background: #dbeafe; color: #1d4ed8; }
.status-receiving { background: #f1ebff; color: #6d4bc2; }
.status-done { background: #dcfce7; color: #15803d; }
.status-cancelled { background: #e5e7eb; color: #374151; }
.info-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.info-grid div, .address-panel { padding: 14px; border-radius: 8px; background: var(--soft); }
.info-grid span { display: block; color: var(--muted); font-size: 13px; }
.info-grid strong { display: block; margin-top: 8px; font-size: 16px; }
.price { color: #be123c; font-size: 20px !important; }
.address-panel { margin-top: 16px; }
.address-panel h3 { font-size: 16px; margin-bottom: 8px; }
.address-panel p { color: var(--muted); line-height: 1.7; }
.muted { color: var(--muted); }
.action-card { padding: 18px; }
.action-card h3 { font-size: 18px; margin-bottom: 14px; }
.action-list { display: grid; gap: 10px; }
.creator-hint { text-align: center; color: var(--muted); font-size: 13px; padding: 8px 0; }
.primary, .secondary, .danger { min-height: 44px; padding: 0 18px; border-radius: 8px; font-weight: 800; cursor: pointer; font: inherit; }
.primary { border: 0; color: #fff; background: var(--accent); }
.primary:hover { background: var(--accent-dark); }
.primary:disabled, .danger:disabled { opacity: 0.6; cursor: not-allowed; }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
.danger { border: 0; color: #fff; background: #be123c; }
.danger:hover { background: #9f1239; }
.full { width: 100%; }
.empty-state { min-height: 200px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); }
.empty-state strong { display: block; color: var(--ink); font-size: 18px; }
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
@media (max-width: 860px) {
  .detail-layout, .info-grid, .form-row { grid-template-columns: 1fr; }
}
</style>
