<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { OrderItem } from '@/types/order'
import { getOrderList, approveReturn, rejectReturn } from '@/api/order'
import { ElMessage, ElMessageBox } from 'element-plus'
defineOptions({ name: 'AdminOrdersView' })

const orders = ref<OrderItem[]>([])
const loading = ref(false)
const totalCount = ref(0)
const searchQuery = ref('')
const filterStatus = ref('')

const statusMap: Record<string, string> = {
  created: '已创建',
  pending_payment: '待付款',
  paid: '已支付',
  completed: '已完成',
  cancelled: '已取消',
  closed: '已关闭',
  pending_return: '待审核退货',
  refunded: '已退款',
}

const statusClassMap: Record<string, string> = {
  created: 'pending',
  pending_payment: 'pending',
  paid: 'alert',
  completed: 'done',
  cancelled: 'done',
  closed: 'done',
  pending_return: 'alert',
  refunded: 'alert',
}

async function loadOrders() {
  loading.value = true
  try {
    const res = await getOrderList({
      page: 1,
      page_size: 50,
      keyword: searchQuery.value || undefined,
      status: filterStatus.value || undefined,
    })
    if (res.code === 200) {
      orders.value = res.data.results
      totalCount.value = res.data.count
    }
  } catch (e) {
    console.error('加载订单失败', e)
  } finally {
    loading.value = false
  }
}

function handleSearch() { loadOrders() }
function handleFilter() { loadOrders() }

async function handleApprove(orderId: string) {
  try {
    await ElMessageBox.confirm('确认通过此退货申请？通过后将执行退款并扣除买家信用分。', '通过退货', {
      confirmButtonText: '确认通过',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  try {
    const res = await approveReturn(orderId)
    if (res.code === 200) {
      ElMessage.success('退货已通过，订单已退款')
      loadOrders()
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '操作失败')
  }
}

async function handleReject(orderId: string) {
  let reason = ''
  try {
    const result = await ElMessageBox.prompt('请输入驳回原因。', '驳回退货', {
      confirmButtonText: '确认驳回',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入驳回原因',
      inputValidator: value => !!value?.trim() || '请填写驳回原因',
      type: 'warning',
    })
    reason = result.value
  } catch {
    return
  }
  try {
    const res = await rejectReturn(orderId, reason)
    if (res.code === 200) {
      ElMessage.success('退货已驳回')
      loadOrders()
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '操作失败')
  }
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadOrders()
})
</script>

<template>
  <section class="page-head">
    <div>
      <p class="eyebrow">订单处理</p>
      <h1>订单管理</h1>
      <p>查看订单状态、处理异常订单、跟踪发货与收货进度</p>
    </div>
  </section>

  <section class="data-grid">
    <article class="data-card">
      <span>总订单数</span><strong>{{ totalCount }}</strong><p>全部订单</p>
    </article>
    <article class="data-card">
      <span>待付款</span><strong>{{ orders.filter(o => o.status === 'pending_payment').length }}</strong><p>需跟进付款</p>
    </article>
    <article class="data-card">
      <span>已支付</span><strong>{{ orders.filter(o => o.status === 'paid').length }}</strong><p>待确认完成</p>
    </article>
    <article class="data-card">
      <span>已完成</span><strong>{{ orders.filter(o => o.status === 'completed').length }}</strong><p>交易完成</p>
    </article>
  </section>

  <section class="toolbar">
    <div class="search-box"><input v-model="searchQuery" type="search" placeholder="输入订单编号、买家昵称或商品名称" @keyup.enter="handleSearch"></div>
    <select v-model="filterStatus" @change="handleFilter">
      <option value="">全部状态</option>
      <option value="pending_payment">待付款</option>
      <option value="paid">已支付</option>
      <option value="completed">已完成</option>
      <option value="cancelled">已取消</option>
      <option value="pending_return">待审核退货</option>
      <option value="refunded">已退款</option>
    </select>
    <button class="primary" type="button" :disabled="loading" @click="loadOrders">{{ loading ? '加载中...' : '刷新订单' }}</button>
  </section>

  <section class="content-row">
    <article class="table-panel">
      <div class="section-head">
        <div><p class="eyebrow">订单列表</p><h2>全部订单</h2></div>
        <span class="count-badge">共 {{ totalCount }} 条</span>
      </div>
      <div v-if="loading" class="loading-state">加载中...</div>
      <div v-else class="table-wrap">
        <table>
          <thead><tr><th>订单编号</th><th>买家</th><th>卖家</th><th>商品</th><th>金额</th><th>状态</th><th>下单时间</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="o in orders" :key="o.order_id">
              <td>{{ o.order_id }}</td>
              <td>{{ o.buyer_name }}</td>
              <td>{{ o.seller_name }}</td>
              <td>{{ o.product_name }}</td>
              <td class="price">¥{{ Number(o.amount).toFixed(2) }}</td>
              <td><span class="status" :class="statusClassMap[o.status]">{{ statusMap[o.status] }}</span></td>
              <td>{{ formatDate(o.created_at) }}</td>
              <td>
                <template v-if="o.status === 'pending_return'">
                  <button class="primary small" type="button" @click="handleApprove(o.order_id)">通过</button>
                  <button class="danger small" type="button" @click="handleReject(o.order_id)">驳回</button>
                </template>
                <span v-else class="muted">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>

    <aside class="panel">
      <div class="panel-title"><h3>异常订单处理</h3></div>
      <ul class="info-list">
        <li><strong>退款申请</strong><p>买家提交退款原因后，管理员核对付款与物流状态。</p></li>
        <li><strong>超时未发货</strong><p>系统自动标记后，管理员提醒卖家并记录跟进结果。</p></li>
        <li><strong>收货争议</strong><p>管理员查看订单详情、聊天记录与物流信息后进行处理。</p></li>
      </ul>
    </aside>
  </section>
</template>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 20px; }
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; } h1 { font-size: 32px; }
.page-head > div > p:last-child { margin-top: 8px; color: var(--muted); }

.data-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-bottom: 20px; }
.data-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 20px; }
.data-card span { color: var(--muted); font-size: 14px; }
.data-card strong { display: block; margin-top: 10px; font-size: 30px; }
.data-card p { margin-top: 8px; color: var(--muted); }

.toolbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; padding: 18px; margin-bottom: 20px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.search-box { flex: 1; min-width: 200px; }
.search-box input { width: 100%; height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 14px; font: inherit; background: var(--soft); }
select { height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; font: inherit; background: var(--soft); min-width: 120px; }
.primary { height: 42px; padding: 0 18px; border: 0; border-radius: 8px; background: var(--accent); color: #fff; font-weight: 800; cursor: pointer; font: inherit; }
.primary:hover { background: var(--accent-dark); }
.primary.small, .danger.small { height: 30px; padding: 0 10px; font-size: 12px; margin-right: 6px; }
.danger { border: 0; border-radius: 8px; background: #be123c; color: #fff; font-weight: 800; cursor: pointer; font: inherit; }
.danger:hover { background: #9f1239; }
.secondary { height: 42px; padding: 0 16px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); font-weight: 700; cursor: pointer; font: inherit; }
.muted { color: var(--muted); font-size: 13px; }

.content-row { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.7fr); gap: 18px; align-items: start; }
.table-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); overflow: hidden; }
.section-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; border-bottom: 1px solid var(--line); }
.section-head .eyebrow { margin-bottom: 4px; }
.count-badge { color: var(--muted); font-size: 14px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 14px 16px; border-bottom: 1px solid var(--line); text-align: left; font-size: 14px; white-space: nowrap; }
th { color: var(--muted); font-size: 12px; font-weight: 700; background: var(--soft); }
tr:last-child td { border-bottom: 0; }
.price { color: #be123c; font-weight: 700; }
.status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status.pending { background: #fef3c7; color: #b45309; }
.status.alert { background: #dbeafe; color: #1d4ed8; }
.status.done { background: #dcfce7; color: #15803d; }
.loading-state { padding: 40px; text-align: center; color: var(--muted); }

.panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 18px; box-shadow: none; }
.panel-title { margin-bottom: 14px; }
.panel-title h3 { font-size: 18px; }
.info-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
.info-list li { padding: 12px 14px; border: 1px solid var(--line); border-radius: 8px; background: var(--soft); }
.info-list strong { display: block; margin-bottom: 6px; font-size: 14px; }
.info-list p { margin: 0; color: var(--muted); font-size: 13px; line-height: 1.5; }

@media (max-width: 1100px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .content-row { grid-template-columns: 1fr; } }
</style>
