<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { getMarketDetail, cancelListing, type MarketItem } from '@/api/market'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const item = ref<MarketItem | null>(null)
const loading = ref(false)

const statusMap: Record<string, { text: string; cls: string }> = {
  active: { text: '在售', cls: 'status-active' },
  locked: { text: '锁定', cls: 'status-locked' },
  sold: { text: '已售', cls: 'status-sold' },
  cancelled: { text: '已取消', cls: 'status-cancelled' },
  removed: { text: '已下架', cls: 'status-cancelled' },
}

async function loadDetail() {
  loading.value = true
  try {
    const id = route.params.id as string
    const res = await getMarketDetail(id)
    if (res.code === 200) {
      item.value = res.data
    }
  } catch (e) {
    console.error('加载挂单详情失败', e)
  } finally {
    loading.value = false
  }
}

async function handleCancel() {
  if (!item.value) return
  if (!confirm('确认取消此挂单？')) return
  try {
    const res = await cancelListing(item.value.listing_id)
    if (res.code === 200) {
      alert('取消成功')
      loadDetail()
    } else {
      alert(res.message || '取消失败')
    }
  } catch (e: any) {
    alert(e?.response?.data?.message || '取消失败')
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadDetail()
})
</script>

<template>
  <TopBar />
  <main class="page">
    <section class="page-head">
      <div>
        <p class="eyebrow">交易市场</p>
        <h1>挂单详情</h1>
      </div>
      <button class="secondary" type="button" @click="router.push('/market')">返回市场</button>
    </section>

    <div v-if="loading" class="empty-state"><strong>加载中...</strong></div>
    <div v-else-if="!item" class="empty-state"><strong>挂单不存在</strong></div>
    <section v-else class="detail-layout">
      <article class="detail-main">
        <div class="detail-header">
          <div>
            <p class="code">挂单 {{ item.listing_id }}</p>
            <h2>{{ item.product_name }}</h2>
          </div>
          <span :class="['status', statusMap[item.status]?.cls]">{{ statusMap[item.status]?.text }}</span>
        </div>

        <div class="info-grid">
          <div><span>售价</span><strong class="price">¥{{ item.price }}</strong></div>
          <div><span>数量</span><strong>{{ item.quantity }}</strong></div>
          <div><span>卖家</span><strong>{{ item.seller_name }}</strong></div>
          <div><span>发布时间</span><strong>{{ formatDate(item.created_at) }}</strong></div>
        </div>

        <div class="desc-section">
          <h3>商品描述</h3>
          <p>{{ item.description || '暂无描述' }}</p>
        </div>

        <div class="images-section">
          <h3>商品图片</h3>
          <div v-if="item.images && item.images.length > 0" class="image-list">
            <img v-for="(img, idx) in item.images" :key="idx" :src="img.image_url" alt="商品图片">
          </div>
          <div v-else-if="item.product_image" class="image-list">
            <img :src="item.product_image" alt="商品图片">
          </div>
          <p v-else class="no-image">暂无图片</p>
        </div>
      </article>

      <aside class="detail-side">
        <section class="action-card">
          <h3>操作</h3>
          <div class="action-list">
            <button v-if="item.status === 'active' && userStore.userInfo?.id !== item.seller_id" class="primary full" type="button" @click="router.push(`/my-orders/create?listing=${item.listing_id}`)">发起交易</button>
            <p v-else-if="item.status === 'active' && userStore.userInfo?.id === item.seller_id" class="self-hint">这是您发布的商品，无法发起交易</p>
            <button v-if="item.status === 'active'" class="danger full" type="button" @click="handleCancel">取消挂单</button>
            <button class="secondary full" type="button" @click="router.push('/market')">返回市场</button>
          </div>
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
.detail-layout { display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 20px; align-items: start; }
.detail-main, .action-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.detail-main { padding: 24px; }
.detail-header { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 20px; }
.code { margin-bottom: 8px; color: var(--accent); font-size: 13px; font-weight: 800; }
.detail-header h2 { font-size: 26px; }
.status { display: inline-flex; align-items: center; height: 28px; padding: 0 10px; border-radius: 999px; font-size: 13px; font-weight: 700; }
.status-active { background: #eaf6f8; color: var(--accent); }
.status-locked { background: #ffedd5; color: #c2410c; }
.status-sold { background: #dcfce7; color: #15803d; }
.status-cancelled { background: #e5e7eb; color: #374151; }
.info-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-bottom: 24px; }
.info-grid div { padding: 14px; border-radius: 8px; background: var(--soft); }
.info-grid span { display: block; color: var(--muted); font-size: 13px; }
.info-grid strong { display: block; margin-top: 8px; font-size: 16px; }
.price { color: #be123c; font-size: 24px !important; }
.desc-section, .images-section { margin-bottom: 20px; }
.desc-section h3, .images-section h3 { font-size: 18px; margin-bottom: 10px; }
.desc-section p { color: var(--muted); line-height: 1.7; }
.image-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.image-list img { width: 100%; height: 200px; object-fit: cover; border-radius: 8px; }
.no-image { color: var(--muted); font-size: 14px; }
.action-card { padding: 18px; }
.action-card h3 { font-size: 18px; margin-bottom: 14px; }
.action-list { display: grid; gap: 10px; }
.self-hint { color: var(--muted); font-size: 13px; text-align: center; margin: 0; }
.primary, .secondary, .danger { min-height: 44px; padding: 0 18px; border-radius: 8px; font-weight: 800; cursor: pointer; font: inherit; }
.primary { border: 0; color: #fff; background: var(--accent); }
.primary:hover { background: var(--accent-dark); }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
.danger { border: 0; color: #fff; background: #be123c; }
.danger:hover { background: #9f1239; }
.full { width: 100%; }
.empty-state { min-height: 200px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); }
.empty-state strong { display: block; color: var(--ink); font-size: 18px; }

@media (max-width: 860px) { .detail-layout { grid-template-columns: 1fr; } }
</style>
