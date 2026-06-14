<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { useUserStore } from '@/stores/user'
import {
  getGroupDetail, joinGroup, leaveGroup, cancelGroup,
  getMyTeamOrder, payTeamOrder, confirmTeamOrder, returnTeamOrder,
  type GroupDetailItem, type TeamOrderItem, type TeamItemOption
} from '@/api/group'
import { getAddresses, addAddress, getDivisions, type AddressForm, type AddressItem, type DivisionItem } from '@/api/address'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const detail = ref<GroupDetailItem | null>(null)
const loading = ref(false)
const actionLoading = ref(false)
const myOrder = ref<TeamOrderItem | null>(null)

// 地址弹窗相关
const showAddressModal = ref(false)
const pendingItemId = ref<string | null>(null)
const addresses = ref<AddressItem[]>([])
const selectedAddressId = ref<number | null>(null)
const useNewAddress = ref(false)
const provinces = ref<DivisionItem[]>([])
const cities = ref<DivisionItem[]>([])
const districts = ref<DivisionItem[]>([])

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

// 支付弹窗相关
const showPayDialog = ref(false)

const currentUserId = computed(() => userStore.userInfo?.id || '')
const isCreator = computed(() => detail.value?.creator_id === currentUserId.value)
const isParticipant = computed(() => {
  if (!detail.value?.participants) return false
  return detail.value.participants.some(p => p.user_id === currentUserId.value && p.status === 'joined')
})
const creatorHasJoined = computed(() => {
  if (!detail.value?.participants) return false
  return detail.value.participants.some(p => p.user_id === detail.value?.creator_id && p.status === 'joined')
})

const selectedAddress = computed(() => addresses.value.find(a => a.id === selectedAddressId.value) || null)

const statusMap: Record<string, { text: string; cls: string }> = {
  recruiting: { text: '招募中', cls: 'status-active' },
  success: { text: '已成团', cls: 'status-done' },
  failed: { text: '已失败', cls: 'status-cancelled' },
  cancelled: { text: '已取消', cls: 'status-cancelled' },
}

const participantStatusMap: Record<string, string> = {
  joined: '已参与',
  cancelled: '已退出',
  refunded: '已退款',
}

const canJoin = computed(() => {
  if (!detail.value) return false
  if (detail.value.status !== 'recruiting' || detail.value.is_expired) return false
  if (detail.value.current_count >= detail.value.target_count) return false
  // 发起人未参与时，只有发起人可以加入
  if (!creatorHasJoined.value && !isCreator.value) return false
  // 已参与且不是发起人的不能再次加入
  if (isParticipant.value && !isCreator.value) return false
  // 发起人已参与且已选小商品，不能再次加入
  if (isCreator.value && isParticipant.value) return false
  return true
})

// ========== 数据加载 ==========

async function loadDetail() {
  loading.value = true
  try {
    const id = route.params.id as string
    const res = await getGroupDetail(id)
    if (res.code === 200) {
      detail.value = res.data
      if (res.data.status === 'success' && isParticipant.value) {
        loadMyOrder()
      }
    }
  } catch (e) {
    ElMessage.error('加载拼团详情失败')
  } finally {
    loading.value = false
  }
}

async function loadMyOrder() {
  try {
    const id = route.params.id as string
    const res = await getMyTeamOrder(id)
    if (res.code === 200) myOrder.value = res.data
  } catch (e) {
    console.error('加载拼团订单失败', e)
  }
}

// ========== 地址弹窗（参与拼团时选择地址） ==========

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

async function handleItemClick(item: TeamItemOption) {
  if (item.is_selected) return
  if (!detail.value || detail.value.status !== 'recruiting' || detail.value.is_expired) return
  if (!canJoin.value) return

  pendingItemId.value = item.item_id
  useNewAddress.value = addresses.value.length === 0
  if (!provinces.value.length) await loadProvinces()
  await loadJoinAddresses()
  resetAddressForm()
  showAddressModal.value = true
}

async function loadJoinAddresses() {
  try {
    const res = await getAddresses()
    if (res.code === 200) {
      addresses.value = res.data || []
      selectedAddressId.value = addresses.value.find(a => a.is_default)?.id || addresses.value[0]?.id || null
    }
  } catch (e) {
    console.error('加载地址失败', e)
  }
}

function closeAddressModal() {
  showAddressModal.value = false
  pendingItemId.value = null
  actionLoading.value = false
}

async function ensureAddressId(): Promise<number | null> {
  if (!useNewAddress.value) {
    if (!selectedAddressId.value) {
      ElMessage.warning('请选择收货地址')
      return null
    }
    return selectedAddressId.value
  }
  // 创建新地址
  if (!addressForm.receiver_name || !addressForm.receiver_phone || !addressForm.province_code || !addressForm.city_code || !addressForm.district_code || !addressForm.street || !addressForm.detail) {
    ElMessage.warning('请填写完整的地址信息')
    return null
  }
  const res = await addAddress(addressForm)
  if (res.code !== 200) {
    ElMessage.error(res.message || '创建地址失败')
    return null
  }
  await loadJoinAddresses()
  selectedAddressId.value = res.data.id
  return res.data.id
}

async function submitJoinWithAddress() {
  if (!detail.value || !pendingItemId.value) return
  actionLoading.value = true
  try {
    const addressId = await ensureAddressId()
    if (!addressId) { actionLoading.value = false; return }

    const res = await joinGroup(detail.value.team_id, {
      item_id: pendingItemId.value,
      address_id: addressId,
    })
    if (res.code === 200) {
      ElMessage.success('参与拼团成功')
      closeAddressModal()
      loadDetail()
    } else {
      ElMessage.error(res.message || '参与失败')
      actionLoading.value = false
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '参与失败')
    actionLoading.value = false
  }
}

// ========== 支付弹窗（拼团成功后支付） ==========

async function handleOpenPay() {
  useNewAddress.value = false
  if (!provinces.value.length) await loadProvinces()
  // 加载地址到共享的 addresses 列表
  try {
    const res = await getAddresses()
    if (res.code === 200) {
      addresses.value = res.data || []
      selectedAddressId.value = addresses.value.find(a => a.is_default)?.id || addresses.value[0]?.id || null
      if (addresses.value.length === 0) useNewAddress.value = true
    }
  } catch (e) {
    console.error('加载地址失败', e)
  }
  resetAddressForm()
  showPayDialog.value = true
}

async function handlePay() {
  actionLoading.value = true
  try {
    const addressId = await ensureAddressId()
    if (!addressId) { actionLoading.value = false; return }

    const id = route.params.id as string
    const res = await payTeamOrder(id, {
      pay_method: 'simulated',
      address_id: addressId
    })
    if (res.code === 200) {
      ElMessage.success('支付成功')
      showPayDialog.value = false
      loadMyOrder()
    } else {
      ElMessage.error(res.message || '支付失败')
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '支付失败')
  } finally {
    actionLoading.value = false
  }
}

// ========== 其他操作 ==========

async function handleConfirm() {
  try {
    await ElMessageBox.confirm('确认已收到商品？', '确认收货', {
      confirmButtonText: '确认收货', cancelButtonText: '取消', type: 'info',
    })
  } catch { return }
  actionLoading.value = true
  try {
    const id = route.params.id as string
    const res = await confirmTeamOrder(id)
    if (res.code === 200) { ElMessage.success('确认收货成功'); loadMyOrder() }
    else ElMessage.error(res.message || '确认失败')
  } catch (e: any) { ElMessage.error(e?.response?.data?.message || '确认失败') }
  finally { actionLoading.value = false }
}

async function handleReturn() {
  try {
    await ElMessageBox.confirm('确认要退货吗？退货后将退款。', '申请退货', {
      confirmButtonText: '确认退货', cancelButtonText: '取消', type: 'warning',
    })
  } catch { return }
  actionLoading.value = true
  try {
    const id = route.params.id as string
    const res = await returnTeamOrder(id, { reason: '买家申请退货' })
    if (res.code === 200) { ElMessage.success('退货成功'); loadMyOrder() }
    else ElMessage.error(res.message || '退货失败')
  } catch (e: any) { ElMessage.error(e?.response?.data?.message || '退货失败') }
  finally { actionLoading.value = false }
}

async function handleCancel() {
  if (!detail.value) return
  try {
    await ElMessageBox.confirm('取消后所有参与者将退出。', '确认取消此拼团？', {
      confirmButtonText: '确认取消', cancelButtonText: '再想想', type: 'warning',
    })
  } catch { return }
  actionLoading.value = true
  try {
    const res = await cancelGroup(detail.value.team_id)
    if (res.code === 200) { ElMessage.success('已取消'); router.push('/group/my') }
    else ElMessage.error(res.message || '取消失败')
  } catch (e: any) { ElMessage.error(e?.response?.data?.message || '取消失败') }
  finally { actionLoading.value = false }
}

async function handleLeave() {
  if (!detail.value) return
  try {
    await ElMessageBox.confirm('退出后将从该拼团参与者列表中移除。', '确认退出此拼团？', {
      confirmButtonText: '确认退出', cancelButtonText: '再想想', type: 'warning',
    })
  } catch { return }
  actionLoading.value = true
  try {
    const res = await leaveGroup(detail.value.team_id)
    if (res.code === 200) { ElMessage.success('已退出拼团'); loadDetail() }
    else ElMessage.error(res.message || '退出失败')
  } catch (e: any) { ElMessage.error(e?.response?.data?.message || '退出失败') }
  finally { actionLoading.value = false }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function getProgress() {
  if (!detail.value || detail.value.target_count === 0) return 0
  return Math.round((detail.value.current_count / detail.value.target_count) * 100)
}

onMounted(() => { loadDetail() })
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">拼团市场</p>
        <h1>拼团详情</h1>
      </div>
      <button class="secondary" type="button" @click="router.push('/group')">返回拼团</button>
    </section>

    <div v-if="loading" class="empty-state"><strong>加载中...</strong></div>
    <div v-else-if="!detail" class="empty-state"><strong>拼团不存在</strong></div>
    <section v-else class="detail-layout">
      <article class="detail-main">
        <div class="detail-header">
          <div>
            <p class="code">拼团 {{ detail.team_id }}</p>
            <h2>{{ detail.product_name_display }}</h2>
          </div>
          <span :class="['status', statusMap[detail.status]?.cls]">{{ statusMap[detail.status]?.text }}</span>
        </div>

        <div class="info-grid">
          <div><span>发起人</span><strong>{{ detail.creator_name }}</strong></div>
          <div><span>团购价</span><strong class="price">¥{{ detail.team_price }}/人</strong></div>
          <div><span>创建时间</span><strong>{{ formatDate(detail.created_at) }}</strong></div>
          <div><span>截止时间</span><strong>{{ formatDate(detail.deadline) }}</strong></div>
          <div><span>更新时间</span><strong>{{ formatDate(detail.updated_at) }}</strong></div>
        </div>

        <!-- 小商品选项卡片 -->
        <div v-if="detail.items && detail.items.length > 0" class="items-section">
          <h3>选择你想要的小商品 ({{ detail.items.filter(i => i.is_selected).length }} / {{ detail.items.length }} 已选)</h3>
          <p v-if="detail.status === 'recruiting' && !detail.is_expired && isCreator && !isParticipant" class="items-hint">请先选择一个小商品参与拼团，之后其他用户才能加入</p>
          <p v-else-if="detail.status === 'recruiting' && !detail.is_expired && !isParticipant && !isCreator && !creatorHasJoined" class="items-hint">等待发起人先参与拼团...</p>
          <p v-else-if="detail.status === 'recruiting' && !detail.is_expired && !isParticipant && !isCreator" class="items-hint">点击灰色可选卡片即可参与拼团</p>
          <div class="items-grid">
            <div
              v-for="item in detail.items"
              :key="item.item_id"
              :class="['item-card', { 'item-taken': item.is_selected, 'item-available': !item.is_selected && canJoin }]"
              @click="handleItemClick(item)"
            >
              <div class="item-card-body">
                <span class="item-name">{{ item.name }}</span>
                <span v-if="item.is_selected" class="item-badge taken">已被选</span>
                <span v-else-if="canJoin" class="item-badge available">可选</span>
                <span v-else class="item-badge unavailable">不可选</span>
              </div>
              <div v-if="item.is_selected && item.selected_user_name" class="item-card-footer">
                {{ item.selected_user_name }}
              </div>
            </div>
          </div>
        </div>

        <div class="progress-section">
          <div class="progress-head">
            <h3>拼团进度</h3>
            <strong>{{ detail.current_count }} / {{ detail.target_count }} 人 ({{ getProgress() }}%)</strong>
          </div>
          <div class="progress-bar">
            <span :style="{ width: getProgress() + '%' }"></span>
          </div>
          <p class="progress-hint">还需 {{ Math.max(0, detail.target_count - detail.current_count) }} 人参与即可成团</p>
        </div>

        <div v-if="detail.participants && detail.participants.length > 0" class="participants-section">
          <h3>参与者 ({{ detail.participants.length }})</h3>
          <div class="participant-list">
            <div v-for="p in detail.participants" :key="p.participant_id" class="participant-item">
              <div class="participant-info">
                <strong>{{ p.user_name }}</strong>
                <span v-if="p.selected_item_name" class="participant-item-tag">{{ p.selected_item_name }}</span>
                <span class="participant-status">{{ participantStatusMap[p.status] || p.status }}</span>
              </div>
              <span class="participant-time">{{ formatDate(p.joined_at) }}</span>
            </div>
          </div>
        </div>
      </article>

      <aside class="detail-side">
        <section class="action-card">
          <h3>操作</h3>
          <div class="action-list">
            <span v-if="isCreator && detail.status === 'recruiting' && !isParticipant" class="hint-text">请先选择一个小商品参与拼团</span>
            <span v-if="isCreator && detail.status === 'recruiting' && isParticipant" class="hint-text">你已参与拼团</span>
            <span v-if="isParticipant && !isCreator && detail.status === 'recruiting'" class="hint-text">已参与</span>
            <button v-if="isCreator && detail.status === 'recruiting'" class="danger full" type="button" :disabled="actionLoading" @click="handleCancel">
              {{ actionLoading ? '取消中...' : '取消拼团' }}
            </button>
            <button v-if="isParticipant && !isCreator && detail.status === 'recruiting'" class="danger full" type="button" :disabled="actionLoading" @click="handleLeave">
              {{ actionLoading ? '退出中...' : '退出拼团' }}
            </button>

            <template v-if="detail.status === 'success' && isParticipant && myOrder">
              <div class="order-info">
                <p class="order-label">我的拼团订单</p>
                <p class="order-id">{{ myOrder.order_id }}</p>
                <p class="order-amount">¥{{ Number(myOrder.amount).toFixed(2) }}</p>
              </div>
              <button v-if="myOrder.status === 'pending_payment'" class="primary full" type="button" :disabled="actionLoading" @click="handleOpenPay">
                {{ actionLoading ? '处理中...' : '去支付' }}
              </button>
              <button v-if="myOrder.status === 'receiving'" class="primary full" type="button" :disabled="actionLoading" @click="handleConfirm">
                {{ actionLoading ? '处理中...' : '确认收货' }}
              </button>
              <button v-if="myOrder.status === 'receiving'" class="danger full" type="button" :disabled="actionLoading" @click="handleReturn">
                {{ actionLoading ? '处理中...' : '申请退货' }}
              </button>
              <span v-if="myOrder.status === 'completed'" class="hint-text">订单已完成</span>
              <span v-if="myOrder.status === 'refunded'" class="hint-text">订单已退款</span>
              <span v-if="myOrder.status === 'cancelled'" class="hint-text">订单已取消</span>
            </template>
            <span v-if="detail.status === 'success' && isCreator" class="hint-text">拼团已成功，请等待团员付款</span>

            <button class="secondary full" type="button" @click="router.push('/group')">返回列表</button>
          </div>
        </section>
      </aside>
    </section>

    <!-- 地址弹窗（参与拼团时选择地址） -->
    <div v-if="showAddressModal" class="modal-overlay" @click.self="closeAddressModal">
      <div class="address-modal">
        <div class="modal-head">
          <h2>选择收货地址</h2>
          <button class="modal-close" type="button" @click="closeAddressModal">&times;</button>
        </div>
        <div class="modal-body">
          <p class="modal-tip">你选择了：<strong>{{ detail?.items?.find(i => i.item_id === pendingItemId)?.name }}</strong></p>
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
          <button type="button" class="primary" :disabled="actionLoading" @click="submitJoinWithAddress">
            {{ actionLoading ? '参与中...' : '确认参与' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 支付弹窗（拼团成功后支付） -->
    <div v-if="showPayDialog" class="modal-overlay" @click.self="showPayDialog = false">
      <div class="address-modal">
        <div class="modal-head">
          <h2>选择收货地址并支付</h2>
          <button class="modal-close" type="button" @click="showPayDialog = false">&times;</button>
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
          <button type="button" class="secondary" @click="showPayDialog = false">取消</button>
          <button type="button" class="primary" :disabled="actionLoading" @click="handlePay">
            {{ actionLoading ? '支付中...' : '确认支付' }}
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
.status-active { background: #eaf6f8; color: var(--accent); }
.status-done { background: #dcfce7; color: #15803d; }
.status-cancelled { background: #e5e7eb; color: #374151; }
.info-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-bottom: 24px; }
.info-grid div { padding: 14px; border-radius: 8px; background: var(--soft); }
.info-grid span { display: block; color: var(--muted); font-size: 13px; }
.info-grid strong { display: block; margin-top: 8px; font-size: 16px; }
.price { color: #be123c; }

/* 小商品卡片 */
.items-section { margin-bottom: 24px; }
.items-section h3 { font-size: 18px; margin-bottom: 6px; }
.items-hint { color: var(--muted); font-size: 13px; margin-bottom: 12px; }
.items-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; }
.item-card { padding: 16px; border-radius: 10px; border: 2px solid var(--line); background: var(--soft); transition: all 0.15s; }
.item-card-body { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.item-name { font-weight: 700; font-size: 14px; }
.item-badge { font-size: 12px; padding: 2px 8px; border-radius: 4px; font-weight: 600; white-space: nowrap; }
.item-badge.available { background: #e5e7eb; color: #374151; }
.item-badge.taken { background: #dcfce7; color: #15803d; }
.item-badge.unavailable { background: #f3f4f6; color: #9ca3af; }
.item-card-footer { margin-top: 8px; font-size: 12px; color: var(--muted); }
.item-taken { border-color: #86efac; background: #f0fdf4; cursor: default; }
.item-available { border-color: #d1d5db; background: #f9fafb; cursor: pointer; }
.item-available:hover { border-color: var(--accent); background: #eef8fa; transform: translateY(-1px); }

.progress-section { margin-bottom: 24px; }
.progress-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.progress-head h3 { font-size: 18px; }
.progress-head strong { color: var(--accent); }
.progress-bar { height: 16px; border-radius: 999px; background: #e5eef1; overflow: hidden; }
.progress-bar span { display: block; height: 100%; border-radius: inherit; background: var(--accent); transition: width 0.3s; }
.progress-hint { margin-top: 8px; color: var(--muted); font-size: 14px; }
.participants-section h3 { font-size: 18px; margin-bottom: 12px; }
.participant-list { display: grid; gap: 10px; }
.participant-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 14px; border-radius: 8px; background: var(--soft); }
.participant-info { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.participant-info strong { font-size: 15px; }
.participant-status { font-size: 12px; color: var(--accent); background: #eaf6f8; padding: 2px 8px; border-radius: 4px; }
.participant-item-tag { font-size: 12px; color: #15803d; background: #dcfce7; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
.participant-time { color: var(--muted); font-size: 13px; }
.action-card { padding: 18px; }
.action-card h3 { font-size: 18px; margin-bottom: 14px; }
.action-list { display: grid; gap: 10px; }
.hint-text { text-align: center; color: var(--muted); font-size: 13px; padding: 8px 0; }
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

@media (max-width: 860px) { .detail-layout { grid-template-columns: 1fr; } }

.order-info { padding: 14px; border-radius: 8px; background: var(--soft); text-align: center; }
.order-label { color: var(--muted); font-size: 13px; margin-bottom: 6px; }
.order-id { color: var(--accent); font-size: 14px; font-weight: 700; margin-bottom: 4px; }
.order-amount { color: #be123c; font-size: 20px; font-weight: 800; }

/* 地址弹窗 */
.modal-overlay { position: fixed; inset: 0; z-index: 1000; display: grid; place-items: center; padding: 20px; background: rgba(0,0,0,0.45); }
.address-modal { width: min(720px, 100%); max-height: 90vh; overflow-y: auto; border-radius: 12px; background: var(--panel); box-shadow: 0 24px 70px rgba(0,0,0,0.24); }
.modal-head { display: flex; align-items: center; justify-content: space-between; padding: 22px 24px; border-bottom: 1px solid var(--line); }
.modal-head h2 { font-size: 22px; }
.modal-close { width: 38px; height: 38px; border: 0; border-radius: 8px; background: var(--soft); color: var(--muted); font-size: 24px; cursor: pointer; }
.modal-body { display: grid; gap: 16px; padding: 24px; }
.modal-tip { padding: 12px 14px; border-radius: 8px; background: #eef8fa; color: var(--accent); font-size: 14px; }
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

/* 支付弹窗 */
</style>
