<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { getGroupList, joinGroup, type GroupItem } from '@/api/group'

const router = useRouter()
const groups = ref<GroupItem[]>([])
const loading = ref(false)
const totalCount = ref(0)

const statusMap: Record<string, string> = {
  recruiting: '拼团中',
  success: '已成团',
  failed: '已失败',
  cancelled: '已取消',
}

const statusClassMap: Record<string, string> = {
  recruiting: 'status-doing',
  success: 'status-done',
  failed: 'status-cancelled',
  cancelled: 'status-cancelled',
}

async function loadGroups() {
  loading.value = true
  try {
    const res = await getGroupList({ page: 1, page_size: 20 })
    if (res.code === 200) {
      groups.value = res.data.results
      totalCount.value = res.data.count
    }
  } catch (e) {
    console.error('加载拼团列表失败', e)
  } finally {
    loading.value = false
  }
}

async function handleJoin(group: GroupItem) {
  try {
    const res = await joinGroup(group.team_id)
    if (res.code === 200) {
      alert('参与拼团成功')
      loadGroups()
    }
  } catch (e) {
    alert('参与失败')
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
    <section class="hero">
      <div class="hero-text">
        <p class="eyebrow">拼团项目</p>
        <h1>浏览拼团项目并判断是否值得参与</h1>
        <p>围绕谷子品类、参团人数和截止时间展示拼团状态，帮助您决定是否值得参与。</p>
      </div>
      <div class="hero-tools">
        <form class="search-box" @submit.prevent>
          <input type="search" placeholder="搜索谷子名称 / IP / 角色">
          <button type="button">搜索</button>
        </form>
        <div class="hero-actions">
          <button class="primary" type="button" @click="router.push('/group/publish')">发起拼团</button>
          <button class="secondary" type="button" @click="router.push('/group/my')">我的拼团</button>
        </div>
      </div>
    </section>

    <section class="group-layout">
      <aside class="filter-panel" aria-label="拼团筛选条件">
        <div class="section-head"><p class="eyebrow">筛选条件</p><h2>拼团筛选</h2></div>
        <label><span>拼团状态</span>
          <select><option>全部状态</option><option>拼团中</option><option>已成团</option><option>已失败</option></select>
        </label>
        <button class="primary full" type="button">应用筛选</button>
      </aside>

      <section class="list-panel">
        <div class="section-head list-head">
          <div><p class="eyebrow">拼团项目列表</p><h2>当前拼团</h2></div>
          <span>{{ totalCount }} 个项目</span>
        </div>

        <div v-if="loading" class="empty-state">
          <strong>加载中...</strong>
        </div>

        <div v-else-if="groups.length === 0" class="empty-state">
          <strong>暂无拼团</strong>
          <p>还没有拼团项目，快来发起第一个吧</p>
        </div>

        <article v-for="group in groups" :key="group.team_id" class="group-card">
          <div class="group-main">
            <div>
              <p class="code">拼团项目 {{ group.team_id }}</p>
              <h3>{{ group.product_name }}</h3>
              <div class="tags">
                <span>发起人：{{ group.creator_name }}</span>
              </div>
            </div>
            <strong class="price">¥{{ group.team_price }}/人</strong>
          </div>
          <div class="progress-block">
            <div class="progress-head">
              <span>当前人数 {{ group.current_count }} / {{ group.target_count }}</span>
              <strong>{{ getProgress(group) }}%</strong>
            </div>
            <div class="progress-bar">
              <span :style="{ width: getProgress(group) + '%' }"></span>
            </div>
            <div class="progress-meta">
              <span>剩余人数：{{ group.target_count - group.current_count }}人</span>
              <span>截止时间：{{ formatDate(group.deadline) }}</span>
            </div>
          </div>
          <div class="card-bottom">
            <span :class="['status', statusClassMap[group.status]]">{{ statusMap[group.status] }}</span>
            <span v-if="group.is_expired" class="status status-expired">已过期</span>
            <div class="card-actions">
              <button class="secondary" type="button" @click="router.push(`/group/${group.team_id}`)">查看</button>
              <button v-if="group.status === 'recruiting' && !group.is_expired" class="primary" type="button" @click="handleJoin(group)">参与</button>
            </div>
          </div>
        </article>
      </section>

      <aside class="right-panel" aria-label="我的拼团状态">
        <section class="state-card">
          <div class="section-head"><p class="eyebrow">我的拼团</p><h2>状态统计</h2></div>
          <div class="state-grid">
            <div><span>总拼团数</span><strong>{{ totalCount }}</strong></div>
          </div>
          <button class="primary full" type="button" @click="router.push('/group/my')">查看全部拼团记录</button>
        </section>
      </aside>
    </section>
  </main>
</template>

<style scoped>
.page { width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.hero {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(420px, 540px);
  gap: 28px; align-items: center; padding: 34px; border-radius: 10px; color: #fff;
  background: linear-gradient(rgba(10,74,90,0.88), rgba(10,74,90,0.92)),
    url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80") center/cover;
  box-shadow: var(--shadow);
}
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 40px; line-height: 1.16; }
.hero-text p:last-child { max-width: 660px; margin-top: 14px; color: rgba(255,255,255,0.84); line-height: 1.8; }
.hero-tools { display: grid; gap: 12px; }
.search-box { display: grid; grid-template-columns: minmax(0, 1fr) 92px; gap: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.28); border-radius: 10px; background: rgba(255,255,255,0.14); }
input, select { width: 100%; height: 44px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; color: var(--ink); background: #fff; outline: none; font: inherit; }
.search-box input { border: 0; }
.primary, .secondary, .search-box button { min-height: 44px; border-radius: 8px; font-weight: 800; cursor: pointer; font: inherit; }
.primary, .search-box button { border: 0; color: #fff; background: var(--accent); }
.primary:hover, .search-box button:hover { background: var(--accent-dark); }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
.hero-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.group-layout { display: grid; grid-template-columns: 250px minmax(0, 1fr) 280px; gap: 20px; margin-top: 20px; }
.filter-panel, .list-panel, .state-card, .group-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.filter-panel { align-self: start; display: grid; gap: 14px; padding: 20px; }
.section-head { margin-bottom: 14px; }
.section-head .eyebrow { color: var(--accent); }
h2 { font-size: 23px; }
label { display: grid; gap: 8px; color: var(--muted); font-size: 14px; }
.full { width: 100%; }
.list-panel { display: grid; gap: 16px; padding: 22px; }
.list-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.list-head span { color: var(--muted); font-size: 14px; }
.group-card { display: grid; gap: 16px; padding: 18px; box-shadow: none; }
.group-main { display: flex; justify-content: space-between; gap: 18px; align-items: flex-start; }
.code { margin-bottom: 8px; color: var(--accent); font-size: 13px; font-weight: 800; }
.group-main h3 { font-size: 20px; line-height: 1.35; }
.price { flex: 0 0 auto; color: var(--accent); font-size: 24px; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.tags span { padding: 6px 10px; border-radius: 7px; color: var(--accent); background: #eaf6f8; font-size: 13px; font-weight: 800; }
.progress-block { display: grid; gap: 8px; }
.progress-head, .progress-meta, .card-bottom { display: flex; justify-content: space-between; gap: 12px; align-items: center; }
.progress-head span, .progress-meta span { color: var(--muted); font-size: 14px; }
.progress-head strong { color: var(--accent); }
.progress-bar { height: 12px; border-radius: 999px; background: #e5eef1; overflow: hidden; }
.progress-bar span { display: block; height: 100%; border-radius: inherit; background: var(--accent); }
.status { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 13px; font-weight: 800; }
.status-doing { color: var(--accent); background: #eaf6f8; }
.status-done { color: #1f7a4d; background: #e8f7ef; }
.status-cancelled { color: #6b7280; background: #f3f4f6; }
.status-expired { color: #b86b00; background: #fff3d7; }
.card-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 110px)); gap: 10px; }
.right-panel { align-self: start; display: grid; gap: 16px; }
.state-card { padding: 18px; }
.state-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-bottom: 14px; }
.state-grid div { padding: 12px; border-radius: 8px; background: var(--soft); }
.state-grid span { display: block; color: var(--muted); font-size: 13px; }
.state-grid strong { display: block; margin-top: 8px; font-size: 22px; }
.empty-state { min-height: 200px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); }
.empty-state strong { display: block; margin-bottom: 8px; color: var(--ink); font-size: 18px; }

@media (max-width: 1120px) {
  .group-layout { grid-template-columns: 240px minmax(0, 1fr); }
  .right-panel { grid-column: 1 / -1; }
}
@media (max-width: 860px) {
  .hero, .group-layout { grid-template-columns: 1fr; }
}
@media (max-width: 620px) {
  .page { width: min(100% - 20px, 1240px); }
  .hero, .list-panel { padding: 20px; }
  h1 { font-size: 30px; }
  .search-box, .hero-actions, .group-main, .progress-head, .progress-meta, .card-bottom, .card-actions, .state-grid { grid-template-columns: 1fr; }
  .group-main, .progress-head, .progress-meta, .card-bottom { align-items: flex-start; flex-direction: column; }
}
</style>
