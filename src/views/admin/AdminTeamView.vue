<script setup lang="ts">
import { ref } from 'vue'
defineOptions({ name: 'AdminTeamView' })

const metrics = [
  { label: '招募中项目', value: '24', note: '需关注截止时间' },
  { label: '即将成团', value: '6', note: '当前人数接近目标' },
  { label: '已成团项目', value: '42', note: '本月累计' },
  { label: '失败项目', value: '5', note: '需做原因分析' },
]

const teams = ref([
  { id: 'T202605060001', goods: '色纸套组 A', leader: '团长阿夏', progress: '4 / 5', price: '￥69.00', status: 'recruiting', deadline: '2026-05-08 20:00' },
  { id: 'T202605050014', goods: '吧唧福袋', leader: '风铃', progress: '5 / 5', price: '￥118.00', status: 'success', deadline: '2026-05-07 18:00' },
  { id: 'T202605040009', goods: '亚克力立牌', leader: '七濑', progress: '2 / 6', price: '￥52.00', status: 'failed', deadline: '2026-05-05 12:00' },
])
const statusMap: Record<string, { text: string; cls: string }> = {
  recruiting: { text: '招募中', cls: 'pending' },
  success: { text: '已成团', cls: 'done' },
  failed: { text: '已失败', cls: 'failed' },
}
</script>

<template>
  <section class="page-head">
    <div>
      <p class="eyebrow">拼团管理</p>
      <h1>拼团项目</h1>
      <p>查看拼团项目、管理拼团进度、处理成团与失败状态</p>
    </div>
  </section>

  <section class="data-grid">
    <article v-for="(m, i) in metrics" :key="i" class="data-card">
      <span>{{ m.label }}</span><strong>{{ m.value }}</strong><p>{{ m.note }}</p>
    </article>
  </section>

  <section class="toolbar">
    <div class="search-box"><input type="search" placeholder="输入拼团编号或商品名称"></div>
    <select><option>全部状态</option><option>待发布</option><option>招募中</option><option>已成团</option><option>已失败</option><option>已结束</option></select>
    <button class="primary" type="button">查询拼团</button>
    <button class="secondary" type="button">导出项目</button>
  </section>

  <section class="content-row">
    <article class="table-panel">
      <div class="section-head">
        <div><p class="eyebrow">拼团列表</p><h2>全部拼团项目</h2></div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>拼团编号</th><th>商品</th><th>发起用户</th><th>人数进度</th><th>团购价</th><th>状态</th><th>截止时间</th></tr></thead>
          <tbody>
            <tr v-for="(t, i) in teams" :key="i">
              <td>{{ t.id }}</td>
              <td>{{ t.goods }}</td>
              <td>{{ t.leader }}</td>
              <td>{{ t.progress }}</td>
              <td class="price">{{ t.price }}</td>
              <td><span class="status" :class="statusMap[t.status].cls">{{ statusMap[t.status].text }}</span></td>
              <td>{{ t.deadline }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>

    <aside class="panel">
      <div class="panel-title"><h3>拼团管理动作</h3></div>
      <ul class="info-list">
        <li><strong>项目审核</strong><p>核对商品信息、团购价格、截止时间与人数设置是否合理。</p></li>
        <li><strong>状态维护</strong><p>人数达标标记已成团，超时未满足标记已失败。</p></li>
        <li><strong>成员查看</strong><p>查看拼团参与记录，用于后续对账与通知。</p></li>
      </ul>
      <div class="form-actions" style="margin-top:14px">
        <button class="primary" type="button">查看参与成员</button>
        <button class="secondary" type="button">更新状态</button>
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
select { height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; font: inherit; background: var(--soft); min-width: 120px; }
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
.status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status.pending { background: #dbeafe; color: #1d4ed8; }
.status.done { background: #dcfce7; color: #15803d; }
.status.failed { background: #fee2e2; color: #be123c; }

.panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 18px; box-shadow: none; }
.panel-title { margin-bottom: 14px; }
.panel-title h3 { font-size: 18px; }
.info-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
.info-list li { padding: 12px 14px; border: 1px solid var(--line); border-radius: 8px; background: var(--soft); }
.info-list strong { display: block; margin-bottom: 6px; font-size: 14px; }
.info-list p { margin: 0; color: var(--muted); font-size: 13px; line-height: 1.5; }
.form-actions { display: flex; gap: 8px; }

@media (max-width: 1100px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .content-row { grid-template-columns: 1fr; } }
</style>
