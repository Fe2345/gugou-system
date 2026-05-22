<script setup lang="ts">
import { ref } from 'vue'

defineOptions({ name: 'AdminGoodsView' })
const activeTab = ref('待审核')

const metrics = [
  { label: '待审核商品', value: '24', note: '今日新增审核 9 件' },
  { label: '上架中商品', value: '3,286', note: '平台可交易商品' },
  { label: '今日通过', value: '18', note: '审核通过率 86%' },
  { label: '未通过/下架', value: '7', note: '图片或价格异常较多' },
]

const products = ref([
  { name: '蓝色幻想系列 限定徽章套组', seller: 'BJUT000126', time: '12 分钟前', price: '￥128', tags: ['待审核', '徽章', '热门IP'] },
  { name: '樱花季角色亚克力立牌', seller: 'BJUT000219', time: '28 分钟前', price: '￥68', tags: ['待审核', '立牌', '图片待核验'] },
  { name: '限定拍立得收藏卡 随机款', seller: 'BJUT000308', time: '1 小时前', price: '￥45', tags: ['待审核', '拍立得', '价格异常'] },
])

const tableData = ref([
  { name: '蓝色幻想系列 限定徽章套组', code: 'PRBJUT0001260001', category: '徽章/吧唧', seller: 'BJUT000126', price: '￥128', stock: 12, time: '10:28', status: 'pending' },
  { name: '樱花季角色亚克力立牌', code: 'PRBJUT0002190004', category: '亚克力立牌', seller: 'BJUT000219', price: '￥68', stock: 8, time: '09:52', status: 'pending' },
  { name: '限定拍立得收藏卡 随机款', code: 'PRBJUT0003080011', category: '拍立得/色纸', seller: 'BJUT000308', price: '￥45', stock: 20, time: '昨天', status: 'reject' },
  { name: '角色挂件 生日纪念款', code: 'PRBJUT0001760022', category: '挂件', seller: 'BJUT000176', price: '￥36', stock: 15, time: '昨天', status: 'online' },
])
const statusMap: Record<string, string> = { pending: '待审核', online: '已上架', reject: '未通过' }

const records = [
  { text: '通过"生日纪念挂件"上架', desc: '审核员：系统管理员', time: '10:36' },
  { text: '驳回"限定拍立得收藏卡"', desc: '原因：价格异常', time: '09:58' },
  { text: '修改"亚克力立牌"分类', desc: '从"挂件"调整为"亚克力立牌"', time: '昨天' },
  { text: '下架异常商品', desc: '原因：用户举报图片与实物不符', time: '昨天' },
]
</script>

<template>
  <section class="page-head">
    <div>
      <p class="eyebrow">商品审核</p>
      <h1>商品管理</h1>
      <p>审核商品、上架/下架、修改商品信息与追踪处理记录</p>
    </div>
    <button class="primary" type="button">新增商品</button>
  </section>

  <section class="data-grid">
    <article v-for="(m, i) in metrics" :key="i" class="data-card">
      <span>{{ m.label }}</span>
      <strong>{{ m.value }}</strong>
      <p>{{ m.note }}</p>
    </article>
  </section>

  <section class="toolbar">
    <div class="search-box"><input type="search" placeholder="输入商品名称 / 商品编号 / 卖家ID"></div>
    <select><option>全部状态</option><option>待审核</option><option>已上架</option><option>未通过</option><option>已下架</option></select>
    <select><option>全部分类</option><option>徽章/吧唧</option><option>亚克力立牌</option><option>色纸/拍立得</option><option>手办/挂件</option></select>
    <select><option>提交时间</option><option>今天</option><option>近7天</option><option>近30天</option></select>
    <button class="primary" type="button">筛选商品</button>
  </section>

  <section class="card-grid">
    <article v-for="(p, i) in products" :key="i" class="product-card">
      <div class="product-cover" :class="'cover-' + i">
        <div class="cover-mark">{{ ['谷', 'IP', '限'][i] }}</div>
      </div>
      <div class="product-body">
        <div class="product-top">
          <div>
            <strong>{{ p.name }}</strong>
            <span class="meta">卖家：{{ p.seller }} · {{ p.time }}</span>
          </div>
          <span class="price">{{ p.price }}</span>
        </div>
        <div class="tags"><span v-for="tag in p.tags" :key="tag">{{ tag }}</span></div>
        <div class="product-actions">
          <button class="primary sm" type="button">通过上架</button>
          <button class="danger sm" type="button">不通过</button>
          <button class="secondary sm" type="button">修改信息</button>
        </div>
      </div>
    </article>
  </section>

  <section class="table-panel" style="margin-top:20px">
    <div class="section-head">
      <div><p class="eyebrow">审核记录</p><h2>商品审核列表</h2></div>
      <div class="head-actions">
        <button class="secondary sm" type="button">批量通过</button>
        <button class="secondary sm" type="button">批量下架</button>
      </div>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr><th>商品名称</th><th>编号</th><th>分类</th><th>卖家</th><th>价格</th><th>库存</th><th>提交时间</th><th>状态</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="(row, i) in tableData" :key="i">
            <td><strong>{{ row.name }}</strong></td>
            <td class="muted">{{ row.code }}</td>
            <td>{{ row.category }}</td>
            <td>{{ row.seller }}</td>
            <td class="price">{{ row.price }}</td>
            <td>{{ row.stock }}</td>
            <td>{{ row.time }}</td>
            <td><span class="status" :class="row.status">{{ statusMap[row.status] }}</span></td>
            <td class="actions">
              <button v-if="row.status !== 'online'" class="primary sm" type="button">上架</button>
              <button v-if="row.status === 'pending'" class="danger sm" type="button">驳回</button>
              <button v-if="row.status === 'reject'" class="primary sm" type="button">复审</button>
              <button v-if="row.status === 'online'" class="warn sm" type="button">下架</button>
              <button class="secondary sm" type="button">编辑</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="pagination">
      <span>共 128 条，当前 1-4 条</span>
      <div class="page-btns"><button>‹</button><button class="active">1</button><button>2</button><button>3</button><button>›</button></div>
    </div>
  </section>

  <section class="side-section">
    <article class="panel">
      <div class="panel-title"><h3>审核流程</h3></div>
      <div class="flow">
        <div v-for="(step, i) in [
          { title: '待审核', desc: '管理员检查图片、描述、价格和分类。', cls: 'active' },
          { title: '审核通过', desc: '商品状态更新为已上架，进入前台交易市场。', cls: 'success' },
          { title: '未通过', desc: '图片不清晰、价格异常等问题将被驳回。', cls: 'reject' },
          { title: '下架/归档', desc: '商品售出或违规后进入已下架状态。', cls: '' },
        ]" :key="i" class="flow-step" :class="step.cls">
          <div class="flow-icon">{{ i + 1 }}</div>
          <div><strong>{{ step.title }}</strong><p>{{ step.desc }}</p></div>
        </div>
      </div>
    </article>
    <article class="panel">
      <div class="panel-title"><h3>最近处理</h3></div>
      <ul class="record-list">
        <li v-for="(r, i) in records" :key="i">
          <div><strong>{{ r.text }}</strong><span>{{ r.desc }}</span></div>
          <span class="time">{{ r.time }}</span>
        </li>
      </ul>
    </article>
  </section>
</template>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 20px; }
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, h3, p { margin: 0; }
h1 { font-size: 32px; }
.page-head > div > p:last-child { margin-top: 8px; color: var(--muted); }
.primary { height: 42px; padding: 0 18px; border: 0; border-radius: 8px; background: var(--accent); color: #fff; font-weight: 800; cursor: pointer; font: inherit; }
.primary:hover { background: var(--accent-dark); }
.primary.sm { height: 32px; padding: 0 12px; font-size: 13px; }
.secondary.sm { height: 32px; padding: 0 12px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); font-weight: 700; cursor: pointer; font: inherit; font-size: 13px; }
.danger.sm { height: 32px; padding: 0 12px; border: 0; border-radius: 8px; background: #fee2e2; color: #be123c; font-weight: 700; cursor: pointer; font: inherit; font-size: 13px; }
.warn.sm { height: 32px; padding: 0 12px; border: 0; border-radius: 8px; background: #fef3c7; color: #b45309; font-weight: 700; cursor: pointer; font: inherit; font-size: 13px; }

.data-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-bottom: 20px; }
.data-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 20px; }
.data-card span { color: var(--muted); font-size: 14px; }
.data-card strong { display: block; margin-top: 10px; font-size: 30px; }
.data-card p { margin-top: 8px; color: var(--muted); }

.toolbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; padding: 18px; margin-bottom: 20px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.search-box { flex: 1; min-width: 200px; }
.search-box input { width: 100%; height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 14px; font: inherit; background: var(--soft); }
select { height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; font: inherit; background: var(--soft); min-width: 120px; }

.card-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.product-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); overflow: hidden; transition: transform 0.18s; }
.product-card:hover { transform: translateY(-2px); }
.product-cover { position: relative; height: 120px; background: linear-gradient(135deg, #93c5fd, #c4b5fd 55%, #f9a8d4); }
.cover-1 { background: linear-gradient(135deg, #fda4af, #fcd34d 50%, #86efac); }
.cover-2 { background: linear-gradient(135deg, #67e8f9, #60a5fa 46%, #818cf8); }
.cover-mark { position: absolute; left: 16px; bottom: 16px; width: 44px; height: 44px; border-radius: 12px; background: rgba(255,255,255,.9); display: grid; place-items: center; color: var(--accent); font-size: 18px; font-weight: 900; box-shadow: 0 8px 16px rgba(22,32,51,.12); }
.product-body { padding: 14px; }
.product-top { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 8px; }
.product-top strong { font-size: 14px; line-height: 1.4; }
.meta { display: block; margin-top: 4px; color: var(--muted); font-size: 12px; }
.price { color: #be123c; font-weight: 900; white-space: nowrap; }
.tags { display: flex; gap: 6px; flex-wrap: wrap; margin: 10px 0; }
.tags span { height: 22px; padding: 0 8px; border-radius: 999px; background: var(--soft); color: var(--accent); font-size: 11px; font-weight: 800; display: inline-flex; align-items: center; }
.product-actions { display: flex; gap: 6px; margin-top: 10px; }

.table-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); overflow: hidden; }
.section-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; border-bottom: 1px solid var(--line); }
.section-head .eyebrow { margin-bottom: 4px; }
.head-actions { display: flex; gap: 8px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 14px 16px; border-bottom: 1px solid var(--line); text-align: left; font-size: 14px; }
th { color: var(--muted); font-size: 12px; font-weight: 700; background: var(--soft); }
tr:last-child td { border-bottom: 0; }
.muted { color: var(--muted); font-size: 12px; }
.status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status.pending { background: #fef3c7; color: #b45309; }
.status.online { background: #dcfce7; color: #15803d; }
.status.reject { background: #fee2e2; color: #be123c; }
.actions { display: flex; gap: 6px; }
.pagination { display: flex; justify-content: space-between; align-items: center; padding: 14px 20px; border-top: 1px solid var(--line); }
.pagination span { color: var(--muted); font-size: 13px; }
.page-btns { display: flex; gap: 6px; }
.page-btns button { min-width: 30px; height: 30px; border: 1px solid var(--line); border-radius: 6px; background: #fff; color: var(--muted); cursor: pointer; font-weight: 800; font: inherit; }
.page-btns button.active { background: var(--accent); color: #fff; border-color: var(--accent); }

.side-section { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 20px; }
.panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 18px; box-shadow: none; }
.panel-title { margin-bottom: 14px; }
.panel-title h3 { font-size: 18px; }

.flow { display: grid; gap: 16px; }
.flow-step { display: grid; grid-template-columns: 32px minmax(0, 1fr); gap: 10px; }
.flow-icon { width: 32px; height: 32px; border-radius: 8px; background: var(--soft); color: var(--accent); display: grid; place-items: center; font-weight: 900; font-size: 12px; }
.flow-step.active .flow-icon { background: var(--accent); color: #fff; }
.flow-step.success .flow-icon { background: #dcfce7; color: #15803d; }
.flow-step.reject .flow-icon { background: #fee2e2; color: #be123c; }
.flow-step strong { font-size: 14px; }
.flow-step p { margin-top: 3px; color: var(--muted); font-size: 12px; line-height: 1.5; }

.record-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 0; }
.record-list li { display: flex; justify-content: space-between; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--line); }
.record-list li:last-child { border-bottom: 0; }
.record-list strong { display: block; font-size: 14px; }
.record-list > li > div > span { display: block; margin-top: 3px; color: var(--muted); font-size: 12px; }
.time { color: var(--muted); font-size: 12px; white-space: nowrap; flex: 0 0 auto; }

@media (max-width: 1100px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .side-section { grid-template-columns: 1fr; } }
@media (max-width: 760px) { .card-grid, .data-grid { grid-template-columns: 1fr; } .toolbar { flex-direction: column; align-items: stretch; } }
</style>
