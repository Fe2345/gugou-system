<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { getSwapList, type SwapItem } from '@/api/swap'

const router = useRouter()
const swaps = ref<SwapItem[]>([])
const loading = ref(false)
const totalCount = ref(0)
const searchQuery = ref('')
const statusFilter = ref('')

const statusMap: Record<string, string> = {
  active: '可交易',
  matched: '匹配中',
  completed: '已完成',
  cancelled: '已取消',
  expired: '已过期',
}

const statusClassMap: Record<string, string> = {
  active: 'status-open',
  matched: 'status-matching',
  completed: 'status-done',
  cancelled: 'status-cancelled',
  expired: 'status-cancelled',
}

async function loadSwaps() {
  loading.value = true
  try {
    const res = await getSwapList({ page: 1, page_size: 50 })
    if (res.code === 200) {
      let results = res.data.results
      // 前端搜索过滤
      if (searchQuery.value.trim()) {
        const q = searchQuery.value.trim().toLowerCase()
        results = results.filter(s =>
          s.offered_asset_name.toLowerCase().includes(q) ||
          s.owner_name.toLowerCase().includes(q) ||
          s.exchange_id.toLowerCase().includes(q)
        )
      }
      // 状态筛选
      if (statusFilter.value) {
        results = results.filter(s => s.status === statusFilter.value)
      }
      swaps.value = results
      totalCount.value = results.length
    }
  } catch (e) {
    console.error('加载换物列表失败', e)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  loadSwaps()
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

onMounted(() => {
  loadSwaps()
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="hero">
      <div class="hero-text">
        <p class="eyebrow">交换交易</p>
        <h1>发布交换需求与浏览交换列表</h1>
        <p>围绕「我提供什么」和「我想换什么」展示交换需求，帮助你快速找到合适的交易伙伴。</p>
      </div>
      <div class="hero-tools">
        <form class="search-box" @submit.prevent="handleSearch">
          <input v-model="searchQuery" type="search" placeholder="搜索谷子名称 / IP / 角色">
          <button type="submit">搜索</button>
        </form>
        <div class="hero-actions">
          <button class="primary" type="button" @click="router.push('/swap/publish')">发布交换</button>
          <button class="secondary" type="button" @click="router.push('/swap/my')">我的交换</button>
        </div>
      </div>
    </section>

    <section class="swap-layout">
      <aside class="filter-panel" aria-label="交换筛选条件">
        <div class="section-head">
          <p class="eyebrow">筛选条件</p><h2>交换筛选</h2>
        </div>
        <label><span>交换状态</span>
          <select v-model="statusFilter">
            <option value="">全部状态</option>
            <option value="active">可交易</option>
            <option value="matched">匹配中</option>
            <option value="completed">已完成</option>
          </select>
        </label>
        <button class="primary full" type="button" @click="loadSwaps">应用筛选</button>
      </aside>

      <section class="list-panel">
        <div class="section-head list-head">
          <div><p class="eyebrow">交换广场</p><h2>最新交换列表</h2></div>
          <span>{{ totalCount }} 个交换</span>
        </div>

        <div v-if="loading" class="empty-state">
          <strong>加载中...</strong>
        </div>

        <div v-else-if="swaps.length === 0" class="empty-state">
          <strong>暂无换物请求</strong>
          <p>还没有人发布交换需求，快来第一个发布吧</p>
        </div>

        <article v-for="swap in swaps" :key="swap.exchange_id" class="swap-card">
          <div class="card-meta">
            <strong>交换编号 {{ swap.exchange_id }}</strong>
            <span>发起人：{{ swap.owner_name }} · {{ formatDate(swap.created_at) }}</span>
          </div>
          <div class="compare">
            <section>
              <p class="label">我提供</p>
              <h3>{{ swap.offered_asset_name }}</h3>
              <ul>
                <li v-if="swap.target_condition">期望条件：{{ swap.target_condition }}</li>
              </ul>
            </section>
            <div class="arrow">→</div>
            <section>
              <p class="label want">我想换</p>
              <h3>{{ swap.target_condition || '不限' }}</h3>
            </section>
          </div>
          <div class="card-bottom">
            <span :class="['status', statusClassMap[swap.status]]">{{ statusMap[swap.status] }}</span>
            <div class="card-actions">
              <button class="secondary" type="button" @click="router.push(`/swap/${swap.exchange_id}`)">查看详情</button>
              <button v-if="swap.status === 'active'" class="primary" type="button" @click="router.push(`/swap/${swap.exchange_id}`)">发起交换</button>
            </div>
          </div>
        </article>
      </section>

      <aside class="right-panel" aria-label="我的交换状态">
        <section class="state-card">
          <div class="section-head"><p class="eyebrow">我的交换</p><h2>状态统计</h2></div>
          <div class="state-grid">
            <div><span>总交换数</span><strong>{{ totalCount }}</strong></div>
          </div>
          <button class="primary full" type="button" @click="router.push('/swap/my')">查看全部交换记录</button>
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
.swap-layout { display: grid; grid-template-columns: 250px minmax(0, 1fr) 280px; gap: 20px; margin-top: 20px; }
.filter-panel, .list-panel, .state-card, .swap-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.filter-panel { align-self: start; display: grid; gap: 14px; padding: 20px; }
.section-head { margin-bottom: 14px; }
.section-head .eyebrow { color: var(--accent); }
h2 { font-size: 23px; }
label { display: grid; gap: 8px; color: var(--muted); font-size: 14px; }
.full { width: 100%; }
.list-panel { display: grid; gap: 16px; padding: 22px; }
.list-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.list-head span { color: var(--muted); font-size: 14px; }
.swap-card { display: grid; gap: 16px; padding: 18px; box-shadow: none; }
.card-meta { display: flex; justify-content: space-between; gap: 14px; align-items: center; color: var(--muted); }
.card-meta strong { color: var(--ink); font-size: 18px; }
.compare { display: grid; grid-template-columns: minmax(0, 1fr) 54px minmax(0, 1fr); gap: 14px; align-items: stretch; }
.compare section { padding: 16px; border-radius: 10px; background: var(--soft); }
.label { margin-bottom: 8px; color: var(--accent); font-size: 13px; font-weight: 800; }
.label.want { color: #6d4bc2; }
.compare h3 { font-size: 18px; line-height: 1.35; }
.compare ul { margin: 12px 0 0; padding-left: 18px; color: var(--muted); line-height: 1.8; }
.arrow { display: grid; place-items: center; border-radius: 10px; color: #172126; background: var(--gold); font-weight: 900; }
.card-bottom { display: flex; justify-content: space-between; gap: 12px; align-items: center; }
.status { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 13px; font-weight: 800; }
.status-open { color: #1f7a4d; background: #e8f7ef; }
.status-matching { color: var(--accent); background: #eaf6f8; }
.status-done { color: #1f7a4d; background: #e8f7ef; }
.status-cancelled { color: #6b7280; background: #f3f4f6; }
.card-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 120px)); gap: 10px; }
.right-panel { align-self: start; display: grid; gap: 16px; }
.state-card { padding: 18px; }
.state-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-bottom: 14px; }
.state-grid div { padding: 12px; border-radius: 8px; background: var(--soft); }
.state-grid span { display: block; color: var(--muted); font-size: 13px; }
.state-grid strong { display: block; margin-top: 8px; font-size: 22px; }
.empty-state { min-height: 200px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); }
.empty-state strong { display: block; margin-bottom: 8px; color: var(--ink); font-size: 18px; }

@media (max-width: 1120px) {
  .swap-layout { grid-template-columns: 240px minmax(0, 1fr); }
  .right-panel { grid-column: 1 / -1; }
}
@media (max-width: 860px) {
  .hero, .swap-layout, .compare { grid-template-columns: 1fr; }
  .arrow { min-height: 42px; }
}
@media (max-width: 620px) {
  .page { width: min(100% - 20px, 1240px); }
  .hero, .list-panel { padding: 20px; }
  h1 { font-size: 30px; }
  .search-box, .hero-actions, .card-bottom, .card-actions, .state-grid { grid-template-columns: 1fr; }
  .card-meta { align-items: flex-start; flex-direction: column; }
}
</style>
