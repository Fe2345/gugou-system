<script setup lang="ts">
import { ref, reactive } from 'vue'
import TopBar from '@/layouts/TopBar.vue'

interface Product {
  image: string
  name: string
  price: string
  ip: string
  role: string
  category: string
  description: string
}

const selectedImage = ref('')
const imagePreviewRef = ref<HTMLImageElement | null>(null)
const uploadTextRef = ref<HTMLSpanElement | null>(null)
const products = ref<Product[]>([
  {
    image: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80',
    name: '玛奇朵',
    price: '85.00',
    ip: '精灵宝可梦联动',
    role: '玛奇朵',
    category: '色纸',
    description: '精灵宝可梦联动原版限定',
  },
])

const form = reactive({
  name: '',
  price: '',
  ip: '',
  role: '',
  category: '',
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

function addProduct() {
  const name = form.name.trim()
  const price = form.price.trim()
  if (!selectedImage.value || !name || !price) return

  const desc = [
    form.ip || 'IP 待定',
    form.role || '角色待定',
    form.category || '品类待定',
  ].join(' · ')

  products.value.unshift({
    image: selectedImage.value,
    name,
    price: Number(price).toFixed(2),
    ip: form.ip || 'IP 待定',
    role: form.role || '角色待定',
    category: form.category || '品类待定',
    description: desc,
  })

  form.name = ''
  form.price = ''
  form.ip = ''
  form.role = ''
  form.category = ''
  selectedImage.value = ''
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
      <form class="search-box" @submit.prevent>
        <input type="search" placeholder="搜索产品名称、IP或角色">
        <button type="button">搜索</button>
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
          <input type="text" placeholder="请输入 IP 名称">
        </label>
        <label>
          <span>角色</span>
          <input type="text" placeholder="请输入角色名称">
        </label>
        <label>
          <span>品类</span>
          <select>
            <option>全部品类</option><option>徽章</option><option>色纸</option><option>卡片</option>
            <option>亚克力</option><option>明信片</option>
          </select>
        </label>
        <label>
          <span>发行时间</span>
          <select>
            <option>不限时间</option><option>近一个月</option><option>近三个月</option>
            <option>近一年</option><option>早期发行</option>
          </select>
        </label>
        <label>
          <span>价格区间</span>
          <div class="price-row">
            <input type="number" placeholder="最低价">
            <input type="number" placeholder="最高价">
          </div>
        </label>
        <button class="secondary" type="button">应用筛选</button>
      </aside>

      <section class="content">
        <section class="upload-panel">
          <div class="section-head">
            <p class="eyebrow">自定义产品</p>
            <h2>添加产品信息</h2>
          </div>
          <form class="product-form" @submit.prevent="addProduct">
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
              <button class="primary" type="submit">添加到产品列表</button>
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
                <strong class="product-price">¥ {{ p.price }}</strong>
                <h3>{{ p.name }}</h3>
                <p>{{ p.description }}</p>
              </div>
            </article>
          </div>
        </section>

        <section class="detail-panel">
          <div class="section-head">
            <p class="eyebrow">产品详情</p>
            <h2>详情信息占位</h2>
          </div>
          <div class="detail-grid">
            <article>
              <span>基础信息</span>
              <p>展示产品名称、IP、角色、品类、发行时间等完整信息。</p>
            </article>
            <article>
              <span>参考价格</span>
              <p>展示用户自定义价格及平台参考价。</p>
            </article>
            <article>
              <span>近期成交</span>
              <p>显示近期成交和最新成交记录。</p>
            </article>
            <article>
              <span>价格分析链接</span>
              <p>可直接跳转至价格分析页面。</p>
            </article>
          </div>
        </section>
      </section>
    </section>
  </main>
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
.detail-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.detail-grid article { padding: 16px; border-radius: 10px; background: var(--soft); }
.detail-grid span { display: block; color: var(--accent); font-weight: 800; }
.detail-grid p { margin-top: 10px; color: var(--muted); line-height: 1.6; }

@media (max-width: 980px) {
  .hero, .layout, .product-form { grid-template-columns: 1fr; }
  .product-grid, .detail-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 620px) {
  .page { width: min(100% - 20px, 1180px); }
  .hero, .upload-panel, .list-panel, .detail-panel { padding: 20px; }
  h1 { font-size: 30px; }
  .search-box, .form-grid, .price-row, .product-grid, .detail-grid { grid-template-columns: 1fr; }
}
</style>
