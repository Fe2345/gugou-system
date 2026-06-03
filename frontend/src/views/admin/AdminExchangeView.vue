<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  getAdminExchangeList, getAdminExchangeDetail,
  adminExpireExchange, adminCancelExchange, adminCompleteExchange,
  adminHandleAbnormalExchange,
} from '@/api/admin'
import type { SwapItem, SwapDetailItem, SwapMatchItem, SwapStatusLogItem } from '@/api/swap'
defineOptions({ name: 'AdminExchangeView' })

const requests = ref<SwapItem[]>([])
const loading = ref(false)
const totalCount = ref(0)
const page = ref(1)
const pageSize = ref(10)

// 搜索与筛选
const keyword = ref('')
const statusFilter = ref('')
const startDate = ref('')
const endDate = ref('')

// 详情弹窗
const showDetail = ref(false)
const detailData = ref<SwapDetailItem | null>(null)
const detailLoading = ref(false)

// 操作弹窗
const showAction = ref(false)
const actionType = ref<'expire' | 'cancel' | 'complete' | 'abnormal'>('cancel')
const actionReason = ref('')
const actionTarget = ref('')
const actionLoading = ref(false)

const statusMap: Record<string, { text: string; cls: string }> = {
  active: { text: '可交易', cls: 'pending' },
  matched: { text: '匹配中', cls: 'confirming' },
  completed: { text: '已完成', cls: 'done' },
  cancelled: { text: '已取消', cls: 'expired' },
  expired: { text: '已过期', cls: 'expired' },
}

const matchStatusMap: Record<string, string> = {
  pending: '待确认',
  accepted: '已接受',
  rejected: '已拒绝',
  expired: '已过期',
}

async function loadSwaps() {
  loading.value = true
  try {
    const res = await getAdminExchangeList({
      keyword: keyword.value || undefined,
      status: statusFilter.value || undefined,
      start_date: startDate.value || undefined,
      end_date: endDate.value || undefined,
      page: page.value,
      page_size: pageSize.value,
    })
    if (res.code === 200) {
      requests.value = res.data.results
      totalCount.value = res.data.count
    }
  } catch (e) {
    console.error('加载换物请求失败', e)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  loadSwaps()
}

function handleReset() {
  keyword.value = ''
  statusFilter.value = ''
  startDate.value = ''
  endDate.value = ''
  page.value = 1
  loadSwaps()
}

function changePage(newPage: number) {
  page.value = newPage
  loadSwaps()
}

async function viewDetail(id: string) {
  detailLoading.value = true
  showDetail.value = true
  try {
    const res = await getAdminExchangeDetail(id)
    if (res.code === 200) {
      detailData.value = res.data
    }
  } catch (e) {
    console.error('加载详情失败', e)
  } finally {
    detailLoading.value = false
  }
}

function openAction(id: string, type: 'expire' | 'cancel' | 'complete' | 'abnormal') {
  actionTarget.value = id
  actionType.value = type
  actionReason.value = ''
  showAction.value = true
}

async function doAction() {
  actionLoading.value = true
  try {
    let res
    if (actionType.value === 'expire') {
      res = await adminExpireExchange(actionTarget.value)
    } else if (actionType.value === 'cancel') {
      res = await adminCancelExchange(actionTarget.value, actionReason.value || undefined)
    } else if (actionType.value === 'complete') {
      res = await adminCompleteExchange(actionTarget.value)
    } else {
      res = await adminHandleAbnormalExchange(actionTarget.value, actionReason.value)
    }
    if (res.code === 200) {
      showAction.value = false
      loadSwaps()
    } else {
      alert(res.message || '操作失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '操作失败')
  } finally {
    actionLoading.value = false
  }
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

onMounted(() => {
  loadSwaps()
})
</script>

<template>
  <section class="page-head">
    <div>
      <p class="eyebrow">换物管理</p>
      <h1>换物请求</h1>
      <p>管理换物请求、查看匹配状态、处理异常与取消记录</p>
    </div>
  </section>

  <section class="data-grid">
    <article class="data-card">
      <span>总请求数</span><strong>{{ totalCount }}</strong><p>全部换物请求</p>
    </article>
    <article class="data-card">
      <span>可交易</span><strong>{{ requests.filter(r => r.status === 'active').length }}</strong><p>等待匹配</p>
    </article>
    <article class="data-card">
      <span>匹配中</span><strong>{{ requests.filter(r => r.status === 'matched').length }}</strong><p>双方确认中</p>
    </article>
    <article class="data-card">
      <span>已完成</span><strong>{{ requests.filter(r => r.status === 'completed').length }}</strong><p>已完成</p>
    </article>
  </section>

  <section class="toolbar">
    <div class="search-box"><input v-model="keyword" type="search" placeholder="输入换物请求编号或发起用户" @keyup.enter="handleSearch"></div>
    <select v-model="statusFilter">
      <option value="">全部状态</option>
      <option value="active">可交易</option>
      <option value="matched">匹配中</option>
      <option value="completed">已完成</option>
      <option value="cancelled">已取消</option>
      <option value="expired">已过期</option>
    </select>
    <input v-model="startDate" type="date" title="开始日期">
    <input v-model="endDate" type="date" title="结束日期">
    <button class="primary" type="button" @click="handleSearch">搜索</button>
    <button class="secondary" type="button" @click="handleReset">重置</button>
  </section>

  <section class="content-row">
    <article class="table-panel">
      <div class="section-head">
        <div><p class="eyebrow">换物列表</p><h2>全部换物请求</h2></div>
        <span class="count-badge">共 {{ totalCount }} 条</span>
      </div>
      <div v-if="loading" class="loading-state">加载中...</div>
      <div v-else class="table-wrap">
        <table>
          <thead><tr><th>请求编号</th><th>发起用户</th><th>换出资产</th><th>目标条件</th><th>状态</th><th>创建时间</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="r in requests" :key="r.exchange_id">
              <td><button class="link-btn" type="button" @click="viewDetail(r.exchange_id)">{{ r.exchange_id }}</button></td>
              <td>{{ r.owner_name }}</td>
              <td>{{ r.offered_asset_name }}</td>
              <td>{{ r.target_condition || '不限' }}</td>
              <td><span class="status" :class="statusMap[r.status]?.cls">{{ statusMap[r.status]?.text }}</span></td>
              <td>{{ formatDate(r.created_at) }}</td>
              <td class="actions-cell">
                <button class="link-btn" type="button" @click="viewDetail(r.exchange_id)">详情</button>
                <button v-if="r.status === 'active' || r.status === 'matched'" class="link-btn warn" type="button" @click="openAction(r.exchange_id, 'expire')">标记过期</button>
                <button v-if="r.status === 'active' || r.status === 'matched'" class="link-btn danger" type="button" @click="openAction(r.exchange_id, 'cancel')">取消</button>
                <button v-if="r.status === 'matched'" class="link-btn ok" type="button" @click="openAction(r.exchange_id, 'complete')">确认完成</button>
                <button v-if="r.status === 'active' || r.status === 'matched'" class="link-btn danger" type="button" @click="openAction(r.exchange_id, 'abnormal')">处理异常</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="totalCount > pageSize" class="pagination">
        <button class="secondary" type="button" :disabled="page <= 1" @click="changePage(page - 1)">上一页</button>
        <span>第 {{ page }} / {{ Math.ceil(totalCount / pageSize) }} 页</span>
        <button class="secondary" type="button" :disabled="page >= Math.ceil(totalCount / pageSize)" @click="changePage(page + 1)">下一页</button>
      </div>
    </article>

    <aside class="panel">
      <div class="panel-title"><h3>换物管理说明</h3></div>
      <ul class="info-list">
        <li><strong>状态管理</strong><p>可标记过期、取消、确认完成，资产状态自动同步。</p></li>
        <li><strong>匹配查看</strong><p>查看匹配记录，协助双方完成交换。</p></li>
        <li><strong>异常处理</strong><p>资产不可用或系统异常时，可处理异常并释放资产。</p></li>
      </ul>
    </aside>
  </section>

  <!-- 详情弹窗 -->
  <div v-if="showDetail" class="modal-overlay" @click.self="showDetail = false">
    <div class="modal">
      <div class="modal-header">
        <h2>换物详情</h2>
        <button class="modal-close" @click="showDetail = false">&times;</button>
      </div>
      <div v-if="detailLoading" class="modal-body"><p>加载中...</p></div>
      <div v-else-if="detailData" class="modal-body">
        <div class="detail-grid">
          <div><span>请求编号</span><strong>{{ detailData.exchange_id }}</strong></div>
          <div><span>发起用户</span><strong>{{ detailData.owner_name }} ({{ detailData.owner_id }})</strong></div>
          <div><span>换出资产</span><strong>{{ detailData.offered_asset_name }}</strong></div>
          <div><span>目标条件</span><strong>{{ detailData.target_condition || '不限' }}</strong></div>
          <div><span>补差说明</span><strong>{{ detailData.price_difference_note || '无' }}</strong></div>
          <div><span>状态</span><strong><span class="status" :class="statusMap[detailData.status]?.cls">{{ statusMap[detailData.status]?.text }}</span></strong></div>
          <div><span>创建时间</span><strong>{{ formatDate(detailData.created_at) }}</strong></div>
          <div><span>更新时间</span><strong>{{ formatDate(detailData.updated_at) }}</strong></div>
        </div>

        <div v-if="detailData.matches?.length" class="sub-section">
          <h3>匹配记录</h3>
          <table class="inner-table">
            <thead><tr><th>匹配编号</th><th>申请用户</th><th>申请资产</th><th>状态</th><th>时间</th></tr></thead>
            <tbody>
              <tr v-for="m in detailData.matches" :key="m.match_id">
                <td>{{ m.match_id }}</td>
                <td>{{ m.applicant_name }}</td>
                <td>{{ m.applicant_asset_name }}</td>
                <td>{{ matchStatusMap[m.status] || m.status }}</td>
                <td>{{ formatDate(m.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="detailData.status_logs?.length" class="sub-section">
          <h3>状态日志</h3>
          <table class="inner-table">
            <thead><tr><th>操作</th><th>操作人</th><th>备注</th><th>时间</th></tr></thead>
            <tbody>
              <tr v-for="l in detailData.status_logs" :key="l.log_id">
                <td>{{ l.from_status || '-' }} → {{ l.to_status }}</td>
                <td>{{ l.operator_name }}</td>
                <td>{{ l.note || '-' }}</td>
                <td>{{ formatDate(l.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- 操作确认弹窗 -->
  <div v-if="showAction" class="modal-overlay" @click.self="showAction = false">
    <div class="modal modal-sm">
      <div class="modal-header">
        <h2>{{ actionType === 'expire' ? '标记过期' : actionType === 'cancel' ? '取消换物' : actionType === 'complete' ? '确认完成' : '处理异常' }}</h2>
        <button class="modal-close" @click="showAction = false">&times;</button>
      </div>
      <div class="modal-body">
        <p v-if="actionType === 'expire'">确认将换物请求 <strong>{{ actionTarget }}</strong> 标记为已过期？资产将被释放。</p>
        <p v-else-if="actionType === 'cancel'">确认取消换物请求 <strong>{{ actionTarget }}</strong>？资产将被释放。</p>
        <p v-else-if="actionType === 'complete'">确认完成换物请求 <strong>{{ actionTarget }}</strong>？双方资产将交换归属。</p>
        <p v-else>处理异常换物请求 <strong>{{ actionTarget }}</strong>，资产将被释放。</p>
        <div v-if="actionType === 'cancel'" class="form-group">
          <label>取消原因</label>
          <input v-model="actionReason" type="text" placeholder="请输入取消原因（可选）">
        </div>
        <div v-if="actionType === 'abnormal'" class="form-group">
          <label>异常原因 <span class="required">*</span></label>
          <input v-model="actionReason" type="text" placeholder="请输入异常原因（必填）" required>
        </div>
      </div>
      <div class="modal-actions">
        <button class="secondary" type="button" @click="showAction = false">取消</button>
        <button class="primary" type="button" :disabled="actionLoading" @click="doAction">
          {{ actionLoading ? '处理中...' : '确认' }}
        </button>
      </div>
    </div>
  </div>
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
select, input[type="date"] { height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; font: inherit; background: var(--soft); min-width: 120px; }
.primary { height: 42px; padding: 0 18px; border: 0; border-radius: 8px; background: var(--accent); color: #fff; font-weight: 800; cursor: pointer; font: inherit; }
.primary:hover { background: var(--accent-dark); }
.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.secondary { height: 42px; padding: 0 16px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); font-weight: 700; cursor: pointer; font: inherit; }

.content-row { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.7fr); gap: 18px; align-items: start; }
.table-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); overflow: hidden; }
.section-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; border-bottom: 1px solid var(--line); }
.section-head .eyebrow { margin-bottom: 4px; }
.count-badge { color: var(--muted); font-size: 14px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 14px 16px; border-bottom: 1px solid var(--line); text-align: left; font-size: 14px; }
th { color: var(--muted); font-size: 12px; font-weight: 700; background: var(--soft); }
tr:last-child td { border-bottom: 0; }
.status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status.pending { background: #dbeafe; color: #1d4ed8; }
.status.confirming { background: #ffedd5; color: #c2410c; }
.status.done { background: #dcfce7; color: #15803d; }
.status.expired { background: #e5e7eb; color: #374151; }
.loading-state { padding: 40px; text-align: center; color: var(--muted); }
.actions-cell { display: flex; gap: 8px; flex-wrap: wrap; }
.link-btn { border: 0; background: transparent; color: var(--accent); font-weight: 700; cursor: pointer; font: inherit; font-size: 13px; padding: 0; }
.link-btn:hover { text-decoration: underline; }
.link-btn.warn { color: #d97706; }
.link-btn.danger { color: #be123c; }
.link-btn.ok { color: #15803d; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; padding: 16px; border-top: 1px solid var(--line); }
.pagination span { color: var(--muted); font-size: 14px; }

.panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 18px; box-shadow: none; }
.panel-title { margin-bottom: 14px; }
.panel-title h3 { font-size: 18px; }
.info-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
.info-list li { padding: 12px 14px; border: 1px solid var(--line); border-radius: 8px; background: var(--soft); }
.info-list strong { display: block; margin-bottom: 6px; font-size: 14px; }
.info-list p { margin: 0; color: var(--muted); font-size: 13px; line-height: 1.5; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: grid; place-items: center; z-index: 1000; padding: 20px; }
.modal { background: var(--panel); border-radius: 16px; width: min(800px, 100%); max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
.modal-sm { width: min(480px, 100%); }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid var(--line); }
.modal-header h2 { font-size: 20px; }
.modal-close { width: 36px; height: 36px; border: 0; border-radius: 8px; background: var(--soft); color: var(--muted); font-size: 22px; cursor: pointer; display: grid; place-items: center; }
.modal-close:hover { background: #fee2e2; color: #be123c; }
.modal-body { padding: 24px; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; padding: 16px 24px; border-top: 1px solid var(--line); }

.detail-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-bottom: 20px; }
.detail-grid div { padding: 12px 14px; border-radius: 8px; background: var(--soft); }
.detail-grid span { display: block; color: var(--muted); font-size: 12px; margin-bottom: 6px; }
.detail-grid strong { font-size: 14px; }
.sub-section { margin-top: 20px; }
.sub-section h3 { font-size: 16px; margin-bottom: 12px; }
.inner-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.inner-table th, .inner-table td { padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; }
.inner-table th { color: var(--muted); background: var(--soft); font-weight: 700; }

.form-group { margin-top: 12px; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 700; font-size: 14px; }
.form-group input { width: 100%; height: 40px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; font: inherit; background: var(--soft); box-sizing: border-box; }
.required { color: #be123c; }

@media (max-width: 1100px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .content-row { grid-template-columns: 1fr; } }
</style>
