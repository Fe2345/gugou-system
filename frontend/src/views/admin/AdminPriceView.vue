<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { getAdminPriceRecords, addPriceRecord } from '@/api/admin'
import type { AdminPriceRecord } from '@/api/admin'

defineOptions({ name: 'AdminPriceView' })

const loading = ref(false)
const records = ref<AdminPriceRecord[]>([])
const searchQuery = ref('')
const filterPeriod = ref('')
const filterChange = ref('')

const newRecord = reactive({
  name: '',
  price: '',
  period: '近7天',
  change: '',
  note: '',
})

const metrics = computed(() => {
  const today = records.value.length
  const volatileCount = records.value.filter(r => Math.abs(r.change) > 15).length
  const avgPrice = records.value.length ? (records.value.reduce((s, r) => s + r.price, 0) / records.value.length).toFixed(1) : '0'
  return [
    { label: '价格记录总数', value: String(today), note: '已同步记录' },
    { label: '波动较大商品', value: String(volatileCount), note: '涨跌幅超过 15%' },
    { label: '均价', value: '¥' + avgPrice, note: '当前记录均值' },
    { label: '待复核记录', value: '4', note: '来源异常待确认' },
  ]
})

async function loadRecords() {
  loading.value = true
  try {
    const res = await getAdminPriceRecords({
      keyword: searchQuery.value || undefined,
      period: filterPeriod.value || undefined,
      change: filterChange.value || undefined,
    })
    records.value = res.data
  } catch (e) {
    console.error('加载价格记录失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadRecords() })

function handleSearch() { loadRecords() }
function handleFilter() { loadRecords() }

async function handleAddRecord() {
  if (!newRecord.name || !newRecord.price) return
  loading.value = true
  try {
    await addPriceRecord({
      name: newRecord.name,
      price: Number(newRecord.price),
      period: newRecord.period,
      change: Number(newRecord.change) || 0,
      note: newRecord.note,
    })
    newRecord.name = ''
    newRecord.price = ''
    newRecord.change = ''
    newRecord.note = ''
    await loadRecords()
  } catch (e) {
    console.error('添加记录失败', e)
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
      <p>查看商品历史成交价格、涨跌幅、统计区间与记录维护情况</p>
    </div>
  </section>

  <section class="data-grid">
    <article v-for="(m, i) in metrics" :key="i" class="data-card">
      <span>{{ m.label }}</span><strong>{{ m.value }}</strong><p>{{ m.note }}</p>
    </article>
  </section>

  <section class="toolbar">
    <div class="search-box"><input v-model="searchQuery" type="search" placeholder="输入商品名称或记录编号" @keyup.enter="handleSearch"></div>
    <select v-model="filterPeriod" @change="handleFilter">
      <option value="">统计区间</option><option value="近7天">近7天</option><option value="近30天">近30天</option><option value="近90天">近90天</option>
    </select>
    <select v-model="filterChange" @change="handleFilter">
      <option value="">波动范围</option><option value="上涨">上涨</option><option value="下跌">下跌</option>
    </select>
    <button class="primary" type="button" :disabled="loading" @click="handleSearch">{{ loading ? '加载中...' : '查询记录' }}</button>
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
          <thead><tr><th>记录编号</th><th>商品名称</th><th>成交价格</th><th>统计区间</th><th>涨跌幅</th><th>统计时间</th></tr></thead>
          <tbody>
            <tr v-for="r in records" :key="r.id">
              <td>{{ r.id }}</td>
              <td>{{ r.name }}</td>
              <td class="price">¥{{ r.price.toFixed(2) }}</td>
              <td>{{ r.period }}</td>
              <td><span class="change" :class="r.change > 0 ? 'up' : r.change < 0 ? 'down' : 'flat'">{{ r.change > 0 ? '+' : '' }}{{ r.change }}%</span></td>
              <td>{{ r.time }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>

    <aside class="panel">
      <div class="panel-title"><h3>新增价格记录</h3></div>
      <form class="form-stack" @submit.prevent="handleAddRecord">
        <input v-model="newRecord.name" type="text" placeholder="商品名称" required />
        <input v-model="newRecord.price" type="number" min="0" step="0.01" placeholder="成交价格" required />
        <select v-model="newRecord.period">
          <option value="近7天">近7天</option><option value="近30天">近30天</option><option value="近90天">近90天</option>
        </select>
        <input v-model="newRecord.change" type="number" step="0.1" placeholder="涨跌幅 (%)" />
        <textarea v-model="newRecord.note" placeholder="填写数据来源、记录说明或复核备注"></textarea>
        <div class="form-actions">
          <button class="primary" type="submit" :disabled="loading">{{ loading ? '保存中...' : '保存记录' }}</button>
        </div>
      </form>
    </aside>
  </section>
</template>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 20px; }
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; } h1 { font-size: 32px; }
.page-head > div > p:last-child { margin-top: 8px; color: var(--muted); }

.data-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-bottom: 20px; }
.data-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 20px; }
.data-card span { color: var(--muted); font-size: 14px; }
.data-card strong { display: block; margin-top: 10px; font-size: 30px; }
.data-card p { margin-top: 8px; color: var(--muted); }

.toolbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; padding: 18px; margin-bottom: 20px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.search-box { flex: 1; min-width: 200px; }
.search-box input { width: 100%; height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 14px; font: inherit; background: var(--soft); }
select, input[type="text"], input[type="number"] { height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; font: inherit; background: var(--soft); min-width: 120px; }
textarea { border: 1px solid var(--line); border-radius: 8px; padding: 12px; font: inherit; background: var(--soft); min-height: 80px; resize: vertical; width: 100%; box-sizing: border-box; }
.primary { height: 42px; padding: 0 18px; border: 0; border-radius: 8px; background: var(--accent); color: #fff; font-weight: 800; cursor: pointer; font: inherit; }
.primary:hover { background: var(--accent-dark); }
.primary:disabled { opacity: 0.6; cursor: not-allowed; }

.content-row { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.7fr); gap: 18px; align-items: start; }
.table-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); overflow: hidden; }
.section-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; border-bottom: 1px solid var(--line); }
.section-head .eyebrow { margin-bottom: 4px; }
.section-head span { color: var(--muted); font-size: 13px; }
.empty-state { min-height: 120px; display: grid; place-items: center; color: var(--muted); }
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

.panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 18px; }
.panel-title { margin-bottom: 14px; }
.panel-title h3 { font-size: 18px; }
.form-stack { display: grid; gap: 12px; }
.form-actions { display: flex; gap: 8px; }

@media (max-width: 1100px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .content-row { grid-template-columns: 1fr; } }
</style>
