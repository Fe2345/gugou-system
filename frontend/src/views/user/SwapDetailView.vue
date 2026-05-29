<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { getSwapDetail, matchSwap, acceptMatch, rejectMatch, completeSwap, cancelSwap, type SwapDetailItem, type SwapMatchItem } from '@/api/swap'
import { getAssetsList } from '@/api/assets'
import type { AssetItem } from '@/types/assets'

const route = useRoute()
const router = useRouter()
const detail = ref<SwapDetailItem | null>(null)
const loading = ref(false)
const actionLoading = ref(false)
const showMatchDialog = ref(false)
const selectedAssetId = ref('')
const assetsList = ref<AssetItem[]>([])

const statusMap: Record<string, { text: string; cls: string }> = {
  active: { text: '可交易', cls: 'status-active' },
  matched: { text: '匹配中', cls: 'status-matched' },
  completed: { text: '已完成', cls: 'status-done' },
  cancelled: { text: '已取消', cls: 'status-cancelled' },
  expired: { text: '已过期', cls: 'status-cancelled' },
}

const matchStatusMap: Record<string, { text: string; cls: string }> = {
  pending: { text: '待处理', cls: 'status-active' },
  accepted: { text: '已接受', cls: 'status-done' },
  rejected: { text: '已拒绝', cls: 'status-cancelled' },
  expired: { text: '已过期', cls: 'status-cancelled' },
}

async function loadDetail() {
  loading.value = true
  try {
    const id = route.params.id as string
    const res = await getSwapDetail(id)
    if (res.code === 200) {
      detail.value = res.data
    }
  } catch (e) {
    console.error('加载换物详情失败', e)
  } finally {
    loading.value = false
  }
}

async function loadAssets() {
  try {
    const res = await getAssetsList()
    if (res.code === 200) {
      assetsList.value = res.data.list.filter(a => a.status === 'holding')
    }
  } catch (e) {
    console.error('加载资产失败', e)
  }
}

async function handleMatch() {
  if (!detail.value || !selectedAssetId.value) return
  actionLoading.value = true
  try {
    const res = await matchSwap(detail.value.exchange_id, { applicant_asset_id: selectedAssetId.value })
    if (res.code === 200) {
      alert('匹配请求已发送')
      showMatchDialog.value = false
      selectedAssetId.value = ''
      loadDetail()
    } else {
      alert(res.message || '匹配失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '匹配失败')
  } finally {
    actionLoading.value = false
  }
}

async function handleAccept(match: SwapMatchItem) {
  if (!detail.value) return
  actionLoading.value = true
  try {
    const res = await acceptMatch(detail.value.exchange_id, match.match_id)
    if (res.code === 200) {
      alert('已接受匹配')
      loadDetail()
    } else {
      alert(res.message || '操作失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '操作失败')
  } finally {
    actionLoading.value = false
  }
}

async function handleReject(match: SwapMatchItem) {
  if (!detail.value) return
  actionLoading.value = true
  try {
    const res = await rejectMatch(detail.value.exchange_id, match.match_id)
    if (res.code === 200) {
      alert('已拒绝匹配')
      loadDetail()
    } else {
      alert(res.message || '操作失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '操作失败')
  } finally {
    actionLoading.value = false
  }
}

async function handleComplete() {
  if (!detail.value) return
  if (!confirm('确认完成此换物？')) return
  actionLoading.value = true
  try {
    const res = await completeSwap(detail.value.exchange_id)
    if (res.code === 200) {
      alert('换物已完成')
      loadDetail()
    } else {
      alert(res.message || '操作失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '操作失败')
  } finally {
    actionLoading.value = false
  }
}

async function handleCancel() {
  if (!detail.value) return
  if (!confirm('确认取消此换物请求？')) return
  actionLoading.value = true
  try {
    const res = await cancelSwap(detail.value.exchange_id)
    if (res.code === 200) {
      alert('已取消')
      router.push('/swap/my')
    } else {
      alert(res.message || '取消失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '取消失败')
  } finally {
    actionLoading.value = false
  }
}

function openMatchDialog() {
  loadAssets()
  showMatchDialog.value = true
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadDetail()
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">换物市场</p>
        <h1>换物详情</h1>
      </div>
      <button class="secondary" type="button" @click="router.push('/swap')">返回换物</button>
    </section>

    <div v-if="loading" class="empty-state"><strong>加载中...</strong></div>
    <div v-else-if="!detail" class="empty-state"><strong>换物请求不存在</strong></div>
    <section v-else class="detail-layout">
      <article class="detail-main">
        <div class="detail-header">
          <div>
            <p class="code">换物 {{ detail.exchange_id }}</p>
            <h2>{{ detail.offered_asset_name }}</h2>
          </div>
          <span :class="['status', statusMap[detail.status]?.cls]">{{ statusMap[detail.status]?.text }}</span>
        </div>

        <div class="info-grid">
          <div><span>发起人</span><strong>{{ detail.owner_name }}</strong></div>
          <div><span>换出资产</span><strong>{{ detail.offered_asset_name }}</strong></div>
          <div><span>创建时间</span><strong>{{ formatDate(detail.created_at) }}</strong></div>
          <div><span>更新时间</span><strong>{{ formatDate(detail.updated_at) }}</strong></div>
        </div>

        <div class="desc-section">
          <h3>目标条件</h3>
          <p>{{ detail.target_condition || '不限' }}</p>
        </div>

        <div v-if="detail.price_difference_note" class="desc-section">
          <h3>差价说明</h3>
          <p>{{ detail.price_difference_note }}</p>
        </div>

        <div v-if="detail.matches && detail.matches.length > 0" class="matches-section">
          <h3>匹配记录 ({{ detail.matches.length }})</h3>
          <div class="match-list">
            <div v-for="match in detail.matches" :key="match.match_id" class="match-card">
              <div class="match-info">
                <div>
                  <strong>{{ match.applicant_name }}</strong>
                  <span>提供资产：{{ match.applicant_asset_name }}</span>
                </div>
                <span :class="['match-status', matchStatusMap[match.status]?.cls]">{{ matchStatusMap[match.status]?.text }}</span>
              </div>
              <div v-if="match.status === 'pending'" class="match-actions">
                <button class="primary sm" type="button" :disabled="actionLoading" @click="handleAccept(match)">接受</button>
                <button class="danger sm" type="button" :disabled="actionLoading" @click="handleReject(match)">拒绝</button>
              </div>
              <p class="match-time">{{ formatDate(match.created_at) }}</p>
            </div>
          </div>
        </div>

        <div v-if="detail.status_logs && detail.status_logs.length > 0" class="logs-section">
          <h3>状态记录</h3>
          <div class="log-list">
            <div v-for="log in detail.status_logs" :key="log.log_id" class="log-item">
              <span class="log-status">{{ log.from_status }} → {{ log.to_status }}</span>
              <span class="log-operator">{{ log.operator_name }}</span>
              <span v-if="log.note" class="log-note">{{ log.note }}</span>
              <span class="log-time">{{ formatDate(log.created_at) }}</span>
            </div>
          </div>
        </div>
      </article>

      <aside class="detail-side">
        <section class="action-card">
          <h3>操作</h3>
          <div class="action-list">
            <button v-if="detail.status === 'active'" class="primary full" type="button" @click="openMatchDialog">发起匹配</button>
            <button v-if="detail.status === 'matched'" class="primary full" type="button" :disabled="actionLoading" @click="handleComplete">确认完成</button>
            <button v-if="detail.status === 'active' || detail.status === 'matched'" class="danger full" type="button" :disabled="actionLoading" @click="handleCancel">取消换物</button>
            <button class="secondary full" type="button" @click="router.push('/swap')">返回列表</button>
          </div>
        </section>
      </aside>
    </section>

    <div v-if="showMatchDialog" class="dialog-overlay" @click.self="showMatchDialog = false">
      <div class="dialog">
        <h3>选择匹配资产</h3>
        <div class="form-group">
          <label>我的资产</label>
          <select v-model="selectedAssetId">
            <option value="">请选择资产</option>
            <option v-for="a in assetsList" :key="a.id" :value="a.id">{{ a.productName }} ({{ a.category }})</option>
          </select>
        </div>
        <div class="dialog-actions">
          <button class="secondary" type="button" @click="showMatchDialog = false">取消</button>
          <button class="primary" type="button" :disabled="!selectedAssetId || actionLoading" @click="handleMatch">
            {{ actionLoading ? '提交中...' : '确认匹配' }}
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
.status-matched { background: #ffedd5; color: #c2410c; }
.status-done { background: #dcfce7; color: #15803d; }
.status-cancelled { background: #e5e7eb; color: #374151; }
.info-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-bottom: 20px; }
.info-grid div { padding: 14px; border-radius: 8px; background: var(--soft); }
.info-grid span { display: block; color: var(--muted); font-size: 13px; }
.info-grid strong { display: block; margin-top: 8px; font-size: 16px; }
.desc-section { margin-bottom: 20px; }
.desc-section h3 { font-size: 18px; margin-bottom: 8px; }
.desc-section p { color: var(--muted); line-height: 1.7; }
.matches-section { margin-bottom: 20px; }
.matches-section h3 { font-size: 18px; margin-bottom: 12px; }
.match-list { display: grid; gap: 12px; }
.match-card { padding: 14px; border: 1px solid var(--line); border-radius: 8px; background: var(--soft); }
.match-info { display: flex; justify-content: space-between; gap: 12px; align-items: center; }
.match-info strong { display: block; font-size: 15px; }
.match-info span { display: block; color: var(--muted); font-size: 13px; margin-top: 4px; }
.match-status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.match-actions { display: flex; gap: 8px; margin-top: 10px; }
.match-time { margin-top: 8px; color: var(--muted); font-size: 12px; }
.logs-section h3 { font-size: 18px; margin-bottom: 12px; }
.log-list { display: grid; gap: 8px; }
.log-item { display: flex; gap: 12px; align-items: center; padding: 10px 14px; border-radius: 8px; background: var(--soft); font-size: 14px; }
.log-status { font-weight: 700; }
.log-operator { color: var(--accent); }
.log-note { color: var(--muted); }
.log-time { margin-left: auto; color: var(--muted); font-size: 13px; }
.action-card { padding: 18px; }
.action-card h3 { font-size: 18px; margin-bottom: 14px; }
.action-list { display: grid; gap: 10px; }
.primary, .secondary, .danger { min-height: 44px; padding: 0 18px; border-radius: 8px; font-weight: 800; cursor: pointer; font: inherit; }
.primary { border: 0; color: #fff; background: var(--accent); }
.primary:hover { background: var(--accent-dark); }
.primary:disabled, .danger:disabled { opacity: 0.6; cursor: not-allowed; }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
.danger { border: 0; color: #fff; background: #be123c; }
.danger:hover { background: #9f1239; }
.sm { min-height: 34px; padding: 0 14px; font-size: 13px; }
.full { width: 100%; }
.empty-state { min-height: 200px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); }
.empty-state strong { display: block; color: var(--ink); font-size: 18px; }
.dialog-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: grid; place-items: center; z-index: 1000; }
.dialog { width: min(480px, calc(100% - 32px)); background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.18); }
.dialog h3 { font-size: 20px; margin-bottom: 18px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 700; font-size: 14px; }
select { width: 100%; height: 44px; border: 1px solid var(--line); border-radius: 8px; padding: 0 14px; font: inherit; background: var(--soft); box-sizing: border-box; }
.dialog-actions { display: flex; gap: 10px; justify-content: flex-end; }

@media (max-width: 860px) { .detail-layout { grid-template-columns: 1fr; } }
</style>
