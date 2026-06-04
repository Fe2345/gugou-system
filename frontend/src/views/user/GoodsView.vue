<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { addGoods, getGoodsCategories, getGoodsList, getMyGoodsList, updateGoods, deleteGoods } from '@/api/goods'
import { useUserStore } from '@/stores/user'
import type { GoodsItem } from '@/types/goods'

const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)
const saving = ref(false)
const products = ref<GoodsItem[]>([])
const myProducts = ref<GoodsItem[]>([])
const searchQuery = ref('')
const categories = ref<{ value: string; label: string }[]>([])
const selectedProduct = ref<GoodsItem | null>(null)
const editingProduct = ref<GoodsItem | null>(null)
const showForm = ref(false)
const totalCount = ref(0)
const defaultPageSize = 100

const filterForm = reactive({
  ipName: '',
  characterName: '',
  category: '',
  minPrice: '',
  maxPrice: '',
})

const goodsForm = reactive({
  name: '',
  ipName: '',
  characterName: '',
  category: 'other',
  referencePrice: '',
  description: '',
})
const mainImageFile = ref<File | null>(null)
const mainImagePreview = ref('')

async function loadProducts(keyword?: string) {
  loading.value = true
  try {
    const params: any = { pageSize: defaultPageSize }
    if (keyword?.trim()) params.keyword = keyword.trim()
    if (filterForm.ipName.trim()) params.ipName = filterForm.ipName.trim()
    if (filterForm.characterName.trim()) params.characterName = filterForm.characterName.trim()
    if (filterForm.category) params.category = filterForm.category

    const res = await getGoodsList(params)
    let list = res.data.list
    const minPrice = Number(filterForm.minPrice)
    const maxPrice = Number(filterForm.maxPrice)
    if (!Number.isNaN(minPrice) && filterForm.minPrice !== '') {
      list = list.filter(item => Number(item.referencePrice) >= minPrice)
    }
    if (!Number.isNaN(maxPrice) && filterForm.maxPrice !== '') {
      list = list.filter(item => Number(item.referencePrice) <= maxPrice)
    }
    products.value = list
    totalCount.value = res.data.total
  } catch (e) {
    console.error('加载商品失败', e)
  } finally {
    loading.value = false
  }
}

async function loadMyProducts() {
  if (!userStore.isLoggedIn || userStore.isAdmin) {
    myProducts.value = []
    return
  }
  const res = await getMyGoodsList()
  myProducts.value = res.data.list
}

onMounted(async () => {
  const keyword = route.query.keyword as string
  if (keyword) searchQuery.value = keyword
  const catRes = await getGoodsCategories()
  categories.value = catRes.data
  goodsForm.category = categories.value[0]?.value || 'other'
  await Promise.all([loadProducts(searchQuery.value), loadMyProducts()])
})

function handleSearch() {
  loadProducts(searchQuery.value)
}

function handleFilter() {
  loadProducts(searchQuery.value)
}

function resetFilter() {
  filterForm.ipName = ''
  filterForm.characterName = ''
  filterForm.category = ''
  filterForm.minPrice = ''
  filterForm.maxPrice = ''
  loadProducts(searchQuery.value)
}

function resetGoodsForm() {
  goodsForm.name = ''
  goodsForm.ipName = ''
  goodsForm.characterName = ''
  goodsForm.category = categories.value[0]?.value || 'other'
  goodsForm.referencePrice = ''
  goodsForm.description = ''
  mainImageFile.value = null
  mainImagePreview.value = ''
}

function handleImageChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.length) {
    mainImageFile.value = input.files[0]
    mainImagePreview.value = URL.createObjectURL(input.files[0])
  } else {
    mainImageFile.value = null
    mainImagePreview.value = ''
  }
}

function openCreateForm() {
  editingProduct.value = null
  resetGoodsForm()
  showForm.value = true
}

function canEdit(product: GoodsItem): boolean {
  if (product.status === 'inactive') return true
  if (product.status === 'active' && !product.isInUse) return true
  return false
}

function canDelete(product: GoodsItem): boolean {
  if (product.status === 'inactive') return true
  if (product.status === 'active' && !product.isInUse) return true
  return false
}

function openEditForm(product: GoodsItem) {
  if (!canEdit(product)) return
  editingProduct.value = product
  goodsForm.name = product.name
  goodsForm.ipName = product.ipName
  goodsForm.characterName = product.characterName
  goodsForm.category = product.category
  goodsForm.referencePrice = String(product.referencePrice)
  goodsForm.description = product.description
  mainImageFile.value = null
  mainImagePreview.value = product.mainImage || ''
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingProduct.value = null
}

async function saveGoods() {
  if (!goodsForm.name.trim()) return
  saving.value = true
  try {
    const formData = new FormData()
    formData.append('name', goodsForm.name.trim())
    formData.append('ipName', goodsForm.ipName.trim())
    formData.append('characterName', goodsForm.characterName.trim())
    formData.append('category', goodsForm.category || 'other')
    formData.append('referencePrice', String(Number(goodsForm.referencePrice) || 0))
    formData.append('description', goodsForm.description.trim())
    if (mainImageFile.value) {
      formData.append('mainImage', mainImageFile.value)
    }
    if (editingProduct.value) {
      await updateGoods(editingProduct.value.id, formData)
    } else {
      await addGoods(formData)
    }
    closeForm()
    await Promise.all([loadProducts(searchQuery.value), loadMyProducts()])
  } finally {
    saving.value = false
  }
}

function viewDetail(product: GoodsItem) {
  selectedProduct.value = product
}

function closeDetail() {
  selectedProduct.value = null
}

async function handleDeleteProduct(product: GoodsItem) {
  if (!confirm(`确定要删除商品"${product.name}"吗？此操作不可恢复。`)) return
  try {
    const res = await deleteGoods(product.id)
    if (res.code === 200) {
      await Promise.all([loadProducts(searchQuery.value), loadMyProducts()])
    } else {
      alert(res.message || '删除失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '删除失败')
  }
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    active: '已上架',
    inactive: '待审核',
    frozen: '已驳回',
    archived: '已归档',
  }
  return map[status] || status
}
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="hero">
      <div>
        <p class="eyebrow">商品库</p>
        <h1>商品查询与提交</h1>
        <p>用户可以提交商品并在待审核期间修改信息；审核通过上架后，若商品未被其他功能使用，仍可修改或删除（修改需重新审核）。</p>
      </div>
      <form class="search-box" @submit.prevent="handleSearch">
        <input v-model="searchQuery" type="search" placeholder="搜索商品名称、IP 或角色" />
        <button type="submit" :disabled="loading">{{ loading ? '查询中' : '搜索' }}</button>
      </form>
    </section>

    <section v-if="userStore.isLoggedIn && !userStore.isAdmin" class="submit-panel">
      <div>
        <p class="eyebrow">我的提交</p>
        <h2>上传商品</h2>
      </div>
      <button class="primary" type="button" @click="openCreateForm">添加商品</button>
    </section>

    <section v-if="myProducts.length" class="my-panel">
      <div class="section-head list-head">
        <div>
          <p class="eyebrow">我的商品</p>
          <h2>审核进度</h2>
        </div>
      </div>
      <div class="mine-list">
        <article v-for="p in myProducts" :key="p.id" class="mine-item">
          <img :src="p.mainImage" :alt="p.name" />
          <div>
            <strong>{{ p.name }}</strong>
            <p>{{ p.ipName }} / {{ p.characterName }} / {{ p.category }}</p>
          </div>
          <span class="status-badge" :class="p.status">{{ getStatusText(p.status) }}</span>
          <button v-if="canEdit(p)" class="secondary" type="button" @click="openEditForm(p)">修改</button>
          <button v-else class="secondary" type="button" disabled>不可修改</button>
          <button v-if="canDelete(p)" class="danger-btn" type="button" @click="handleDeleteProduct(p)">删除</button>
        </article>
      </div>
    </section>

    <section class="layout">
      <aside class="filter-panel" aria-label="商品筛选">
        <div class="section-head">
          <p class="eyebrow">筛选</p>
          <h2>查询条件</h2>
        </div>
        <label>
          <span>IP</span>
          <input v-model="filterForm.ipName" type="text" placeholder="输入 IP 名称" />
        </label>
        <label>
          <span>角色</span>
          <input v-model="filterForm.characterName" type="text" placeholder="输入角色名称" />
        </label>
        <label>
          <span>品类</span>
          <select v-model="filterForm.category">
            <option value="">全部品类</option>
            <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
          </select>
        </label>
        <label>
          <span>价格区间</span>
          <div class="price-row">
            <input v-model="filterForm.minPrice" type="number" min="0" placeholder="最低价" />
            <input v-model="filterForm.maxPrice" type="number" min="0" placeholder="最高价" />
          </div>
        </label>
        <div class="filter-actions">
          <button class="primary" type="button" :disabled="loading" @click="handleFilter">应用筛选</button>
          <button class="secondary" type="button" :disabled="loading" @click="resetFilter">重置</button>
        </div>
      </aside>

      <section class="list-panel">
        <div class="section-head list-head">
          <div>
            <p class="eyebrow">已上架商品</p>
            <h2>可查询商品</h2>
          </div>
          <span>显示 {{ products.length }} / {{ totalCount }} 个商品</span>
        </div>

        <div v-if="!products.length" class="empty-state">
          <strong>暂无已上架商品</strong>
          <p>可以调整搜索词或筛选条件后再试。</p>
        </div>
        <div v-else class="product-grid">
          <article v-for="p in products" :key="p.id" class="product-card">
            <img :src="p.mainImage" :alt="p.name" />
            <div class="product-info">
              <div class="product-header">
                <strong class="product-price">¥{{ p.referencePrice }}</strong>
                <span class="status-badge" :class="p.status">{{ getStatusText(p.status) }}</span>
              </div>
              <h3>{{ p.name }}</h3>
              <p class="product-meta">{{ p.ipName }} / {{ p.characterName }} / {{ p.category }}</p>
              <p>{{ p.description }}</p>
            </div>
            <div class="product-actions">
              <button class="action-btn view" type="button" @click="viewDetail(p)">查看详情</button>
            </div>
          </article>
        </div>
      </section>
    </section>
  </main>

  <div v-if="showForm" class="modal-overlay" @click.self="closeForm">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ editingProduct ? (editingProduct.status === 'active' ? '修改商品（将重新审核）' : '修改待审核商品') : '添加商品' }}</h2>
        <button class="modal-close" type="button" @click="closeForm">&times;</button>
      </div>
      <form class="modal-form" @submit.prevent="saveGoods">
        <label><span>商品名称</span><input v-model="goodsForm.name" type="text" required /></label>
        <label><span>参考价</span><input v-model="goodsForm.referencePrice" type="number" min="0" step="0.01" /></label>
        <label><span>IP</span><input v-model="goodsForm.ipName" type="text" /></label>
        <label><span>角色</span><input v-model="goodsForm.characterName" type="text" /></label>
        <label>
          <span>品类</span>
          <select v-model="goodsForm.category">
            <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
          </select>
        </label>
        <label>
          <span>商品图片</span>
          <input type="file" accept="image/*" @change="handleImageChange" />
        </label>
        <div v-if="mainImagePreview" class="image-preview">
          <img :src="mainImagePreview" alt="预览" />
        </div>
        <label class="full"><span>描述</span><textarea v-model="goodsForm.description" rows="3"></textarea></label>
        <div class="modal-actions">
          <button type="button" class="secondary" @click="closeForm">取消</button>
          <button type="submit" class="primary" :disabled="saving">{{ saving ? '保存中' : '提交审核' }}</button>
        </div>
      </form>
    </div>
  </div>

  <div v-if="selectedProduct" class="modal-overlay" @click.self="closeDetail">
    <div class="modal">
      <div class="modal-header">
        <h2>商品详情</h2>
        <button class="modal-close" type="button" @click="closeDetail">&times;</button>
      </div>
      <div class="detail-content">
        <div class="detail-image">
          <img :src="selectedProduct.mainImage" :alt="selectedProduct.name" />
        </div>
        <div class="detail-info">
          <h3>{{ selectedProduct.name }}</h3>
          <div class="detail-meta">
            <span class="detail-price">¥{{ selectedProduct.referencePrice }}</span>
            <span class="status-badge" :class="selectedProduct.status">{{ getStatusText(selectedProduct.status) }}</span>
          </div>
          <div class="detail-fields">
            <div><span>商品编号</span><strong>{{ selectedProduct.id }}</strong></div>
            <div><span>IP</span><strong>{{ selectedProduct.ipName }}</strong></div>
            <div><span>角色</span><strong>{{ selectedProduct.characterName }}</strong></div>
            <div><span>品类</span><strong>{{ selectedProduct.category }}</strong></div>
            <div><span>创建时间</span><strong>{{ selectedProduct.createdAt }}</strong></div>
          </div>
          <p class="detail-desc">{{ selectedProduct.description || '暂无描述' }}</p>
        </div>
      </div>
      <div class="modal-actions">
        <button type="button" class="primary" @click="closeDetail">关闭</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.hero {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(320px, 440px);
  gap: 28px; align-items: center; padding: 36px; border-radius: 10px; color: #fff;
  background: linear-gradient(rgba(10,74,90,0.88), rgba(10,74,90,0.92)),
    url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80") center/cover;
  box-shadow: var(--shadow);
}
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 42px; line-height: 1.16; }
.hero p:last-child { max-width: 660px; margin-top: 14px; color: rgba(255,255,255,0.84); line-height: 1.8; }
.search-box { display: grid; grid-template-columns: minmax(0, 1fr) 92px; gap: 10px; padding: 12px; border: 1px solid rgba(255,255,255,0.28); border-radius: 10px; background: rgba(255,255,255,0.14); }
input, select { width: 100%; height: 46px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; color: var(--ink); background: #fff; outline: none; font: inherit; box-sizing: border-box; }
textarea { font: inherit; }
input:focus, select:focus, textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 4px rgba(15,100,120,0.12); outline: none; }
.search-box input { border: 0; }
.primary, .secondary, .search-box button { min-height: 46px; border-radius: 8px; font-weight: 800; cursor: pointer; font: inherit; }
.primary, .search-box button { border: 0; color: #fff; background: var(--accent); }
.secondary { border: 1px solid var(--line); color: var(--ink); background: var(--panel); }
.secondary:disabled { opacity: 0.55; cursor: not-allowed; }
.primary:hover, .search-box button:hover { background: var(--accent-dark); }
.submit-panel, .my-panel { margin-top: 20px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.submit-panel { display: flex; justify-content: space-between; gap: 16px; align-items: center; padding: 20px 22px; }
.my-panel { padding: 22px; }
.mine-list { display: grid; gap: 10px; }
.mine-item { display: grid; grid-template-columns: 56px minmax(0, 1fr) auto auto auto; gap: 12px; align-items: center; padding: 12px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
.danger-btn { min-height: 32px; border: 1px solid #fecaca; border-radius: 6px; padding: 0 12px; color: #be123c; background: #fff; font-weight: 700; cursor: pointer; font: inherit; font-size: 13px; }
.danger-btn:hover { background: #fee2e2; }
.mine-item img { width: 56px; height: 56px; border-radius: 8px; object-fit: cover; background: var(--soft); }
.mine-item p { color: var(--muted); font-size: 13px; margin-top: 4px; }
.layout { display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 20px; margin-top: 20px; }
.filter-panel, .list-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.filter-panel { align-self: start; display: grid; gap: 16px; padding: 22px; }
.section-head { margin-bottom: 16px; }
.section-head .eyebrow { color: var(--accent); }
h2 { font-size: 24px; }
label { display: grid; gap: 8px; color: var(--muted); font-size: 14px; }
.price-row, .filter-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.list-panel { padding: 24px; }
.list-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.list-head span { color: var(--muted); }
.empty-state { min-height: 180px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); }
.empty-state strong { display: block; margin-bottom: 8px; color: var(--ink); font-size: 18px; }
.product-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.product-card { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; background: #fff; }
.product-card img { width: 100%; height: 300px; object-fit: contain; background: #f3f7f8; }
.product-info { display: grid; gap: 8px; padding: 16px; }
.product-info h3 { font-size: 17px; }
.product-info p { color: var(--muted); font-size: 14px; line-height: 1.6; }
.product-price { color: var(--accent); font-size: 20px; line-height: 1; font-weight: 800; }
.product-header { display: flex; justify-content: space-between; gap: 10px; align-items: center; }
.product-meta { color: var(--accent); font-size: 14px; margin-bottom: 6px; }
.status-badge { display: inline-flex; align-items: center; height: 28px; padding: 0 12px; border-radius: 999px; font-size: 13px; font-weight: 700; }
.status-badge.active { background: #dcfce7; color: #15803d; }
.status-badge.inactive { background: #fef3c7; color: #b45309; }
.status-badge.frozen { background: #fee2e2; color: #be123c; }
.status-badge.archived { background: #e5e7eb; color: #6b7280; }
.product-actions { display: flex; gap: 8px; padding: 12px 16px; border-top: 1px solid var(--line); }
.action-btn { flex: 1; height: 38px; border: 0; border-radius: 8px; font-size: 14px; font-weight: 700; cursor: pointer; font: inherit; }
.action-btn.view { background: var(--soft); color: var(--accent); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: grid; place-items: center; z-index: 1000; padding: 20px; }
.modal { background: var(--panel); border-radius: 16px; width: min(760px, 100%); max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 24px 28px; border-bottom: 1px solid var(--line); }
.modal-close { width: 40px; height: 40px; border: 0; border-radius: 10px; background: var(--soft); color: var(--muted); font-size: 24px; cursor: pointer; display: grid; place-items: center; }
.modal-form { padding: 24px 28px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.modal-form input[type="file"] { padding: 8px; }
.modal-form input, .modal-form textarea, .modal-form select { width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 10px 14px; box-sizing: border-box; background: #fff; }
.image-preview { grid-column: 1 / -1; }
.image-preview img { max-width: 200px; max-height: 200px; border-radius: 8px; object-fit: contain; border: 1px solid var(--line); }
.modal-form textarea { resize: vertical; min-height: 80px; }
.modal-form .full, .modal-actions { grid-column: 1 / -1; }
.detail-content { display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 24px; padding: 28px; }
.detail-image { border-radius: 12px; overflow: hidden; background: var(--soft); }
.detail-image img { width: 100%; height: 280px; object-fit: contain; }
.detail-info { display: grid; gap: 14px; }
.detail-info h3 { font-size: 26px; }
.detail-meta { display: flex; align-items: center; gap: 14px; }
.detail-price { color: var(--accent); font-size: 34px; font-weight: 800; }
.detail-fields { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.detail-fields div { display: grid; gap: 4px; }
.detail-fields span { color: var(--muted); font-size: 13px; }
.detail-fields strong { font-size: 16px; }
.detail-desc { color: var(--muted); line-height: 1.7; }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; padding-top: 8px; }
.detail-content + .modal-actions { padding: 20px 28px; border-top: 1px solid var(--line); }

@media (max-width: 980px) {
  .hero, .layout, .detail-content { grid-template-columns: 1fr; }
  .mine-item { grid-template-columns: 56px minmax(0, 1fr); }
}
@media (max-width: 620px) {
  .page { width: min(100% - 20px, 1180px); }
  .hero, .list-panel { padding: 20px; }
  h1 { font-size: 30px; }
  .search-box, .price-row, .filter-actions, .product-grid, .detail-fields, .modal-form { grid-template-columns: 1fr; }
}
</style>
