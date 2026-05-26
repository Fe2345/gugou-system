<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import TopBar from '@/layouts/TopBar.vue'
import { useUserStore } from '@/stores/user'
import { getUserInfo, updateUserInfo } from '@/api/user'
import type { UserInfo } from '@/types/user'

defineOptions({ name: 'ProfileView' })

const userStore = useUserStore()
const user = ref<UserInfo | null>(null)
const loading = ref(false)
const saving = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')

// 编辑弹窗
const showEditModal = ref(false)
const editForm = reactive({ nickname: '', bio: '', contact: '' })

// 侧边菜单
const activeMenu = ref('basic')
const menus = [
  { key: 'basic', label: '基本信息' },
  { key: 'address', label: '地址管理' },
  { key: 'security', label: '安全设置' },
  { key: 'credit', label: '信用评价' },
  { key: 'messages', label: '消息通知' },
]

function showMessage(msg: string, type: 'success' | 'error' = 'success') {
  message.value = msg
  messageType.value = type
  setTimeout(() => { message.value = '' }, 3000)
}

function maskPhone(phone: string) {
  if (phone.length === 11) return phone.slice(0, 3) + '****' + phone.slice(7)
  return phone
}

const roleMap: Record<string, string> = { user: '普通用户', admin: '管理员' }
const statusMap: Record<string, string> = { normal: '正常', frozen: '冻结', disabled: '停用', deleted: '已注销' }
const statusClassMap: Record<string, string> = { normal: 'tag ok', frozen: 'tag warn', disabled: 'tag warn', deleted: 'tag' }

function getCreditLevel(score: number) {
  if (score >= 90) return '优秀用户'
  if (score >= 70) return '良好用户'
  if (score >= 50) return '一般用户'
  return '需改善'
}

async function loadUser() {
  loading.value = true
  try {
    const res = await getUserInfo()
    user.value = res.data
    userStore.setUserInfo(res.data)
  } catch {
    showMessage('加载用户信息失败', 'error')
  } finally {
    loading.value = false
  }
}

function openEdit() {
  if (!user.value) return
  editForm.nickname = user.value.nickname
  editForm.bio = user.value.bio || ''
  editForm.contact = user.value.contact || ''
  showEditModal.value = true
}

function closeEdit() {
  showEditModal.value = false
}

async function handleSave() {
  if (!user.value) return
  saving.value = true
  try {
    await updateUserInfo({
      nickname: editForm.nickname,
      bio: editForm.bio,
      contact: editForm.contact,
    } as any)
    showEditModal.value = false
    showMessage('保存成功')
    await loadUser()
  } catch {
    showMessage('保存失败', 'error')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadUser()
})
</script>

<template>
  <TopBar />

  <main v-if="loading" class="page">
    <p class="loading-text">加载中...</p>
  </main>

  <main v-else-if="!user" class="page">
    <p class="loading-text">无法加载用户信息，请确认已登录。</p>
  </main>

  <main v-else class="page">
    <!-- 用户头部卡片 -->
    <section class="user-hero">
      <div class="avatar">{{ (user.nickname || user.phone).charAt(0) }}</div>
      <div class="user-info">
        <p class="eyebrow">用户中心</p>
        <h1>{{ user.nickname || '未设置昵称' }}</h1>
        <div class="user-meta">
          <span>账号ID：{{ user.id }}</span>
          <span>手机号：{{ maskPhone(user.phone) }}</span>
          <span>信用等级：{{ getCreditLevel(user.creditScore) }}</span>
          <span>账户状态：{{ statusMap[user.status] || user.status }}</span>
        </div>
      </div>
      <div class="hero-actions">
        <button class="primary" type="button" @click="openEdit">编辑资料</button>
        <button class="secondary" type="button" disabled>修改密码</button>
        <button class="secondary" type="button" disabled>查看交易记录</button>
      </div>
    </section>

    <div v-if="message" class="toast" :class="{ error: messageType === 'error' }">{{ message }}</div>

    <section class="profile-layout">
      <!-- 侧边菜单 -->
      <aside class="side-menu" aria-label="用户中心菜单">
        <button
          v-for="m in menus"
          :key="m.key"
          type="button"
          :class="{ active: activeMenu === m.key }"
          @click="activeMenu = m.key"
        >
          {{ m.label }}
        </button>
      </aside>

      <!-- 主内容区 -->
      <section class="content">
        <!-- 基本信息 -->
        <section v-show="activeMenu === 'basic'" class="panel">
          <div class="section-head">
            <div><p class="eyebrow">基本信息</p><h2>账户基本信息</h2></div>
            <div class="panel-actions">
              <button class="secondary" type="button" @click="openEdit">编辑资料</button>
            </div>
          </div>
          <div class="profile-grid">
            <div><span>头像</span><strong>{{ user.avatar ? '已设置' : '未设置' }}</strong></div>
            <div><span>昵称</span><strong>{{ user.nickname || '未设置' }}</strong></div>
            <div><span>手机号</span><strong>{{ maskPhone(user.phone) }}</strong></div>
            <div><span>联系方式</span><strong>{{ user.contact || '未填写' }}</strong></div>
            <div><span>注册时间</span><strong>{{ user.createdAt ? new Date(user.createdAt).toLocaleDateString('zh-CN') : '-' }}</strong></div>
            <div><span>信用分</span><strong>{{ user.creditScore }}（{{ getCreditLevel(user.creditScore) }}）</strong></div>
          </div>
          <div v-if="user.bio" class="bio-section">
            <span>个人简介</span>
            <p>{{ user.bio }}</p>
          </div>
        </section>

        <!-- 地址管理（占位） -->
        <section v-show="activeMenu === 'address'" class="panel">
          <div class="section-head">
            <div><p class="eyebrow">地址管理</p><h2>收货地址</h2></div>
          </div>
          <div class="empty-state">
            <strong>地址管理功能开发中</strong>
            <p>后续版本将支持收货地址的增删改查。</p>
          </div>
        </section>

        <!-- 安全设置（占位） -->
        <section v-show="activeMenu === 'security'" class="panel">
          <div class="section-head"><div><p class="eyebrow">安全设置</p><h2>账户安全</h2></div></div>
          <div class="table-wrap">
            <table>
              <thead><tr><th>安全项目</th><th>当前状态</th><th>操作</th></tr></thead>
              <tbody>
                <tr><td>登录密码</td><td>已设置</td><td class="link-text">修改密码（开发中）</td></tr>
                <tr><td>手机号</td><td>已绑定</td><td class="link-text">更换手机号（开发中）</td></tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- 信用评价（占位） -->
        <section v-show="activeMenu === 'credit'" class="panel">
          <div class="section-head"><div><p class="eyebrow">信用评价</p><h2>信用状态</h2></div></div>
          <div class="credit-grid">
            <div><span>信用分</span><strong>{{ user.creditScore }}</strong></div>
            <div><span>信用等级</span><strong>{{ getCreditLevel(user.creditScore) }}</strong></div>
          </div>
          <p class="muted-text">详细评价记录功能开发中。</p>
        </section>

        <!-- 消息通知（占位） -->
        <section v-show="activeMenu === 'messages'" class="panel">
          <div class="section-head"><div><p class="eyebrow">消息通知</p><h2>消息列表</h2></div></div>
          <div class="empty-state">
            <strong>消息功能开发中</strong>
            <p>后续版本将支持系统通知和交易消息。</p>
          </div>
        </section>
      </section>

      <!-- 右侧面板 -->
      <aside class="right-panel" aria-label="信息与提醒">
        <section class="remind-card">
          <div class="section-head"><p class="eyebrow">账户信息</p><h2>当前状态</h2></div>
          <ul>
            <li>账户状态：{{ statusMap[user.status] || '正常' }}</li>
            <li>信用分：{{ user.creditScore }}</li>
            <li>角色：{{ roleMap[user.role] || user.role }}</li>
          </ul>
        </section>
      </aside>
    </section>
  </main>

  <!-- 编辑资料弹窗 -->
  <div v-if="showEditModal" class="modal-overlay" @click.self="closeEdit">
    <div class="modal">
      <div class="modal-header">
        <h2>编辑资料</h2>
        <button class="modal-close" @click="closeEdit">&times;</button>
      </div>
      <form class="modal-form" @submit.prevent="handleSave">
        <label>
          <span>昵称</span>
          <input v-model="editForm.nickname" type="text" maxlength="50" placeholder="输入昵称">
        </label>
        <label>
          <span>联系方式</span>
          <input v-model="editForm.contact" type="text" maxlength="100" placeholder="微信/QQ等">
        </label>
        <label>
          <span>个人简介</span>
          <textarea v-model="editForm.bio" rows="3" maxlength="200" placeholder="简单介绍一下自己"></textarea>
        </label>
        <div class="modal-actions">
          <button type="button" class="secondary" @click="closeEdit">取消</button>
          <button type="submit" class="primary" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.page { width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.loading-text { text-align: center; color: var(--muted); padding: 60px 0; font-size: 18px; }
.toast {
  margin-top: 16px; padding: 12px 18px; border-radius: 8px; color: #1f6b45; background: #e8f7ef;
  border: 1px solid #bce5ce; font-weight: 600;
}
.toast.error { color: #b9352b; background: #fdecea; border-color: #f0b8b3; }
.user-hero {
  display: grid; grid-template-columns: 86px minmax(0, 1fr) 360px;
  gap: 20px; align-items: center; padding: 30px; border-radius: 10px; color: #fff;
  background: linear-gradient(rgba(10,74,90,0.88), rgba(10,74,90,0.92)),
    url("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=80") center/cover;
  box-shadow: var(--shadow);
}
.avatar { width: 86px; height: 86px; display: grid; place-items: center; border-radius: 10px; color: #172126; background: var(--gold); font-size: 34px; font-weight: 900; text-transform: uppercase; }
.eyebrow { margin: 0 0 8px; color: var(--gold); font-size: 13px; font-weight: 800; }
h1, h2, p { margin: 0; }
h1 { font-size: 34px; }
.user-meta { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 12px; }
.user-meta span { padding: 7px 10px; border-radius: 7px; background: rgba(255,255,255,0.13); color: rgba(255,255,255,0.86); font-size: 13px; }
.hero-actions, .panel-actions { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
.primary, .secondary { min-height: 42px; border-radius: 8px; padding: 0 14px; font-weight: 800; cursor: pointer; font: inherit; }
.primary { border: 0; color: #fff; background: var(--accent); }
.primary:hover { background: var(--accent-dark); }
.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
.secondary:disabled { opacity: 0.5; cursor: not-allowed; }
.profile-layout { display: grid; grid-template-columns: 190px minmax(0, 1fr) 260px; gap: 20px; margin-top: 20px; }
.side-menu, .panel, .remind-card { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); box-shadow: var(--shadow); }
.side-menu { align-self: start; display: grid; gap: 8px; padding: 14px; }
.side-menu button { min-height: 42px; border: 0; border-radius: 8px; padding: 0 12px; color: var(--muted); background: transparent; text-align: left; font-weight: 800; cursor: pointer; font: inherit; }
.side-menu button.active, .side-menu button:hover { color: #fff; background: var(--accent); }
.content, .right-panel { display: grid; gap: 20px; }
.right-panel { align-self: start; }
.panel, .remind-card { padding: 22px; }
.section-head { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 16px; }
.section-head .eyebrow { color: var(--accent); }
h2 { font-size: 23px; }
.profile-grid, .credit-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.profile-grid div, .credit-grid div { padding: 14px; border-radius: 8px; background: var(--soft); }
.profile-grid span, .credit-grid span { display: block; color: var(--muted); font-size: 13px; }
.profile-grid strong, .credit-grid strong { display: block; margin-top: 8px; }
.credit-grid { margin-bottom: 16px; }
.credit-grid strong { font-size: 22px; }
.bio-section { margin-top: 16px; padding: 14px; border-radius: 8px; background: var(--soft); }
.bio-section span { display: block; color: var(--muted); font-size: 13px; margin-bottom: 8px; }
.bio-section p { color: var(--ink); line-height: 1.6; }
.muted-text { color: var(--muted); font-size: 14px; margin-top: 12px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; min-width: 500px; border-collapse: collapse; font-size: 14px; }
th, td { padding: 13px 12px; border-bottom: 1px solid var(--line); text-align: left; }
th { color: var(--muted); background: var(--soft); }
.link-text { color: var(--accent); font-weight: 800; }
.tag { display: inline-flex; min-height: 26px; align-items: center; border-radius: 999px; padding: 0 10px; color: var(--muted); background: #edf1f3; font-size: 13px; font-weight: 800; }
.tag.ok { color: #1f7a4d; background: #e8f7ef; }
.tag.warn { color: #b86b00; background: #fff3d7; }
.empty-state { min-height: 120px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); }
.empty-state strong { display: block; margin-bottom: 8px; color: var(--ink); font-size: 18px; }
.empty-state p { font-size: 14px; }
.remind-card ul { margin: 0; padding-left: 20px; color: var(--muted); line-height: 2; }

/* 弹窗 */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: grid; place-items: center; z-index: 1000; padding: 20px; }
.modal { background: var(--panel); border-radius: 16px; width: min(520px, 100%); max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 24px 28px; border-bottom: 1px solid var(--line); }
.modal-header h2 { font-size: 24px; }
.modal-close { width: 40px; height: 40px; border: 0; border-radius: 10px; background: var(--soft); color: var(--muted); font-size: 24px; cursor: pointer; display: grid; place-items: center; }
.modal-close:hover { background: #fee2e2; color: #be123c; }
.modal-form { padding: 28px; display: grid; gap: 18px; }
.modal-form label { display: grid; gap: 8px; }
.modal-form label span { color: var(--muted); font-size: 14px; font-weight: 600; }
.modal-form input, .modal-form textarea { width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 12px 14px; font: inherit; font-size: 14px; background: #fff; box-sizing: border-box; }
.modal-form textarea { resize: vertical; min-height: 70px; }
.modal-form input:focus, .modal-form textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(15,100,120,0.1); outline: none; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; padding: 18px 28px; border-top: 1px solid var(--line); }

@media (max-width: 1120px) {
  .user-hero, .profile-layout { grid-template-columns: 1fr; }
  .side-menu { grid-template-columns: repeat(5, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
  .section-head { align-items: flex-start; flex-direction: column; }
  .hero-actions, .panel-actions, .side-menu, .profile-grid, .credit-grid { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .page { width: min(100% - 20px, 1240px); }
  .user-hero, .panel, .remind-card { padding: 20px; }
  h1 { font-size: 28px; }
}
</style>
