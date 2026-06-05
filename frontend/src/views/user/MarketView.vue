<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { getMarketList, getMyListings, type MarketItem } from '@/api/market'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const router = useRouter()
const listings = ref<MarketItem[]>([])
const myListings = ref<MarketItem[]>([])
const loading = ref(false)
const totalCount = ref(0)
const myStats = ref({
  total: 0,
  active: 0,
  sold: 0,
  cancelled: 0,
})

const statusMap: Record<string, string> = {
  active: '在售',
  locked: '锁定',
  sold: '已售',
  cancelled: '已取消',
  removed: '已下架',
}

// 搜索和筛选条件
const searchQuery = ref('')
const filters = reactive({
  ip_name: '',
  character_name: '',
  category: '',
  price_range: '',
  min_price: undefined as number | undefined,
  max_price: undefined as number | undefined,
  sort: 'default',
})

// 品类映射
const categoryMap: Record<string, string> = {
  '手办': 'figure',
  '徽章': 'badge',
  '海报': 'poster',
  '亚克力': 'acrylic',
  '玩偶': 'doll',
  '卡片': 'card',
  '其他': 'other',
}

// 价格区间映射
const priceRangeMap: Record<string, { min?: number; max?: number }> = {
  '0 至 50': { min: 0, max: 50 },
  '50 至 100': { min: 50, max: 100 },
  '100 至 300': { min: 100, max: 300 },
  '300 以上': { min: 300 },
}

async function loadListings() {
  loading.value = true
  try {
    const params: any = {
      page: 1,
      page_size: 20,
    }

    // 应用价格筛选
    if (filters.price_range && priceRangeMap[filters.price_range]) {
      const range = priceRangeMap[filters.price_range]
      if (range.min !== undefined) params.min_price = range.min
      if (range.max !== undefined) params.max_price = range.max
    }

    // 应用自定义价格
    if (filters.min_price !== undefined && filters.min_price > 0) {
      params.min_price = filters.min_price
    }
    if (filters.max_price !== undefined && filters.max_price > 0) {
      params.max_price = filters.max_price
    }

    // 应用 IP 名称筛选
    if (filters.ip_name) {
      params.ip_name = filters.ip_name
    }

    // 应用角色名称筛选
    if (filters.character_name) {
      params.character_name = filters.character_name
    }

    // 应用品类筛选
    if (filters.category) {
      params.category = categoryMap[filters.category] || filters.category
    }

    // 应用排序
    if (filters.sort !== 'default') {
      params.sort = filters.sort
    }

    const res = await getMarketList(params)
    if (res.code === 200) {
      listings.value = res.data.results
      totalCount.value = res.data.count
    }
  } catch (e) {
    console.error('加载挂单列表失败', e)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  // 搜索时将搜索词赋给ip_name进行模糊搜索
  filters.ip_name = searchQuery.value
  loadListings()
}

function applyFilters() {
  loadListings()
}

function resetFilters() {
  filters.ip_name = ''
  filters.character_name = ''
  filters.category = ''
  filters.price_range = ''
  filters.min_price = undefined
  filters.max_price = undefined
  filters.sort = 'default'
  loadListings()
}

async function loadMyListings() {
  try {
    const res = await getMyListings({ page: 1, page_size: 20 })
    if (res.code === 200) {
      myListings.value = res.data.results
      if (res.data.stats) {
        myStats.value = res.data.stats
      }
    }
  } catch (e) {
    console.error('加载我的挂单失败', e)
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

onMounted(() => {
  loadListings()
  loadMyListings()
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="market-hero">
      <div class="hero-title">
        <p class="eyebrow">交易市场</p>
        <h1>寻找谷子也可以交易自己的谷子</h1>
        <p>按谷子、IP、角色、品类等条件浏览在售谷子列表，结合参考价和信誉度辅助交易决策。</p>
      </div>
      <div class="search-area">
        <form class="search-box" @submit.prevent="handleSearch">
          <input v-model="searchQuery" type="search" placeholder="搜索谷子 / IP / 角色 / 品类">
          <button type="submit">搜索</button>
        </form>
        <div class="hero-actions">
          <button class="primary" type="button" @click="router.push('/market/publish')">发布在售谷子</button>
          <button class="secondary" type="button" @click="router.push('/market/my')">我的发布</button>
        </div>
        <div class="hot-words">
          <span>热门搜索：</span>
          <button type="button">精灵宝可梦</button>
          <button type="button">盲盒</button>
          <button type="button">亚克力</button>
          <button type="button">徽章</button>
        </div>
      </div>
    </section>

    <section class="market-layout">
      <aside class="filter-panel" aria-label="筛选条件">
        <div class="section-head">
          <p class="eyebrow">筛选条件</p>
          <h2>精准确认</h2>
        </div>
        <label><span>IP 名称</span><input v-model="filters.ip_name" type="text" placeholder="如：原神、明日方舟"></label>
        <label><span>角色名称</span><input v-model="filters.character_name" type="text" placeholder="输入角色名称"></label>
        <label><span>谷子品类</span>
          <select v-model="filters.category">
            <option value="">全部品类</option>
            <option>手办</option>
            <option>徽章</option>
            <option>海报</option>
            <option>亚克力</option>
            <option>玩偶</option>
            <option>卡片</option>
            <option>其他</option>
          </select>
        </label>
        <label><span>价格区间</span>
          <select v-model="filters.price_range">
            <option value="">不限价格</option>
            <option>0 至 50</option>
            <option>50 至 100</option>
            <option>100 至 300</option>
            <option>300 以上</option>
          </select>
        </label>
        <div class="price-custom">
          <input v-model.number="filters.min_price" type="number" placeholder="最低价">
          <input v-model.number="filters.max_price" type="number" placeholder="最高价">
        </div>
        <label><span>排列方式</span>
          <select v-model="filters.sort">
            <option value="default">默认排序</option>
            <option value="price_asc">价格低到高</option>
            <option value="price_desc">价格高到低</option>
            <option value="time">发布时间</option>
          </select>
        </label>
        <div class="filter-actions">
          <button class="primary full" type="button" @click="applyFilters">应用筛选</button>
          <button class="secondary full" type="button" @click="resetFilters">重置筛选</button>
        </div>
      </aside>

      <section class="goods-panel">
        <div class="section-head list-head">
          <div>
            <p class="eyebrow">在售谷子列表</p>
            <h2>当前挂牌</h2>
          </div>
          <span>{{ totalCount }} 个谷子</span>
        </div>

        <div v-if="loading" class="empty-state">
          <strong>加载中...</strong>
        </div>

        <div v-else-if="listings.length === 0" class="empty-state">
          <strong>暂无挂单</strong>
          <p>还没有人发布谷子，快来第一个发布吧</p>
        </div>

        <div v-else class="sale-list">
          <article v-for="item in listings" :key="item.listing_id" class="sale-card">
            <img :src="item.images?.[0]?.image_url || item.product_image || '/default-product.png'" :alt="item.product_name">
            <div class="sale-info">
              <div class="sale-title">
                <h3>{{ item.product_name }}</h3>
                <span class="listing-status">{{ statusMap[item.status] || item.status }}</span>
              </div>
              <p class="desc">{{ item.description || '暂无描述' }}</p>
              <div class="price-line">
                <strong>售价：¥{{ item.price }}</strong>
              </div>
              <div class="meta-grid">
                <div><span>数量</span><strong>{{ item.quantity }}</strong></div>
                <div><span>卖家</span><strong>{{ item.seller_name }}</strong></div>
                <div><span>发布时间</span><strong>{{ formatDate(item.created_at) }}</strong></div>
                <div><span>挂单编号</span><strong>{{ item.listing_id }}</strong></div>
              </div>
              <div class="card-actions">
                <button class="secondary" type="button" @click="router.push(`/market/${item.listing_id}`)">查看详情</button>
                <button v-if="userStore.userInfo?.id !== item.seller_id" class="primary" type="button" @click="router.push(`/my-orders/create?listing=${item.listing_id}`)">发起交易</button>
                <span v-else class="self-listing-hint">这是您发布的商品</span>
              </div>
            </div>
          </article>
        </div>
      </section>

      <aside class="assist-panel" aria-label="交易辅助">
        <section class="assist-card">
          <div class="section-head">
            <p class="eyebrow">我的发布</p><h2>发布状态</h2>
          </div>
          <div class="publish-row"><span>在售谷子</span><strong>{{ myStats.active }}</strong></div>
          <div class="publish-row"><span>已售谷子</span><strong>{{ myStats.sold }}</strong></div>
          <div class="publish-row"><span>已取消</span><strong>{{ myStats.cancelled }}</strong></div>
          <div class="publish-row"><span>总发布</span><strong>{{ myStats.total }}</strong></div>
        </section>
        <section class="assist-card safe-card">
          <div class="section-head"><p class="eyebrow">安全与提示</p><h2>交易前确认</h2></div>
          <ul>
            <li>查看卖家信誉和历史成交</li>
            <li>确认谷子状态与瑕疵说明</li>
            <li>参考近期成交价做决策</li>
            <li>使用平台担保支付</li>
          </ul>
        </section>
      </aside>
    </section>
  </main>
</template>

<style scoped>
.page { width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.market-hero {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(420px, 520px);
  gap: 28px; align-items: center; padding: 36px; border-radius: 10px; color: #fff;
  background: linear-gradient(rgba(10,74,90,0.88), rgba(10,74,90,0.92)),
    url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80") center/cover;
  box-shadow: var(--shadow);
}
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 40px; line-height: 1.16; }
.hero-title p:last-child { max-width: 650px; margin-top: 14px; color: rgba(255,255,255,0.84); line-height: 1.8; }
.search-area { display: grid; gap: 12px; }
.search-box { display: grid; grid-template-columns: minmax(0, 1fr) 92px; gap: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.28); border-radius: 10px; background: rgba(255,255,255,0.14); }
input, select { width: 100%; height: 44px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; color: var(--ink); background: #fff; outline: none; font: inherit; }
.search-box input { border: 0; }
.primary, .secondary, .search-box button { min-height: 44px; border-radius: 8px; font-weight: 800; cursor: pointer; font: inherit; }
.primary, .search-box button { border: 0; color: #fff; background: var(--accent); }
.primary:hover, .search-box button:hover { background: var(--accent-dark); }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
.hero-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.hot-words { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; color: rgba(255,255,255,0.82); font-size: 14px; }
.hot-words button { min-height: 30px; border: 1px solid rgba(255,255,255,0.28); border-radius: 7px; color: #fff; background: rgba(255,255,255,0.12); cursor: pointer; font: inherit; }
.market-layout { display: grid; grid-template-columns: 250px minmax(0, 1fr) 280px; gap: 20px; margin-top: 20px; }
.filter-panel, .goods-panel, .assist-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.filter-panel { align-self: start; display: grid; gap: 14px; padding: 20px; }
.section-head { margin-bottom: 14px; }
.section-head .eyebrow { color: var(--accent); }
h2 { font-size: 23px; }
label { display: grid; gap: 8px; color: var(--muted); font-size: 14px; }
.price-custom { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.filter-actions { display: grid; gap: 8px; }
.full { width: 100%; }
.goods-panel { padding: 22px; }
.list-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.list-head span { color: var(--muted); font-size: 14px; }
.sale-list { display: grid; gap: 16px; }
.sale-card { display: grid; grid-template-columns: 260px minmax(0, 1fr); gap: 18px; padding: 16px; border: 1px solid var(--line); border-radius: 10px; background: var(--soft); }
.sale-card img { width: 100%; height: 300px; object-fit: contain; border-radius: 8px; background: #fff; }
.sale-info { display: grid; gap: 14px; }
.sale-title { display: flex; justify-content: space-between; gap: 12px; align-items: start; }
.sale-title h3 { font-size: 22px; }
.listing-status { padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; background: #eaf6f8; color: var(--accent); }
.desc { color: var(--muted); line-height: 1.7; }
.price-line { display: flex; flex-wrap: wrap; gap: 14px; align-items: baseline; }
.price-line strong { color: var(--accent); font-size: 24px; }
.meta-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.meta-grid div { padding: 12px; border-radius: 8px; background: #fff; }
.meta-grid span { display: block; color: var(--muted); font-size: 13px; }
.meta-grid strong { display: block; margin-top: 8px; font-size: 14px; }
.card-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.self-listing-hint { display: flex; align-items: center; justify-content: center; color: var(--muted); font-size: 13px; }
.assist-panel { align-self: start; display: grid; gap: 16px; }
.assist-card { padding: 18px; }
.publish-row { padding: 12px; border-radius: 8px; background: var(--soft); }
.publish-row span { display: block; color: var(--muted); font-size: 13px; }
.publish-row strong { display: block; margin-top: 8px; font-size: 22px; }
.safe-card ul { margin: 0; padding-left: 18px; color: var(--muted); line-height: 1.9; }
.empty-state { min-height: 200px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); }
.empty-state strong { display: block; margin-bottom: 8px; color: var(--ink); font-size: 18px; }

@media (max-width: 1100px) {
  .market-layout { grid-template-columns: 240px minmax(0, 1fr); }
  .assist-panel { grid-column: 1 / -1; grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 860px) {
  .market-hero, .market-layout, .sale-card, .assist-panel { grid-template-columns: 1fr; }
}
@media (max-width: 620px) {
  .page { width: min(100% - 20px, 1240px); }
  .market-hero, .goods-panel { padding: 20px; }
  h1 { font-size: 30px; }
  .search-box, .hero-actions, .price-custom, .meta-grid, .card-actions { grid-template-columns: 1fr; }
}
</style>
