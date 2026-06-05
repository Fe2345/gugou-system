<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { queryPrice, getHotPrices, getMyAssetPrices } from '@/api/pricing'
import { useUserStore } from '@/stores/user'
import type { PriceItem } from '@/types/pricing'

const userStore = useUserStore()
const route = useRoute()
const keyword = ref('')
const range = ref<'7d' | '30d' | '90d'>('30d')
const loading = ref(false)
const item = ref<PriceItem | null>(null)
const hotPrices = ref<PriceItem[]>([])
const myAssets = ref<(PriceItem & { quantity: number; acquirePrice: number | null })[]>([])
const selectedAssetId = ref<string | null>(null)

const categoryMap: Record<string, string> = {
  figure: '手办', badge: '徽章', poster: '海报/色纸', acrylic: '亚克力',
  doll: '玩偶', card: '卡片', other: '其他',
}
function categoryLabel(val: string) { return categoryMap[val] || val }

const rangeLabel = computed(() => {
  const map = { '7d': '近7天', '30d': '近30天', '90d': '近90天' }
  return map[range.value]
})

const chartPoints = computed(() => {
  if (!item.value?.trend?.length) return { polyline: '', points: [] as { cx: number; cy: number; label: string; price: number }[] }
  const data = item.value.trend
  const prices = data.map(d => d.price)
  const minP = Math.min(...prices) - 10
  const maxP = Math.max(...prices) + 10
  const rangeP = maxP - minP || 1
  const stepX = 790 / (data.length - 1)
  const pts = data.map((d, i) => {
    const cx = 70 + i * stepX
    const cy = 60 + (1 - (d.price - minP) / rangeP) * 280
    return { cx, cy, label: d.date, price: d.price }
  })
  const polyline = pts.map(p => `${p.cx},${p.cy}`).join(' ')
  return { polyline, points: pts, minP, maxP }
})

const gridLabels = computed(() => {
  if (!item.value?.trend?.length) return []
  const prices = item.value.trend.map(d => d.price)
  const minP = Math.min(...prices) - 10
  const maxP = Math.max(...prices) + 10
  const step = (maxP - minP) / 4
  return Array.from({ length: 5 }, (_, i) => Math.round(maxP - i * step))
})

const changeClass = computed(() => {
  if (!item.value) return ''
  return item.value.changePercent > 0 ? 'up' : item.value.changePercent < 0 ? 'down' : ''
})

const conclusionTexts = computed(() => {
  if (!item.value) return []
  const p = item.value
  const texts: string[] = []
  texts.push(`当前参考价为¥${p.currentPrice}，较近${range.value === '90d' ? '90日' : range.value === '30d' ? '30日' : '7日'}均值${p.currentPrice > p.avgPrice ? '略高' : p.currentPrice < p.avgPrice ? '略低' : '持平'}。`)
  if (p.changePercent > 0) {
    texts.push('谷子处于上升趋势中，短期存在小幅波动。')
    texts.push('若用户计划出售，当前价格水平较适合挂出。')
  } else if (p.changePercent < 0) {
    texts.push('谷子处于下降趋势中，短期内可能继续回调。')
    texts.push('若用户计划购入，可等待价格企稳后再出手。')
  } else {
    texts.push('谷子价格近期保持平稳，波动较小。')
  }
  if (p.currentPrice > p.avgPrice * 1.1) {
    texts.push('当前价格明显高于均值，需关注回调风险。')
  }
  return texts
})

async function handleSearch() {
  if (!keyword.value.trim()) return
  loading.value = true
  selectedAssetId.value = null
  const res = await queryPrice({ keyword: keyword.value, range: range.value })
  item.value = res.data
  loading.value = false
}

async function loadMyAssets() {
  if (!userStore.isLoggedIn) return
  try {
    const res = await getMyAssetPrices(range.value)
    myAssets.value = res.data || []
  } catch {
    myAssets.value = []
  }
}

function selectAsset(asset: PriceItem) {
  selectedAssetId.value = asset.id
  item.value = asset
}

function setRange(r: '7d' | '30d' | '90d') {
  range.value = r
  loadMyAssets()
  if (selectedAssetId.value) {
    const asset = myAssets.value.find(a => a.id === selectedAssetId.value)
    if (asset) {
      getMyAssetPrices(r).then(res => {
        const updated = (res.data || []).find(a => a.id === selectedAssetId.value)
        if (updated) item.value = updated
      })
      return
    }
  }
  handleSearch()
}

onMounted(async () => {
  // 从 URL 参数读取关键词并自动搜索
  const queryKeyword = route.query.keyword as string
  if (queryKeyword) {
    keyword.value = queryKeyword
    await handleSearch()
  }

  await loadMyAssets()
  if (!queryKeyword) {
    const firstAsset = myAssets.value[0]
    if (firstAsset) {
      selectAsset(firstAsset)
    } else {
      keyword.value = '玛奇朵'
      await handleSearch()
    }
  }
  const res = await getHotPrices()
  hotPrices.value = res.data
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="query-panel">
      <div>
        <p class="eyebrow">价格分析</p>
        <h1>查询谷子参考价与价格走势</h1>
        <p>输入谷子名称、IP 或角色查看当前参考价、最高最低成交价和趋势数据。</p>
      </div>
      <form class="query-form" @submit.prevent="handleSearch">
        <input type="search" v-model="keyword" aria-label="搜索谷子" placeholder="输入谷子名称 / IP / 角色">
        <div class="range-tabs" aria-label="时间范围">
          <button type="button" :class="{ active: range === '7d' }" @click="setRange('7d')">近7天</button>
          <button type="button" :class="{ active: range === '30d' }" @click="setRange('30d')">近30天</button>
          <button type="button" :class="{ active: range === '90d' }" @click="setRange('90d')">近90天</button>
        </div>
        <button class="primary" type="button" @click="handleSearch">查询</button>
      </form>
    </section>

    <section class="summary-panel" v-if="item">
      <div class="product-info">
        <p class="eyebrow">当前谷子</p>
        <h2>{{ item.name }}</h2>
        <div class="meta-tags">
          <span>{{ item.ipName }}</span><span>{{ item.characterName }}</span><span>{{ categoryLabel(item.category) }}</span>
        </div>
      </div>
      <div class="metric-grid" aria-label="价格指标">
        <article><span>当前参考价</span><strong>¥{{ item.currentPrice }}</strong></article>
        <article><span>{{ rangeLabel }}均价</span><strong>¥{{ item.avgPrice }}</strong></article>
        <article><span>最高成交价</span><strong>¥{{ item.maxPrice }}</strong></article>
        <article><span>最低成交价</span><strong>¥{{ item.minPrice }}</strong></article>
        <article :class="changeClass"><span>涨跌幅</span><strong>{{ item.changePercent > 0 ? '+' : '' }}{{ item.changePercent }}%</strong></article>
      </div>
    </section>
    <section class="summary-panel" v-else-if="keyword.trim() && !loading">
      <div class="product-info">
        <p class="eyebrow">当前谷子</p>
        <h2>未找到匹配结果</h2>
      </div>
    </section>

    <section class="my-assets-panel" v-if="userStore.isLoggedIn && myAssets.length > 0">
      <div class="section-head">
        <div>
          <p class="eyebrow">资产价格分析</p>
          <h2>我的资产价格分析</h2>
        </div>
        <div class="range-tabs" aria-label="时间范围">
          <button type="button" :class="{ active: range === '7d' }" @click="setRange('7d')">近7天</button>
          <button type="button" :class="{ active: range === '30d' }" @click="setRange('30d')">近30天</button>
          <button type="button" :class="{ active: range === '90d' }" @click="setRange('90d')">近90天</button>
        </div>
      </div>
      <div class="asset-grid">
        <article v-for="a in myAssets" :key="a.id" class="asset-card" :class="{ active: selectedAssetId === a.id }" @click="selectAsset(a)">
          <h3>{{ a.name }}</h3>
          <p class="asset-meta">{{ a.ipName }} · {{ categoryLabel(a.category) }} · x{{ a.quantity }}</p>
          <div class="asset-bottom">
            <strong>¥{{ a.currentPrice }}</strong>
            <span :class="{ up: a.changePercent > 0, down: a.changePercent < 0 }">{{ a.changePercent > 0 ? '+' : '' }}{{ a.changePercent }}%</span>
          </div>
          <p class="asset-cost" v-if="a.acquirePrice">购入价 ¥{{ a.acquirePrice }}</p>
        </article>
      </div>
    </section>

    <section class="chart-panel" v-if="item">
      <div class="section-head">
        <div>
          <p class="eyebrow">价格走势图</p>
          <h2>{{ rangeLabel }}价格走势</h2>
        </div>
        <span>当前参考价参考线：¥{{ item.currentPrice }}</span>
      </div>

      <div class="chart-wrap">
        <svg class="line-chart" viewBox="0 0 920 420" role="img" :aria-label="item.name + '价格变化折线图'">
          <line class="grid-line" x1="70" y1="60" x2="860" y2="60" />
          <line class="grid-line" x1="70" y1="130" x2="860" y2="130" />
          <line class="grid-line" x1="70" y1="200" x2="860" y2="200" />
          <line class="grid-line" x1="70" y1="270" x2="860" y2="270" />
          <line class="grid-line" x1="70" y1="340" x2="860" y2="340" />
          <text x="20" y="65">¥{{ gridLabels[0] }}</text>
          <text x="20" y="135">¥{{ gridLabels[1] }}</text>
          <text x="20" y="205">¥{{ gridLabels[2] }}</text>
          <text x="20" y="275">¥{{ gridLabels[3] }}</text>
          <text x="20" y="345">¥{{ gridLabels[4] }}</text>
          <line class="axis" x1="70" y1="40" x2="70" y2="340" />
          <line class="axis" x1="70" y1="340" x2="860" y2="340" />
          <polyline class="trend-line" :points="chartPoints.polyline" />
          <g v-for="(pt, idx) in chartPoints.points" :key="idx" class="point"
            :class="{ high: pt.price === item.maxPrice, current: idx === chartPoints.points.length - 1 }">
            <circle :cx="pt.cx" :cy="pt.cy" r="5" />
            <text v-if="pt.price === item.maxPrice" :x="pt.cx - 20" :y="pt.cy - 16">最高 ¥{{ pt.price }}</text>
            <text v-if="pt.price === item.minPrice" :x="pt.cx + 10" :y="pt.cy + 6">最低 ¥{{ pt.price }}</text>
            <text v-if="idx === chartPoints.points.length - 1" :x="pt.cx - 40" :y="pt.cy + 26">当前 ¥{{ pt.price }}</text>
          </g>
          <text v-for="(pt, idx) in chartPoints.points" :key="'x' + idx" class="x-label"
            :x="pt.cx - 20" y="382">{{ pt.label }}</text>
        </svg>
      </div>

      <p class="chart-note">{{ item.name }}近{{ rangeLabel.replace('近', '') }}价格{{ item.changePercent > 0 ? '呈整体上升趋势' : item.changePercent < 0 ? '呈下降趋势' : '保持平稳' }}，当前参考价¥{{ item.currentPrice }}，均值¥{{ item.avgPrice }}。</p>
    </section>

    <section class="hot-panel" v-if="hotPrices.length">
      <div class="section-head"><div><p class="eyebrow">热门行情</p><h2>热门谷子价格</h2></div></div>
      <div class="hot-grid">
        <article v-for="h in hotPrices" :key="h.id" class="hot-card" @click="keyword = h.name; handleSearch()">
          <h3>{{ h.name }}</h3>
          <p class="hot-meta">{{ h.ipName }} · {{ h.characterName }} · {{ categoryLabel(h.category) }}</p>
          <div class="hot-bottom">
            <strong>¥{{ h.currentPrice }}</strong>
            <span :class="{ up: h.changePercent > 0, down: h.changePercent < 0 }">{{ h.changePercent > 0 ? '+' : '' }}{{ h.changePercent }}%</span>
          </div>
        </article>
      </div>
    </section>

    <section class="bottom-layout" v-if="item">
      <section class="table-panel">
        <div class="section-head">
          <div><p class="eyebrow">近期成交参考</p><h2>成交记录</h2></div>
          <span>共 {{ item.transactions.length }} 条记录</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>成交时间</th><th>谷子名称</th><th>成交价</th><th>谷子状态</th><th>交易方式</th></tr></thead>
            <tbody>
              <tr v-for="(tx, idx) in item.transactions" :key="idx">
                <td>{{ tx.date }}</td><td>{{ tx.name }}</td><td>¥{{ tx.price }}</td><td>{{ tx.condition }}</td><td>{{ tx.method }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="conclusion-panel">
        <div class="section-head"><div><p class="eyebrow">分析结论</p><h2>价格判断</h2></div></div>
        <ul>
          <li v-for="(text, idx) in conclusionTexts" :key="idx">{{ text }}</li>
        </ul>
      </aside>
    </section>
  </main>
</template>

<style scoped>
.page { width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.query-panel, .summary-panel, .chart-panel, .table-panel, .conclusion-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.query-panel {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(460px, 560px);
  gap: 28px; align-items: center; padding: 30px; color: #fff;
  background: linear-gradient(rgba(10,74,90,0.88), rgba(10,74,90,0.92)),
    url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80") center/cover;
}
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, p { margin: 0; }
h1 { font-size: 38px; line-height: 1.16; }
.query-panel p:last-child { max-width: 650px; margin-top: 12px; color: rgba(255,255,255,0.84); line-height: 1.8; }
.query-form { display: grid; grid-template-columns: minmax(0, 1fr) 220px 88px; gap: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.28); border-radius: 10px; background: rgba(255,255,255,0.14); }
input { width: 100%; height: 44px; border: 0; border-radius: 8px; padding: 0 12px; outline: none; font: inherit; }
.range-tabs { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; }
.range-tabs button { border: 1px solid rgba(255,255,255,0.28); border-radius: 8px; color: #fff; background: rgba(255,255,255,0.12); cursor: pointer; font: inherit; }
.range-tabs button.active { color: #172126; background: var(--gold); }
.primary { min-height: 44px; border: 0; border-radius: 8px; color: #fff; background: var(--accent); font-weight: 800; cursor: pointer; font: inherit; }
.primary:hover { background: var(--accent-dark); }
.summary-panel { margin-top: 20px; padding: 24px; }
.product-info { display: flex; justify-content: space-between; gap: 18px; align-items: center; margin-bottom: 18px; }
.summary-panel .eyebrow, .chart-panel .eyebrow, .table-panel .eyebrow, .conclusion-panel .eyebrow { color: var(--accent); }
h2 { font-size: 26px; }
.meta-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.meta-tags span { padding: 7px 10px; border-radius: 7px; color: var(--accent); background: #eaf6f8; font-size: 13px; font-weight: 800; }
.metric-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; }
.metric-grid article { padding: 18px; border-radius: 10px; background: var(--soft); }
.metric-grid span { color: var(--muted); font-size: 14px; }
.metric-grid strong { display: block; margin-top: 10px; font-size: 28px; }
.metric-grid .up strong { color: #1f7a4d; }
.metric-grid .down strong { color: #c0392b; }
.chart-panel { margin-top: 20px; padding: 24px; }
.section-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 16px; }
.section-head span { color: var(--muted); font-size: 14px; }
.chart-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; background: #fff; }
.line-chart { width: 100%; min-width: 920px; height: auto; display: block; }
.line-chart :deep(text) { fill: var(--muted); font-size: 13px; }
.grid-line { stroke: #e4edf0; stroke-width: 1; }
.axis { stroke: #9dafb6; stroke-width: 1.5; }
.reference { stroke: var(--gold); stroke-width: 2; stroke-dasharray: 8 6; }
.reference-text { fill: #9a5d00; font-weight: 800; }
.trend-line { fill: none; stroke: var(--accent); stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }
.point :deep(circle) { fill: #fff; stroke: var(--accent); stroke-width: 3; }
.point.high :deep(circle) { stroke: var(--gold); }
.point.current :deep(circle) { fill: var(--accent); stroke: #fff; }
.point :deep(text) { fill: var(--ink); font-weight: 800; }
.x-label { font-size: 12px; }
.chart-note { margin-top: 16px; color: var(--muted); line-height: 1.8; }
.hot-panel { margin-top: 20px; padding: 24px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.hot-panel .eyebrow { color: var(--accent); }
.hot-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.my-assets-panel { margin-top: 20px; padding: 24px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.my-assets-panel .eyebrow { color: var(--accent); }
.my-assets-panel .range-tabs { display: flex; gap: 6px; }
.my-assets-panel .range-tabs button { border: 1px solid var(--line); border-radius: 8px; padding: 6px 14px; color: var(--muted); background: var(--soft); cursor: pointer; font: inherit; font-size: 13px; }
.my-assets-panel .range-tabs button.active { color: #fff; background: var(--accent); border-color: var(--accent); }
.asset-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }
.asset-card { padding: 16px; border: 2px solid var(--line); border-radius: 10px; background: var(--soft); cursor: pointer; transition: border-color 0.2s, box-shadow 0.2s; }
.asset-card:hover { box-shadow: 0 4px 14px rgba(0,0,0,0.08); }
.asset-card.active { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent); }
.asset-card h3 { font-size: 15px; margin: 0; }
.asset-meta { margin: 6px 0 0; color: var(--muted); font-size: 12px; }
.asset-bottom { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.asset-bottom strong { font-size: 20px; }
.asset-bottom span { font-size: 13px; font-weight: 800; }
.asset-bottom .up { color: #1f7a4d; }
.asset-bottom .down { color: #c0392b; }
.asset-cost { margin: 6px 0 0; color: var(--muted); font-size: 12px; }
.hot-card { padding: 18px; border: 1px solid var(--line); border-radius: 10px; background: var(--soft); cursor: pointer; transition: box-shadow 0.2s; }
.hot-card:hover { box-shadow: 0 4px 14px rgba(0,0,0,0.1); }
.hot-card h3 { font-size: 16px; }
.hot-meta { margin-top: 6px; color: var(--muted); font-size: 13px; }
.hot-bottom { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; }
.hot-bottom strong { font-size: 22px; }
.hot-bottom span { font-size: 14px; font-weight: 800; }
.hot-bottom .up { color: #1f7a4d; }
.hot-bottom .down { color: #c0392b; }
.bottom-layout { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 20px; margin-top: 20px; }
.table-panel, .conclusion-panel { padding: 22px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; min-width: 760px; border-collapse: collapse; font-size: 14px; }
th, td { padding: 14px 12px; border-bottom: 1px solid var(--line); text-align: left; }
th { color: var(--muted); background: var(--soft); }
.conclusion-panel ul { margin: 0; padding-left: 20px; color: var(--muted); line-height: 2; }

@media (max-width: 1080px) {
  .query-panel, .bottom-layout { grid-template-columns: 1fr; }
  .metric-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .asset-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
  .product-info, .section-head { align-items: flex-start; flex-direction: column; }
  .query-form, .metric-grid, .hot-grid { grid-template-columns: 1fr; }
  .asset-grid { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .page { width: min(100% - 20px, 1240px); }
  .query-panel, .summary-panel, .chart-panel, .table-panel, .conclusion-panel, .hot-panel { padding: 20px; }
  h1 { font-size: 30px; }
}
</style>
