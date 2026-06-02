<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  approveGoods,
  getAdminGoodsList,
  offlineGoods,
  rejectGoods,
} from '@/api/admin'
import { getGoodsCategories } from '@/api/goods'
import type { GoodsItem } from '@/types/goods'

defineOptions({ name: 'AdminGoodsView' })

type AdminGoodsItem = GoodsItem & { seller: string; submittedAt: string; stock: number }

const loading = ref(false)
const goods = ref<AdminGoodsItem[]>([])
const searchQuery = ref('')
const filterStatus = ref('all')
const filterCategory = ref('')
const categories = ref<{ value: string; label: string }[]>([])
const goodsStats = ref({ active: 0, inactive: 0, frozen: 0, total: 0 })
const totalCount = ref(0)

const metrics = computed(() => [
  { label: '已上架商品', value: String(goodsStats.value.active), note: '审核通过后可被用户查看' },
  { label: '待审核商品', value: String(goodsStats.value.inactive), note: '等待管理员审核' },
  { label: '已驳回商品', value: String(goodsStats.value.frozen), note: '审核未通过或被冻结' },
  { label: '全部商品', value: String(goodsStats.value.total), note: '商品总数' },
])

const statusMap: Record<string, string> = {
  active: '已上架',
  inactive: '待审核',
  frozen: '已驳回',
  archived: '已归档',
}

async function loadGoods() {
  loading.value = true
  try {
    const res = await getAdminGoodsList({
      keyword: searchQuery.value || undefined,
      status: filterStatus.value !== 'all' ? filterStatus.value : undefined,
      category: filterCategory.value || undefined,
      page_size: 100,
    })
    goods.value = res.data.results
    totalCount.value = res.data.count
    if (res.data.stats) goodsStats.value = res.data.stats
  } catch (e) {
    console.error('加载商品失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadGoods()
  const catRes = await getGoodsCategories()
  categories.value = catRes.data
})

function handleSearch() { loadGoods() }
function handleFilter() { loadGoods() }

async function handleApprove(id: string) {
  loading.value = true
  try {
    await approveGoods(id)
    await loadGoods()
  } finally {
    loading.value = false
  }
}

async function handleReject(id: string) {
  loading.value = true
  try {
    await rejectGoods(id)
    await loadGoods()
  } finally {
    loading.value = false
  }
}

async function handleOffline(id: string) {
  loading.value = true
  try {
    await offlineGoods(id)
    await loadGoods()
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="page-head">
    <div>
      <p class="eyebrow">商品审核</p>
      <h1>商品库审核</h1>
      <p>管理员只负责审核用户提交的商品，通过后上架；商品信息由用户在待审核期间维护。</p>
    </div>
  </section>

  <section class="data-grid">
    <article v-for="(m, i) in metrics" :key="i" class="data-card">
      <span>{{ m.label }}</span>
      <strong>{{ m.value }}</strong>
      <p>{{ m.note }}</p>
    </article>
  </section>

  <section class="toolbar">
    <div class="search-box">
      <input v-model="searchQuery" type="search" placeholder="输入商品名称 / 商品编号 / 创建人ID" @keyup.enter="handleSearch" />
    </div>
    <select v-model="filterStatus" @change="handleFilter">
      <option value="all">全部状态</option>
      <option value="inactive">待审核</option>
      <option value="active">已上架</option>
      <option value="frozen">已驳回</option>
      <option value="archived">已归档</option>
    </select>
    <select v-model="filterCategory" @change="handleFilter">
      <option value="">全部分类</option>
      <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
    </select>
    <button class="primary" type="button" :disabled="loading" @click="handleSearch">{{ loading ? '加载中' : '查询商品' }}</button>
  </section>

  <section class="table-panel">
    <div class="section-head">
      <div><p class="eyebrow">商品列表</p><h2>审核列表</h2></div>
      <span>共 {{ totalCount }} 条数据</span>
    </div>
    <div v-if="!goods.length" class="empty-state">
      <strong>暂无商品数据</strong>
    </div>
    <div v-else class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>商品</th><th>编号</th><th>分类</th><th>创建人</th><th>价格</th><th>库存</th><th>提交时间</th><th>状态</th><th>审核操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in goods" :key="row.id">
            <td>
              <div class="goods-cell">
                <img :src="row.mainImage" :alt="row.name" />
                <div><strong>{{ row.name }}</strong><span>{{ row.ipName }} / {{ row.characterName }}</span></div>
              </div>
            </td>
            <td class="muted">{{ row.id }}</td>
            <td>{{ row.category }}</td>
            <td>{{ row.seller || '-' }}</td>
            <td class="price">¥{{ row.referencePrice }}</td>
            <td>{{ row.stock }}</td>
            <td>{{ row.submittedAt }}</td>
            <td><span class="status" :class="row.status">{{ statusMap[row.status] || row.status }}</span></td>
            <td class="actions">
              <button v-if="row.status === 'inactive'" class="primary sm" type="button" @click="handleApprove(row.id)">通过上架</button>
              <button v-if="row.status === 'inactive'" class="danger sm" type="button" @click="handleReject(row.id)">驳回</button>
              <button v-if="row.status === 'active'" class="warn sm" type="button" @click="handleOffline(row.id)">下架复审</button>
              <span v-if="row.status !== 'inactive' && row.status !== 'active'" class="muted">无可用操作</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 20px; }
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 32px; }
.page-head > div > p:last-child { margin-top: 8px; color: var(--muted); }
.primary { height: 42px; padding: 0 18px; border: 0; border-radius: 8px; background: var(--accent); color: #fff; font-weight: 800; cursor: pointer; font: inherit; }
.primary:hover { background: var(--accent-dark); }
.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.primary.sm, .danger.sm, .warn.sm { height: 32px; padding: 0 12px; font-size: 13px; white-space: nowrap; }
.danger.sm { border: 0; border-radius: 8px; background: #fee2e2; color: #be123c; font-weight: 700; cursor: pointer; font: inherit; }
.warn.sm { border: 0; border-radius: 8px; background: #fef3c7; color: #b45309; font-weight: 700; cursor: pointer; font: inherit; }
.data-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-bottom: 20px; }
.data-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 20px; }
.data-card span { color: var(--muted); font-size: 14px; }
.data-card strong { display: block; margin-top: 10px; font-size: 30px; }
.data-card p { margin-top: 8px; color: var(--muted); }
.toolbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; padding: 18px; margin-bottom: 20px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.search-box { flex: 1; min-width: 220px; }
.search-box input, select { width: 100%; height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 14px; font: inherit; background: var(--soft); box-sizing: border-box; }
select { min-width: 130px; }
.table-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); overflow: hidden; }
.section-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; border-bottom: 1px solid var(--line); }
.section-head .eyebrow { margin-bottom: 4px; }
.section-head span { color: var(--muted); font-size: 13px; }
.empty-state { min-height: 120px; display: grid; place-items: center; color: var(--muted); }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 14px 16px; border-bottom: 1px solid var(--line); text-align: left; font-size: 14px; vertical-align: middle; }
th { color: var(--muted); font-size: 12px; font-weight: 700; background: var(--soft); }
tr:last-child td { border-bottom: 0; }
.goods-cell { display: flex; align-items: center; gap: 10px; min-width: 240px; }
.goods-cell img { width: 48px; height: 48px; border-radius: 8px; object-fit: cover; background: var(--soft); flex: 0 0 auto; }
.goods-cell span { display: block; margin-top: 4px; color: var(--muted); font-size: 12px; }
.muted { color: var(--muted); font-size: 12px; }
.price { color: #be123c; font-weight: 900; }
.status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status.active { background: #dcfce7; color: #15803d; }
.status.inactive { background: #fef3c7; color: #b45309; }
.status.frozen { background: #fee2e2; color: #be123c; }
.status.archived { background: #e5e7eb; color: #6b7280; }
.actions { display: flex; gap: 6px; flex-wrap: wrap; min-width: 180px; align-items: center; }
@media (max-width: 1100px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 760px) {
  .data-grid { grid-template-columns: 1fr; }
  .toolbar { flex-direction: column; align-items: stretch; }
  .page-head { flex-direction: column; }
}
</style>
