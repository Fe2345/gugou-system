<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { useUserStore } from '@/stores/user'
import { getMarketDetail, type MarketItem } from '@/api/market'
import { createOrder } from '@/api/order'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const creditScore = computed(() => userStore.userInfo?.creditScore ?? 100)
const canTrade = computed(() => creditScore.value >= 40)
const listing = ref<MarketItem | null>(null)
const loading = ref(false)
const submitting = ref(false)
const quantity = ref(1)

async function loadListing() {
  const listingId = route.query.listing as string
  if (!listingId) return
  loading.value = true
  try {
    const res = await getMarketDetail(listingId)
    if (res.code === 200) {
      listing.value = res.data
    }
  } catch (e) {
    console.error('加载挂单信息失败', e)
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!listing.value) return
  submitting.value = true
  try {
    const res = await createOrder({
      listing_id: listing.value.listing_id,
      quantity: quantity.value,
    })
    if (res.code === 200) {
      alert('下单成功')
      router.push(`/my-orders/${res.data.order_id}`)
    } else {
      alert(res.message || '下单失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '下单失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadListing()
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">创建订单</p>
        <h1>确认下单</h1>
        <p>确认商品信息和数量后提交订单</p>
      </div>
      <button class="secondary" type="button" @click="router.back()">返回</button>
    </section>

    <div v-if="!canTrade" class="credit-warning">
      信用分过低（当前 {{ creditScore }} 分），禁止交易。请提升信用分或联系管理员。
    </div>

    <div v-if="loading" class="empty-state"><strong>加载中...</strong></div>
    <div v-else-if="!listing" class="empty-state">
      <strong>挂单信息不存在</strong>
      <p>请从市场页面重新选择商品</p>
      <button class="primary" type="button" @click="router.push('/market')">去市场</button>
    </div>
    <section v-else class="order-layout">
      <article class="order-info">
        <h2>商品信息</h2>
        <div class="info-grid">
          <div><span>商品名称</span><strong>{{ listing.product_name }}</strong></div>
          <div><span>卖家</span><strong>{{ listing.seller_name }}</strong></div>
          <div><span>单价</span><strong class="price">¥{{ listing.price }}</strong></div>
          <div><span>可购数量</span><strong>{{ listing.quantity }}</strong></div>
        </div>
        <div class="desc-section">
          <h3>商品描述</h3>
          <p>{{ listing.description || '暂无描述' }}</p>
        </div>
      </article>

      <aside class="order-side">
        <section class="confirm-card">
          <h3>确认订单</h3>
          <div class="form-group">
            <label>购买数量</label>
            <input v-model.number="quantity" type="number" :min="1" :max="listing.quantity" placeholder="1">
          </div>
          <div class="total-row">
            <span>合计金额</span>
            <strong class="price">¥{{ (listing.price * quantity).toFixed(2) }}</strong>
          </div>
          <button class="primary full" type="button" :disabled="submitting || !canTrade" @click="handleSubmit">
            {{ submitting ? '提交中...' : '确认下单' }}
          </button>
        </section>
      </aside>
    </section>
  </main>
</template>

<style scoped>
.page { width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 20px; }
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 32px; }
.page-head > div > p:last-child { margin-top: 8px; color: var(--muted); }
.order-layout { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 20px; align-items: start; }
.order-info, .confirm-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 24px; }
.order-info h2 { font-size: 22px; margin-bottom: 16px; }
.info-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-bottom: 20px; }
.info-grid div { padding: 14px; border-radius: 8px; background: var(--soft); }
.info-grid span { display: block; color: var(--muted); font-size: 13px; }
.info-grid strong { display: block; margin-top: 8px; font-size: 16px; }
.price { color: #be123c; }
.desc-section h3 { font-size: 18px; margin-bottom: 8px; }
.desc-section p { color: var(--muted); line-height: 1.7; }
.confirm-card h3 { font-size: 18px; margin-bottom: 16px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 700; font-size: 14px; }
input { width: 100%; height: 44px; border: 1px solid var(--line); border-radius: 8px; padding: 0 14px; font: inherit; background: var(--soft); box-sizing: border-box; }
.total-row { display: flex; justify-content: space-between; align-items: center; padding: 14px 0; margin-bottom: 16px; border-top: 1px solid var(--line); font-size: 16px; }
.total-row .price { font-size: 24px; }
.primary, .secondary { min-height: 44px; padding: 0 18px; border-radius: 8px; font-weight: 800; cursor: pointer; font: inherit; }
.primary { border: 0; color: #fff; background: var(--accent); }
.primary:hover { background: var(--accent-dark); }
.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
.full { width: 100%; }
.credit-warning { padding: 14px 18px; border-radius: 8px; background: #fdecea; border: 1px solid #f0b8b3; color: #be123c; font-weight: 600; margin-bottom: 16px; }
.empty-state { min-height: 200px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); }
.empty-state strong { display: block; margin-bottom: 8px; color: var(--ink); font-size: 18px; }
.empty-state .primary { margin-top: 12px; }

@media (max-width: 860px) { .order-layout { grid-template-columns: 1fr; } }
</style>
