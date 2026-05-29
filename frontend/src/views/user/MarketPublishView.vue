<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { publishToMarket } from '@/api/market'
import { getGoodsList } from '@/api/goods'
import { getAssetsList } from '@/api/assets'
import type { GoodsItem } from '@/types/goods'
import type { AssetItem } from '@/types/assets'

const router = useRouter()
const goodsList = ref<GoodsItem[]>([])
const assetsList = ref<AssetItem[]>([])
const submitting = ref(false)

const form = ref({
  product_id: '',
  asset_id: '',
  price: '',
  quantity: '1',
  description: '',
})

async function loadOptions() {
  try {
    const [goodsRes, assetsRes] = await Promise.all([
      getGoodsList({ page: 1, pageSize: 100 }),
      getAssetsList(),
    ])
    if (goodsRes.code === 200) goodsList.value = goodsRes.data.list
    if (assetsRes.code === 200) assetsList.value = assetsRes.data.list
  } catch (e) {
    console.error('加载选项失败', e)
  }
}

async function handleSubmit() {
  if (!form.value.product_id || !form.value.asset_id || !form.value.price) {
    alert('请填写必填项')
    return
  }
  submitting.value = true
  try {
    const res = await publishToMarket({
      product_id: form.value.product_id,
      asset_id: form.value.asset_id,
      price: Number(form.value.price),
      quantity: Number(form.value.quantity) || 1,
      description: form.value.description,
    })
    if (res.code === 200) {
      alert('发布成功')
      router.push('/market/my')
    } else {
      alert(res.message || '发布失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '发布失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadOptions()
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">交易市场</p>
        <h1>发布在售谷子</h1>
        <p>填写商品信息和出售价格，将谷子发布到交易市场</p>
      </div>
      <button class="secondary" type="button" @click="router.push('/market')">返回市场</button>
    </section>

    <section class="form-panel">
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>选择商品 <span class="required">*</span></label>
          <select v-model="form.product_id" required>
            <option value="">请选择商品</option>
            <option v-for="g in goodsList" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>选择资产 <span class="required">*</span></label>
          <select v-model="form.asset_id" required>
            <option value="">请选择资产</option>
            <option v-for="a in assetsList" :key="a.id" :value="a.id">{{ a.productName }} (数量: {{ a.quantity }})</option>
          </select>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>售价 (元) <span class="required">*</span></label>
            <input v-model="form.price" type="number" min="0.01" step="0.01" placeholder="输入售价" required>
          </div>
          <div class="form-group">
            <label>数量</label>
            <input v-model="form.quantity" type="number" min="1" placeholder="1">
          </div>
        </div>
        <div class="form-group">
          <label>商品描述</label>
          <textarea v-model="form.description" rows="4" placeholder="描述商品状态、瑕疵等信息"></textarea>
        </div>
        <div class="form-actions">
          <button class="secondary" type="button" @click="router.push('/market')">取消</button>
          <button class="primary" type="submit" :disabled="submitting">{{ submitting ? '发布中...' : '确认发布' }}</button>
        </div>
      </form>
    </section>
  </main>
</template>

<style scoped>
.page { width: min(900px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 20px; }
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 32px; }
.page-head > div > p:last-child { margin-top: 8px; color: var(--muted); }
.form-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 28px; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 700; font-size: 14px; }
.required { color: #be123c; }
.form-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
input, select, textarea { width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 0 14px; font: inherit; background: var(--soft); box-sizing: border-box; }
input, select { height: 44px; }
textarea { height: auto; padding: 12px 14px; resize: vertical; }
.form-actions { display: flex; gap: 10px; justify-content: flex-end; padding-top: 12px; border-top: 1px solid var(--line); }
.primary, .secondary { min-height: 44px; padding: 0 24px; border-radius: 8px; font-weight: 800; cursor: pointer; font: inherit; }
.primary { border: 0; color: #fff; background: var(--accent); }
.primary:hover { background: var(--accent-dark); }
.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
</style>
