<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { getGoodsList, addGoods, updateGoods, deleteGoods, getGoodsCategories } from '@/api/goods'
import type { GoodsItem } from '@/types/goods'

const route = useRoute()
const selectedImage = ref('')
const loading = ref(false)
const products = ref<GoodsItem[]>([])
const searchQuery = ref('')
const categories = ref<string[]>([])

// 弹窗状态
const selectedProduct = ref<GoodsItem | null>(null)
const editingProduct = ref<GoodsItem | null>(null)
const showDeleteConfirm = ref(false)
const productToDelete = ref<GoodsItem | null>(null)

const form = reactive({
  name: '',
  price: '',
  ip: '',
  role: '',
  category: '',
})

const editForm = reactive({
  name: '',
  price: '',
  ip: '',
  role: '',
  category: '',
  description: '',
})

const filterForm = reactive({
  ip: '',
  role: '',
  category: '',
  timeRange: '',
  minPrice: '',
  maxPrice: '',
})

// 加载产品列表
async function loadProducts(keyword?: string) {
  loading.value = true
  try {
    const res = await getGoodsList({ keyword })
    products.value = res.data.list
  } catch (e) {
    console.error('加载产品失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const keyword = route.query.keyword as string
  if (keyword) {
    searchQuery.value = keyword
    loadProducts(keyword)
  } else {
    loadProducts()
  }
  const catRes = await getGoodsCategories()
  categories.value = catRes.data
})

function onImageChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.addEventListener('load', () => {
    selectedImage.value = reader.result as string
  })
  reader.readAsDataURL(file)
}

async function handleAddProduct() {
  const name = form.name.trim()
  const price = form.price.trim()
  if (!name || !price) return

  loading.value = true
  try {
    await addGoods({
      name,
      price: Number(price),
      image: selectedImage.value,
      ip: form.ip || 'IP 待定',
      role: form.role || '角色待定',
      category: form.category || '品类待定',
    })
    form.name = ''
    form.price = ''
    form.ip = ''
    form.role = ''
    form.category = ''
    selectedImage.value = ''
    loadProducts()
  } catch (e) {
    console.error('添加产品失败', e)
  } finally {
    loading.value = false
  }
}

async function handleSearch() {
  await loadProducts(searchQuery.value)
}

async function handleFilter() {
  loading.value = true
  try {
    const params: any = {}
    if (filterForm.category) params.category = filterForm.category
    const res = await getGoodsList(params)
    products.value = res.data.list
  } catch (e) {
    console.error('筛选失败', e)
  } finally {
    loading.value = false
  }
}

// 查看详情
function viewDetail(product: GoodsItem) {
  selectedProduct.value = product
}

function closeDetail() {
  selectedProduct.value = null
}

// 编辑商品
function startEdit(product: GoodsItem) {
  editingProduct.value = product
  editForm.name = product.name
  editForm.price = String(product.price)
  editForm.ip = product.ip
  editForm.role = product.role
  editForm.category = product.category
  editForm.description = product.description
}

function cancelEdit() {
  editingProduct.value = null
}

async function handleSaveEdit() {
  if (!editingProduct.value) return
  loading.value = true
  try {
    await updateGoods(editingProduct.value.id, {
      name: editForm.name,
      price: Number(editForm.price),
      ip: editForm.ip,
      role: editForm.role,
      category: editForm.category,
      description: editForm.description,
    })
    editingProduct.value = null
    await loadProducts()
  } catch (e) {
    console.error('编辑失败', e)
  } finally {
    loading.value = false
  }
}

// 删除商品
function confirmDelete(product: GoodsItem) {
  productToDelete.value = product
  showDeleteConfirm.value = true
}

function cancelDelete() {
  showDeleteConfirm.value = false
  productToDelete.value = null
}

async function handleDelete() {
  if (!productToDelete.value) return
  loading.value = true
  try {
    await deleteGoods(productToDelete.value.id)
    showDeleteConfirm.value = false
    productToDelete.value = null
    await loadProducts()
  } catch (e) {
    console.error('删除失败', e)
  } finally {
    loading.value = false
  }
}

// 上下架
async function toggleStatus(product: GoodsItem) {
  const newStatus = product.status === 'approved' ? 'pending' : 'approved'
  loading.value = true
  try {
    await updateGoods(product.id, { status: newStatus })
    await loadProducts()
  } catch (e) {
    console.error('状态更新失败', e)
  } finally {
    loading.value = false
  }
}

// 状态文本
function getStatusText(status: string) {
  const map: Record<string, string> = {
    pending: '待审核',
    approved: '已上架',
    rejected: '已下架',
  }
  return map[status] || status
}

function getStatusClass(status: string) {
  return status
}
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="hero">
      <div>
        <p class="eyebrow">产品管理中心</p>
        <h1>我的产品库</h1>
        <p>按产品名称、IP或角色查询并集中管理产品信息，包括自录入价格的参考值和查询历史数据</p>
      </div>
      <form class="search-box" @submit.prevent="handleSearch">
        <input v-model="searchQuery" type="search" placeholder="搜索产品名称、IP或角色">
        <button type="submit" :disabled="loading">搜索</button>
      </form>
    </section>

    <section class="layout">
      <aside class="filter-panel" aria-label="信息筛选">
        <div class="section-head">
          <p class="eyebrow">条件筛选</p>
          <h2>筛选条件</h2>
        </div>
        <label>
          <span>IP</span>
          <input v-model="filterForm.ip" type="text" placeholder="请输入 IP 名称">
        </label>
        <label>
          <span>角色</span>
          <input v-model="filterForm.role" type="text" placeholder="请输入角色名称">
        </label>
        <label>
          <span>品类</span>
          <select v-model="filterForm.category">
            <option value="">全部品类</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </label>
        <label>
          <span>发行时间</span>
          <select v-model="filterForm.timeRange">
            <option value="">不限时间</option><option value="1m">近一个月</option><option value="3m">近三个月</option>
            <option value="1y">近一年</option><option value="old">早期发行</option>
          </select>
        </label>
        <label>
          <span>价格区间</span>
          <div class="price-row">
            <input v-model="filterForm.minPrice" type="number" placeholder="最低价">
            <input v-model="filterForm.maxPrice" type="number" placeholder="最高价">
          </div>
        </label>
        <button class="secondary" type="button" :disabled="loading" @click="handleFilter">应用筛选</button>
      </aside>

      <section class="content">
        <section class="upload-panel">
          <div class="section-head">
            <p class="eyebrow">自定义产品</p>
            <h2>添加产品信息</h2>
          </div>
          <form class="product-form" @submit.prevent="handleAddProduct">
            <label class="upload-box">
              <input name="image" type="file" accept="image/*" @change="onImageChange">
              <span v-if="!selectedImage">上传产品图片</span>
              <img v-else :src="selectedImage" alt="产品图片预览">
            </label>
            <div class="form-grid">
              <label>
                <span>产品名称</span>
                <input v-model="form.name" type="text" placeholder="请输入产品名称">
              </label>
              <label>
                <span>参考价</span>
                <input v-model="form.price" type="number" min="0" step="0.01" placeholder="请输入自定义价格">
              </label>
              <label>
                <span>IP</span>
                <input v-model="form.ip" type="text" placeholder="选填">
              </label>
              <label>
                <span>角色</span>
                <input v-model="form.role" type="text" placeholder="选填">
              </label>
              <label>
                <span>品类</span>
                <input v-model="form.category" type="text" placeholder="选填">
              </label>
              <button class="primary" type="submit" :disabled="loading">{{ loading ? '添加中...' : '添加到产品列表' }}</button>
            </div>
          </form>
        </section>

        <section class="list-panel">
          <div class="section-head list-head">
            <div>
              <p class="eyebrow">产品列表</p>
              <h2>产品目录</h2>
            </div>
            <span>{{ products.length }} 个产品</span>
          </div>

          <div v-if="!products.length" class="empty-state">
            <strong>暂无产品数据</strong>
          </div>
          <div v-else class="product-grid">
            <article v-for="(p, i) in products" :key="i" class="product-card">
              <img :src="p.image" :alt="p.name">
              <div class="product-info">
                <div class="product-header">
                  <strong class="product-price">¥ {{ p.price }}</strong>
                  <span class="status-badge" :class="getStatusClass(p.status)">{{ getStatusText(p.status) }}</span>
                </div>
                <h3>{{ p.name }}</h3>
                <p class="product-meta">{{ p.ip }} · {{ p.role }} · {{ p.category }}</p>
                <p>{{ p.description }}</p>
              </div>
              <div class="product-actions">
                <button class="action-btn view" @click="viewDetail(p)">详情</button>
                <button class="action-btn edit" @click="startEdit(p)">编辑</button>
                <button class="action-btn toggle" @click="toggleStatus(p)">
                  {{ p.status === 'approved' ? '下架' : '上架' }}
                </button>
                <button class="action-btn delete" @click="confirmDelete(p)">删除</button>
              </div>
            </article>
          </div>
        </section>

        <section class="detail-panel">
          <div class="section-head">
            <p class="eyebrow">产品详情</p>
            <h2>详情信息</h2>
          </div>
          <div class="empty-detail">
            <p>点击产品卡片的"详情"按钮查看完整信息</p>
          </div>
        </section>
      </section>
    </section>
  </main>

  <!-- 详情弹窗 -->
  <div v-if="selectedProduct" class="modal-overlay" @click.self="closeDetail">
    <div class="modal modal-detail">
      <div class="modal-header">
        <h2>商品详情</h2>
        <button class="modal-close" @click="closeDetail">&times;</button>
      </div>
      <div class="detail-content">
        <div class="detail-image">
          <img :src="selectedProduct.image" :alt="selectedProduct.name">
        </div>
        <div class="detail-info">
          <h3>{{ selectedProduct.name }}</h3>
          <div class="detail-meta">
            <span class="detail-price">¥ {{ selectedProduct.price }}</span>
            <span class="status-badge" :class="getStatusClass(selectedProduct.status)">
              {{ getStatusText(selectedProduct.status) }}
            </span>
          </div>
          <div class="detail-fields">
            <div class="field"><label>IP</label><span>{{ selectedProduct.ip }}</span></div>
            <div class="field"><label>角色</label><span>{{ selectedProduct.role }}</span></div>
            <div class="field"><label>品类</label><span>{{ selectedProduct.category }}</span></div>
            <div class="field"><label>创建时间</label><span>{{ selectedProduct.createdAt }}</span></div>
          </div>
          <p class="detail-desc">{{ selectedProduct.description }}</p>
        </div>
      </div>
      <div class="modal-actions">
        <button type="button" class="secondary" @click="closeDetail">关闭</button>
        <button type="button" class="primary" @click="closeDetail; startEdit(selectedProduct)">编辑</button>
      </div>
    </div>
  </div>

  <!-- 编辑弹窗 -->
  <div v-if="editingProduct" class="modal-overlay" @click.self="cancelEdit">
    <div class="modal">
      <div class="modal-header">
        <h2>编辑商品</h2>
        <button class="modal-close" @click="cancelEdit">&times;</button>
      </div>
      <form class="modal-form" @submit.prevent="handleSaveEdit">
        <label>
          <span>产品名称</span>
          <input v-model="editForm.name" type="text" required>
        </label>
        <label>
          <span>参考价</span>
          <input v-model="editForm.price" type="number" min="0" step="0.01" required>
        </label>
        <label>
          <span>IP</span>
          <input v-model="editForm.ip" type="text">
        </label>
        <label>
          <span>角色</span>
          <input v-model="editForm.role" type="text">
        </label>
        <label>
          <span>品类</span>
          <input v-model="editForm.category" type="text">
        </label>
        <label>
          <span>描述</span>
          <textarea v-model="editForm.description" rows="3"></textarea>
        </label>
        <div class="modal-actions">
          <button type="button" class="secondary" @click="cancelEdit">取消</button>
          <button type="submit" class="primary" :disabled="loading">{{ loading ? '保存中...' : '保存' }}</button>
        </div>
      </form>
    </div>
  </div>

  <!-- 删除确认弹窗 -->
  <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="cancelDelete">
    <div class="modal modal-confirm">
      <div class="modal-header">
        <h2>确认删除</h2>
        <button class="modal-close" @click="cancelDelete">&times;</button>
      </div>
      <div class="modal-body">
        <p>确定要删除商品"{{ productToDelete?.name }}"吗？</p>
        <p class="warning">此操作不可恢复。</p>
      </div>
      <div class="modal-actions">
        <button type="button" class="secondary" @click="cancelDelete">取消</button>
        <button type="button" class="danger" :disabled="loading" @click="handleDelete">
          {{ loading ? '删除中...' : '确认删除' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.hero {
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(360px, 440px);
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
input, select { width: 100%; height: 46px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; color: var(--ink); background: #fff; outline: none; font: inherit; }
input:focus, select:focus { border-color: var(--accent); box-shadow: 0 0 0 4px rgba(15,100,120,0.12); }
.search-box input { border: 0; }
.primary, .secondary, .search-box button { min-height: 46px; border: 0; border-radius: 8px; color: #fff; background: var(--accent); font-weight: 800; cursor: pointer; font: inherit; }
.primary:hover, .secondary:hover, .search-box button:hover { background: var(--accent-dark); }
.layout { display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 20px; margin-top: 20px; }
.filter-panel, .upload-panel, .list-panel, .detail-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.filter-panel { align-self: start; display: grid; gap: 16px; padding: 22px; }
.section-head { margin-bottom: 16px; }
.section-head .eyebrow { color: var(--accent); }
h2 { font-size: 24px; }
label { display: grid; gap: 8px; color: var(--muted); font-size: 14px; }
.price-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.content { display: grid; gap: 20px; }
.upload-panel, .list-panel, .detail-panel { padding: 24px; }
.product-form { display: grid; grid-template-columns: 220px minmax(0, 1fr); gap: 18px; }
.upload-box { min-height: 220px; display: grid; place-items: center; border: 1px dashed #b8c9cf; border-radius: 10px; color: var(--accent); background: var(--soft); overflow: hidden; cursor: pointer; }
.upload-box input { display: none; }
.upload-box img { width: 100%; height: 100%; object-fit: cover; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.form-grid .primary { align-self: end; }
.list-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; }

.empty-state { min-height: 180px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); }
.empty-state strong { display: block; margin-bottom: 8px; color: var(--ink); font-size: 18px; }
.product-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.product-card { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; background: #fff; }
.product-card img { width: 100%; height: 320px; object-fit: contain; background: #f3f7f8; }
.product-info { display: grid; gap: 8px; padding: 16px; }
.product-info h3 { font-size: 17px; }
.product-info p { color: var(--muted); font-size: 14px; line-height: 1.6; }
.product-price { color: var(--accent); font-size: 20px; line-height: 1; font-weight: 800; }
.product-header { display: flex; justify-content: space-between; align-items: center; }
.product-meta { color: var(--accent); font-size: 14px; margin-bottom: 6px; }
.status-badge { display: inline-flex; align-items: center; height: 28px; padding: 0 12px; border-radius: 999px; font-size: 14px; font-weight: 700; }
.status-badge.approved { background: #dcfce7; color: #15803d; }
.status-badge.pending { background: #fef3c7; color: #b45309; }
.status-badge.rejected { background: #fee2e2; color: #be123c; }
.product-actions { display: flex; gap: 8px; padding: 12px 16px; border-top: 1px solid var(--line); }
.action-btn { flex: 1; height: 36px; border: 0; border-radius: 8px; font-size: 14px; font-weight: 700; cursor: pointer; font: inherit; transition: background 0.2s; }
.action-btn.view { background: var(--soft); color: var(--accent); }
.action-btn.view:hover { background: #eaf6f8; }
.action-btn.edit { background: #dbeafe; color: #1d4ed8; }
.action-btn.edit:hover { background: #bfdbfe; }
.action-btn.toggle { background: #fef3c7; color: #b45309; }
.action-btn.toggle:hover { background: #fde68a; }
.action-btn.delete { background: #fee2e2; color: #be123c; }
.action-btn.delete:hover { background: #fecaca; }

/* 详情弹窗内容 */
.detail-content { display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 24px; padding: 28px; }
.detail-image { border-radius: 12px; overflow: hidden; background: var(--soft); }
.detail-image img { width: 100%; height: 280px; object-fit: contain; }
.detail-info { display: grid; gap: 14px; }
.detail-info h3 { font-size: 26px; }
.detail-meta { display: flex; align-items: center; gap: 14px; }
.detail-price { color: var(--accent); font-size: 38px; font-weight: 800; }
.detail-fields { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.field { display: grid; gap: 6px; }
.field label { color: var(--muted); font-size: 16px; }
.field span { font-weight: 600; font-size: 18px; }
.detail-desc { color: var(--muted); line-height: 1.6; margin-top: 12px; font-size: 18px; }

/* 弹窗样式 */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: grid; place-items: center; z-index: 1000; padding: 20px; }
.modal { background: var(--panel); border-radius: 16px; width: min(600px, 100%); max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
.modal-detail { width: min(720px, 100%); }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 24px 28px; border-bottom: 1px solid var(--line); }
.modal-header h2 { font-size: 28px; }
.modal-close { width: 40px; height: 40px; border: 0; border-radius: 10px; background: var(--soft); color: var(--muted); font-size: 24px; cursor: pointer; display: grid; place-items: center; }
.modal-close:hover { background: #fee2e2; color: #be123c; }
.modal-form { padding: 28px; display: grid; gap: 18px; }
.modal-form label { display: grid; gap: 8px; }
.modal-form label span { color: var(--muted); font-size: 18px; font-weight: 600; }
.modal-form input, .modal-form textarea { width: 100%; border: 1px solid var(--line); border-radius: 10px; padding: 14px 18px; font: inherit; font-size: 18px; background: #fff; box-sizing: border-box; }
.modal-form textarea { resize: vertical; min-height: 80px; }
.modal-form input:focus, .modal-form textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(15,100,120,0.1); outline: none; }
.modal-actions { display: flex; gap: 14px; justify-content: flex-end; padding: 20px 28px; border-top: 1px solid var(--line); }
.modal-confirm .modal-body { padding: 28px; }
.modal-confirm .modal-body p { margin: 0; line-height: 1.6; font-size: 20px; }
.modal-confirm .modal-body .warning { color: #be123c; margin-top: 10px; font-size: 18px; }
.modal-confirm .modal-actions { padding: 0 28px 28px; border-top: 0; }
.danger { min-height: 56px; border: 0; border-radius: 12px; padding: 0 24px; color: #fff; background: #be123c; font-weight: 800; cursor: pointer; font: inherit; font-size: 18px; }
.danger:hover { background: #9f1239; }
.danger:disabled { opacity: 0.6; cursor: not-allowed; }

@media (max-width: 980px) {
  .hero, .layout, .product-form { grid-template-columns: 1fr; }
  .product-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .detail-content { grid-template-columns: 1fr; }
  .detail-fields { grid-template-columns: 1fr; }
}
@media (max-width: 620px) {
  .page { width: min(100% - 20px, 1180px); }
  .hero, .upload-panel, .list-panel, .detail-panel { padding: 20px; }
  h1 { font-size: 30px; }
  .search-box, .form-grid, .price-row, .product-grid { grid-template-columns: 1fr; }
  .product-actions { flex-wrap: wrap; }
  .action-btn { flex: 1 1 calc(50% - 4px); }
}
</style>
