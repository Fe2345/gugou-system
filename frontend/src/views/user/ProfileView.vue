<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import TopBar from '@/layouts/TopBar.vue'
import { useUserStore } from '@/stores/user'
import { getUserInfo, updateUserInfo, changePassword, changePhone, getLoginRecords } from '@/api/user'
import { getAddresses, addAddress, updateAddress, deleteAddress, getDivisions } from '@/api/address'
import type { AddressItem, AddressForm, DivisionItem } from '@/api/address'
import type { UserInfo } from '@/types/user'
import type { LoginRecordItem } from '@/api/user'

defineOptions({ name: 'ProfileView' })

const router = useRouter()
const userStore = useUserStore()
const user = ref<UserInfo | null>(null)
const loading = ref(false)
const saving = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')

// 侧边菜单
const activeMenu = ref('basic')
const menus = [
  { key: 'basic', label: '基本信息' },
  { key: 'address', label: '地址管理' },
  { key: 'security', label: '安全设置' },
  { key: 'credit', label: '信用评价' },
  { key: 'messages', label: '消息通知' },
]

// 编辑资料弹窗
const showEditModal = ref(false)
const editForm = reactive({ nickname: '', bio: '', contact: '' })

// 修改密码弹窗
const showPasswordModal = ref(false)
const passwordForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })

// 更换手机号弹窗
const showPhoneModal = ref(false)
const phoneForm = reactive({ phone: '' })

// 登录记录
const loginRecords = ref<LoginRecordItem[]>([])
const loadingRecords = ref(false)

// --- 地址管理 ---
const addresses = ref<AddressItem[]>([])
const loadingAddresses = ref(false)
const showAddrModal = ref(false)
const editingAddrId = ref<number | null>(null)
const addrForm = reactive<AddressForm>({
  receiver_name: '', receiver_phone: '',
  province_code: '', city_code: '', district_code: '',
  street: '', detail: '', is_default: false,
})
// 区划数据
const provinces = ref<DivisionItem[]>([])
const cities = ref<DivisionItem[]>([])
const districts = ref<DivisionItem[]>([])
const addrProvName = ref('')
const addrCityName = ref('')
const addrDistName = ref('')

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

function getCreditLevel(score: number) {
  if (score >= 90) return '优秀用户'
  if (score >= 70) return '良好用户'
  if (score >= 50) return '一般用户'
  return '需改善'
}

async function loadUser() {
  if (!userStore.isLoggedIn) {
    router.replace('/login')
    return
  }
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

function loadRecords() {
  loadingRecords.value = true
  getLoginRecords()
    .then(res => { loginRecords.value = res.data })
    .catch(() => {})
    .finally(() => { loadingRecords.value = false })
}

// --- 编辑资料 ---
function openEdit() {
  if (!user.value) return
  editForm.nickname = user.value.nickname
  editForm.bio = user.value.bio || ''
  editForm.contact = user.value.contact || ''
  showEditModal.value = true
}

function closeEdit() { showEditModal.value = false }

async function handleSave() {
  if (!user.value) return
  saving.value = true
  try {
    await updateUserInfo({ nickname: editForm.nickname, bio: editForm.bio, contact: editForm.contact } as any)
    showEditModal.value = false
    showMessage('保存成功')
    await loadUser()
  } catch {
    showMessage('保存失败', 'error')
  } finally { saving.value = false }
}

// --- 修改密码 ---
function openPasswordModal() {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  showPasswordModal.value = true
}

function closePasswordModal() { showPasswordModal.value = false }

async function handleChangePassword() {
  if (passwordForm.newPassword.length < 6) { showMessage('新密码至少 6 位', 'error'); return }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) { showMessage('两次输入不一致', 'error'); return }
  saving.value = true
  try {
    await changePassword(passwordForm.oldPassword, passwordForm.newPassword)
    showPasswordModal.value = false
    showMessage('密码修改成功，请使用新密码重新登录')
    setTimeout(() => {
      userStore.logout()
      router.push('/login')
    }, 1500)
  } catch (e: any) {
    showMessage(e?.response?.data?.message || '修改失败', 'error')
  } finally { saving.value = false }
}

// --- 更换手机号 ---
function openPhoneModal() {
  phoneForm.phone = ''
  showPhoneModal.value = true
}

function closePhoneModal() { showPhoneModal.value = false }

async function handleChangePhone() {
  if (!/^1[3-9]\d{9}$/.test(phoneForm.phone)) { showMessage('请输入有效的 11 位手机号', 'error'); return }
  saving.value = true
  try {
    const res = await changePhone(phoneForm.phone)
    if (user.value) user.value.phone = res.data.phone
    showPhoneModal.value = false
    showMessage('手机号修改成功')
  } catch (e: any) {
    showMessage(e?.response?.data?.message || '修改失败', 'error')
  } finally { saving.value = false }
}

// --- 地址管理函数 ---
async function loadAddresses() {
  loadingAddresses.value = true
  try { addresses.value = (await getAddresses()).data }
  catch { /* ignore */ }
  finally { loadingAddresses.value = false }
}

async function openAddrModal(addr?: AddressItem) {
  await loadProvinceList()
  if (addr) {
    editingAddrId.value = addr.id
    addrForm.receiver_name = addr.receiver_name
    addrForm.receiver_phone = addr.receiver_phone
    addrForm.province_code = addr.province.code
    addrForm.city_code = addr.city.code
    addrForm.district_code = addr.district.code
    addrForm.street = addr.street
    addrForm.detail = addr.detail
    addrForm.is_default = addr.is_default
    addrProvName.value = addr.province.name
    addrCityName.value = addr.city.name
    addrDistName.value = addr.district.name
    await loadCities(addr.province.code)
    await loadDistricts(addr.city.code)
  } else {
    editingAddrId.value = null
    resetAddrForm()
  }
  showAddrModal.value = true
}

function closeAddrModal() { showAddrModal.value = false }

function resetAddrForm() {
  addrForm.receiver_name = ''
  addrForm.receiver_phone = ''
  addrForm.province_code = ''
  addrForm.city_code = ''
  addrForm.district_code = ''
  addrForm.street = ''
  addrForm.detail = ''
  addrForm.is_default = false
  addrProvName.value = ''
  addrCityName.value = ''
  addrDistName.value = ''
  cities.value = []
  districts.value = []
}

async function loadProvinceList() {
  if (provinces.value.length) return
  try { provinces.value = (await getDivisions()).data }
  catch { /* ignore */ }
}

async function loadCities(parentCode: string) {
  cities.value = []
  districts.value = []
  addrForm.city_code = ''
  addrForm.district_code = ''
  addrCityName.value = ''
  addrDistName.value = ''
  const p = provinces.value.find(p => p.code === parentCode)
  addrProvName.value = p?.name || ''
  try { cities.value = (await getDivisions(parentCode)).data }
  catch { /* ignore */ }
}

async function loadDistricts(parentCode: string) {
  districts.value = []
  addrForm.district_code = ''
  addrDistName.value = ''
  const c = cities.value.find(c => c.code === parentCode)
  addrCityName.value = c?.name || ''
  try { districts.value = (await getDivisions(parentCode)).data }
  catch { /* ignore */ }
}

function onDistrictSelect(code: string) {
  const d = districts.value.find(d => d.code === code)
  addrDistName.value = d?.name || ''
}

async function handleSaveAddress() {
  if (!addrForm.receiver_name || !addrForm.receiver_phone || !addrForm.province_code || !addrForm.city_code || !addrForm.district_code || !addrForm.detail) {
    showMessage('请填写完整的地址信息', 'error'); return
  }
  saving.value = true
  try {
    if (editingAddrId.value) {
      await updateAddress(editingAddrId.value, { ...addrForm })
    } else {
      await addAddress({ ...addrForm })
    }
    showAddrModal.value = false
    showMessage(editingAddrId.value ? '地址已更新' : '地址已添加')
    await loadAddresses()
  } catch (e: any) {
    showMessage(e?.response?.data?.message || '保存失败', 'error')
  } finally { saving.value = false }
}

async function handleDeleteAddress(id: number) {
  if (!confirm('确定要删除该地址吗？')) return
  saving.value = true
  try {
    await deleteAddress(id)
    showMessage('地址已删除')
    await loadAddresses()
  } catch { showMessage('删除失败', 'error') }
  finally { saving.value = false }
}

onMounted(() => {
  loadUser()
  loadRecords()
  loadAddresses()
})
</script>

<template>
  <TopBar />

  <main v-if="loading" class="page">
    <p class="loading-text">加载中...</p>
  </main>

  <main v-else-if="!user" class="page">
    <p class="loading-text">请先登录后查看用户中心。</p>
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
        <button class="secondary" type="button" @click="openPasswordModal">修改密码</button>
      </div>
    </section>

    <div v-if="message" class="toast" :class="{ error: messageType === 'error' }">{{ message }}</div>

    <section class="profile-layout">
      <aside class="side-menu" aria-label="用户中心菜单">
        <button v-for="m in menus" :key="m.key" type="button" :class="{ active: activeMenu === m.key }" @click="activeMenu = m.key">
          {{ m.label }}
        </button>
      </aside>

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
            <span>个人简介</span><p>{{ user.bio }}</p>
          </div>
        </section>

        <!-- 地址管理 -->
        <section v-show="activeMenu === 'address'" class="panel">
          <div class="section-head">
            <div><p class="eyebrow">地址管理</p><h2>收货地址</h2></div>
            <button class="primary small" type="button" @click="openAddrModal()">添加新地址</button>
          </div>
          <div v-if="!addresses.length" class="empty-state"><strong>暂无收货地址</strong><p>点击"添加新地址"录入收货信息。</p></div>
          <div v-else class="addr-list">
            <div v-for="a in addresses" :key="a.id" class="addr-card" :class="{ default: a.is_default }">
              <div class="addr-body">
                <div class="addr-line">
                  <strong>{{ a.receiver_name }}</strong>
                  <span>{{ a.receiver_phone }}</span>
                  <span v-if="a.is_default" class="tag ok">默认</span>
                </div>
                <p class="addr-full">
                  {{ a.province.name }} {{ a.city.name }} {{ a.district.name }} {{ a.street }} {{ a.detail }}
                </p>
              </div>
              <div class="addr-actions">
                <button class="link-btn" type="button" @click="openAddrModal(a)">编辑</button>
                <button class="link-btn danger" type="button" @click="handleDeleteAddress(a.id)">删除</button>
              </div>
            </div>
          </div>
        </section>

        <!-- 安全设置 -->
        <section v-show="activeMenu === 'security'" class="panel">
          <div class="section-head"><div><p class="eyebrow">安全设置</p><h2>账户安全</h2></div></div>
          <div class="table-wrap">
            <table>
              <thead><tr><th>安全项目</th><th>操作</th></tr></thead>
              <tbody>
                <tr><td>登录密码</td><td class="link-text"><button type="button" class="link-btn" @click="openPasswordModal">修改密码</button></td></tr>
                <tr><td>手机号</td><td class="link-text"><button type="button" class="link-btn" @click="openPhoneModal">更换手机号</button></td></tr>
              </tbody>
            </table>
          </div>
          <div class="section-head" style="margin-top: 24px;"><div><p class="eyebrow">登录记录</p><h2>最近登录</h2></div></div>
          <div v-if="loginRecords.length === 0" style="color: var(--muted); font-size: 14px;">暂无记录</div>
          <div v-else class="table-wrap">
            <table>
              <thead><tr><th>登录时间</th><th>IP 地址</th></tr></thead>
              <tbody>
                <tr v-for="(r, i) in loginRecords" :key="i">
                  <td>{{ new Date(r.time).toLocaleString('zh-CN') }}</td>
                  <td>{{ r.ip }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- 信用评价 -->
        <section v-show="activeMenu === 'credit'" class="panel">
          <div class="section-head"><div><p class="eyebrow">信用评价</p><h2>信用状态</h2></div></div>
          <div class="credit-grid">
            <div><span>信用分</span><strong>{{ user.creditScore }}</strong></div>
            <div><span>信用等级</span><strong>{{ getCreditLevel(user.creditScore) }}</strong></div>
          </div>
          <p class="muted-text">详细评价记录功能开发中。</p>
        </section>

        <!-- 消息通知 -->
        <section v-show="activeMenu === 'messages'" class="panel">
          <div class="section-head"><div><p class="eyebrow">消息通知</p><h2>消息列表</h2></div></div>
          <div class="empty-state"><strong>功能开发中</strong><p>后续版本将支持消息通知。</p></div>
        </section>
      </section>

      <aside class="right-panel">
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
      <div class="modal-header"><h2>编辑资料</h2><button class="modal-close" @click="closeEdit">&times;</button></div>
      <form class="modal-form" @submit.prevent="handleSave">
        <label><span>昵称</span><input v-model="editForm.nickname" type="text" maxlength="50" placeholder="输入昵称"></label>
        <label><span>联系方式</span><input v-model="editForm.contact" type="text" maxlength="100" placeholder="微信/QQ等"></label>
        <label><span>个人简介</span><textarea v-model="editForm.bio" rows="3" maxlength="200" placeholder="简单介绍一下自己"></textarea></label>
        <div class="modal-actions">
          <button type="button" class="secondary" @click="closeEdit">取消</button>
          <button type="submit" class="primary" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
        </div>
      </form>
    </div>
  </div>

  <!-- 修改密码弹窗 -->
  <div v-if="showPasswordModal" class="modal-overlay" @click.self="closePasswordModal">
    <div class="modal">
      <div class="modal-header"><h2>修改密码</h2><button class="modal-close" @click="closePasswordModal">&times;</button></div>
      <form class="modal-form" @submit.prevent="handleChangePassword">
        <label><span>当前密码</span><input v-model="passwordForm.oldPassword" type="password" required placeholder="请输入当前密码"></label>
        <label><span>新密码</span><input v-model="passwordForm.newPassword" type="password" required minlength="6" placeholder="至少 6 位"></label>
        <label><span>确认密码</span><input v-model="passwordForm.confirmPassword" type="password" required placeholder="再次输入新密码"></label>
        <div class="modal-actions">
          <button type="button" class="secondary" @click="closePasswordModal">取消</button>
          <button type="submit" class="primary" :disabled="saving">{{ saving ? '提交中...' : '确认修改' }}</button>
        </div>
      </form>
    </div>
  </div>

  <!-- 更换手机号弹窗 -->
  <div v-if="showPhoneModal" class="modal-overlay" @click.self="closePhoneModal">
    <div class="modal">
      <div class="modal-header"><h2>更换手机号</h2><button class="modal-close" @click="closePhoneModal">&times;</button></div>
      <form class="modal-form" @submit.prevent="handleChangePhone">
        <label>
          <span>当前手机号</span>
          <input :value="maskPhone(user!.phone)" disabled style="color: var(--muted); background: var(--soft);">
        </label>
        <label>
          <span>新手机号</span>
          <input v-model="phoneForm.phone" type="tel" maxlength="11" required placeholder="请输入新手机号">
        </label>
        <div class="modal-actions">
          <button type="button" class="secondary" @click="closePhoneModal">取消</button>
          <button type="submit" class="primary" :disabled="saving">{{ saving ? '提交中...' : '确认更换' }}</button>
        </div>
      </form>
    </div>
  </div>

  <!-- 地址编辑弹窗 -->
  <div v-if="showAddrModal" class="modal-overlay" @click.self="closeAddrModal">
    <div class="modal modal-addr">
      <div class="modal-header"><h2>{{ editingAddrId ? '编辑地址' : '添加地址' }}</h2><button class="modal-close" @click="closeAddrModal">&times;</button></div>
      <form class="modal-form" @submit.prevent="handleSaveAddress">
        <div class="form-row">
          <label><span>收货人</span><input v-model="addrForm.receiver_name" required maxlength="30" placeholder="姓名"></label>
          <label><span>手机号</span><input v-model="addrForm.receiver_phone" type="tel" required maxlength="11" placeholder="11 位手机号"></label>
        </div>
        <div class="form-row three">
          <label>
            <span>省</span>
            <select v-model="addrForm.province_code" @change="loadCities(addrForm.province_code)">
              <option value="">请选择</option>
              <option v-for="p in provinces" :key="p.code" :value="p.code">{{ p.name }}</option>
            </select>
          </label>
          <label>
            <span>市</span>
            <select v-model="addrForm.city_code" @change="loadDistricts(addrForm.city_code)" :disabled="!cities.length">
              <option value="">请选择</option>
              <option v-for="c in cities" :key="c.code" :value="c.code">{{ c.name }}</option>
            </select>
          </label>
          <label>
            <span>区</span>
            <select v-model="addrForm.district_code" @change="onDistrictSelect(addrForm.district_code)" :disabled="!districts.length">
              <option value="">请选择</option>
              <option v-for="d in districts" :key="d.code" :value="d.code">{{ d.name }}</option>
            </select>
          </label>
        </div>
        <label><span>街道/镇</span><input v-model="addrForm.street" maxlength="100" placeholder="如：粤海街道"></label>
        <label><span>详细地址</span><input v-model="addrForm.detail" required maxlength="200" placeholder="楼栋、门牌号等"></label>
        <label class="check-line">
          <input v-model="addrForm.is_default" type="checkbox">
          <span>设为默认地址</span>
        </label>
        <div class="modal-actions">
          <button type="button" class="secondary" @click="closeAddrModal">取消</button>
          <button type="submit" class="primary" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.page { width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 44px; }
.loading-text { text-align: center; color: var(--muted); padding: 60px 0; font-size: 18px; }
.toast { margin-top: 16px; padding: 12px 18px; border-radius: 8px; color: #1f6b45; background: #e8f7ef; border: 1px solid #bce5ce; font-weight: 600; }
.toast.error { color: #b9352b; background: #fdecea; border-color: #f0b8b3; }
.user-hero {
  display: grid; grid-template-columns: 86px minmax(0, 1fr) 240px; gap: 20px; align-items: center;
  padding: 30px; border-radius: 10px; color: #fff;
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
.hero-actions, .panel-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.primary, .secondary { min-height: 42px; border-radius: 8px; padding: 0 14px; font-weight: 800; cursor: pointer; font: inherit; }
.primary { border: 0; color: #fff; background: var(--accent); }
.primary:hover { background: var(--accent-dark); }
.primary:disabled { opacity: 0.6; cursor: not-allowed; }
.secondary { border: 1px solid var(--line); color: var(--accent); background: #fff; }
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
table { width: 100%; min-width: 400px; border-collapse: collapse; font-size: 14px; }
th, td { padding: 13px 12px; border-bottom: 1px solid var(--line); text-align: left; }
th { color: var(--muted); background: var(--soft); }
.link-text { color: var(--accent); font-weight: 800; }
.link-btn { border: 0; background: transparent; color: var(--accent); font-weight: 800; cursor: pointer; font: inherit; padding: 0; }
.link-btn:hover { text-decoration: underline; }
.empty-state { min-height: 100px; display: grid; place-items: center; text-align: center; border: 1px dashed #bfd0d5; border-radius: 10px; color: var(--muted); background: var(--soft); padding: 20px; }
.empty-state strong { display: block; margin-bottom: 8px; color: var(--ink); font-size: 18px; }
.empty-state p { font-size: 14px; }
.remind-card ul { margin: 0; padding-left: 20px; color: var(--muted); line-height: 2; }

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
.modal-form input:focus, .modal-form textarea:focus, .modal-form select:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(15,100,120,0.1); outline: none; }
.modal-form select { width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 12px 14px; font: inherit; font-size: 14px; background: #fff; box-sizing: border-box; }
.modal-form select:disabled { background: var(--soft); color: var(--muted); }
.modal-addr { width: min(640px, 100%); }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; padding: 18px 28px; border-top: 1px solid var(--line); }
.check-line { display: flex !important; flex-direction: row !important; align-items: center; gap: 10px; }
.check-line input { width: 18px !important; height: 18px; }
.form-row { display: grid; gap: 14px; }
.form-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.form-row.three { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.primary.small { min-height: 36px; padding: 0 14px; font-size: 14px; }

/* 地址列表 */
.addr-list { display: grid; gap: 12px; }
.addr-card { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 12px; padding: 16px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel); }
.addr-card.default { border-color: var(--accent); background: #f6fbfc; }
.addr-line { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }
.addr-line strong { font-size: 16px; }
.addr-line .tag { display: inline-flex; min-height: 24px; align-items: center; border-radius: 999px; padding: 0 10px; font-size: 12px; font-weight: 800; }
.addr-line .tag.ok { color: #1f7a4d; background: #e8f7ef; }
.addr-full { margin: 0; color: var(--muted); font-size: 14px; line-height: 1.5; }
.addr-actions { display: flex; align-items: flex-start; gap: 12px; }
.link-btn { border: 0; background: transparent; color: var(--accent); font-weight: 800; cursor: pointer; font: inherit; font-size: 14px; }
.link-btn:hover { text-decoration: underline; }
.link-btn.danger { color: #be123c; }

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
