<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { getOrderDetail, cancelOrder, confirmOrder, createPayment, confirmPayment } from '@/api/order'
import type { OrderItem } from '@/types/order'

const route = useRoute()
const router = useRouter()
const order = ref<OrderItem | null>(null)
const loading = ref(false)
const actionLoading = ref(false)

const statusMap: Record<string, { text: string; cls: string }> = {
  created: { text: '已创建', cls: 'status-pending' },
  pending_payment: { text: '待付款', cls: 'status-pending' },
  paid: { text: '已支付', cls: 'status-active' },
  completed: { text: '已完成', cls: 'status-done' },
  cancelled: { text: '已取消', cls: 'status-cancelled' },
  closed: { text: '已关闭', cls: 'status-cancelled' },
  refunded: { text: '已退款', cls: 'status-cancelled' },
}

async function loadOrder() {
  loading.value = true
  try {
    const id = route.params.id as string
    const res = await getOrderDetail(id)
    if (res.code === 200) {
      order.value = res.data
    }
  } catch (e) {
    console.error('加载订单详情失败', e)
  } finally {
    loading.value = false
  }
}

async function handlePay() {
  if (!order.value) return
  actionLoading.value = true
  try {
    const payRes = await createPayment(order.value.order_id)
    if (payRes.code === 200) {
      const confirmRes = await confirmPayment(order.value.order_id, payRes.data.payment_id)
      if (confirmRes.code === 200) {
        alert('支付成功')
        loadOrder()
      } else {
        alert(confirmRes.message || '支付确认失败')
      }
    } else {
      alert(payRes.message || '创建支付失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '支付失败')
  } finally {
    actionLoading.value = false
  }
}

async function handleConfirm() {
  if (!order.value) return
  if (!confirm('确认完成此订单？')) return
  actionLoading.value = true
  try {
    const res = await confirmOrder(order.value.order_id)
    if (res.code === 200) {
      alert('订单已确认完成')
      loadOrder()
    } else {
      alert(res.message || '确认失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '确认失败')
  } finally {
    actionLoading.value = false
  }
}

async function handleCancel() {
  if (!order.value) return
  if (!confirm('确认取消此订单？')) return
  actionLoading.value = true
  try {
    const res = await cancelOrder(order.value.order_id)
    if (res.code === 200) {
      alert('订单已取消')
      loadOrder()
    } else {
      alert(res.message || '取消失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '取消失败')
  } finally {
    actionLoading.value = false
  }
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadOrder()
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
      </article>

      <aside class="detail-side">
        <section class="action-card">
          <h3>订单操作</h3>
          <div class="action-list">
            <button v-if="order.status === 'pending_payment'" class="primary full" type="button" :disabled="actionLoading" @click="handlePay">
              {{ actionLoading ? '处理中...' : '去支付' }}
            </button>
            <button v-if="order.status === 'paid'" class="primary full" type="button" :disabled="actionLoading" @click="handleConfirm">
              {{ actionLoading ? '处理中...' : '确认完成' }}
            </button>
            <button v-if="order.status === 'pending_payment'" class="danger full" type="button" :disabled="actionLoading" @click="handleCancel">
              {{ actionLoading ? '处理中...' : '取消订单' }}
            </button>
            <button class="secondary full" type="button" @click="router.push('/my-orders')">返回列表</button>
          </div>
        </section>
      </aside>
    </section>
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
.status-done { background: #dcfce7; color: #15803d; }
.status-cancelled { background: #e5e7eb; color: #374151; }
.info-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.info-grid div { padding: 14px; border-radius: 8px; background: var(--soft); }
.info-grid span { display: block; color: var(--muted); font-size: 13px; }
.info-grid strong { display: block; margin-top: 8px; font-size: 16px; }
.price { color: #be123c; font-size: 20px !important; }
.action-card { padding: 18px; }
.action-card h3 { font-size: 18px; margin-bottom: 14px; }
.action-list { display: grid; gap: 10px; }
.primary, .secondary, .danger { min-height: 44px; padding: 0 18px; border-radius: 8px; font-weight: 800; cursor: pointer; font: inherit; }
.primary { border: 0; color: #fff; background: var(--accent); }
.primary:hover { background: var(--accent-dark); }
.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
.danger { border: 0; color: #fff; background: #be123c; }
.danger:hover { background: #9f1239; }
.danger:disabled { opacity: 0.6; cursor: not-allowed; }
.full { width: 100%; }
.empty-state { min-height: 200px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); }
.empty-state strong { display: block; color: var(--ink); font-size: 18px; }

@media (max-width: 860px) { .detail-layout { grid-template-columns: 1fr; } }
</style>
