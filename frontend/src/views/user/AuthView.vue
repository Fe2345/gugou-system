<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { login as loginApi, register as registerApi, resetPassword } from '@/api/user'
import { useUserStore } from '@/stores/user'

defineOptions({ name: 'AuthView' })

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')
const loginForm = reactive({ account: '', password: '' })
const registerForm = reactive({ phone: '', password: '', confirmPassword: '', agreement: false })
const forgotForm = reactive({ phone: '', password: '' })

function showMessage(msg: string, type: 'success' | 'error' = 'success') {
  message.value = msg
  messageType.value = type
}

function clearMessage() {
  message.value = ''
}

function isPhone(value: string) {
  return /^1[3-9]\d{9}$/.test(value)
}

function handleTab(tab: string) {
  activeTab.value = tab
  clearMessage()
}

async function handleLogin() {
  clearMessage()
  const account = loginForm.account.trim()
  if (!account) { showMessage('请填写手机号或账号', 'error'); return }
  if (!loginForm.password) { showMessage('请填写密码', 'error'); return }

  loading.value = true
  try {
    const res = await loginApi({ account, password: loginForm.password })
    userStore.setTokens(res.data.access, res.data.refresh)
    userStore.setUserInfo(res.data.user)
    loginForm.account = ''
    loginForm.password = ''
    showMessage('登录成功')
    setTimeout(() => router.push('/'), 1000)
  } catch (e: any) {
    showMessage(e?.response?.data?.message || '登录失败，请检查账号密码', 'error')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  clearMessage()
  const phone = registerForm.phone.trim()
  if (!isPhone(phone)) { showMessage('请输入有效的 11 位手机号', 'error'); return }
  if (registerForm.password.length < 6) { showMessage('密码至少需要 6 位', 'error'); return }
  if (registerForm.password !== registerForm.confirmPassword) { showMessage('两次输入的密码不一致', 'error'); return }
  if (!registerForm.agreement) { showMessage('请先同意用户协议', 'error'); return }

  loading.value = true
  try {
    await registerApi({ phone, password: registerForm.password, confirmPassword: registerForm.confirmPassword })
    registerForm.phone = ''
    registerForm.password = ''
    registerForm.confirmPassword = ''
    registerForm.agreement = false
    activeTab.value = 'login'
    showMessage('注册成功，请登录')
  } catch (e: any) {
    showMessage(e?.response?.data?.message || '注册失败，请稍后重试', 'error')
  } finally {
    loading.value = false
  }
}

async function handleForgot() {
  clearMessage()
  const phone = forgotForm.phone.trim()
  if (!isPhone(phone)) { showMessage('请输入有效的 11 位手机号', 'error'); return }
  if (forgotForm.password.length < 6) { showMessage('密码至少需要 6 位', 'error'); return }

  loading.value = true
  try {
    await resetPassword({ phone, password: forgotForm.password })
    forgotForm.phone = ''
    forgotForm.password = ''
    activeTab.value = 'login'
    showMessage('密码修改成功，请使用新密码登录')
  } catch (e: any) {
    showMessage(e?.response?.data?.message || '密码重置失败，请稍后重试', 'error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-card" aria-label="用户账户管理">
      <div class="brand">
        <div class="brand-mark">G</div>
        <div>
          <h1>用户账户管理</h1>
          <p>安全便捷地完成账号访问与密码恢复</p>
        </div>
      </div>

      <nav class="tabs" aria-label="账户入口">
        <button class="tab" :class="{ active: activeTab === 'login' }" type="button" @click="handleTab('login')">登录</button>
        <button class="tab" :class="{ active: activeTab === 'register' }" type="button" @click="handleTab('register')">注册</button>
        <button class="tab" :class="{ active: activeTab === 'forgot' }" type="button" @click="handleTab('forgot')">找回密码</button>
      </nav>

      <div v-if="message" class="message" :class="{ error: messageType === 'error' }">{{ message }}</div>

      <section v-show="activeTab === 'login'" class="view">
        <div class="view-head">
          <p class="eyebrow">统一入口</p>
          <h2>欢迎登录</h2>
        </div>
        <form class="form" @submit.prevent="handleLogin">
          <label>
            <span>手机号或账号</span>
            <input v-model="loginForm.account" autocomplete="username" placeholder="请输入手机号或账号">
          </label>
          <label>
            <span>密码</span>
            <input v-model="loginForm.password" type="password" autocomplete="current-password" placeholder="请输入密码">
          </label>
          <button class="primary" type="submit" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
          <div class="form-links">
            <button type="button" @click="handleTab('register')">立即注册</button>
            <button type="button" @click="handleTab('forgot')">忘记密码</button>
          </div>
        </form>
      </section>

      <section v-show="activeTab === 'register'" class="view">
        <div class="view-head">
          <p class="eyebrow">新用户建档</p>
          <h2>创建账号</h2>
        </div>
        <form class="form" @submit.prevent="handleRegister">
          <label>
            <span>手机号</span>
            <input v-model="registerForm.phone" autocomplete="tel" placeholder="请输入 11 位手机号">
          </label>
          <label>
            <span>密码</span>
            <input v-model="registerForm.password" type="password" autocomplete="new-password" placeholder="至少 6 位">
          </label>
          <label>
            <span>确认密码</span>
            <input v-model="registerForm.confirmPassword" type="password" autocomplete="new-password" placeholder="再次输入密码">
          </label>
          <label class="check-line">
            <input v-model="registerForm.agreement" type="checkbox">
            <span>我已阅读并同意《用户协议》</span>
          </label>
          <button class="primary" type="submit" :disabled="loading">{{ loading ? '注册中...' : '注册' }}</button>
          <div class="form-links single">
            <button type="button" @click="handleTab('login')">已有账号，去登录</button>
          </div>
        </form>
      </section>

      <section v-show="activeTab === 'forgot'" class="view">
        <div class="view-head">
          <p class="eyebrow">账户恢复</p>
          <h2>找回密码</h2>
        </div>
        <form class="form" @submit.prevent="handleForgot">
          <label>
            <span>手机号</span>
            <input v-model="forgotForm.phone" autocomplete="tel" placeholder="请输入注册手机号">
          </label>
          <label>
            <span>新密码</span>
            <input v-model="forgotForm.password" type="password" autocomplete="new-password" placeholder="设置新密码">
          </label>
          <button class="primary" type="submit" :disabled="loading">{{ loading ? '提交中...' : '确认修改' }}</button>
          <div class="form-links single">
            <button type="button" @click="handleTab('login')">返回登录</button>
          </div>
        </form>
      </section>
    </section>
  </main>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 30px 16px;
  background:
    linear-gradient(rgba(10, 70, 87, 0.86), rgba(10, 70, 87, 0.9)),
    url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1600&q=80") center/cover fixed;
}

.auth-card {
  width: min(520px, 100%);
  padding: 34px;
  border: 1px solid rgba(255, 255, 255, 0.52);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 28px 80px rgba(13, 54, 66, 0.18);
  backdrop-filter: blur(18px);
}

.brand {
  display: flex;
  gap: 18px;
  align-items: center;
  margin-bottom: 28px;
}

.brand-mark {
  flex: 0 0 auto;
  width: 58px;
  height: 58px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: var(--gold);
  color: #172126;
  font-size: 30px;
  font-weight: 800;
}

h1, h2, p { margin: 0; }
h1 { font-size: 30px; line-height: 1.25; }
.brand p { margin-top: 8px; color: var(--muted); line-height: 1.6; }

.tabs {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  padding: 6px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #f4f8fa;
}

.tab {
  min-height: 42px;
  border: 0;
  border-radius: 6px;
  color: var(--muted);
  background: transparent;
  font-weight: 700;
  cursor: pointer;
  font: inherit;
}

.tab.active {
  color: #fff;
  background: var(--accent);
  box-shadow: 0 10px 24px rgba(15, 93, 114, 0.2);
}

.view { padding-top: 28px; }
.view-head { margin-bottom: 22px; }
.eyebrow { margin-bottom: 6px; color: var(--accent); font-size: 13px; font-weight: 800; }
h2 { font-size: 28px; }

.form { display: grid; gap: 16px; }
label { display: grid; gap: 8px; color: var(--muted); font-size: 14px; }

input {
  width: 100%;
  height: 50px;
  padding: 0 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  color: var(--ink);
  background: #fff;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font: inherit;
}

input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 4px rgba(15, 93, 114, 0.12);
}

.check-line { display: flex; align-items: center; gap: 10px; }
.check-line input { width: 18px; height: 18px; }

.primary {
  min-height: 50px;
  border: 0;
  border-radius: 8px;
  color: #fff;
  background: var(--accent);
  font-weight: 800;
  cursor: pointer;
  font: inherit;
  box-shadow: 0 12px 28px rgba(15, 93, 114, 0.22);
}
.primary:hover { background: var(--accent-dark); }
.primary:disabled { opacity: 0.7; cursor: not-allowed; }

.form-links { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.form-links.single { grid-template-columns: 1fr; }
.form-links button {
  border: 0;
  background: transparent;
  color: var(--accent);
  text-align: left;
  padding: 2px 0;
  cursor: pointer;
  font: inherit;
}
.form-links button:last-child { text-align: right; }
.form-links.single button { text-align: center; }

.message {
  margin-top: 18px;
  padding: 12px 14px;
  border: 1px solid #bce5ce;
  border-radius: 8px;
  color: #1f6b45;
  background: #e8f7ef;
}
.message.error { color: #b9352b; border-color: #f0b8b3; background: #fdecea; }

@media (max-width: 560px) {
  .auth-page { align-items: start; padding-top: 22px; }
  .auth-card { padding: 24px; }
  .brand { align-items: flex-start; }
  h1 { font-size: 25px; }
  h2 { font-size: 24px; }
  .tabs, .form-links { grid-template-columns: 1fr; }
  .form-links button, .form-links button:last-child { text-align: center; }
}
</style>
