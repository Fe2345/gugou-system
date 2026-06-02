<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import {
  addPriceRecord,
  getAdminGoodsList,
  getAdminPriceHistory,
  getAdminPriceRecords,
} from '@/api/admin'
import type { AdminPriceHistoryPoint, AdminPriceRecord } from '@/api/admin'
import type { GoodsItem } from '@/types/goods'

defineOptions({ name: 'AdminPriceView' })

type AdminGoodsOption = GoodsItem & { seller: string; submittedAt: string; stock: number }

const loading = ref(false)
const records = ref<AdminPriceRecord[]>([])
const goodsOptions = ref<AdminGoodsOption[]>([])
const historyPoints = ref<AdminPriceHistoryPoint[]>([])
const searchQuery = ref('')
const selectedProductId = ref('')
const rangeValue = ref('30d')
const startDate = ref('')
const endDate = ref('')

const newRecord = reactive({
  productId: '',
  name: '',
  price: '',
  recordedAt: '',
  note: '',
})

const selectedProduct = computed(() => goodsOptions.value.find(item => item.id === selectedProductId.value) || null)

const metrics = computed(() => {
  const volatileCount = records.value.filter(r => Math.abs(r.change) > 15).length
  const avgPrice = records.value.length
    ? (records.value.reduce((sum, item) => sum + Number(item.price), 0) / records.value.length).toFixed(1)
    : '0'
  return [
    { label: '价格记录总数', value: String(records.value.length), note: '当前筛选结果' },
    { label: '波动较大商品', value: String(volatileCount), note: '涨跌幅超过 15%' },
    { label: '均价', value: '¥' + avgPrice, note: '当前记录均值' },
    { label: '曲线点数', value: String(historyPoints.value.length), note: '历史价格样本' },
  ]
})

const chartPoints = computed(() => {
  const points = historyPoints.value
  if (!points.length) return []
  const prices = points.map(point => point.price)
  const minPrice = Math.min(...prices)
  const maxPrice = Math.max(...prices)
  const span = Math.max(maxPrice - minPrice, 1)
  return points.map((point, index) => {
    const x = points.length === 1 ? 60 : 60 + (index / (points.length - 1)) * 620
    const y = 250 - ((point.price - minPrice) / span) * 180
    return { ...point, x, y }
  })
})

const chartPolyline = computed(() => chartPoints.value.map(point => `${point.x},${point.y}`).join(' '))

async function loadGoodsOptions() {
  const res = await getAdminGoodsList({ page_size: 200 })
  goodsOptions.value = res.data.results
  const first = goodsOptions.value[0]
  if (!selectedProductId.value && first) {
    selectedProductId.value = first.id
    newRecord.productId = first.id
    newRecord.name = first.name
  }
}

async function loadRecords() {
  loading.value = true
  try {
    const res = await getAdminPriceRecords({
      keyword: searchQuery.value || undefined,
      productId: selectedProductId.value || undefined,
      startDate: startDate.value || undefined,
      endDate: endDate.value || undefined,
    })
    records.value = res.data
  } catch (e) {
    console.error('加载价格记录失败', e)
  } finally {
    loading.value = false
  }
}

async function loadHistory() {
  if (!selectedProductId.value) {
    historyPoints.value = []
    return
  }
  const res = await getAdminPriceHistory({
    productId: selectedProductId.value,
    range: rangeValue.value,
    startDate: startDate.value || undefined,
    endDate: endDate.value || undefined,
  })
  historyPoints.value = res.data.points
}

async function refreshAll() {
  await loadRecords()
  await loadHistory()
}

onMounted(async () => {
  await loadGoodsOptions()
  await refreshAll()
})

function handleProductChange() {
  const product = selectedProduct.value
  if (product) {
    newRecord.productId = product.id
    newRecord.name = product.name
  }
  refreshAll()
}

function handleNewRecordProductChange() {
  const product = goodsOptions.value.find(item => item.id === newRecord.productId)
  newRecord.name = product?.name || ''
}

function handleSearch() {
  refreshAll()
}

function handleDateChange() {
  refreshAll()
}

async function handleAddRecord() {
  if (!newRecord.productId || !newRecord.price) return
  loading.value = true
  try {
    const product = goodsOptions.value.find(item => item.id === newRecord.productId)
    await addPriceRecord({
      productId: newRecord.productId,
      name: product?.name || newRecord.name,
      price: Number(newRecord.price),
      period: 'manual',
      change: 0,
      note: newRecord.note,
      recordedAt: newRecord.recordedAt,
    })
    newRecord.price = ''
    newRecord.recordedAt = ''
    newRecord.note = ''
    await refreshAll()
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="page-head">
    <div>
      <p class="eyebrow">价格记录</p>
      <h1>价格管理</h1>
      <p>按商品和时间范围查询价格记录，并查看对应商品的历史价格曲线。</p>
    </div>
  </section>

  <section class="data-grid">
    <article v-for="(m, i) in metrics" :key="i" class="data-card">
      <span>{{ m.label }}</span><strong>{{ m.value }}</strong><p>{{ m.note }}</p>
    </article>
  </section>

  <section class="toolbar">
    <div class="search-box">
      <input v-model="searchQuery" type="search" placeholder="输入商品名称、IP 或记录编号" @keyup.enter="handleSearch" />
    </div>
    <select v-model="selectedProductId" @change="handleProductChange">
      <option value="">全部商品</option>
      <option v-for="item in goodsOptions" :key="item.id" :value="item.id">{{ item.name }}</option>
    </select>
    <select v-model="rangeValue" @change="handleDateChange">
      <option value="7d">近 7 天</option>
      <option value="30d">近 30 天</option>
      <option value="90d">近 90 天</option>
      <option value="180d">近 180 天</option>
      <option value="1y">近一年</option>
    </select>
    <input v-model="startDate" type="date" @change="handleDateChange" />
    <input v-model="endDate" type="date" @change="handleDateChange" />
    <button class="primary" type="button" :disabled="loading" @click="handleSearch">{{ loading ? '加载中' : '查询' }}</button>
  </section>

  <section class="chart-panel">
    <div class="section-head">
      <div>
        <p class="eyebrow">价格历史曲线</p>
        <h2>{{ selectedProduct?.name || '请选择商品' }}</h2>
      </div>
      <span>{{ historyPoints.length }} 个价格点</span>
    </div>
    <div v-if="!selectedProductId" class="empty-state">
      <strong>请选择一个商品查看价格曲线</strong>
    </div>
    <div v-else-if="!historyPoints.length" class="empty-state">
      <strong>暂无价格历史</strong>
      <p>可以先在右侧新增一条价格记录。</p>
    </div>
    <div v-else class="chart-wrap">
      <svg class="line-chart" viewBox="0 0 740 300" role="img" aria-label="价格历史曲线">
        <line x1="60" y1="250" x2="700" y2="250" />
        <line x1="60" y1="40" x2="60" y2="250" />
        <polyline :points="chartPolyline" />
        <g v-for="(point, index) in chartPoints" :key="point.time">
          <circle :cx="point.x" :cy="point.y" r="5" />
          <text v-if="index === 0 || index === chartPoints.length - 1" :x="point.x" :y="point.y - 12" text-anchor="middle">
            ¥{{ point.price }}
          </text>
          <text v-if="index === 0 || index === chartPoints.length - 1" :x="point.x" y="278" text-anchor="middle">
            {{ point.date }}
          </text>
        </g>
      </svg>
    </div>
  </section>

  <section class="content-row">
    <article class="table-panel">
      <div class="section-head">
        <div><p class="eyebrow">价格列表</p><h2>价格记录</h2></div>
        <span>共 {{ records.length }} 条</span>
      </div>
      <div v-if="!records.length" class="empty-state">
        <strong>暂无价格记录</strong>
      </div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr><th>记录编号</th><th>商品名称</th><th>成交价格</th><th>来源</th><th>涨跌幅</th><th>统计时间</th></tr>
          </thead>
          <tbody>
            <tr v-for="r in records" :key="r.id">
              <td>{{ r.id }}</td>
              <td>{{ r.name }}</td>
              <td class="price">¥{{ Number(r.price).toFixed(2) }}</td>
              <td>{{ r.period }}</td>
              <td>
                <span class="change" :class="r.change > 0 ? 'up' : r.change < 0 ? 'down' : 'flat'">
                  {{ r.change > 0 ? '+' : '' }}{{ r.change }}%
                </span>
              </td>
              <td>{{ r.time }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>

    <aside class="panel">
      <div class="panel-title"><h3>新增价格记录</h3></div>
      <form class="form-stack" @submit.prevent="handleAddRecord">
        <select v-model="newRecord.productId" required @change="handleNewRecordProductChange">
          <option value="">请选择商品</option>
          <option v-for="item in goodsOptions" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
        <input v-model="newRecord.price" type="number" min="0" step="0.01" placeholder="成交价格" required />
        <input v-model="newRecord.recordedAt" type="date" />
        <textarea v-model="newRecord.note" placeholder="填写数据来源、记录说明或复核备注"></textarea>
        <div class="form-actions">
          <button class="primary" type="submit" :disabled="loading">{{ loading ? '保存中' : '保存记录' }}</button>
        </div>
      </form>
    </aside>
  </section>
</template>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 20px; }
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 32px; }
.page-head > div > p:last-child { margin-top: 8px; color: var(--muted); }
.data-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-bottom: 20px; }
.data-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 20px; }
.data-card span { color: var(--muted); font-size: 14px; }
.data-card strong { display: block; margin-top: 10px; font-size: 30px; }
.data-card p { margin-top: 8px; color: var(--muted); }
.toolbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; padding: 18px; margin-bottom: 20px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.search-box { flex: 1; min-width: 220px; }
.search-box input, select, input[type="date"], input[type="number"] { height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; font: inherit; background: var(--soft); min-width: 130px; box-sizing: border-box; }
.search-box input { width: 100%; }
textarea { border: 1px solid var(--line); border-radius: 8px; padding: 12px; font: inherit; background: var(--soft); min-height: 80px; resize: vertical; width: 100%; box-sizing: border-box; }
.primary { height: 42px; padding: 0 18px; border: 0; border-radius: 8px; background: var(--accent); color: #fff; font-weight: 800; cursor: pointer; font: inherit; }
.primary:hover { background: var(--accent-dark); }
.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.chart-panel, .table-panel, .panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); overflow: hidden; }
.chart-panel { margin-bottom: 18px; }
.section-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; border-bottom: 1px solid var(--line); }
.section-head .eyebrow { margin-bottom: 4px; }
.section-head span { color: var(--muted); font-size: 13px; }
.chart-wrap { overflow-x: auto; padding: 18px; }
.line-chart { width: 100%; min-width: 680px; height: 300px; display: block; }
.line-chart line { stroke: var(--line); stroke-width: 2; }
.line-chart polyline { fill: none; stroke: var(--accent); stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }
.line-chart circle { fill: #fff; stroke: var(--accent); stroke-width: 3; }
.line-chart text { fill: var(--muted); font-size: 12px; }
.content-row { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.7fr); gap: 18px; align-items: start; }
.empty-state { min-height: 120px; display: grid; place-items: center; text-align: center; color: var(--muted); padding: 20px; }
.empty-state strong { color: var(--ink); }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 14px 16px; border-bottom: 1px solid var(--line); text-align: left; font-size: 14px; }
th { color: var(--muted); font-size: 12px; font-weight: 700; background: var(--soft); }
tr:last-child td { border-bottom: 0; }
.price { color: #be123c; font-weight: 700; }
.change { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.change.up { background: #dcfce7; color: #15803d; }
.change.down { background: #fee2e2; color: #be123c; }
.change.flat { background: var(--soft); color: var(--muted); }
.panel { padding: 18px; }
.panel-title { margin-bottom: 14px; }
.panel-title h3 { font-size: 18px; }
.form-stack { display: grid; gap: 12px; }
.form-actions { display: flex; gap: 8px; }
@media (max-width: 1100px) {
  .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .content-row { grid-template-columns: 1fr; }
}
@media (max-width: 760px) {
  .data-grid { grid-template-columns: 1fr; }
  .toolbar { flex-direction: column; align-items: stretch; }
  .toolbar > *, .toolbar select, .toolbar input[type="date"] { width: 100%; }
}
</style>
