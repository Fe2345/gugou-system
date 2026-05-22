<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

defineOptions({ name: 'AdminDashboardView' })
const router = useRouter()
const activeTab = ref('月度')

const metrics = [
  { label: '用户总数', value: '1,245', trend: '+8.6%', note: '本周新增 96 位用户' },
  { label: '商品总数', value: '3,678', trend: '+4.2%', note: '上架商品 218 件' },
  { label: '订单统计', value: '856', trend: '+12.4%', note: '今日成交 72 笔' },
  { label: '待审核事项', value: '32', trend: '+5', note: '需要在 24 小时内处理' },
]

const tasks = [
  { title: '用户注册审核', desc: '实名认证与资料完整性', count: 5 },
  { title: '商品上架审核', desc: '图片、价格与描述检查', count: 12 },
  { title: '订单异常处理', desc: '退款、超时与申诉订单', count: 3 },
  { title: '换物请求审核', desc: '交换双方信息确认', count: 4 },
]

const records = [
  { title: '商品上架审核', user: '张同学', time: '10:28', status: '待审核' },
  { title: '订单异常处理', user: '李同学', time: '09:46', status: '需跟进' },
  { title: '用户注册审核', user: '王同学', time: '昨天', status: '已通过' },
]
</script>

<template>
  <section class="hero">
    <div class="hero-text">
      <p class="eyebrow">后台首页</p>
      <h1>管理控制台</h1>
      <p>今日运营状态、待处理事务和关键数据总览</p>
    </div>
    <form class="search-box" @submit.prevent>
      <input type="search" placeholder="搜索用户、商品或订单">
      <button type="button">搜索</button>
    </form>
  </section>

  <section class="data-grid" aria-label="关键指标">
    <article v-for="(m, i) in metrics" :key="i" class="data-card">
      <span>{{ m.label }}</span>
      <strong>{{ m.value }}</strong>
      <p>{{ m.note }}</p>
    </article>
  </section>

  <section class="workspace">
    <div class="workspace-main">
      <article class="panel">
        <div class="panel-title">
          <h3>资产估值趋势</h3>
          <div class="tabs">
            <button v-for="t in ['月度', '季度', '年度']" :key="t" :class="{ active: activeTab === t }" @click="activeTab = t" type="button">{{ t }}</button>
          </div>
        </div>
        <div class="chart-area">
          <div class="chart-bars">
            <div v-for="(v, i) in [60, 72, 65, 80, 88, 82, 92]" :key="i" class="bar" :style="{ height: v + '%' }">
              <span class="bar-label">{{ ['1月','2月','3月','4月','5月','6月','7月'][i] }}</span>
            </div>
          </div>
        </div>
      </article>

      <article class="panel">
        <div class="panel-title">
          <h3>最近处理记录</h3>
          <span>系统内高频操作</span>
        </div>
        <table>
          <thead><tr><th>事项</th><th>提交人</th><th>时间</th><th>状态</th></tr></thead>
          <tbody>
            <tr v-for="(r, i) in records" :key="i">
              <td>{{ r.title }}</td>
              <td>{{ r.user }}</td>
              <td>{{ r.time }}</td>
              <td><span class="status" :class="{ pending: r.status === '待审核', alert: r.status === '需跟进', done: r.status === '已通过' }">{{ r.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </article>
    </div>

    <aside class="workspace-side">
      <article class="panel">
        <div class="panel-title">
          <h3>待处理事务</h3>
          <span>按优先级排序</span>
        </div>
        <ul class="task-list">
          <li v-for="(t, i) in tasks" :key="i">
            <div>
              <strong>{{ t.title }}</strong>
              <span>{{ t.desc }}</span>
            </div>
            <span class="badge">{{ t.count }}</span>
          </li>
        </ul>
      </article>

      <article class="panel">
        <div class="panel-title">
          <h3>快捷操作</h3>
          <span>常用入口</span>
        </div>
        <div class="quick-grid">
          <button type="button" @click="router.push('/admin/goods')"><strong>商品审核</strong><span>审核上架请求</span></button>
          <button type="button" @click="router.push('/admin/users')"><strong>用户管理</strong><span>查看用户信息</span></button>
          <button type="button" @click="router.push('/admin/orders')"><strong>订单处理</strong><span>处理异常订单</span></button>
          <button type="button" @click="router.push('/admin/exchange')"><strong>换物审核</strong><span>审核换物请求</span></button>
        </div>
      </article>
    </aside>
  </section>
</template>

<style scoped>
.hero {
  min-height: 200px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 400px);
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

.search-box {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 88px;
  gap: 10px;
  padding: 12px;
  border: 1px solid rgba(255,255,255,0.28);
  border-radius: 10px;
  background: rgba(255,255,255,0.14);
}
.search-box input { width: 100%; height: 44px; border: 0; border-radius: 8px; padding: 0 14px; outline: none; font: inherit; }
.search-box button { border: 0; border-radius: 8px; color: #fff; background: var(--accent); font-weight: 800; cursor: pointer; font: inherit; }

.data-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-top: 20px; }
.data-card {
  border: 1px solid var(--line); border-radius: 10px; background: var(--panel);
  box-shadow: var(--shadow); padding: 20px;
}
.data-card span { color: var(--muted); font-size: 14px; }
.data-card strong { display: block; margin-top: 10px; font-size: 30px; }
.data-card p { margin-top: 8px; color: var(--muted); }

.workspace { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(300px, 0.85fr); gap: 18px; margin-top: 20px; align-items: start; }
.workspace-main, .workspace-side { display: grid; gap: 18px; }

.panel {
  border: 1px solid var(--line); border-radius: 10px; background: var(--panel);
  box-shadow: var(--shadow); padding: 18px; box-shadow: none;
}
.panel-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.panel-title h3 { font-size: 18px; }
.panel-title span { color: var(--muted); font-size: 13px; }

.tabs { display: inline-flex; padding: 3px; border-radius: 8px; background: #eef2f7; }
.tabs button { height: 28px; padding: 0 10px; border: 0; border-radius: 6px; background: transparent; color: var(--muted); cursor: pointer; font-size: 12px; font-weight: 700; font: inherit; }
.tabs button.active { background: #fff; color: var(--ink); box-shadow: 0 2px 8px rgba(22,32,51,0.08); }

.chart-area { height: 240px; padding-top: 10px; }
.chart-bars { display: flex; align-items: flex-end; gap: 12px; height: 100%; }
.bar { flex: 1; background: linear-gradient(to top, var(--accent), #38bdf8); border-radius: 6px 6px 0 0; position: relative; min-height: 16px; }
.bar-label { position: absolute; bottom: -22px; left: 50%; transform: translateX(-50%); font-size: 11px; color: var(--muted); white-space: nowrap; }

table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px 14px; border-bottom: 1px solid var(--line); text-align: left; font-size: 14px; }
th { color: var(--muted); font-size: 12px; font-weight: 700; background: var(--soft); }
tr:last-child td { border-bottom: 0; }

.status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status.done { background: #dcfce7; color: #15803d; }
.status.pending { background: #fef3c7; color: #b45309; }
.status.alert { background: #ffe4e6; color: #be123c; }

.task-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 0; }
.task-list li { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--line); }
.task-list li:last-child { border-bottom: 0; }
.task-list strong { display: block; font-size: 14px; }
.task-list > li > div > span { display: block; margin-top: 3px; color: var(--muted); font-size: 12px; }
.badge { display: inline-flex; align-items: center; justify-content: center; min-width: 28px; height: 24px; padding: 0 8px; border-radius: 999px; background: var(--soft); color: var(--accent); font-size: 12px; font-weight: 800; flex: 0 0 auto; }

.quick-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.quick-grid button { min-height: 72px; padding: 14px; text-align: left; border: 0; border-radius: 8px; color: #fff; background: var(--accent); font-weight: 800; cursor: pointer; font: inherit; }
.quick-grid button:hover { background: var(--accent-dark); }
.quick-grid strong, .quick-grid span { display: block; }
.quick-grid strong { font-size: 15px; }
.quick-grid span { margin-top: 6px; color: rgba(255,255,255,0.78); font-size: 12px; }

@media (max-width: 980px) { .hero { grid-template-columns: 1fr; } .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .workspace { grid-template-columns: 1fr; } }
@media (max-width: 620px) { .hero { padding: 20px; } h1 { font-size: 28px; } .data-grid, .quick-grid { grid-template-columns: 1fr; } }
</style>
