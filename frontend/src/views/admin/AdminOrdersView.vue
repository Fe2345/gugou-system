<script setup lang="ts">
import { ref } from 'vue'
defineOptions({ name: 'AdminOrdersView' })

const metrics = [
  { label: '今日新增订单', value: '128', note: '较昨日增加 12 单' },
  { label: '待发货订单', value: '36', note: '需优先跟进' },
  { label: '异常处理中', value: '9', note: '退款与纠纷混合' },
  { label: '已完成订单', value: '452', note: '本周累计' },
]

const orders = ref([
  { id: 'O202605061030010001', buyer: '星野', seller: '柚子茶', goods: '吧唧套组 A', amount: '￥128.00', status: 'pending', time: '2026-05-06 10:30' },
  { id: 'O202605061122210002', buyer: '白昼', seller: '林深', goods: '色纸限定款', amount: '￥89.00', status: 'alert', time: '2026-05-06 11:22' },
  { id: 'O202605051558100018', buyer: '月海', seller: '塔塔', goods: '立牌单品', amount: '￥56.00', status: 'done', time: '2026-05-05 15:58' },
])
const statusMap: Record<string, string> = { pending: '待发货', alert: '异常处理', done: '已完成' }
</script>

<template>
  <section class="page-head">
    <div>
      <p class="eyebrow">订单处理</p>
      <h1>订单管理</h1>
      <p>查看订单状态、处理异常订单、跟踪发货与收货进度</p>
    </div>
  </section>

  <section class="data-grid">
    <article v-for="(m, i) in metrics" :key="i" class="data-card">
      <span>{{ m.label }}</span><strong>{{ m.value }}</strong><p>{{ m.note }}</p>
    </article>
  </section>

  <section class="toolbar">
    <div class="search-box"><input type="search" placeholder="输入订单编号或买家昵称"></div>
    <select><option>全部状态</option><option>待支付</option><option>已支付</option><option>待发货</option><option>待收货</option><option>已完成</option><option>异常处理中</option></select>
    <select><option>全部时间</option><option>今天</option><option>近3天</option><option>近7天</option></select>
    <button class="primary" type="button">查询订单</button>
    <button class="secondary" type="button">导出报表</button>
  </section>

  <section class="content-row">
    <article class="table-panel">
      <div class="section-head">
        <div><p class="eyebrow">订单列表</p><h2>全部订单</h2></div>
        <div class="head-actions">
          <button class="secondary sm" type="button">批量发货</button>
          <button class="danger sm" type="button">异常挂起</button>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>订单编号</th><th>买家</th><th>卖家</th><th>商品</th><th>金额</th><th>状态</th><th>下单时间</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="(o, i) in orders" :key="i">
              <td>{{ o.id }}</td>
              <td>{{ o.buyer }}</td>
              <td>{{ o.seller }}</td>
              <td>{{ o.goods }}</td>
              <td class="price">{{ o.amount }}</td>
              <td><span class="status" :class="o.status">{{ statusMap[o.status] }}</span></td>
              <td>{{ o.time }}</td>
              <td class="actions">
                <button class="secondary sm" type="button">查看</button>
                <button v-if="o.status === 'pending'" class="primary sm" type="button">发货</button>
                <button v-if="o.status === 'alert'" class="danger sm" type="button">介入</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>

    <aside class="panel">
      <div class="panel-title"><h3>异常订单处理</h3></div>
      <ul class="info-list">
        <li><strong>退款申请</strong><p>买家提交退款原因后，管理员核对付款与物流状态。</p></li>
        <li><strong>超时未发货</strong><p>系统自动标记后，管理员提醒卖家并记录跟进结果。</p></li>
        <li><strong>收货争议</strong><p>管理员查看订单详情、聊天记录与物流信息后进行处理。</p></li>
      </ul>
    </aside>
  </section>
</template>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 20px; }
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; } h1 { font-size: 32px; }
.page-head > div > p:last-child { margin-top: 8px; color: var(--muted); }

.data-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-bottom: 20px; }
.data-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 20px; }
.data-card span { color: var(--muted); font-size: 14px; }
.data-card strong { display: block; margin-top: 10px; font-size: 30px; }
.data-card p { margin-top: 8px; color: var(--muted); }

.toolbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; padding: 18px; margin-bottom: 20px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.search-box { flex: 1; min-width: 200px; }
.search-box input { width: 100%; height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 14px; font: inherit; background: var(--soft); }
select { height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; font: inherit; background: var(--soft); min-width: 120px; }
.primary { height: 42px; padding: 0 18px; border: 0; border-radius: 8px; background: var(--accent); color: #fff; font-weight: 800; cursor: pointer; font: inherit; }
.primary:hover { background: var(--accent-dark); }
.primary.sm { height: 32px; padding: 0 12px; font-size: 13px; }
.secondary { height: 42px; padding: 0 16px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); font-weight: 700; cursor: pointer; font: inherit; }
.secondary.sm { height: 32px; padding: 0 12px; font-size: 13px; }
.danger.sm { height: 32px; padding: 0 12px; border: 0; border-radius: 8px; background: #fee2e2; color: #be123c; font-weight: 700; cursor: pointer; font: inherit; font-size: 13px; }

.content-row { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.7fr); gap: 18px; align-items: start; }
.table-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); overflow: hidden; }
.section-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; border-bottom: 1px solid var(--line); }
.section-head .eyebrow { margin-bottom: 4px; }
.head-actions { display: flex; gap: 8px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 14px 16px; border-bottom: 1px solid var(--line); text-align: left; font-size: 14px; white-space: nowrap; }
th { color: var(--muted); font-size: 12px; font-weight: 700; background: var(--soft); }
tr:last-child td { border-bottom: 0; }
.price { color: #be123c; font-weight: 700; }
.status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status.pending { background: #fef3c7; color: #b45309; }
.status.alert { background: #ffe4e6; color: #be123c; }
.status.done { background: #dcfce7; color: #15803d; }
.actions { display: flex; gap: 6px; }

.panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 18px; box-shadow: none; }
.panel-title { margin-bottom: 14px; }
.panel-title h3 { font-size: 18px; }
.info-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
.info-list li { padding: 12px 14px; border: 1px solid var(--line); border-radius: 8px; background: var(--soft); }
.info-list strong { display: block; margin-bottom: 6px; font-size: 14px; }
.info-list p { margin: 0; color: var(--muted); font-size: 13px; line-height: 1.5; }

@media (max-width: 1100px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .content-row { grid-template-columns: 1fr; } }
</style>
