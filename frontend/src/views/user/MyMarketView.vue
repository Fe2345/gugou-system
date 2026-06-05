<script setup lang="ts">
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { getMyListings, cancelListing, type MarketItem } from '@/api/market'

const router = useRouter()
const listings = ref<MarketItem[]>([])
const allListings = ref<MarketItem[]>([])
const loading = ref(false)
const searchQuery = ref('')
const myStats = ref({
  total: 0,
  active: 0,
  sold: 0,
  cancelled: 0,
})

const statusMap: Record<string, { text: string; cls: string }> = {
  active: { text: '在售', cls: 'status-active' },
  locked: { text: '锁定', cls: 'status-locked' },
  sold: { text: '已售', cls: 'status-sold' },
  cancelled: { text: '已取消', cls: 'status-cancelled' },
  removed: { text: '已下架', cls: 'status-cancelled' },
}

async function loadListings() {
  loading.value = true
  try {
    const res = await getMyListings({ page: 1, page_size: 50 })
    if (res.code === 200) {
      allListings.value = res.data.results
      if (res.data.stats) {
        myStats.value = res.data.stats
      }
      filterListings()
    }
  } catch (e) {
    console.error('加载我的挂单失败', e)
  } finally {
    loading.value = false
  }
}

function filterListings() {
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    listings.value = allListings.value.filter(l =>
      l.product_name.toLowerCase().includes(q) ||
      l.listing_id.toLowerCase().includes(q)
    )
  } else {
    listings.value = allListings.value
  }
}

function handleSearch() {
  filterListings()
}

async function handleCancel(item: MarketItem) {
  try {
    await ElMessageBox.confirm(`确认取消挂单 ${item.listing_id}？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  try {
    const res = await cancelListing(item.listing_id)
    if (res.code === 200) {
      ElMessage.success('取消成功')
      loadListings()
    } else {
      ElMessage.error(res.message || '取消失败')
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '取消失败')
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadListings()
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">交易市场</p>
        <h1>我的发布</h1>
        <p>管理已发布的谷子挂单，查看状态与操作</p>
      </div>
      <div class="head-actions">
        <button class="secondary" type="button" @click="router.push('/market')">返回市场</button>
        <button class="primary" type="button" @click="router.push('/market/publish')">发布新谷子</button>
      </div>
    </section>

    <section class="search-section">
      <form class="search-box" @submit.prevent="handleSearch">
        <input v-model="searchQuery" type="search" placeholder="搜索商品名称 / 挂单编号">
        <button type="submit">搜索</button>
      </form>
    </section>

    <section class="data-grid">
      <article class="data-card">
        <span>总挂单</span><strong>{{ myStats.total }}</strong><p>全部发布</p>
      </article>
      <article class="data-card">
        <span>在售</span><strong>{{ myStats.active }}</strong><p>展示中</p>
      </article>
      <article class="data-card">
        <span>已售</span><strong>{{ myStats.sold }}</strong><p>交易完成</p>
      </article>
      <article class="data-card">
        <span>已取消</span><strong>{{ myStats.cancelled }}</strong><p>已下架</p>
      </article>
    </section>

    <div v-if="loading" class="empty-state"><strong>加载中...</strong></div>
    <div v-else-if="listings.length === 0" class="empty-state">
      <strong>暂无挂单</strong>
      <p>还没有发布谷子，快去发布吧</p>
      <button class="primary" type="button" @click="router.push('/market/publish')">去发布</button>
    </div>
    <section v-else class="list-wrap">
      <article v-for="item in listings" :key="item.listing_id" class="list-card">
        <div class="card-main">
          <div>
            <p class="code">挂单 {{ item.listing_id }}</p>
            <h3>{{ item.product_name }}</h3>
            <p class="desc">{{ item.description || '暂无描述' }}</p>
          </div>
          <strong class="price">¥{{ item.price }}</strong>
        </div>
        <div class="card-meta">
          <span>数量: {{ item.quantity }}</span>
          <span :class="['status', statusMap[item.status]?.cls]">{{ statusMap[item.status]?.text }}</span>
          <span>{{ formatDate(item.created_at) }}</span>
        </div>
        <div class="card-actions">
          <button class="secondary" type="button" @click="router.push(`/market/${item.listing_id}`)">查看详情</button>
          <button v-if="item.status === 'active'" class="danger" type="button" @click="handleCancel(item)">取消挂单</button>
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
.card-main { display: flex; justify-content: space-between; gap: 18px; align-items: flex-start; }
.code { margin-bottom: 8px; color: var(--accent); font-size: 13px; font-weight: 800; }
.card-main h3 { font-size: 20px; }
.desc { margin-top: 6px; color: var(--muted); font-size: 14px; }
.price { color: var(--accent); font-size: 24px; flex-shrink: 0; }
.card-meta { display: flex; gap: 16px; align-items: center; margin-top: 14px; color: var(--muted); font-size: 14px; }
.status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status-active { background: #eaf6f8; color: var(--accent); }
.status-locked { background: #ffedd5; color: #c2410c; }
.status-sold { background: #dcfce7; color: #15803d; }
.status-cancelled { background: #e5e7eb; color: #374151; }
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
@media (max-width: 620px) { .data-grid { grid-template-columns: 1fr; } .card-main { flex-direction: column; } .card-actions { flex-direction: column; } }
</style>
