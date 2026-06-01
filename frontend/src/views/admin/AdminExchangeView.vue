<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getSwapList, type SwapItem } from '@/api/swap'
defineOptions({ name: 'AdminExchangeView' })

const requests = ref<SwapItem[]>([])
const loading = ref(false)
const totalCount = ref(0)

const statusMap: Record<string, { text: string; cls: string }> = {
  active: { text: '可交易', cls: 'pending' },
  matched: { text: '匹配中', cls: 'confirming' },
  completed: { text: '已完成', cls: 'done' },
  cancelled: { text: '已取消', cls: 'expired' },
  expired: { text: '已过期', cls: 'expired' },
}

async function loadSwaps() {
  loading.value = true
  try {
    const res = await getSwapList({ page: 1, page_size: 50 })
    if (res.code === 200) {
      requests.value = res.data.results
      totalCount.value = res.data.count
    }
  } catch (e) {
    console.error('加载换物请求失败', e)
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadSwaps()
})
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
    <article class="data-card">
      <span>总请求数</span><strong>{{ totalCount }}</strong><p>全部换物请求</p>
    </article>
    <article class="data-card">
      <span>可交易</span><strong>{{ requests.filter(r => r.status === 'active').length }}</strong><p>等待匹配</p>
    </article>
    <article class="data-card">
      <span>匹配中</span><strong>{{ requests.filter(r => r.status === 'matched').length }}</strong><p>双方确认中</p>
    </article>
    <article class="data-card">
      <span>已完成</span><strong>{{ requests.filter(r => r.status === 'completed').length }}</strong><p>本月累计</p>
    </article>
  </section>

  <section class="toolbar">
    <div class="search-box"><input type="search" placeholder="输入换物请求编号或发起用户"></div>
    <select><option>全部状态</option><option>可交易</option><option>匹配中</option><option>已完成</option><option>已取消</option></select>
    <button class="primary" type="button" @click="loadSwaps">刷新请求</button>
  </section>

  <section class="content-row">
    <article class="table-panel">
      <div class="section-head">
        <div><p class="eyebrow">换物列表</p><h2>全部换物请求</h2></div>
        <span class="count-badge">共 {{ totalCount }} 条</span>
      </div>
      <div v-if="loading" class="loading-state">加载中...</div>
      <div v-else class="table-wrap">
        <table>
          <thead><tr><th>请求编号</th><th>发起用户</th><th>换出资产</th><th>目标条件</th><th>状态</th><th>创建时间</th></tr></thead>
          <tbody>
            <tr v-for="r in requests" :key="r.exchange_id">
              <td>{{ r.exchange_id }}</td>
              <td>{{ r.owner_name }}</td>
              <td>{{ r.offered_asset_name }}</td>
              <td>{{ r.target_condition || '不限' }}</td>
              <td><span class="status" :class="statusMap[r.status]?.cls">{{ statusMap[r.status]?.text }}</span></td>
              <td>{{ formatDate(r.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>

    <aside class="panel">
      <div class="panel-title"><h3>换物审核备注</h3></div>
      <ul class="info-list">
        <li><strong>请求审核</strong><p>核对换出资产信息、目标条件是否合理。</p></li>
        <li><strong>匹配管理</strong><p>查看匹配记录，协助双方完成交换。</p></li>
        <li><strong>状态维护</strong><p>超时请求标记失效，完成请求归档。</p></li>
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
.secondary { height: 42px; padding: 0 16px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); font-weight: 700; cursor: pointer; font: inherit; }

.content-row { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.7fr); gap: 18px; align-items: start; }
.table-panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); overflow: hidden; }
.section-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; border-bottom: 1px solid var(--line); }
.section-head .eyebrow { margin-bottom: 4px; }
.count-badge { color: var(--muted); font-size: 14px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 14px 16px; border-bottom: 1px solid var(--line); text-align: left; font-size: 14px; }
th { color: var(--muted); font-size: 12px; font-weight: 700; background: var(--soft); }
tr:last-child td { border-bottom: 0; }
.status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status.pending { background: #dbeafe; color: #1d4ed8; }
.status.confirming { background: #ffedd5; color: #c2410c; }
.status.done { background: #dcfce7; color: #15803d; }
.status.expired { background: #e5e7eb; color: #374151; }
.loading-state { padding: 40px; text-align: center; color: var(--muted); }

.panel { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); padding: 18px; box-shadow: none; }
.panel-title { margin-bottom: 14px; }
.panel-title h3 { font-size: 18px; }
.info-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
.info-list li { padding: 12px 14px; border: 1px solid var(--line); border-radius: 8px; background: var(--soft); }
.info-list strong { display: block; margin-bottom: 6px; font-size: 14px; }
.info-list p { margin: 0; color: var(--muted); font-size: 13px; line-height: 1.5; }

@media (max-width: 1100px) { .data-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .content-row { grid-template-columns: 1fr; } }
</style>
