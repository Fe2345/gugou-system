<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { getMarketList, getMyListings, type MarketItem } from '@/api/market'

const router = useRouter()
const listings = ref<MarketItem[]>([])
const myListings = ref<MarketItem[]>([])
const loading = ref(false)
const totalCount = ref(0)
const myCount = ref(0)

const statusMap: Record<string, string> = {
  active: '在售',
  locked: '锁定',
  sold: '已售',
  cancelled: '已取消',
  removed: '已下架',
}

async function loadListings() {
  loading.value = true
  try {
    const res = await getMarketList({ page: 1, page_size: 20 })
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

async function loadMyListings() {
  try {
    const res = await getMyListings({ page: 1, page_size: 20 })
    if (res.code === 200) {
      myListings.value = res.data.results
      myCount.value = res.data.count
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
        <form class="search-box" @submit.prevent>
          <input type="search" placeholder="搜索谷子 / IP / 角色 / 品类">
          <button type="button">搜索</button>
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
        <label><span>IP 来源</span>
          <select><option>全部 IP</option><option>动漫</option><option>游戏</option><option>文学角色</option><option>影视</option></select>
        </label>
        <label><span>角色名称</span><input type="text" placeholder="输入角色名称"></label>
        <label><span>谷子品类</span>
          <select><option>全部品类</option><option>徽章</option><option>色纸</option><option>卡片</option><option>亚克力</option><option>明信片</option><option>挂件</option></select>
        </label>
        <label><span>价格区间</span>
          <select><option>不限价格</option><option>0 至 50</option><option>50 至 100</option><option>100 至 300</option><option>300 以上</option></select>
        </label>
        <div class="price-custom">
          <input type="number" placeholder="最低价">
          <input type="number" placeholder="最高价">
        </div>
        <label><span>排列方式</span>
          <select><option>默认排序</option><option>价格低到高</option><option>价格高到低</option><option>发布时间</option></select>
        </label>
        <button class="primary full" type="button">应用筛选</button>
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
            <img :src="item.images?.[0]?.image_url || 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80'" :alt="item.product_name">
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
                <button class="primary" type="button" @click="router.push(`/my-orders/create?listing=${item.listing_id}`)">发起交易</button>
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
          <div class="publish-row"><span>在售谷子</span><strong>{{ myCount }}</strong></div>
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
