<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { useUserStore } from '@/stores/user'
import { getGroupDetail, joinGroup, leaveGroup, cancelGroup, type GroupDetailItem } from '@/api/group'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const detail = ref<GroupDetailItem | null>(null)
const loading = ref(false)
const actionLoading = ref(false)

const currentUserId = computed(() => userStore.userInfo?.id || '')
const isCreator = computed(() => detail.value?.creator_id === currentUserId.value)
const isParticipant = computed(() => {
  if (!detail.value?.participants) return false
  return detail.value.participants.some(p => p.user_id === currentUserId.value && p.status === 'joined')
})

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

async function loadDetail() {
  loading.value = true
  try {
    const id = route.params.id as string
    const res = await getGroupDetail(id)
    if (res.code === 200) {
      detail.value = res.data
    }
  } catch (e) {
    ElMessage.error('加载拼团详情失败')
  } finally {
    loading.value = false
  }
}

async function handleJoin() {
  if (!detail.value) return
  actionLoading.value = true
  try {
    const res = await joinGroup(detail.value.team_id)
    if (res.code === 200) {
      alert('参与成功')
      loadDetail()
    } else {
      ElMessage.warning(res.message || '参与失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '参与失败')
  } finally {
    actionLoading.value = false
  }
}

async function handleCancel() {
  if (!detail.value) return
  try {
    await ElMessageBox.confirm('取消后所有参与者将退出。', '确认取消此拼团？', {
      confirmButtonText: '确认取消',
      cancelButtonText: '再想想',
      type: 'warning',
    })
  } catch {
    return
  }
  actionLoading.value = true
  try {
    const res = await cancelGroup(detail.value.team_id)
    if (res.code === 200) {
      ElMessage.success('已取消')
      router.push('/group/my')
    } else {
      ElMessage.error(res.message || '取消失败')
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '取消失败')
  } finally {
    actionLoading.value = false
  }
}

async function handleLeave() {
  if (!detail.value) return
  try {
    await ElMessageBox.confirm('退出后将从该拼团参与者列表中移除。', '确认退出此拼团？', {
      confirmButtonText: '确认退出',
      cancelButtonText: '再想想',
      type: 'warning',
    })
  } catch {
    return
  }
  actionLoading.value = true
  try {
    const res = await leaveGroup(detail.value.team_id)
    if (res.code === 200) {
      ElMessage.success('已退出拼团')
      loadDetail()
    } else {
      ElMessage.error(res.message || '退出失败')
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '退出失败')
  } finally {
    actionLoading.value = false
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function getProgress() {
  if (!detail.value || detail.value.target_count === 0) return 0
  return Math.round((detail.value.current_count / detail.value.target_count) * 100)
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
            <h2>{{ detail.product_name }}</h2>
          </div>
          <span :class="['status', statusMap[detail.status]?.cls]">{{ statusMap[detail.status]?.text }}</span>
        </div>

        <div class="info-grid">
          <div><span>发起人</span><strong>{{ detail.creator_name }}</strong></div>
          <div><span>团购价</span><strong class="price">¥{{ detail.team_price }}/人</strong></div>
          <div><span>商品原价</span><strong>¥{{ detail.product_price }}</strong></div>
          <div><span>创建时间</span><strong>{{ formatDate(detail.created_at) }}</strong></div>
          <div><span>截止时间</span><strong>{{ formatDate(detail.deadline) }}</strong></div>
          <div><span>更新时间</span><strong>{{ formatDate(detail.updated_at) }}</strong></div>
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
            <!-- 未参与且可参与时显示 -->
            <button v-if="detail.status === 'recruiting' && !detail.is_expired && !isParticipant && !isCreator" class="primary full" type="button" :disabled="actionLoading" @click="handleJoin">
              {{ actionLoading ? '参与中...' : '参与拼团' }}
            </button>
            <!-- 已参与提示 -->
            <span v-if="isParticipant && !isCreator && detail.status === 'recruiting'" class="creator-hint">已参与</span>
            <!-- 发起人不能参与自己的拼团 -->
            <span v-if="isCreator && detail.status === 'recruiting'" class="creator-hint">你已是拼团发起人</span>
            <!-- 团长显示取消拼团 -->
            <button v-if="isCreator && detail.status === 'recruiting'" class="danger full" type="button" :disabled="actionLoading" @click="handleCancel">
              {{ actionLoading ? '取消中...' : '取消拼团' }}
            </button>
            <!-- 团员显示退出拼团 -->
            <button v-if="isParticipant && !isCreator && detail.status === 'recruiting'" class="danger full" type="button" :disabled="actionLoading" @click="handleLeave">
              {{ actionLoading ? '退出中...' : '退出拼团' }}
            </button>
            <button class="secondary full" type="button" @click="router.push('/group')">返回列表</button>
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
.status-active { background: #eaf6f8; color: var(--accent); }
.status-done { background: #dcfce7; color: #15803d; }
.status-cancelled { background: #e5e7eb; color: #374151; }
.info-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-bottom: 24px; }
.info-grid div { padding: 14px; border-radius: 8px; background: var(--soft); }
.info-grid span { display: block; color: var(--muted); font-size: 13px; }
.info-grid strong { display: block; margin-top: 8px; font-size: 16px; }
.price { color: #be123c; }
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
.participant-info { display: flex; gap: 10px; align-items: center; }
.participant-info strong { font-size: 15px; }
.participant-status { font-size: 12px; color: var(--accent); background: #eaf6f8; padding: 2px 8px; border-radius: 4px; }
.participant-time { color: var(--muted); font-size: 13px; }
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

@media (max-width: 860px) { .detail-layout { grid-template-columns: 1fr; } }
</style>
