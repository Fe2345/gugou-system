<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboardStats, type DashboardStats } from '@/api/admin'

defineOptions({ name: 'AdminDashboardView' })
const router = useRouter()
const loading = ref(true)
const stats = ref<DashboardStats>({
  user_count: 0,
  product_count: 0,
  order_count: 0,
  pending_count: 0,
  new_users_week: 0,
  orders_today: 0,
})

async function loadStats() {
  loading.value = true
  try {
    const res = await getDashboardStats()
    if (res.code === 200) {
      stats.value = res.data
    }
  } catch (e) {
    console.error('加载统计数据失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>

<template>
  <section class="hero">
    <div class="hero-text">
      <p class="eyebrow">后台首页</p>
      <h1>管理控制台</h1>
      <p>今日运营状态、待处理事务和关键数据总览</p>
    </div>
  </section>

  <div v-if="loading" class="loading-state">加载中...</div>
  <template v-else>
    <section class="data-grid" aria-label="关键指标">
      <article class="data-card">
        <span>用户总数</span>
        <strong>{{ stats.user_count.toLocaleString() }}</strong>
        <p>本周新增 {{ stats.new_users_week }} 位用户</p>
      </article>
      <article class="data-card">
        <span>商品总数</span>
        <strong>{{ stats.product_count.toLocaleString() }}</strong>
        <p>平台上架商品</p>
      </article>
      <article class="data-card">
        <span>订单统计</span>
        <strong>{{ stats.order_count.toLocaleString() }}</strong>
        <p>今日成交 {{ stats.orders_today }} 笔</p>
      </article>
      <article class="data-card">
        <span>待审核事项</span>
        <strong>{{ stats.pending_count }}</strong>
        <p>需要及时处理</p>
      </article>
    </section>

    <section class="workspace">
      <article class="panel">
        <div class="panel-title">
          <h3>快捷操作</h3>
          <span>常用入口</span>
        </div>
        <div class="quick-grid">
          <button type="button" @click="router.push('/admin/goods')"><strong>商品管理</strong><span>审核上架请求</span></button>
          <button type="button" @click="router.push('/admin/users')"><strong>用户管理</strong><span>查看用户信息</span></button>
          <button type="button" @click="router.push('/admin/orders')"><strong>订单处理</strong><span>处理异常订单</span></button>
          <button type="button" @click="router.push('/admin/exchange')"><strong>换物审核</strong><span>审核换物请求</span></button>
        </div>
      </article>
    </section>
  </template>
</template>

<style scoped>
.hero {
  min-height: 160px;
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 38px;
  border-radius: 10px;
  color: #fff;
  background:
    linear-gradient(rgba(10, 74, 90, 0.86), rgba(10, 74, 90, 0.92)),
    url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1600&q=80") center/cover;
  box-shadow: var(--shadow);
}
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 36px; line-height: 1.16; }
.hero-text p:last-child { max-width: 520px; margin-top: 14px; color: rgba(255,255,255,0.84); line-height: 1.8; }

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  color: var(--muted);
  font-size: 16px;
}

.data-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-top: 20px; }
.data-card {
  border: 1px solid var(--line); border-radius: 10px; background: var(--panel);
  box-shadow: var(--shadow); padding: 20px;
}
.data-card span { color: var(--muted); font-size: 14px; }
.data-card strong { display: block; margin-top: 10px; font-size: 30px; }
.data-card p { margin-top: 8px; color: var(--muted); }

.workspace { margin-top: 20px; }

.panel {
  border: 1px solid var(--line); border-radius: 10px; background: var(--panel);
  box-shadow: var(--shadow); padding: 18px;
}
.panel-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.panel-title h3 { font-size: 18px; }
.panel-title span { color: var(--muted); font-size: 13px; }

.quick-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
.quick-grid button { min-height: 72px; padding: 14px; text-align: left; border: 0; border-radius: 8px; color: #fff; background: var(--accent); font-weight: 800; cursor: pointer; font: inherit; }
.quick-grid button:hover { background: var(--accent-dark); }
.quick-grid strong, .quick-grid span { display: block; }
.quick-grid strong { font-size: 15px; }
.quick-grid span { margin-top: 6px; color: rgba(255,255,255,0.78); font-size: 12px; }

@media (max-width: 980px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 620px) { .hero { padding: 20px; } h1 { font-size: 28px; } .data-grid, .quick-grid { grid-template-columns: 1fr; } }
</style>
