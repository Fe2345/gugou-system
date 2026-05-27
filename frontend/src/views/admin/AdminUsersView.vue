<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAdminUsersList, freezeUser, unfreezeUser } from '@/api/admin'
import type { AdminUser } from '@/api/admin'

defineOptions({ name: 'AdminUsersView' })

const loading = ref(false)
const users = ref<AdminUser[]>([])
const searchQuery = ref('')
const filterStatus = ref('')
const filterCredit = ref('')

const selectedUser = ref<AdminUser | null>(null)
const showDetailModal = ref(false)

async function loadUsers() {
  loading.value = true
  try {
    const res = await getAdminUsersList({
      keyword: searchQuery.value || undefined,
      status: filterStatus.value || undefined,
      creditLevel: filterCredit.value || undefined,
    })
    users.value = res.data
  } catch (e) {
    console.error('加载用户失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadUsers() })

function handleSearch() { loadUsers() }
function handleFilter() { loadUsers() }

async function handleToggleStatus(user: AdminUser) {
  loading.value = true
  try {
    if (user.status === 'active') {
      await freezeUser(user.id)
    } else {
      await unfreezeUser(user.id)
    }
    await loadUsers()
  } catch (e) {
    console.error('状态切换失败', e)
  } finally {
    loading.value = false
  }
}

function viewDetail(user: AdminUser) {
  selectedUser.value = user
  showDetailModal.value = true
}

function closeDetailModal() {
  showDetailModal.value = false
  selectedUser.value = null
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
    <div class="search-box"><input v-model="searchQuery" type="search" placeholder="搜索用户ID / 姓名 / 手机号" @keyup.enter="handleSearch"></div>
    <select v-model="filterStatus" @change="handleFilter">
      <option value="">全部状态</option><option value="正常">正常</option><option value="冻结">冻结</option>
    </select>
    <select v-model="filterCredit" @change="handleFilter">
      <option value="">信用等级</option><option value="高">高 (≥90)</option><option value="中">中 (70-89)</option><option value="低">低 (&lt;70)</option>
    </select>
    <button class="primary" type="button" :disabled="loading" @click="handleSearch">{{ loading ? '加载中...' : '应用筛选' }}</button>
  </section>

  <section class="table-panel">
    <div class="section-head">
      <div><p class="eyebrow">用户列表</p><h2>全部用户</h2></div>
      <span>共 {{ users.length }} 条数据</span>
    </div>
    <div v-if="!users.length" class="empty-state">
      <strong>暂无用户数据</strong>
    </div>
    <div v-else class="table-wrap">
      <table>
        <thead>
          <tr><th>用户ID</th><th>姓名</th><th>手机号</th><th>资产总额</th><th>信用分</th><th>注册时间</th><th>状态</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.name }}</td>
            <td>{{ u.phone }}</td>
            <td>¥{{ u.assets.toLocaleString() }}</td>
            <td>{{ u.credit }}</td>
            <td>{{ u.registered }}</td>
            <td><span class="status" :class="u.status === 'active' ? 'hold' : 'frozen'">{{ u.status === 'active' ? '正常' : '冻结' }}</span></td>
            <td class="actions">
              <button class="primary sm" type="button" @click="handleToggleStatus(u)" :disabled="loading">{{ u.status === 'active' ? '冻结' : '解冻' }}</button>
              <button class="secondary sm" type="button" @click="viewDetail(u)">查看详情</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <!-- 用户详情弹窗 -->
  <div v-if="showDetailModal && selectedUser" class="modal-overlay" @click.self="closeDetailModal">
    <div class="modal">
      <div class="modal-header">
        <h2>用户详情</h2>
        <button class="modal-close" @click="closeDetailModal">&times;</button>
      </div>
      <div class="detail-content">
        <div class="detail-fields">
          <div class="field"><label>用户ID</label><span>{{ selectedUser.id }}</span></div>
          <div class="field"><label>姓名</label><span>{{ selectedUser.name }}</span></div>
          <div class="field"><label>手机号</label><span>{{ selectedUser.phone }}</span></div>
          <div class="field"><label>资产总额</label><span>¥{{ selectedUser.assets.toLocaleString() }}</span></div>
          <div class="field"><label>信用分</label><span>{{ selectedUser.credit }}</span></div>
          <div class="field"><label>注册时间</label><span>{{ selectedUser.registered }}</span></div>
          <div class="field"><label>状态</label><span :class="selectedUser.status === 'active' ? 'text-green' : 'text-red'">{{ selectedUser.status === 'active' ? '正常' : '冻结' }}</span></div>
        </div>
      </div>
      <div class="modal-actions">
        <button type="button" class="secondary" @click="closeDetailModal">关闭</button>
        <button type="button" class="primary" @click="handleToggleStatus(selectedUser); closeDetailModal()">
          {{ selectedUser.status === 'active' ? '冻结用户' : '解冻用户' }}
        </button>
      </div>
    </div>
  </div>
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
.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.primary.sm { height: 32px; padding: 0 12px; font-size: 13px; }
.secondary { height: 42px; padding: 0 16px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); font-weight: 700; cursor: pointer; font: inherit; }
.secondary.sm { height: 32px; padding: 0 12px; border: 1px solid var(--line); border-radius: 8px; background: var(--panel); color: var(--ink); font-weight: 700; cursor: pointer; font: inherit; font-size: 13px; }

.table-panel {
  border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); overflow: hidden;
}
.section-head { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px; border-bottom: 1px solid var(--line); }
.section-head .eyebrow { margin-bottom: 4px; }
.section-head span { color: var(--muted); font-size: 13px; }
.empty-state { min-height: 120px; display: grid; place-items: center; color: var(--muted); }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; min-width: 800px; }
th, td { padding: 14px 20px; border-bottom: 1px solid var(--line); text-align: left; font-size: 14px; }
th { color: var(--muted); font-size: 12px; font-weight: 700; background: var(--soft); }
tr:last-child td { border-bottom: 0; }
.status { display: inline-flex; align-items: center; height: 24px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.status.hold { background: #dcfce7; color: #15803d; }
.status.frozen { background: #fee2e2; color: #be123c; }
.actions { display: flex; gap: 6px; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: grid; place-items: center; z-index: 1000; padding: 20px; }
.modal { background: var(--panel); border-radius: 16px; width: min(520px, 100%); max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid var(--line); }
.modal-header h2 { font-size: 22px; }
.modal-close { width: 36px; height: 36px; border: 0; border-radius: 8px; background: var(--soft); color: var(--muted); font-size: 22px; cursor: pointer; display: grid; place-items: center; }
.detail-content { padding: 24px; }
.detail-fields { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.field { display: grid; gap: 6px; }
.field label { color: var(--muted); font-size: 13px; }
.field span { font-weight: 600; font-size: 15px; }
.text-green { color: #15803d; }
.text-red { color: #be123c; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; padding: 16px 24px; border-top: 1px solid var(--line); }

@media (max-width: 980px) { .toolbar { flex-direction: column; align-items: stretch; } .search-box { min-width: auto; } }
</style>
