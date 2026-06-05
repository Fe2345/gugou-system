<script setup lang="ts">
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import type { OrderItem } from '@/types/order'
import { getOrderList, cancelOrder, confirmOrder, createPayment, confirmPayment } from '@/api/order'

const router = useRouter()
const orders = ref<OrderItem[]>([])
const loading = ref(false)
const activeTab = ref('all')

const tabs = [
  { key: 'all', label: '全部' },
  { key: 'pending_payment', label: '待付款' },
  { key: 'paid', label: '已支付' },
  { key: 'completed', label: '已完成' },
  { key: 'cancelled', label: '已取消' },
]

const statusMap: Record<string, string> = {
  created: '已创建',
  pending_payment: '待付款',
  paid: '已支付',
  completed: '已完成',
  cancelled: '已取消',
  closed: '已关闭',
  refunded: '已退款',
}

const statusClassMap: Record<string, string> = {
  created: 'status-pending',
  pending_payment: 'status-pending',
  paid: 'status-paid',
  completed: 'status-completed',
  cancelled: 'status-cancelled',
  closed: 'status-cancelled',
  refunded: 'status-cancelled',
}

async function loadOrders() {
  loading.value = true
  try {
    const params: Record<string, any> = { page: 1, page_size: 50 }
    if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }
    const res = await getOrderList(params)
    if (res.code === 200) {
      orders.value = res.data.results
    }
  } catch (e) {
    ElMessage.error('加载订单失败', e)
  } finally {
    loading.value = false
  }
}

function switchTab(tab: string) {
  activeTab.value = tab
  loadOrders()
}

async function handlePay(order: OrderItem) {
  try {
    const res = await createPayment(order.order_id)
    if (res.code === 200) {
      const payRes = await confirmPayment(order.order_id, res.data.payment_id)
      if (payRes.code === 200) {
        ElMessage.success('支付成功')
        loadOrders()
      }
    }
  } catch (e) {
    ElMessage.error('支付失败')
  }
}

async function handleConfirm(order: OrderItem) {
  try {
    const res = await confirmOrder(order.order_id)
    if (res.code === 200) {
      ElMessage.success('订单已完成')
      loadOrders()
    }
  } catch (e) {
    ElMessage.error('操作失败')
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
  } catch (e) {
    ElMessage.error('取消失败')
  }
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

onMounted(() => {
  loadOrders()
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
            </div>
            <div class="order-price">
              <strong>¥ {{ Number(order.amount).toFixed(2) }}</strong>
            </div>
          </div>
          <div class="order-footer">
            <button v-if="order.status === 'pending_payment'" class="primary" type="button" @click="handlePay(order)">去付款</button>
            <button v-if="order.status === 'paid'" class="primary" type="button" @click="handleConfirm(order)">确认完成</button>
            <button v-if="order.status === 'pending_payment'" class="secondary" type="button" @click="handleCancel(order)">取消订单</button>
            <button class="secondary" type="button" @click="router.push(`/my-orders/${order.order_id}`)">查看详情</button>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>

<style scoped>
.page {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 28px 0 44px;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 28px;
  align-items: center;
  padding: 36px;
  border-radius: 10px;
  color: #fff;
  background: linear-gradient(rgba(10, 74, 90, 0.88), rgba(10, 74, 90, 0.92)),
    url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80") center/cover;
  box-shadow: var(--shadow);
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--gold);
  font-size: 13px;
  font-weight: 800;
}

h1, h2, h3, p {
  margin: 0;
}

h1 {
  font-size: 42px;
  line-height: 1.16;
}

.hero p:last-child {
  max-width: 660px;
  margin-top: 14px;
  color: rgba(255, 255, 255, 0.84);
  line-height: 1.8;
}

.order-section {
  margin-top: 20px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--panel);
  box-shadow: var(--shadow);
  padding: 24px;
}

.tabs {
  display: flex;
  gap: 8px;
  padding: 6px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #f4f8fa;
  margin-bottom: 20px;
}

.tabs button {
  min-height: 42px;
  flex: 1;
  border: 0;
  border-radius: 6px;
  color: var(--muted);
  background: transparent;
  font-weight: 700;
  cursor: pointer;
  font: inherit;
}

.tabs button.active {
  color: #fff;
  background: var(--accent);
  box-shadow: 0 10px 24px rgba(15, 93, 114, 0.2);
}

.empty-state {
  min-height: 200px;
  display: grid;
  place-items: center;
  text-align: center;
  border: 1px dashed #bfd0d5;
  border-radius: 10px;
  color: var(--muted);
  background: var(--soft);
}

.empty-state strong {
  display: block;
  margin-bottom: 8px;
  color: var(--ink);
  font-size: 18px;
}

.order-list {
  display: grid;
  gap: 16px;
}

.order-card {
  border: 1px solid var(--line);
  border-radius: 10px;
  overflow: hidden;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--soft);
  border-bottom: 1px solid var(--line);
}

.order-id {
  font-size: 13px;
  color: var(--muted);
}

.order-date {
  font-size: 13px;
  color: var(--muted);
}

.order-status {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.status-pending {
  background: #fef3c7;
  color: #b45309;
}

.status-paid {
  background: #dbeafe;
  color: #1d4ed8;
}

.status-completed {
  background: #dcfce7;
  color: #15803d;
}

.status-cancelled {
  background: #f3f4f6;
  color: #6b7280;
}

.order-body {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}

.order-info {
  flex: 1;
}

.order-info h3 {
  font-size: 16px;
  margin-bottom: 8px;
}

.order-info p {
  color: var(--muted);
  font-size: 14px;
}

.order-price strong {
  font-size: 20px;
  color: var(--accent);
  font-weight: 800;
}

.order-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 12px 16px;
  border-top: 1px solid var(--line);
}

.primary, .secondary {
  min-height: 38px;
  padding: 0 16px;
  border: 0;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  font: inherit;
}

.primary {
  color: #fff;
  background: var(--accent);
}

.primary:hover {
  background: var(--accent-dark);
}

.secondary {
  color: var(--muted);
  background: var(--soft);
  border: 1px solid var(--line);
}

.secondary:hover {
  background: #edf6f8;
}

@media (max-width: 620px) {
  .page {
    width: min(100% - 20px, 1180px);
  }

  .hero, .order-section {
    padding: 20px;
  }

  h1 {
    font-size: 30px;
  }

  .tabs {
    flex-wrap: wrap;
  }

  .tabs button {
    flex: none;
    min-width: calc(50% - 4px);
  }

  .order-body {
    flex-wrap: wrap;
  }

  .order-footer {
    flex-wrap: wrap;
  }

  .primary, .secondary {
    flex: 1;
    min-width: 120px;
  }
}
</style>
