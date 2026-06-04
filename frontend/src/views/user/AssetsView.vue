<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { getAssetsList, addAsset, updateAsset, deleteAsset, operateAsset } from '@/api/assets'
import { getGoodsList, getGoodsCategories } from '@/api/goods'
import { publishToMarket, cancelListing, getMyListings } from '@/api/market'
import type { AssetItem, AssetForm, AssetSummary, AssetStatus } from '@/types/assets'
import type { GoodsItem } from '@/types/goods'

const router = useRouter()
const loading = ref(false)
const assets = ref<AssetItem[]>([])
const summary = ref<AssetSummary>({ totalCount: 0, categoryCount: 0, totalCost: 0, totalValue: 0, valueChange: 0 })
const searchQuery = ref('')
const statusFilter = ref('all')
const sortBy = ref('time')

// 弹窗状态
const showAddModal = ref(false)
const showDetailModal = ref(false)
const showEditModal = ref(false)
const showDeleteConfirm = ref(false)
const showOperationModal = ref(false)

const selectedAsset = ref<AssetItem | null>(null)
const assetToDelete = ref<AssetItem | null>(null)

// 上架弹窗
const showListModal = ref(false)
const listPrice = ref<number | null>(null)
const listDescription = ref('')

// 下架弹窗
const showDelistModal = ref(false)

const addForm = reactive<AssetForm>({
  productId: '',
  productName: '',
  ipName: '',
  characterName: '',
  category: '',
  quantity: 1,
  acquirePrice: 0,
  description: '',
})
const acquirePriceError = ref(false)

// 商品库搜索
const productSearchQuery = ref('')
const productSearchResults = ref<GoodsItem[]>([])
const productSearchLoading = ref(false)
const showProductDropdown = ref(false)

async function searchProducts() {
  const keyword = productSearchQuery.value.trim()
  if (!keyword) {
    productSearchResults.value = []
    showProductDropdown.value = false
    return
  }
  productSearchLoading.value = true
  try {
    const res = await getGoodsList({ keyword, pageSize: 20 })
    if (res.code === 200) {
      productSearchResults.value = res.data.list
      showProductDropdown.value = res.data.list.length > 0
    }
  } catch (e) {
    console.error('搜索商品失败', e)
  } finally {
    productSearchLoading.value = false
  }
}

function selectProduct(product: GoodsItem) {
  addForm.productId = product.id
  addForm.productName = product.name
  addForm.ipName = product.ipName
  addForm.characterName = product.characterName
  addForm.category = product.category
  productSearchQuery.value = product.name
  showProductDropdown.value = false
}

function clearProductSelection() {
  addForm.productId = ''
  productSearchQuery.value = ''
  productSearchResults.value = []
  showProductDropdown.value = false
}

const categories = ref<{ value: string; label: string }[]>([])

const addFormErrors = reactive<Record<string, string>>({})

function clearAddError(field: string) {
  delete addFormErrors[field]
}

const editForm = reactive({
  productName: '',
  ipName: '',
  characterName: '',
  category: '',
  quantity: 1,
  acquirePrice: 0,
  currentValue: 0,
  description: '',
})

// 加载资产列表
async function loadAssets() {
  loading.value = true
  try {
    const res = await getAssetsList({
      keyword: searchQuery.value || undefined,
      status: statusFilter.value !== 'all' ? statusFilter.value : undefined,
      sortBy: sortBy.value,
    })
    if (res.code === 200) {
      assets.value = res.data.list
      summary.value = res.data.summary
    }
  } catch (e) {
    console.error('加载资产失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  loadAssets()
  try {
    const catRes = await getGoodsCategories()
    if (catRes.code === 200) categories.value = catRes.data
  } catch { /* 品类列表加载失败不影响主流程 */ }
})

// 搜索筛选
function handleSearch() {
  loadAssets()
}

function handleFilter() {
  loadAssets()
}

// 添加资产
function openAddModal() {
  addForm.productId = ''
  addForm.productName = ''
  addForm.ipName = ''
  addForm.characterName = ''
  addForm.category = categories.value[0]?.value || 'other'
  addForm.quantity = 1
  addForm.acquirePrice = 0
  addForm.description = ''
  Object.keys(addFormErrors).forEach(k => delete addFormErrors[k])
  acquirePriceError.value = false
  productSearchQuery.value = ''
  productSearchResults.value = []
  showProductDropdown.value = false
  showAddModal.value = true
}

function closeAddModal() {
  showAddModal.value = false
}

function validateAddForm(): boolean {
  let valid = true
  if (!addForm.productName) {
    addFormErrors.productName = '谷子名称不能为空'
    valid = false
  }
  if (!addForm.ipName || !addForm.ipName.trim()) {
    addFormErrors.ipName = 'IP不能为空'
    valid = false
  }
  if (!addForm.characterName || !addForm.characterName.trim()) {
    addFormErrors.characterName = '角色不能为空'
    valid = false
  }
  if (!addForm.category || !addForm.category.trim()) {
    addFormErrors.category = '品类不能为空'
    valid = false
  }
  if (!addForm.acquirePrice && addForm.acquirePrice !== 0) {
    addFormErrors.acquirePrice = '入手价不能为空'
    valid = false
  } else if (addForm.acquirePrice <= 0) {
    addFormErrors.acquirePrice = '入手价不得小于或等于0'
    valid = false
  }
  return valid
}

async function handleAdd() {
  if (!validateAddForm()) return
  acquirePriceError.value = false
  if (!addForm.acquirePrice || addForm.acquirePrice <= 0) {
    acquirePriceError.value = true
    return
  }
  if (!addForm.productName) return
  loading.value = true
  try {
    const res = await addAsset(addForm)
    if (res.code === 200) {
      showAddModal.value = false
      // 刷新列表，但不因刷新失败而提示添加失败
      loadAssets().catch(() => {})
    } else {
      alert(res.message || '添加失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '添加资产失败')
  } finally {
    loading.value = false
  }
}

// 查看详情
function viewDetail(asset: AssetItem) {
  selectedAsset.value = asset
  showDetailModal.value = true
}

function closeDetailModal() {
  showDetailModal.value = false
  selectedAsset.value = null
}

// 编辑资产
function startEdit(asset: AssetItem) {
  selectedAsset.value = asset
  editForm.productName = asset.productName
  editForm.ipName = asset.ipName
  editForm.characterName = asset.characterName
  editForm.category = asset.category
  editForm.quantity = asset.quantity
  editForm.acquirePrice = asset.acquirePrice
  editForm.currentValue = asset.currentValue
  editForm.description = asset.description
  showEditModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
  selectedAsset.value = null
}

async function handleSaveEdit() {
  if (!selectedAsset.value) return
  loading.value = true
  try {
    const res = await updateAsset(selectedAsset.value.id, {
      productName: editForm.productName,
      ipName: editForm.ipName,
      characterName: editForm.characterName,
      category: editForm.category,
      quantity: editForm.quantity,
      acquirePrice: editForm.acquirePrice,
      currentValue: editForm.currentValue,
      description: editForm.description,
    })
    if (res.code === 200) {
      showEditModal.value = false
      loadAssets().catch(() => {})
    } else {
      alert(res.message || '保存失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '编辑失败')
  } finally {
    loading.value = false
  }
}

// 删除资产
function confirmDelete(asset: AssetItem) {
  assetToDelete.value = asset
  showDeleteConfirm.value = true
}

function cancelDelete() {
  showDeleteConfirm.value = false
  assetToDelete.value = null
}

async function handleDelete() {
  if (!assetToDelete.value) return
  loading.value = true
  try {
    const res = await deleteAsset(assetToDelete.value.id)
    if (res.code === 200) {
      showDeleteConfirm.value = false
      assetToDelete.value = null
      loadAssets().catch(() => {})
    } else {
      alert(res.message || '删除失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '删除失败')
  } finally {
    loading.value = false
  }
}

// 上架到交易市场
function openListModal(asset: AssetItem) {
  selectedAsset.value = asset
  listPrice.value = null
  listDescription.value = ''
  showListModal.value = true
}

function closeListModal() {
  showListModal.value = false
  selectedAsset.value = null
}

async function handleListToMarket() {
  if (!selectedAsset.value || !listPrice.value || listPrice.value <= 0) {
    alert('请输入有效的售价')
    return
  }
  loading.value = true
  try {
    // 创建市场挂单（后端会自动锁定资产并更新状态）
    const marketRes = await publishToMarket({
      product_id: selectedAsset.value.productId,
      asset_id: selectedAsset.value.id,
      price: listPrice.value,
      quantity: selectedAsset.value.quantity,
      description: listDescription.value || selectedAsset.value.description,
    })
    if (marketRes.code !== 200) {
      alert(marketRes.message || '上架失败')
      return
    }
    showListModal.value = false
    loadAssets().catch(() => {})
  } catch (e: any) {
    alert(e?.response?.data?.message || '上架失败')
  } finally {
    loading.value = false
  }
}

// 下架（取消交易市场挂单）
function openDelistModal(asset: AssetItem) {
  selectedAsset.value = asset
  showDelistModal.value = true
}

function closeDelistModal() {
  showDelistModal.value = false
  selectedAsset.value = null
}

async function handleDelistFromMarket() {
  if (!selectedAsset.value) return
  loading.value = true
  try {
    // 1. 查找该资产的活跃挂单
    const myListingsRes = await getMyListings({ page: 1, page_size: 100 })
    if (myListingsRes.code !== 200) {
      alert('获取挂单信息失败')
      return
    }
    const activeListing = myListingsRes.data.results.find(
      (item) => item.product_id === selectedAsset!.value!.productId && item.status === 'active'
    )
    if (!activeListing) {
      alert('未找到该资产的活跃挂单')
      return
    }
    // 2. 取消市场挂单（后端会自动恢复资产状态为持有中）
    const cancelRes = await cancelListing(activeListing.listing_id)
    if (cancelRes.code !== 200) {
      alert(cancelRes.message || '取消挂单失败')
      return
    }
    showDelistModal.value = false
    loadAssets().catch(() => {})
  } catch (e: any) {
    alert(e?.response?.data?.message || '下架失败')
  } finally {
    loading.value = false
  }
}

// 状态文本
function getStatusText(status: string) {
  const map: Record<string, string> = {
    holding: '持有中',
    selling: '出售中',
    exchanging: '换物中',
    sold: '已售出',
    invalid: '已失效',
  }
  return map[status] || status
}

function getStatusClass(status: string) {
  return status
}

// 格式化金额
function formatMoney(amount: number) {
  return '¥' + amount.toLocaleString()
}

// 计算变化值
function getValueChange(asset: AssetItem) {
  return asset.currentValue - asset.acquirePrice
}

// 查看价格走势
function viewPriceTrend(asset: AssetItem) {
  router.push({ path: '/price', query: { keyword: asset.productName } })
}
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">资产管理</p>
        <h1>我的资产</h1>
        <p>集中查看和管理您的谷子资产，了解成本、当前估值和流转状态。</p>
      </div>
      <button class="primary" type="button" @click="openAddModal">添加资产</button>
    </section>

    <section class="overview-grid" aria-label="资产概览">
      <article class="overview-card"><span>资产总数量</span><strong>{{ summary.totalCount }} 件</strong><p>已录入收藏谷子</p></article>
      <article class="overview-card"><span>资产品类数</span><strong>{{ summary.categoryCount }} 种</strong><p>不同谷子品类分布</p></article>
      <article class="overview-card"><span>累计总成本</span><strong>{{ formatMoney(summary.totalCost) }}</strong><p>用户录入购买成本</p></article>
      <article class="overview-card"><span>当前总估值</span><strong>{{ formatMoney(summary.totalValue) }}</strong><p>按参考价估算</p></article>
      <article class="overview-card" :class="{ gain: summary.valueChange >= 0, loss: summary.valueChange < 0 }">
        <span>估值变化</span>
        <strong>{{ summary.valueChange >= 0 ? '+' : '' }}{{ formatMoney(summary.valueChange) }}</strong>
        <p>相对录入成本{{ summary.valueChange >= 0 ? '增长' : '下降' }}</p>
      </article>
    </section>

    <section class="toolbar" aria-label="筛选与搜索">
      <div class="search-box">
        <input v-model="searchQuery" type="search" placeholder="搜索谷子名称 / IP / 角色" @keyup.enter="handleSearch">
      </div>
      <select v-model="statusFilter" aria-label="状态筛选" @change="handleFilter">
        <option value="all">全部状态</option>
        <option value="holding">持有中</option>
        <option value="selling">出售中</option>
        <option value="exchanging">换物中</option>
        <option value="sold">已售出</option>
        <option value="invalid">已失效</option>
      </select>
      <select v-model="sortBy" aria-label="排列方式" @change="handleFilter">
        <option value="time">按录入时间</option>
        <option value="value">按当前估值</option>
        <option value="change">按估值变化</option>
      </select>
      <button class="primary" type="button" :disabled="loading" @click="handleSearch">
        {{ loading ? '加载中...' : '筛选资产' }}
      </button>
    </section>

    <section class="table-panel">
      <div class="section-head">
        <div><p class="eyebrow">资产列表</p><h2>资产明细</h2></div>
        <span>共 {{ assets.length }} 条数据</span>
      </div>
      <div v-if="!assets.length" class="empty-state">
        <strong>暂无资产数据</strong>
        <p>点击"添加资产"按钮录入您的谷子</p>
      </div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>资产编号</th><th>谷子名称</th><th>IP/角色</th><th>品类</th>
              <th>数量</th><th>成本价</th><th>当前估值</th><th>估值变化</th>
              <th>状态</th><th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="asset in assets" :key="asset.id">
              <td>{{ asset.id }}</td>
              <td><strong>{{ asset.productName }}</strong></td>
              <td>{{ asset.ipName }} / {{ asset.characterName }}</td>
              <td>{{ asset.category }}</td>
              <td>{{ asset.quantity }}</td>
              <td>{{ formatMoney(asset.acquirePrice) }}</td>
              <td>{{ formatMoney(asset.currentValue) }}</td>
              <td :class="{ up: getValueChange(asset) >= 0, down: getValueChange(asset) < 0 }">
                {{ getValueChange(asset) >= 0 ? '+' : '' }}{{ formatMoney(getValueChange(asset)) }}
              </td>
              <td><span class="status" :class="getStatusClass(asset.status)">{{ getStatusText(asset.status) }}</span></td>
              <td class="actions">
                <button class="action-btn small" @click="viewDetail(asset)">详情</button>
                <button class="action-btn small" @click="startEdit(asset)">编辑</button>
                <button class="action-btn small trend" @click="viewPriceTrend(asset)">价格走势</button>
                <button v-if="asset.status === 'holding'" class="action-btn small list" @click="openListModal(asset)">上架</button>
                <button v-if="asset.status === 'selling' || asset.status === 'exchanging'" class="action-btn small delist" @click="openDelistModal(asset)">下架</button>
                <button class="action-btn small delete" @click="confirmDelete(asset)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>

  <!-- 添加资产弹窗 -->
  <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
    <div class="modal">
      <div class="modal-header">
        <h2>添加资产</h2>
        <button class="modal-close" @click="closeAddModal">&times;</button>
      </div>
      <form class="modal-form" @submit.prevent="handleAdd">
        <label>
          <span>从商品库选择</span>
          <div class="product-search-wrap">
            <input v-model="productSearchQuery" type="text" placeholder="输入商品名称/IP/角色搜索" @input="searchProducts" @focus="searchProducts">
            <button v-if="addForm.productId" type="button" class="clear-btn" @click="clearProductSelection">清除选择</button>
            <div v-if="showProductDropdown && productSearchResults.length > 0" class="product-dropdown">
              <div v-for="p in productSearchResults" :key="p.product_id" class="product-option" @click="selectProduct(p)">
                <strong>{{ p.name }}</strong>
                <span>{{ p.ipName }} / {{ p.characterName }} · {{ p.category }}</span>
              </div>
            </div>
          </div>
        </label>
        <div v-if="addForm.productId" class="selected-product-info">
          <span>已选商品：{{ addForm.productName }}（{{ addForm.ipName }} / {{ addForm.characterName }}）</span>
        </div>
        <label>
          <span>谷子名称 *</span>
          <input v-model="addForm.productName" type="text" required placeholder="请输入谷子名称" @input="clearAddError('productName')">
          <span v-if="addFormErrors.productName" class="field-error">{{ addFormErrors.productName }}</span>
        </label>
        <div class="form-row">
          <label>
            <span>IP *</span>
            <input v-model="addForm.ipName" type="text" required placeholder="如：原神" @input="clearAddError('ipName')">
            <span v-if="addFormErrors.ipName" class="field-error">{{ addFormErrors.ipName }}</span>
          </label>
          <label>
            <span>角色 *</span>
            <input v-model="addForm.characterName" type="text" required placeholder="如：胡桃" @input="clearAddError('characterName')">
            <span v-if="addFormErrors.characterName" class="field-error">{{ addFormErrors.characterName }}</span>
          </label>
        </div>
        <div class="form-row">
          <label>
            <span>品类 *</span>
            <select v-model="addForm.category" required @change="clearAddError('category')">
              <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
            </select>
            <span v-if="addFormErrors.category" class="field-error">{{ addFormErrors.category }}</span>
          </label>
          <label>
            <span>数量 *</span>
            <input v-model.number="addForm.quantity" type="number" min="1" required>
          </label>
        </div>
        <label>
          <span>入手价 *</span>
          <input v-model.number="addForm.acquirePrice" type="number" min="0" step="0.01" required placeholder="请输入购买价格" @input="clearAddError('acquirePrice')">
          <span v-if="addFormErrors.acquirePrice" class="field-error">{{ addFormErrors.acquirePrice }}</span>
        </label>
        <label>
          <span>描述</span>
          <textarea v-model="addForm.description" rows="3" placeholder="选填"></textarea>
        </label>
        <div class="modal-actions">
          <button type="button" class="secondary" @click="closeAddModal">取消</button>
          <button type="submit" class="primary" :disabled="loading">{{ loading ? '添加中...' : '添加资产' }}</button>
        </div>
      </form>
    </div>
  </div>

  <!-- 详情弹窗 -->
  <div v-if="showDetailModal && selectedAsset" class="modal-overlay" @click.self="closeDetailModal">
    <div class="modal modal-detail">
      <div class="modal-header">
        <h2>资产详情</h2>
        <button class="modal-close" @click="closeDetailModal">&times;</button>
      </div>
      <div class="detail-content">
        <div class="detail-info">
          <h3>{{ selectedAsset.productName }}</h3>
          <div class="detail-meta">
            <span class="detail-price">{{ formatMoney(selectedAsset.currentValue) }}</span>
            <span class="status" :class="getStatusClass(selectedAsset.status)">{{ getStatusText(selectedAsset.status) }}</span>
          </div>
          <div class="detail-fields">
            <div class="field"><label>资产编号</label><span>{{ selectedAsset.id }}</span></div>
            <div class="field"><label>IP</label><span>{{ selectedAsset.ipName }}</span></div>
            <div class="field"><label>角色</label><span>{{ selectedAsset.characterName }}</span></div>
            <div class="field"><label>品类</label><span>{{ selectedAsset.category }}</span></div>
            <div class="field"><label>数量</label><span>{{ selectedAsset.quantity }}</span></div>
            <div class="field"><label>入手价</label><span>{{ formatMoney(selectedAsset.acquirePrice) }}</span></div>
            <div class="field"><label>当前估值</label><span>{{ formatMoney(selectedAsset.currentValue) }}</span></div>
            <div class="field"><label>估值变化</label><span :class="{ up: getValueChange(selectedAsset) >= 0, down: getValueChange(selectedAsset) < 0 }">{{ getValueChange(selectedAsset) >= 0 ? '+' : '' }}{{ formatMoney(getValueChange(selectedAsset)) }}</span></div>
            <div class="field"><label>创建时间</label><span>{{ selectedAsset.created_at }}</span></div>
            <div class="field"><label>更新时间</label><span>{{ selectedAsset.updated_at }}</span></div>
          </div>
          <p v-if="selectedAsset.description" class="detail-desc">{{ selectedAsset.description }}</p>
        </div>
      </div>
      <div class="modal-actions">
        <button type="button" class="secondary" @click="closeDetailModal">关闭</button>
        <button type="button" class="primary" @click="closeDetailModal; startEdit(selectedAsset)">编辑</button>
      </div>
    </div>
  </div>

  <!-- 编辑弹窗 -->
  <div v-if="showEditModal && selectedAsset" class="modal-overlay" @click.self="closeEditModal">
    <div class="modal">
      <div class="modal-header">
        <h2>编辑资产</h2>
        <button class="modal-close" @click="closeEditModal">&times;</button>
      </div>
      <form class="modal-form" @submit.prevent="handleSaveEdit">
        <label>
          <span>谷子名称</span>
          <input v-model="editForm.productName" type="text" required>
        </label>
        <div class="form-row">
          <label>
            <span>IP</span>
            <input v-model="editForm.ipName" type="text">
          </label>
          <label>
            <span>角色</span>
            <input v-model="editForm.characterName" type="text">
          </label>
        </div>
        <div class="form-row">
          <label>
            <span>品类</span>
            <input v-model="editForm.category" type="text">
          </label>
          <label>
            <span>数量</span>
            <input v-model.number="editForm.quantity" type="number" min="1">
          </label>
        </div>
        <div class="form-row">
          <label>
            <span>入手价</span>
            <input v-model.number="editForm.acquirePrice" type="number" min="0" step="0.01">
          </label>
          <label>
            <span>当前估值</span>
            <input v-model.number="editForm.currentValue" type="number" min="0" step="0.01">
          </label>
        </div>
        <label>
          <span>描述</span>
          <textarea v-model="editForm.description" rows="3"></textarea>
        </label>
        <div class="modal-actions">
          <button type="button" class="secondary" @click="closeEditModal">取消</button>
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
        <p>确定要删除资产"{{ assetToDelete?.productName }}"吗？</p>
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

  <!-- 上架弹窗 -->
  <div v-if="showListModal && selectedAsset" class="modal-overlay" @click.self="closeListModal">
    <div class="modal">
      <div class="modal-header">
        <h2>上架到交易市场</h2>
        <button class="modal-close" @click="closeListModal">&times;</button>
      </div>
      <form class="modal-form" @submit.prevent="handleListToMarket">
        <div class="list-product-info">
          <strong>{{ selectedAsset.productName }}</strong>
          <span>{{ selectedAsset.ipName }} / {{ selectedAsset.characterName }} · {{ selectedAsset.category }}</span>
          <span>数量：{{ selectedAsset.quantity }} · 估值：¥{{ selectedAsset.currentValue }}</span>
        </div>
        <label>
          <span>售价（元）*</span>
          <input v-model.number="listPrice" type="number" min="0.01" step="0.01" required placeholder="请输入售价">
        </label>
        <label>
          <span>商品描述</span>
          <textarea v-model="listDescription" rows="3" :placeholder="selectedAsset.description || '描述商品状态、瑕疵等信息（选填）'"></textarea>
        </label>
        <div class="modal-actions">
          <button type="button" class="secondary" @click="closeListModal">取消</button>
          <button type="submit" class="primary" :disabled="loading">{{ loading ? '上架中...' : '确认上架' }}</button>
        </div>
      </form>
    </div>
  </div>

  <!-- 下架确认弹窗 -->
  <div v-if="showDelistModal && selectedAsset" class="modal-overlay" @click.self="closeDelistModal">
    <div class="modal modal-confirm">
      <div class="modal-header">
        <h2>确认下架</h2>
        <button class="modal-close" @click="closeDelistModal">&times;</button>
      </div>
      <div class="modal-body">
        <p>确定要将"{{ selectedAsset.productName }}"从交易市场下架吗？</p>
        <p class="warning">下架后该商品将从交易市场移除，资产恢复为持有状态。</p>
      </div>
      <div class="modal-actions">
        <button type="button" class="secondary" @click="closeDelistModal">取消</button>
        <button type="button" class="primary" :disabled="loading" @click="handleDelistFromMarket">
          {{ loading ? '处理中...' : '确认下架' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.page-head {
  display: flex; justify-content: space-between; gap: 24px; align-items: center; padding: 30px; border-radius: 10px; color: #fff;
  background: linear-gradient(rgba(10,74,90,0.88), rgba(10,74,90,0.92)),
    url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80") center/cover;
  box-shadow: var(--shadow);
}
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, p { margin: 0; }
h1 { font-size: 40px; line-height: 1.16; }
.page-head p:last-child { max-width: 640px; margin-top: 12px; color: rgba(255,255,255,0.84); line-height: 1.8; }
.primary { min-height: 44px; border: 0; border-radius: 8px; padding: 0 18px; color: #fff; background: var(--accent); font-weight: 800; cursor: pointer; font: inherit; }
.primary:hover { background: var(--accent-dark); }
.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.secondary { min-height: 44px; border: 1px solid var(--line); border-radius: 8px; padding: 0 18px; color: var(--ink); background: var(--panel); font-weight: 700; cursor: pointer; font: inherit; }
.secondary:hover { background: var(--soft); }
.danger { min-height: 44px; border: 0; border-radius: 8px; padding: 0 18px; color: #fff; background: #be123c; font-weight: 800; cursor: pointer; font: inherit; }
.danger:hover { background: #9f1239; }
.danger:disabled { opacity: 0.6; cursor: not-allowed; }
.overview-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 16px; margin-top: 20px; }
.overview-card, .toolbar, .table-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.overview-card { padding: 20px; }
.overview-card span { color: var(--muted); font-size: 14px; }
.overview-card strong { display: block; margin-top: 10px; font-size: 28px; }
.overview-card p { margin-top: 8px; color: var(--muted); font-size: 14px; }
.overview-card.gain strong { color: #1f7a4d; }
.overview-card.loss strong { color: #b9352b; }
.toolbar { display: grid; grid-template-columns: minmax(280px, 1fr) 180px 180px 120px; gap: 12px; align-items: center; margin-top: 20px; padding: 18px; }
input, select { width: 100%; height: 44px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; color: var(--ink); background: #fff; outline: none; font: inherit; }
input:focus, select:focus { border-color: var(--accent); box-shadow: 0 0 0 4px rgba(15,100,120,0.12); }
.table-panel { margin-top: 20px; padding: 22px; }
.section-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 16px; }
.section-head .eyebrow { color: var(--accent); }
h2 { font-size: 24px; }
.section-head span { color: var(--muted); font-size: 14px; }
.empty-state { min-height: 180px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); }
.empty-state strong { display: block; margin-bottom: 8px; color: var(--ink); font-size: 18px; }
.empty-state p { font-size: 14px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; min-width: 1120px; border-collapse: collapse; font-size: 14px; }
th, td { padding: 14px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: middle; }
th { color: var(--muted); background: var(--soft); font-weight: 800; }
tbody tr:hover { background: #fbfdfe; }
.up { color: #1f7a4d; font-weight: 800; }
.down { color: #b9352b; font-weight: 800; }
.status { display: inline-flex; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 13px; font-weight: 800; }
.status.holding { color: var(--accent); background: #eaf6f8; }
.status.selling { color: #9a5d00; background: #fff3d7; }
.status.exchanging { color: #6d4bc2; background: #f1ebff; }
.status.sold { color: var(--muted); background: #edf1f3; }
.status.invalid { color: #b9352b; background: #fde8e8; }
.actions { display: flex; gap: 6px; flex-wrap: wrap; }
.action-btn { border: 0; border-radius: 6px; padding: 0 10px; font-size: 13px; font-weight: 700; cursor: pointer; font: inherit; transition: background 0.2s; }
.action-btn.small { min-height: 30px; }
.action-btn { background: var(--soft); color: var(--accent); }
.action-btn:hover { background: #eaf6f8; }
.action-btn.list { background: #fef3c7; color: #b45309; }
.action-btn.list:hover { background: #fde68a; }
.action-btn.delist { background: #dcfce7; color: #15803d; }
.action-btn.delist:hover { background: #bbf7d0; }
.action-btn.delete { background: #fee2e2; color: #be123c; }
.action-btn.delete:hover { background: #fecaca; }
.action-btn.trend { background: #e0e7ff; color: #4338ca; }
.action-btn.trend:hover { background: #c7d2fe; }

/* 弹窗样式 */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: grid; place-items: center; z-index: 1000; padding: 20px; }
.modal { background: var(--panel); border-radius: 16px; width: min(600px, 100%); max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
.modal-detail { width: min(640px, 100%); }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 24px 28px; border-bottom: 1px solid var(--line); }
.modal-header h2 { font-size: 24px; }
.modal-close { width: 40px; height: 40px; border: 0; border-radius: 10px; background: var(--soft); color: var(--muted); font-size: 24px; cursor: pointer; display: grid; place-items: center; }
.modal-close:hover { background: #fee2e2; color: #be123c; }
.modal-form { padding: 28px; display: grid; gap: 18px; }
.modal-form label { display: grid; gap: 8px; }
.modal-form label span { color: var(--muted); font-size: 14px; font-weight: 600; }
.modal-form input, .modal-form textarea { width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 12px 14px; font: inherit; font-size: 14px; background: #fff; box-sizing: border-box; }
.modal-form textarea { resize: vertical; min-height: 70px; }
.modal-form input:focus, .modal-form textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(15,100,120,0.1); outline: none; }
.field-error { color: #be123c; font-size: 13px; margin-top: 2px; }
.form-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.product-search-wrap { position: relative; }
.product-dropdown {
  position: absolute; top: 100%; left: 0; right: 0; z-index: 10;
  max-height: 240px; overflow-y: auto; margin-top: 4px;
  border: 1px solid var(--line); border-radius: 8px;
  background: #fff; box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}
.product-option {
  padding: 10px 14px; cursor: pointer; border-bottom: 1px solid var(--soft);
}
.product-option:last-child { border-bottom: 0; }
.product-option:hover { background: var(--soft); }
.product-option strong { display: block; font-size: 14px; }
.product-option span { display: block; font-size: 12px; color: var(--muted); margin-top: 2px; }
.clear-btn {
  position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
  border: 0; background: var(--soft); color: var(--muted); border-radius: 4px;
  padding: 2px 8px; font-size: 12px; cursor: pointer;
}
.selected-product-info {
  padding: 10px 14px; background: #eaf6f8; border-radius: 8px;
  color: var(--accent); font-size: 14px; font-weight: 600;
}
.input-error { border-color: #be123c !important; }
.input-error:focus { box-shadow: 0 0 0 3px rgba(190,18,60,0.15) !important; }
.error-text { color: #be123c; font-size: 13px; margin-top: 4px; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; padding: 18px 28px; border-top: 1px solid var(--line); }
.modal-confirm .modal-body { padding: 28px; }
.modal-confirm .modal-body p { margin: 0; line-height: 1.6; font-size: 16px; }
.modal-confirm .modal-body .warning { color: #be123c; margin-top: 10px; font-size: 14px; }
.modal-confirm .modal-actions { padding: 0 28px 28px; border-top: 0; }
.list-product-info {
  padding: 14px 16px; background: var(--soft); border-radius: 8px;
  display: grid; gap: 4px;
}
.list-product-info strong { font-size: 16px; }
.list-product-info span { color: var(--muted); font-size: 13px; }

/* 详情弹窗内容 */
.detail-content { padding: 28px; }
.detail-info { display: grid; gap: 14px; }
.detail-info h3 { font-size: 24px; }
.detail-meta { display: flex; align-items: center; gap: 14px; }
.detail-price { color: var(--accent); font-size: 36px; font-weight: 800; }
.detail-fields { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.field { display: grid; gap: 6px; }
.field label { color: var(--muted); font-size: 14px; }
.field span { font-weight: 600; font-size: 16px; }
.detail-desc { color: var(--muted); line-height: 1.6; margin-top: 12px; font-size: 14px; }

@media (max-width: 1100px) {
  .overview-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .toolbar { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 760px) {
  .page-head { align-items: flex-start; flex-direction: column; }
  .overview-grid, .toolbar { grid-template-columns: 1fr; }
  .detail-fields { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .page { width: min(100% - 20px, 1240px); }
  .page-head, .table-panel { padding: 20px; }
  h1 { font-size: 30px; }
  .form-row { grid-template-columns: 1fr; }
}
</style>
