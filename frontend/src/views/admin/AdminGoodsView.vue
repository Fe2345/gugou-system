<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { getAdminGoodsList, approveGoods, rejectGoods, offlineGoods } from '@/api/admin'
import { updateGoods } from '@/api/goods'
import type { GoodsItem } from '@/types/goods'

defineOptions({ name: 'AdminGoodsView' })

type AdminGoodsItem = GoodsItem & { seller: string; submittedAt: string; stock: number }

const loading = ref(false)
const goods = ref<AdminGoodsItem[]>([])
const activeTab = ref('all')
const searchQuery = ref('')
const filterStatus = ref('all')
const filterCategory = ref('')
const filterTime = ref('')

const editingGoods = ref<AdminGoodsItem | null>(null)
const editForm = reactive({ name: '', price: '', category: '', description: '' })

const metrics = computed(() => {
  const pending = goods.value.filter(g => g.status === 'pending').length
  const online = goods.value.filter(g => g.status === 'approved').length
  const rejected = goods.value.filter(g => g.status === 'rejected').length
  return [
    { label: '待审核商品', value: String(pending), note: '需要审核处理' },
    { label: '上架中商品', value: String(online), note: '平台可交易商品' },
    { label: '已通过', value: String(online), note: '审核通过上架' },
    { label: '未通过/下架', value: String(rejected), note: '图片或价格异常' },
  ]
})

const statusMap: Record<string, string> = { pending: '待审核', approved: '已上架', rejected: '未通过' }

async function loadGoods() {
  loading.value = true
  try {
    const res = await getAdminGoodsList({
      keyword: searchQuery.value || undefined,
      status: filterStatus.value !== 'all' ? filterStatus.value : undefined,
      category: filterCategory.value || undefined,
    })
    goods.value = res.data.list
  } catch (e) {
    console.error('加载商品失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadGoods() })

function handleSearch() { loadGoods() }
function handleFilter() { loadGoods() }

async function handleApprove(id: string) {
  loading.value = true
  try {
    await approveGoods(id)
    await loadGoods()
  } catch (e) {
    console.error('审核通过失败', e)
  } finally {
    loading.value = false
  }
}

async function handleReject(id: string) {
  loading.value = true
  try {
    await rejectGoods(id)
    await loadGoods()
  } catch (e) {
    console.error('驳回失败', e)
  } finally {
    loading.value = false
  }
}

async function handleOffline(id: string) {
  loading.value = true
  try {
    await offlineGoods(id)
    await loadGoods()
  } catch (e) {
    console.error('下架失败', e)
  } finally {
    loading.value = false
  }
}

function startEdit(item: AdminGoodsItem) {
  editingGoods.value = item
  editForm.name = item.name
  editForm.price = String(item.price)
  editForm.category = item.category
  editForm.description = item.description
}

function cancelEdit() {
  editingGoods.value = null
}

async function handleSaveEdit() {
  if (!editingGoods.value) return
  loading.value = true
  try {
    await updateGoods(editingGoods.value.id, {
      name: editForm.name,
      price: Number(editForm.price),
      category: editForm.category,
      description: editForm.description,
    })
    editingGoods.value = null
    await loadGoods()
  } catch (e) {
    console.error('编辑失败', e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="page-head">
    <div>
      <p class="eyebrow">商品审核</p>
      <h1>商品管理</h1>
      <p>审核商品、上架/下架、修改商品信息与追踪处理记录</p>
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
    <div class="search-box"><input v-model="searchQuery" type="search" placeholder="输入商品名称 / 商品编号 / 卖家ID" @keyup.enter="handleSearch"></div>
    <select v-model="filterStatus" @change="handleFilter">
      <option value="all">全部状态</option><option value="pending">待审核</option><option value="approved">已上架</option><option value="rejected">未通过</option>
    </select>
    <select v-model="filterCategory" @change="handleFilter">
      <option value="">全部分类</option><option value="徽章/吧唧">徽章/吧唧</option><option value="亚克力立牌">亚克力立牌</option><option value="色纸/拍立得">色纸/拍立得</option><option value="挂件">挂件</option>
    </select>
    <button class="primary" type="button" :disabled="loading" @click="handleSearch">{{ loading ? '加载中...' : '筛选商品' }}</button>
  </section>

  <section class="table-panel">
    <div class="section-head">
      <div><p class="eyebrow">商品列表</p><h2>全部商品</h2></div>
      <span>共 {{ goods.length }} 条数据</span>
    </div>
    <div v-if="!goods.length" class="empty-state">
      <strong>暂无商品数据</strong>
    </div>
    <div v-else class="table-wrap">
      <table>
        <thead>
          <tr><th>商品名称</th><th>编号</th><th>分类</th><th>卖家</th><th>价格</th><th>库存</th><th>提交时间</th><th>状态</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="row in goods" :key="row.id">
            <td><strong>{{ row.name }}</strong></td>
            <td class="muted">{{ row.id }}</td>
            <td>{{ row.category }}</td>
            <td>{{ row.seller }}</td>
            <td class="price">¥{{ row.price }}</td>
            <td>{{ row.stock }}</td>
            <td>{{ row.submittedAt }}</td>
            <td><span class="status" :class="row.status">{{ statusMap[row.status] }}</span></td>
            <td class="actions">
              <button v-if="row.status === 'pending'" class="primary sm" type="button" @click="handleApprove(row.id)">通过</button>
              <button v-if="row.status === 'pending'" class="danger sm" type="button" @click="handleReject(row.id)">驳回</button>
              <button v-if="row.status === 'approved'" class="warn sm" type="button" @click="handleOffline(row.id)">下架</button>
              <button v-if="row.status === 'rejected'" class="primary sm" type="button" @click="handleApprove(row.id)">复审</button>
              <button class="secondary sm" type="button" @click="startEdit(row)">编辑</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <!-- 编辑弹窗 -->
  <div v-if="editingGoods" class="modal-overlay" @click.self="cancelEdit">
    <div class="modal">
      <div class="modal-header">
        <h2>编辑商品</h2>
        <button class="modal-close" @click="cancelEdit">&times;</button>
      </div>
      <form class="modal-form" @submit.prevent="handleSaveEdit">
        <label><span>商品名称</span><input v-model="editForm.name" type="text" required></label>
        <label><span>价格</span><input v-model="editForm.price" type="number" min="0" step="0.01" required></label>
        <label><span>分类</span><input v-model="editForm.category" type="text"></label>
        <label><span>描述</span><textarea v-model="editForm.description" rows="3"></textarea></label>
        <div class="modal-actions">
          <button type="button" class="secondary" @click="cancelEdit">取消</button>
          <button type="submit" class="primary" :disabled="loading">{{ loading ? '保存中...' : '保存' }}</button>
        </div>
      </form>
    </div>
  </div>
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
.primary.sm { height: 32px; padding: 0 12px; font-size: 13px; }
.secondary.sm { height: 32px; padding: 0 12px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); font-weight: 700; cursor: pointer; font: inherit; font-size: 13px; }
.danger.sm { height: 32px; padding: 0 12px; border: 0; border-radius: 8px; background: #fee2e2; color: #be123c; font-weight: 700; cursor: pointer; font: inherit; font-size: 13px; }
.warn.sm { height: 32px; padding: 0 12px; border: 0; border-radius: 8px; background: #fef3c7; color: #b45309; font-weight: 700; cursor: pointer; font: inherit; font-size: 13px; }

.data-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-bottom: 20px; }
.data-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 20px; }
.data-card span { color: var(--muted); font-size: 14px; }
.data-card strong { display: block; margin-top: 10px; font-size: 30px; }
.data-card p { margin-top: 8px; color: var(--muted); }

.toolbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; padding: 18px; margin-bottom: 20px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.search-box { flex: 1; min-width: 200px; }
.search-box input { width: 100%; height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 14px; font: inherit; background: var(--soft); }
select { height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; font: inherit; background: var(--soft); min-width: 120px; }

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
.muted { color: var(--muted); font-size: 12px; }
.price { color: #be123c; font-weight: 900; }
.status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status.pending { background: #fef3c7; color: #b45309; }
.status.approved { background: #dcfce7; color: #15803d; }
.status.rejected { background: #fee2e2; color: #be123c; }
.actions { display: flex; gap: 6px; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: grid; place-items: center; z-index: 1000; padding: 20px; }
.modal { background: var(--panel); border-radius: 16px; width: min(560px, 100%); max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid var(--line); }
.modal-header h2 { font-size: 22px; }
.modal-close { width: 36px; height: 36px; border: 0; border-radius: 8px; background: var(--soft); color: var(--muted); font-size: 22px; cursor: pointer; display: grid; place-items: center; }
.modal-form { padding: 24px; display: grid; gap: 16px; }
.modal-form label { display: grid; gap: 6px; }
.modal-form label span { color: var(--muted); font-size: 14px; font-weight: 600; }
.modal-form input, .modal-form textarea { width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 10px 14px; font: inherit; background: #fff; box-sizing: border-box; }
.modal-form textarea { resize: vertical; min-height: 70px; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; padding: 16px 24px; border-top: 1px solid var(--line); }
.secondary { height: 42px; padding: 0 16px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); font-weight: 700; cursor: pointer; font: inherit; }

@media (max-width: 1100px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 760px) { .data-grid { grid-template-columns: 1fr; } .toolbar { flex-direction: column; align-items: stretch; } }
</style>
