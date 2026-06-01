<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import {
  approveGoods,
  createAdminGoods,
  editGoods,
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

const editingGoods = ref<AdminGoodsItem | null>(null)
const showCreateModal = ref(false)
const editForm = reactive({ name: '', referencePrice: '', category: '', description: '', mainImage: '', ipName: '', characterName: '' })
const createForm = reactive({ name: '', referencePrice: '', category: 'other', description: '', mainImage: '', ipName: '', characterName: '' })

const goodsStats = ref({ active: 0, inactive: 0, frozen: 0, total: 0 })
const totalCount = ref(0)

const metrics = computed(() => [
  { label: '正常商品', value: String(goodsStats.value.active), note: '当前可查询和使用' },
  { label: '未启用商品', value: String(goodsStats.value.inactive), note: '待启用或待处理' },
  { label: '冻结商品', value: String(goodsStats.value.frozen), note: '异常限制中' },
  { label: '全部商品', value: String(goodsStats.value.total), note: '商品总数' },
])

const statusMap: Record<string, string> = { active: '正常', inactive: '未启用', frozen: '冻结', archived: '归档' }

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

function openCreateModal() {
  createForm.name = ''
  createForm.referencePrice = ''
  createForm.category = categories.value[0]?.value || 'other'
  createForm.description = ''
  createForm.mainImage = ''
  createForm.ipName = ''
  createForm.characterName = ''
  showCreateModal.value = true
}

function closeCreateModal() {
  showCreateModal.value = false
}

async function handleCreateGoods() {
  if (!createForm.name.trim()) return
  loading.value = true
  try {
    await createAdminGoods({
      name: createForm.name.trim(),
      referencePrice: Number(createForm.referencePrice) || 0,
      category: createForm.category || 'other',
      description: createForm.description,
      mainImage: createForm.mainImage,
      ipName: createForm.ipName,
      characterName: createForm.characterName,
    })
    closeCreateModal()
    await loadGoods()
  } finally {
    loading.value = false
  }
}

function startEdit(item: AdminGoodsItem) {
  editingGoods.value = item
  editForm.name = item.name
  editForm.referencePrice = String(item.referencePrice)
  editForm.category = item.category
  editForm.description = item.description
  editForm.mainImage = item.mainImage
  editForm.ipName = item.ipName
  editForm.characterName = item.characterName
}

function cancelEdit() {
  editingGoods.value = null
}

async function handleSaveEdit() {
  if (!editingGoods.value) return
  loading.value = true
  try {
    await editGoods(editingGoods.value.id, {
      name: editForm.name,
      referencePrice: Number(editForm.referencePrice),
      category: editForm.category,
      description: editForm.description,
      mainImage: editForm.mainImage,
      ipName: editForm.ipName,
      characterName: editForm.characterName,
    })
    editingGoods.value = null
    await loadGoods()
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="page-head">
    <div>
      <p class="eyebrow">商品管理</p>
      <h1>商品库管理</h1>
      <p>管理员可以查询、添加、启用、下架和编辑商品信息。</p>
    </div>
    <button class="primary" type="button" @click="openCreateModal">添加商品</button>
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
      <option value="active">正常</option>
      <option value="inactive">未启用</option>
      <option value="frozen">冻结</option>
      <option value="archived">归档</option>
    </select>
    <select v-model="filterCategory" @change="handleFilter">
      <option value="">全部分类</option>
      <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
    </select>
    <button class="primary" type="button" :disabled="loading" @click="handleSearch">{{ loading ? '加载中' : '查询商品' }}</button>
  </section>

  <section class="table-panel">
    <div class="section-head">
      <div><p class="eyebrow">商品列表</p><h2>全部商品</h2></div>
      <span>共 {{ totalCount }} 条数据</span>
    </div>
    <div v-if="!goods.length" class="empty-state">
      <strong>暂无商品数据</strong>
    </div>
    <div v-else class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>商品</th><th>编号</th><th>分类</th><th>创建人</th><th>价格</th><th>库存</th><th>提交时间</th><th>状态</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in goods" :key="row.id">
            <td>
              <div class="goods-cell">
                <img :src="row.mainImage" :alt="row.name" />
                <div><strong>{{ row.name }}</strong><span>{{ row.ipName }} · {{ row.characterName }}</span></div>
              </div>
            </td>
            <td class="muted">{{ row.id }}</td>
            <td>{{ row.category }}</td>
            <td>{{ row.seller || '管理员' }}</td>
            <td class="price">¥{{ row.referencePrice }}</td>
            <td>{{ row.stock }}</td>
            <td>{{ row.submittedAt }}</td>
            <td><span class="status" :class="row.status">{{ statusMap[row.status] || row.status }}</span></td>
            <td class="actions">
              <button v-if="row.status === 'inactive'" class="primary sm" type="button" @click="handleApprove(row.id)">启用</button>
              <button v-if="row.status === 'inactive'" class="danger sm" type="button" @click="handleReject(row.id)">驳回</button>
              <button v-if="row.status === 'active'" class="warn sm" type="button" @click="handleOffline(row.id)">下架</button>
              <button v-if="row.status === 'frozen'" class="primary sm" type="button" @click="handleApprove(row.id)">解冻</button>
              <button class="secondary sm" type="button" @click="startEdit(row)">编辑</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
    <div class="modal">
      <div class="modal-header">
        <h2>添加商品</h2>
        <button class="modal-close" type="button" @click="closeCreateModal">&times;</button>
      </div>
      <form class="modal-form" @submit.prevent="handleCreateGoods">
        <label><span>商品名称</span><input v-model="createForm.name" type="text" required /></label>
        <label><span>参考价</span><input v-model="createForm.referencePrice" type="number" min="0" step="0.01" required /></label>
        <label><span>IP</span><input v-model="createForm.ipName" type="text" /></label>
        <label><span>角色</span><input v-model="createForm.characterName" type="text" /></label>
        <label>
          <span>分类</span>
          <select v-model="createForm.category">
            <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
          </select>
        </label>
        <label><span>图片地址</span><input v-model="createForm.mainImage" type="text" placeholder="/images/products/example.png" /></label>
        <label class="full"><span>描述</span><textarea v-model="createForm.description" rows="3"></textarea></label>
        <div class="modal-actions">
          <button type="button" class="secondary" @click="closeCreateModal">取消</button>
          <button type="submit" class="primary" :disabled="loading">{{ loading ? '保存中' : '保存商品' }}</button>
        </div>
      </form>
    </div>
  </div>

  <div v-if="editingGoods" class="modal-overlay" @click.self="cancelEdit">
    <div class="modal">
      <div class="modal-header">
        <h2>编辑商品</h2>
        <button class="modal-close" type="button" @click="cancelEdit">&times;</button>
      </div>
      <form class="modal-form" @submit.prevent="handleSaveEdit">
        <label><span>商品名称</span><input v-model="editForm.name" type="text" required /></label>
        <label><span>参考价</span><input v-model="editForm.referencePrice" type="number" min="0" step="0.01" required /></label>
        <label><span>IP</span><input v-model="editForm.ipName" type="text" /></label>
        <label><span>角色</span><input v-model="editForm.characterName" type="text" /></label>
        <label>
          <span>分类</span>
          <select v-model="editForm.category">
            <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
          </select>
        </label>
        <label><span>图片地址</span><input v-model="editForm.mainImage" type="text" /></label>
        <label class="full"><span>描述</span><textarea v-model="editForm.description" rows="3"></textarea></label>
        <div class="modal-actions">
          <button type="button" class="secondary" @click="cancelEdit">取消</button>
          <button type="submit" class="primary" :disabled="loading">{{ loading ? '保存中' : '保存' }}</button>
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
.primary.sm, .secondary.sm, .danger.sm, .warn.sm { height: 32px; padding: 0 12px; font-size: 13px; white-space: nowrap; }
.secondary.sm, .secondary { border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); font-weight: 700; cursor: pointer; font: inherit; }
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
.actions { display: flex; gap: 6px; flex-wrap: wrap; min-width: 210px; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: grid; place-items: center; z-index: 1000; padding: 20px; }
.modal { background: var(--panel); border-radius: 16px; width: min(720px, 100%); max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid var(--line); }
.modal-header h2 { font-size: 22px; }
.modal-close { width: 36px; height: 36px; border: 0; border-radius: 8px; background: var(--soft); color: var(--muted); font-size: 22px; cursor: pointer; display: grid; place-items: center; }
.modal-form { padding: 24px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.modal-form label { display: grid; gap: 6px; }
.modal-form label span { color: var(--muted); font-size: 14px; font-weight: 600; }
.modal-form input, .modal-form textarea, .modal-form select { width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 10px 14px; font: inherit; background: #fff; box-sizing: border-box; }
.modal-form textarea { resize: vertical; min-height: 76px; }
.modal-form .full, .modal-actions { grid-column: 1 / -1; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; padding-top: 8px; }
.secondary { height: 42px; padding: 0 16px; }
@media (max-width: 1100px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 760px) {
  .data-grid, .modal-form { grid-template-columns: 1fr; }
  .toolbar { flex-direction: column; align-items: stretch; }
  .page-head { flex-direction: column; }
}
</style>
