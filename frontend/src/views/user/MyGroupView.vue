<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { useUserStore } from '@/stores/user'
import { getMyGroups, cancelGroup, leaveGroup, type GroupItem } from '@/api/group'

const router = useRouter()
const userStore = useUserStore()
const groups = ref<GroupItem[]>([])
const loading = ref(false)
const totalCount = ref(0)

const currentUserId = computed(() => userStore.userInfo?.id || '')

const statusMap: Record<string, { text: string; cls: string }> = {
  recruiting: { text: '招募中', cls: 'status-active' },
  success: { text: '已成团', cls: 'status-done' },
  failed: { text: '已失败', cls: 'status-cancelled' },
  cancelled: { text: '已取消', cls: 'status-cancelled' },
}

async function loadGroups() {
  loading.value = true
  try {
    const res = await getMyGroups({ page: 1, page_size: 50 })
    if (res.code === 200) {
      groups.value = res.data.results
      totalCount.value = res.data.count
    }
  } catch (e) {
    console.error('加载我的拼团失败', e)
  } finally {
    loading.value = false
  }
}

async function handleCancel(item: GroupItem) {
  if (!confirm('确认取消此拼团？取消后所有参与者将退出。')) return
  try {
    const res = await cancelGroup(item.team_id)
    if (res.code === 200) {
      alert('已取消')
      loadGroups()
    } else {
      alert(res.message || '取消失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '取消失败')
  }
}

async function handleLeave(item: GroupItem) {
  if (!confirm('确认退出此拼团？')) return
  try {
    const res = await leaveGroup(item.team_id)
    if (res.code === 200) {
      alert('已退出拼团')
      loadGroups()
    } else {
      alert(res.message || '退出失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '退出失败')
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function getProgress(group: GroupItem) {
  if (group.target_count === 0) return 0
  return Math.round((group.current_count / group.target_count) * 100)
}

onMounted(() => {
  loadGroups()
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">拼团市场</p>
        <h1>我的拼团</h1>
        <p>管理发起和参与的拼团项目</p>
      </div>
      <div class="head-actions">
        <button class="secondary" type="button" @click="router.push('/group')">返回拼团</button>
        <button class="primary" type="button" @click="router.push('/group/publish')">发起拼团</button>
      </div>
    </section>

    <section class="data-grid">
      <article class="data-card">
        <span>总拼团</span><strong>{{ totalCount }}</strong><p>全部拼团</p>
      </article>
      <article class="data-card">
        <span>招募中</span><strong>{{ groups.filter(g => g.status === 'recruiting').length }}</strong><p>进行中</p>
      </article>
      <article class="data-card">
        <span>已成团</span><strong>{{ groups.filter(g => g.status === 'success').length }}</strong><p>拼团成功</p>
      </article>
      <article class="data-card">
        <span>已失败</span><strong>{{ groups.filter(g => g.status === 'failed').length }}</strong><p>未达成</p>
      </article>
    </section>

    <div v-if="loading" class="empty-state"><strong>加载中...</strong></div>
    <div v-else-if="groups.length === 0" class="empty-state">
      <strong>暂无拼团</strong>
      <p>还没有发起或参与拼团，快去看看吧</p>
      <button class="primary" type="button" @click="router.push('/group')">去拼团</button>
    </div>
    <section v-else class="list-wrap">
      <article v-for="item in groups" :key="item.team_id" class="list-card">
        <div class="card-main">
          <div>
            <p class="code">拼团 {{ item.team_id }}</p>
            <h3>{{ item.product_name }}</h3>
            <div class="tags">
              <span>发起人：{{ item.creator_name }}</span>
              <span>团购价：¥{{ item.team_price }}/人</span>
            </div>
          </div>
          <span :class="['status', statusMap[item.status]?.cls]">{{ statusMap[item.status]?.text }}</span>
        </div>
        <div class="progress-block">
          <div class="progress-head">
            <span>当前人数 {{ item.current_count }} / {{ item.target_count }}</span>
            <strong>{{ getProgress(item) }}%</strong>
          </div>
          <div class="progress-bar">
            <span :style="{ width: getProgress(item) + '%' }"></span>
          </div>
          <div class="progress-meta">
            <span>截止时间：{{ formatDate(item.deadline) }}</span>
            <span v-if="item.is_expired" class="expired-tag">已过期</span>
          </div>
        </div>
        <div class="card-actions">
          <button class="secondary" type="button" @click="router.push(`/group/${item.team_id}`)">查看详情</button>
          <!-- 团长显示取消拼团 -->
          <button v-if="item.creator_id === currentUserId && item.status === 'recruiting'" class="danger" type="button" @click="handleCancel(item)">取消拼团</button>
          <!-- 团员显示退出拼团 -->
          <button v-if="item.creator_id !== currentUserId && item.status === 'recruiting'" class="danger" type="button" @click="handleLeave(item)">退出拼团</button>
        </div>
      </article>
    </section>
  </main>
</template>

<style scoped>
.page { width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 20px; }
.head-actions { display: flex; gap: 10px; }
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 32px; }
.page-head > div > p:last-child { margin-top: 8px; color: var(--muted); }
.data-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-bottom: 20px; }
.data-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 20px; }
.data-card span { color: var(--muted); font-size: 14px; }
.data-card strong { display: block; margin-top: 10px; font-size: 30px; }
.data-card p { margin-top: 8px; color: var(--muted); }
.list-wrap { display: grid; gap: 16px; }
.list-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 18px; }
.card-main { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; }
.code { margin-bottom: 8px; color: var(--accent); font-size: 13px; font-weight: 800; }
.card-main h3 { font-size: 20px; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.tags span { padding: 4px 10px; border-radius: 7px; color: var(--accent); background: #eaf6f8; font-size: 13px; font-weight: 700; }
.status { display: inline-flex; align-items: center; height: 28px; padding: 0 10px; border-radius: 999px; font-size: 13px; font-weight: 700; flex-shrink: 0; }
.status-active { background: #eaf6f8; color: var(--accent); }
.status-done { background: #dcfce7; color: #15803d; }
.status-cancelled { background: #e5e7eb; color: #374151; }
.progress-block { margin-top: 14px; }
.progress-head, .progress-meta { display: flex; justify-content: space-between; align-items: center; }
.progress-head span, .progress-meta span { color: var(--muted); font-size: 14px; }
.progress-head strong { color: var(--accent); }
.progress-bar { height: 12px; border-radius: 999px; background: #e5eef1; overflow: hidden; margin: 8px 0; }
.progress-bar span { display: block; height: 100%; border-radius: inherit; background: var(--accent); }
.expired-tag { color: #b86b00; background: #fff3d7; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
.card-actions { display: flex; gap: 10px; margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--line); }
.primary, .secondary, .danger { min-height: 40px; padding: 0 18px; border-radius: 8px; font-weight: 800; cursor: pointer; font: inherit; }
.primary { border: 0; color: #fff; background: var(--accent); }
.primary:hover { background: var(--accent-dark); }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
.danger { border: 0; color: #fff; background: #be123c; }
.danger:hover { background: #9f1239; }
.empty-state { min-height: 200px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); }
.empty-state strong { display: block; margin-bottom: 8px; color: var(--ink); font-size: 18px; }
.empty-state .primary { margin-top: 12px; }

@media (max-width: 860px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 620px) { .data-grid { grid-template-columns: 1fr; } .card-main { flex-direction: column; } .card-actions { flex-wrap: wrap; } }
</style>
