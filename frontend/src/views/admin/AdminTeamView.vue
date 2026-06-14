<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  getAdminTeamList, getAdminTeamDetail, getAdminTeamParticipants,
  adminCancelTeam, adminFailTeam, adminSuccessTeam,
} from '@/api/admin'
import type { GroupItem, GroupDetailItem, GroupParticipantItem } from '@/api/group'
defineOptions({ name: 'AdminTeamView' })

const teams = ref<GroupItem[]>([])
const loading = ref(false)
const totalCount = ref(0)
const statusCounts = ref<Record<string, number>>({})
const page = ref(1)
const pageSize = ref(10)

// 搜索与筛选
const keyword = ref('')
const statusFilter = ref('')
const startDate = ref('')
const endDate = ref('')

// 详情弹窗
const showDetail = ref(false)
const detailData = ref<GroupDetailItem | null>(null)
const detailLoading = ref(false)
const participants = ref<GroupParticipantItem[]>([])
const participantsLoading = ref(false)

// 操作弹窗
const showAction = ref(false)
const actionType = ref<'cancel' | 'fail' | 'success'>('cancel')
const actionReason = ref('')
const actionTarget = ref('')
const actionLoading = ref(false)

const statusMap: Record<string, { text: string; cls: string }> = {
  recruiting: { text: '招募中', cls: 'pending' },
  success: { text: '已成团', cls: 'done' },
  failed: { text: '已失败', cls: 'failed' },
  cancelled: { text: '已取消', cls: 'failed' },
}

const participantStatusMap: Record<string, string> = {
  joined: '已参与',
  cancelled: '已取消',
  refunded: '已退款',
}

async function loadTeams() {
  loading.value = true
  try {
    const res = await getAdminTeamList({
      keyword: keyword.value || undefined,
      status: statusFilter.value || undefined,
      start_date: startDate.value || undefined,
      end_date: endDate.value || undefined,
      page: page.value,
      page_size: pageSize.value,
    })
    if (res.code === 200) {
      teams.value = res.data.results
      totalCount.value = res.data.count
      if (res.data.status_counts) {
        statusCounts.value = res.data.status_counts
      }
    }
  } catch (e) {
    console.error('加载拼团项目失败', e)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  loadTeams()
}

function handleReset() {
  keyword.value = ''
  statusFilter.value = ''
  startDate.value = ''
  endDate.value = ''
  page.value = 1
  loadTeams()
}

function changePage(newPage: number) {
  page.value = newPage
  loadTeams()
}

async function viewDetail(id: string) {
  detailLoading.value = true
  participantsLoading.value = true
  showDetail.value = true
  detailData.value = null
  participants.value = []
  try {
    const [detailRes, participantsRes] = await Promise.all([
      getAdminTeamDetail(id),
      getAdminTeamParticipants(id),
    ])
    if (detailRes.code === 200) detailData.value = detailRes.data
    if (participantsRes.code === 200) participants.value = participantsRes.data
  } catch (e) {
    console.error('加载详情失败', e)
  } finally {
    detailLoading.value = false
    participantsLoading.value = false
  }
}

function openAction(id: string, type: 'cancel' | 'fail' | 'success') {
  actionTarget.value = id
  actionType.value = type
  actionReason.value = ''
  showAction.value = true
}

async function doAction() {
  actionLoading.value = true
  try {
    let res
    if (actionType.value === 'cancel') {
      res = await adminCancelTeam(actionTarget.value, actionReason.value || undefined)
    } else if (actionType.value === 'fail') {
      res = await adminFailTeam(actionTarget.value)
    } else {
      res = await adminSuccessTeam(actionTarget.value)
    }
    if (res.code === 200) {
      showAction.value = false
      loadTeams()
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

onMounted(() => {
  loadTeams()
})
</script>

<template>
  <section class="page-head">
    <div>
      <p class="eyebrow">拼团管理</p>
      <h1>拼团项目</h1>
      <p>管理拼团项目、查看参与记录、处理异常拼团</p>
    </div>
  </section>

  <section class="data-grid">
    <article class="data-card">
      <span>总项目数</span><strong>{{ totalCount }}</strong><p>全部拼团项目</p>
    </article>
    <article class="data-card">
      <span>招募中</span><strong>{{ statusCounts['recruiting'] ?? 0 }}</strong><p>需关注截止时间</p>
    </article>
    <article class="data-card">
      <span>已成团</span><strong>{{ statusCounts['success'] ?? 0 }}</strong><p>已成功</p>
    </article>
    <article class="data-card">
      <span>已失败</span><strong>{{ statusCounts['failed'] ?? 0 }}</strong><p>需做原因分析</p>
    </article>
  </section>

  <section class="toolbar">
    <div class="search-box"><input v-model="keyword" type="search" placeholder="输入拼团编号或商品名称" @keyup.enter="handleSearch"></div>
    <select v-model="statusFilter">
      <option value="">全部状态</option>
      <option value="recruiting">招募中</option>
      <option value="success">已成团</option>
      <option value="failed">已失败</option>
      <option value="cancelled">已取消</option>
    </select>
    <input v-model="startDate" type="date" title="开始日期">
    <input v-model="endDate" type="date" title="结束日期">
    <button class="primary" type="button" @click="handleSearch">搜索</button>
    <button class="secondary" type="button" @click="handleReset">重置</button>
  </section>

  <section class="content-row">
    <article class="table-panel">
      <div class="section-head">
        <div><p class="eyebrow">拼团列表</p><h2>全部拼团项目</h2></div>
        <span class="count-badge">共 {{ totalCount }} 条</span>
      </div>
      <div v-if="loading" class="loading-state">加载中...</div>
      <div v-else class="table-wrap">
        <table>
          <thead><tr><th>拼团编号</th><th>商品</th><th>发起用户</th><th>人数进度</th><th>团购价</th><th>状态</th><th>截止时间</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="t in teams" :key="t.team_id">
              <td><button class="link-btn" type="button" @click="viewDetail(t.team_id)">{{ t.team_id }}</button></td>
              <td>{{ t.product_name_display }}</td>
              <td>{{ t.creator_name }}</td>
              <td>{{ t.current_count }} / {{ t.target_count }}</td>
              <td class="price">¥{{ Number(t.team_price).toFixed(2) }}</td>
              <td><span class="status" :class="statusMap[t.status]?.cls">{{ statusMap[t.status]?.text }}</span></td>
              <td>{{ formatDate(t.deadline) }}</td>
              <td class="actions-cell">
                <button class="link-btn" type="button" @click="viewDetail(t.team_id)">详情</button>
                <button v-if="t.status === 'recruiting'" class="link-btn warn" type="button" @click="openAction(t.team_id, 'fail')">标记失败</button>
                <button v-if="t.status === 'recruiting'" class="link-btn danger" type="button" @click="openAction(t.team_id, 'cancel')">取消</button>
                <button v-if="t.status === 'recruiting' && t.current_count >= t.target_count" class="link-btn ok" type="button" @click="openAction(t.team_id, 'success')">确认成功</button>
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
      <div class="panel-title"><h3>拼团管理说明</h3></div>
      <ul class="info-list">
        <li><strong>状态管理</strong><p>可取消、标记失败、确认成功，参与者状态自动同步。</p></li>
        <li><strong>成员查看</strong><p>查看拼团参与记录，用于后续对账与通知。</p></li>
        <li><strong>异常处理</strong><p>人数异常、过期未满等情况可标记失败或取消。</p></li>
      </ul>
    </aside>
  </section>

  <!-- 详情弹窗 -->
  <div v-if="showDetail" class="modal-overlay" @click.self="showDetail = false">
    <div class="modal">
      <div class="modal-header">
        <h2>拼团详情</h2>
        <button class="modal-close" @click="showDetail = false">&times;</button>
      </div>
      <div v-if="detailLoading" class="modal-body"><p>加载中...</p></div>
      <div v-else-if="detailData" class="modal-body">
        <div class="detail-grid">
          <div><span>拼团编号</span><strong>{{ detailData.team_id }}</strong></div>
          <div><span>商品</span><strong>{{ detailData.product_name_display }}</strong></div>
          <div><span>发起用户</span><strong>{{ detailData.creator_name }} ({{ detailData.creator_id }})</strong></div>
          <div><span>团购价</span><strong class="price">¥{{ Number(detailData.team_price).toFixed(2) }}</strong></div>
          <div><span>人数进度</span><strong>{{ detailData.current_count }} / {{ detailData.target_count }}</strong></div>
          <div><span>状态</span><strong><span class="status" :class="statusMap[detailData.status]?.cls">{{ statusMap[detailData.status]?.text }}</span></strong></div>
          <div><span>是否过期</span><strong>{{ detailData.is_expired ? '是' : '否' }}</strong></div>
          <div><span>截止时间</span><strong>{{ formatDate(detailData.deadline) }}</strong></div>
          <div><span>创建时间</span><strong>{{ formatDate(detailData.created_at) }}</strong></div>
        </div>

        <div class="sub-section">
          <h3>参与记录</h3>
          <div v-if="participantsLoading" class="loading-state">加载中...</div>
          <div v-else-if="participants.length === 0" class="empty-text">暂无参与记录</div>
          <table v-else class="inner-table">
            <thead><tr><th>参与编号</th><th>用户</th><th>状态</th><th>参与时间</th></tr></thead>
            <tbody>
              <tr v-for="p in participants" :key="p.participant_id">
                <td>{{ p.participant_id }}</td>
                <td>{{ p.user_name }} ({{ p.user_id }})</td>
                <td>{{ participantStatusMap[p.status] || p.status }}</td>
                <td>{{ formatDate(p.joined_at) }}</td>
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
        <h2>{{ actionType === 'cancel' ? '取消拼团' : actionType === 'fail' ? '标记失败' : '确认成功' }}</h2>
        <button class="modal-close" @click="showAction = false">&times;</button>
      </div>
      <div class="modal-body">
        <p v-if="actionType === 'cancel'">确认取消拼团 <strong>{{ actionTarget }}</strong>？所有参与者状态将更新为已取消。</p>
        <p v-else-if="actionType === 'fail'">确认将拼团 <strong>{{ actionTarget }}</strong> 标记为失败？</p>
        <p v-else>确认将拼团 <strong>{{ actionTarget }}</strong> 标记为成功？参与者将获得信用分奖励。</p>
        <div v-if="actionType === 'cancel'" class="form-group">
          <label>取消原因</label>
          <input v-model="actionReason" type="text" placeholder="请输入取消原因（可选）">
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
.price { color: #be123c; font-weight: 700; }
.status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status.pending { background: #dbeafe; color: #1d4ed8; }
.status.done { background: #dcfce7; color: #15803d; }
.status.failed { background: #fee2e2; color: #be123c; }
.loading-state { padding: 40px; text-align: center; color: var(--muted); }
.empty-text { padding: 20px; text-align: center; color: var(--muted); font-size: 14px; }
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

@media (max-width: 1100px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .content-row { grid-template-columns: 1fr; } }
</style>
