<script setup lang="ts">
import { ref } from 'vue'

defineOptions({ name: 'AdminUsersView' })

const users = ref([
  { id: 'BJUT000001', name: '张三', phone: '13812345678', assets: '12,500', credit: 95, registered: '2026-01-12', status: 'active' },
  { id: 'BJUT000002', name: '李四', phone: '13987654321', assets: '8,600', credit: 88, registered: '2026-02-03', status: 'frozen' },
  { id: 'BJUT000003', name: '王五', phone: '13711223344', assets: '15,200', credit: 99, registered: '2026-03-15', status: 'active' },
  { id: 'BJUT000004', name: '赵六', phone: '13655667788', assets: '6,300', credit: 72, registered: '2026-04-01', status: 'active' },
  { id: 'BJUT000005', name: '孙七', phone: '13599887766', assets: '21,800', credit: 91, registered: '2025-12-20', status: 'frozen' },
])

function toggleStatus(i: number) {
  users.value[i].status = users.value[i].status === 'active' ? 'frozen' : 'active'
}
</script>

<template>
  <section class="page-head">
    <div>
      <p class="eyebrow">用户管理</p>
      <h1>用户列表</h1>
      <p>搜索、冻结/解冻、查看用户详情及资产信息</p>
    </div>
  </section>

  <section class="toolbar">
    <div class="search-box"><input type="search" placeholder="搜索用户ID / 姓名 / 手机号"></div>
    <select><option>全部状态</option><option>正常</option><option>冻结</option></select>
    <select><option>信用等级</option><option>高</option><option>中</option><option>低</option></select>
    <button class="primary" type="button">应用筛选</button>
  </section>

  <section class="table-panel">
    <div class="section-head">
      <div><p class="eyebrow">用户列表</p><h2>全部用户</h2></div>
      <span>共 {{ users.length }} 条数据</span>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr><th>用户ID</th><th>姓名</th><th>手机号</th><th>资产总额</th><th>信用分</th><th>注册时间</th><th>状态</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="(u, i) in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.name }}</td>
            <td>{{ u.phone }}</td>
            <td>{{ u.assets }}</td>
            <td>{{ u.credit }}</td>
            <td>{{ u.registered }}</td>
            <td><span class="status" :class="u.status === 'active' ? 'hold' : 'frozen'">{{ u.status === 'active' ? '正常' : '冻结' }}</span></td>
            <td class="actions">
              <button class="primary sm" type="button" @click="toggleStatus(i)">{{ u.status === 'active' ? '冻结' : '解冻' }}</button>
              <button class="secondary sm" type="button">查看详情</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; margin-bottom: 20px; }
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, p { margin: 0; }
h1 { font-size: 32px; }
.page-head > div > p:last-child { margin-top: 8px; color: var(--muted); }

.toolbar {
  display: flex; gap: 12px; align-items: center; flex-wrap: wrap;
  padding: 18px; margin-bottom: 20px;
  border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow);
}
.search-box { flex: 1; min-width: 200px; }
.search-box input { width: 100%; height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 14px; font: inherit; background: var(--soft); }
select { height: 42px; border: 1px solid var(--line); border-radius: 8px; padding: 0 12px; font: inherit; background: var(--soft); min-width: 120px; }
.primary { height: 42px; padding: 0 18px; border: 0; border-radius: 8px; background: var(--accent); color: #fff; font-weight: 800; cursor: pointer; font: inherit; }
.primary:hover { background: var(--accent-dark); }
.primary.sm { height: 32px; padding: 0 12px; font-size: 13px; }
.secondary.sm { height: 32px; padding: 0 12px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); font-weight: 700; cursor: pointer; font: inherit; font-size: 13px; }

.table-panel {
  border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); overflow: hidden;
}
.section-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; border-bottom: 1px solid var(--line); }
.section-head .eyebrow { margin-bottom: 4px; }
.section-head span { color: var(--muted); font-size: 13px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; min-width: 800px; }
th, td { padding: 14px 20px; border-bottom: 1px solid var(--line); text-align: left; font-size: 14px; }
th { color: var(--muted); font-size: 12px; font-weight: 700; background: var(--soft); }
tr:last-child td { border-bottom: 0; }
.status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status.hold { background: #dcfce7; color: #15803d; }
.status.frozen { background: #fee2e2; color: #be123c; }
.actions { display: flex; gap: 6px; }

@media (max-width: 980px) { .toolbar { flex-direction: column; align-items: stretch; } .search-box { min-width: auto; } }
</style>
