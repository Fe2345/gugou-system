<script setup lang="ts">
import { ref } from 'vue'
defineOptions({ name: 'AdminPriceView' })

const metrics = [
  { label: '新增价格记录', value: '76', note: '今日已同步' },
  { label: '波动较大商品', value: '12', note: '涨跌幅超过 15%' },
  { label: '近7天均价', value: '￥84.6', note: '平台总体均值' },
  { label: '待复核记录', value: '4', note: '来源异常待确认' },
]

const records = ref([
  { id: 'PR202605060001', name: '吧唧限定 A', price: '￥56.00', period: '近7天', change: '+8.5%', cls: 'up' },
  { id: 'PR202605060008', name: '色纸套组 B', price: '￥105.00', period: '近30天', change: '-6.2%', cls: 'down' },
  { id: 'PR202605050022', name: '拍立得单张', price: '￥39.00', period: '近7天', change: '+15.0%', cls: 'warn' },
])
</script>

<template>
  <section class="page-head">
    <div>
      <p class="eyebrow">价格记录</p>
      <h1>价格管理</h1>
      <p>查看商品历史成交价格、涨跌幅、统计区间与记录维护情况</p>
    </div>
  </section>

  <section class="data-grid">
    <article v-for="(m, i) in metrics" :key="i" class="data-card">
      <span>{{ m.label }}</span><strong>{{ m.value }}</strong><p>{{ m.note }}</p>
    </article>
  </section>

  <section class="toolbar">
    <div class="search-box"><input type="search" placeholder="输入商品名称或记录编号"></div>
    <select><option>统计区间</option><option>近7天</option><option>近30天</option><option>近90天</option></select>
    <select><option>波动范围</option><option>全部</option><option>上涨</option><option>下跌</option></select>
    <button class="primary" type="button">查询记录</button>
    <button class="secondary" type="button">导出数据</button>
  </section>

  <section class="content-row">
    <article class="table-panel">
      <div class="section-head">
        <div><p class="eyebrow">价格列表</p><h2>价格记录</h2></div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>记录编号</th><th>商品名称</th><th>成交价格</th><th>统计区间</th><th>涨跌幅</th><th>统计时间</th></tr></thead>
          <tbody>
            <tr v-for="(r, i) in records" :key="i">
              <td>{{ r.id }}</td>
              <td>{{ r.name }}</td>
              <td class="price">{{ r.price }}</td>
              <td>{{ r.period }}</td>
              <td><span class="change" :class="r.cls">{{ r.change }}</span></td>
              <td>{{ r.id === 'PR202605050022' ? '2026-05-05 18:00' : '2026-05-06 ' + (i === 0 ? '08:00' : '09:30') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>

    <aside class="panel">
      <div class="panel-title"><h3>新增价格记录</h3></div>
      <div class="form-stack">
        <input type="text" placeholder="商品名称" />
        <input type="text" placeholder="成交价格" />
        <select><option>统计区间</option><option>近7天</option><option>近30天</option><option>近90天</option></select>
        <input type="text" placeholder="涨跌幅" />
        <textarea placeholder="填写数据来源、记录说明或复核备注"></textarea>
        <div class="form-actions">
          <button class="primary" type="button">保存记录</button>
          <button class="secondary" type="button">取消</button>
        </div>
      </div>
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
select, input[type="text"] { height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; font: inherit; background: var(--soft); min-width: 120px; }
textarea { border: 1px solid var(--line); border-radius: 8px; padding: 12px; font: inherit; background: var(--soft); min-height: 100px; resize: vertical; width: 100%; }
.primary { height: 42px; padding: 0 18px; border: 0; border-radius: 8px; background: var(--accent); color: #fff; font-weight: 800; cursor: pointer; font: inherit; }
.primary:hover { background: var(--accent-dark); }
.secondary { height: 42px; padding: 0 16px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); font-weight: 700; cursor: pointer; font: inherit; }

.content-row { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.7fr); gap: 18px; align-items: start; }
.table-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); overflow: hidden; }
.section-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; border-bottom: 1px solid var(--line); }
.section-head .eyebrow { margin-bottom: 4px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 14px 16px; border-bottom: 1px solid var(--line); text-align: left; font-size: 14px; }
th { color: var(--muted); font-size: 12px; font-weight: 700; background: var(--soft); }
tr:last-child td { border-bottom: 0; }
.price { color: #be123c; font-weight: 700; }
.change { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.change.up { background: #dcfce7; color: #15803d; }
.change.down { background: #fee2e2; color: #be123c; }
.change.warn { background: #ffedd5; color: #c2410c; }

.panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 18px; box-shadow: none; }
.panel-title { margin-bottom: 14px; }
.panel-title h3 { font-size: 18px; }
.form-stack { display: grid; gap: 12px; }
.form-actions { display: flex; gap: 8px; }

@media (max-width: 1100px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .content-row { grid-template-columns: 1fr; } }
</style>
