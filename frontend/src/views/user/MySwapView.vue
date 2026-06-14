<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { getMySwaps, cancelSwap, completeSwap, type SwapItem } from '@/api/swap'

const router = useRouter()
const swaps = ref<SwapItem[]>([])
const allSwaps = ref<SwapItem[]>([])
const loading = ref(false)
const totalCount = ref(0)
const searchQuery = ref('')

const statusMap: Record<string, { text: string; cls: string }> = {
  active: { text: '可交易', cls: 'status-active' },
  matched: { text: '匹配中', cls: 'status-matched' },
  completed: { text: '已完成', cls: 'status-done' },
  cancelled: { text: '已取消', cls: 'status-cancelled' },
  expired: { text: '已过期', cls: 'status-cancelled' },
}

async function loadSwaps() {
  loading.value = true
  try {
    const res = await getMySwaps({ page: 1, page_size: 50 })
    if (res.code === 200) {
      allSwaps.value = res.data.results
      filterSwaps()
    }
  } catch (e) {
    console.error('加载我的换物失败', e)
  } finally {
    loading.value = false
  }
}

function filterSwaps() {
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    swaps.value = allSwaps.value.filter(s =>
      s.offered_asset_name.toLowerCase().includes(q) ||
      s.exchange_id.toLowerCase().includes(q)
    )
  } else {
    swaps.value = allSwaps.value
  }
  totalCount.value = swaps.value.length
}

function handleSearch() {
  filterSwaps()
}

async function handleCancel(item: SwapItem) {
  if (!confirm('确认取消此换物请求？')) return
  try {
    const res = await cancelSwap(item.exchange_id)
    if (res.code === 200) {
      alert('已取消')
      loadSwaps()
    } else {
      alert(res.message || '取消失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '取消失败')
  }
}

async function handleComplete(item: SwapItem) {
  if (!confirm('确认完成此换物？')) return
  try {
    const res = await completeSwap(item.exchange_id)
    if (res.code === 200) {
      alert('已完成')
      loadSwaps()
    } else {
      alert(res.message || '操作失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '操作失败')
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadSwaps()
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">换物市场</p>
        <h1>我的换物</h1>
        <p>管理已发布的换物请求，查看匹配状态</p>
      </div>
      <div class="head-actions">
        <button class="secondary" type="button" @click="router.push('/swap')">返回换物</button>
        <button class="primary" type="button" @click="router.push('/swap/publish')">发布换物</button>
      </div>
    </section>

    <section class="search-section">
      <form class="search-box" @submit.prevent="handleSearch">
        <input v-model="searchQuery" type="search" placeholder="搜索换物名称 / 编号">
        <button type="submit">搜索</button>
      </form>
    </section>

    <section class="data-grid">
      <article class="data-card">
        <span>总请求</span><strong>{{ totalCount }}</strong><p>全部换物</p>
      </article>
      <article class="data-card">
        <span>可交易</span><strong>{{ swaps.filter(s => s.status === 'active').length }}</strong><p>等待匹配</p>
      </article>
      <article class="data-card">
        <span>匹配中</span><strong>{{ swaps.filter(s => s.status === 'matched').length }}</strong><p>确认中</p>
      </article>
      <article class="data-card">
        <span>已完成</span><strong>{{ swaps.filter(s => s.status === 'completed').length }}</strong><p>交换完成</p>
      </article>
    </section>

    <div v-if="loading" class="empty-state"><strong>加载中...</strong></div>
    <div v-else-if="swaps.length === 0" class="empty-state">
      <strong>暂无换物请求</strong>
      <p>还没有发布换物，快去发布吧</p>
      <button class="primary" type="button" @click="router.push('/swap/publish')">去发布</button>
    </div>
    <section v-else class="list-wrap">
      <article v-for="item in swaps" :key="item.exchange_id" class="list-card">
        <div class="card-main">
          <div>
            <p class="code">换物 {{ item.exchange_id }}</p>
            <h3>{{ item.offered_asset_name }}</h3>
            <p class="desc">目标条件：{{ item.target_condition || '不限' }}</p>
          </div>
          <span :class="['status', statusMap[item.status]?.cls]">{{ statusMap[item.status]?.text }}</span>
        </div>
        <div class="card-meta">
          <span>发起人：{{ item.owner_name }}</span>
          <span>{{ formatDate(item.created_at) }}</span>
        </div>
        <div class="card-actions">
          <button class="secondary" type="button" @click="router.push(`/swap/${item.exchange_id}`)">查看详情</button>
          <button v-if="item.status === 'matched'" class="primary" type="button" @click="handleComplete(item)">确认完成</button>
          <button v-if="item.status === 'active' || item.status === 'matched'" class="danger" type="button" @click="handleCancel(item)">取消</button>
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
.search-section { margin-bottom: 20px; }
.search-box { display: flex; gap: 10px; }
.search-box input { flex: 1; height: 44px; border: 1px solid var(--line); border-radius: 8px; padding: 0 14px; font: inherit; background: var(--panel); }
.search-box button { min-height: 44px; padding: 0 24px; border-radius: 8px; font-weight: 800; cursor: pointer; font: inherit; border: 0; color: #fff; background: var(--accent); }
.search-box button:hover { background: var(--accent-dark); }
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
.desc { margin-top: 6px; color: var(--muted); font-size: 14px; }
.status { display: inline-flex; align-items: center; height: 28px; padding: 0 10px; border-radius: 999px; font-size: 13px; font-weight: 700; flex-shrink: 0; }
.status-active { background: #eaf6f8; color: var(--accent); }
.status-matched { background: #ffedd5; color: #c2410c; }
.status-done { background: #dcfce7; color: #15803d; }
.status-cancelled { background: #e5e7eb; color: #374151; }
.card-meta { display: flex; gap: 16px; margin-top: 12px; color: var(--muted); font-size: 14px; }
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
@media (max-width: 620px) { .data-grid { grid-template-columns: 1fr; } .card-actions { flex-wrap: wrap; } }
</style>
