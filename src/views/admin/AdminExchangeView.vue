<script setup lang="ts">
import { ref } from 'vue'
defineOptions({ name: 'AdminExchangeView' })

const metrics = [
  { label: '待匹配请求', value: '18', note: '可重点筛选热门商品' },
  { label: '匹配中请求', value: '11', note: '仍需双方确认' },
  { label: '已完成换物', value: '63', note: '本月累计' },
  { label: '已失效请求', value: '7', note: '需归档处理' },
]

const requests = ref([
  { id: 'E202605060001', user: '星川', offer: '立牌限定 A', want: '同系列色纸 或 吧唧', status: 'pending', time: '2026-05-06 09:20' },
  { id: 'E202605050013', user: '阿零', offer: '吧唧套组 B', want: '等价交换，接受补差', status: 'confirming', time: '2026-05-05 16:10' },
  { id: 'E202605040021', user: '雾野', offer: '拍立得单张', want: '同角色周边优先', status: 'expired', time: '2026-05-04 13:40' },
])
const statusMap: Record<string, { text: string; cls: string }> = {
  pending: { text: '待匹配', cls: 'pending' },
  confirming: { text: '待确认', cls: 'confirming' },
  expired: { text: '已失效', cls: 'expired' },
}
</script>

<template>
  <section class="page-head">
    <div>
      <p class="eyebrow">换物管理</p>
      <h1>换物请求</h1>
      <p>审核换物请求、查看匹配状态、处理取消与失效记录</p>
    </div>
  </section>

  <section class="data-grid">
    <article v-for="(m, i) in metrics" :key="i" class="data-card">
      <span>{{ m.label }}</span><strong>{{ m.value }}</strong><p>{{ m.note }}</p>
    </article>
  </section>

  <section class="toolbar">
    <div class="search-box"><input type="search" placeholder="输入换物请求编号或发起用户"></div>
    <select><option>全部状态</option><option>待匹配</option><option>匹配中</option><option>待确认</option><option>已完成</option><option>已取消</option><option>已失效</option></select>
    <button class="primary" type="button">查询请求</button>
    <button class="secondary" type="button">重置筛选</button>
  </section>

  <section class="content-row">
    <article class="table-panel">
      <div class="section-head">
        <div><p class="eyebrow">换物列表</p><h2>全部换物请求</h2></div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>请求编号</th><th>发起用户</th><th>换出资产</th><th>目标条件</th><th>状态</th><th>创建时间</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="(r, i) in requests" :key="i">
              <td>{{ r.id }}</td>
              <td>{{ r.user }}</td>
              <td>{{ r.offer }}</td>
              <td>{{ r.want }}</td>
              <td><span class="status" :class="statusMap[r.status].cls">{{ statusMap[r.status].text }}</span></td>
              <td>{{ r.time }}</td>
              <td class="actions">
                <button class="secondary sm" type="button">查看</button>
                <button v-if="r.status === 'pending'" class="primary sm" type="button">标记匹配</button>
                <button v-if="r.status === 'confirming'" class="primary sm" type="button">跟进</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>

    <aside class="panel">
      <div class="panel-title"><h3>换物审核备注</h3></div>
      <div class="form-stack">
        <input type="text" placeholder="请求编号" />
        <select><option>审核结果</option><option>通过</option><option>退回修改</option><option>标记失效</option></select>
        <textarea placeholder="填写审核说明、风控备注或跟进结果"></textarea>
        <div class="form-actions">
          <button class="primary" type="button">保存备注</button>
          <button class="secondary" type="button">清空</button>
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
.primary.sm { height: 32px; padding: 0 12px; font-size: 13px; }
.secondary { height: 42px; padding: 0 16px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); font-weight: 700; cursor: pointer; font: inherit; }
.secondary.sm { height: 32px; padding: 0 12px; font-size: 13px; }

.content-row { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.7fr); gap: 18px; align-items: start; }
.table-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); overflow: hidden; }
.section-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; border-bottom: 1px solid var(--line); }
.section-head .eyebrow { margin-bottom: 4px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 14px 16px; border-bottom: 1px solid var(--line); text-align: left; font-size: 14px; }
th { color: var(--muted); font-size: 12px; font-weight: 700; background: var(--soft); }
tr:last-child td { border-bottom: 0; }
.status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status.pending { background: #dbeafe; color: #1d4ed8; }
.status.confirming { background: #ffedd5; color: #c2410c; }
.status.expired { background: #e5e7eb; color: #374151; }
.actions { display: flex; gap: 6px; }

.panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 18px; box-shadow: none; }
.panel-title { margin-bottom: 14px; }
.panel-title h3 { font-size: 18px; }
.form-stack { display: grid; gap: 12px; }
.form-actions { display: flex; gap: 8px; }

@media (max-width: 1100px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .content-row { grid-template-columns: 1fr; } }
</style>
