<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const navItems = [
  { label: '后台首页', to: '/admin' },
  { label: '用户管理', to: '/admin/users' },
  { label: '商品审核', to: '/admin/goods' },
  { label: '订单处理', to: '/admin/orders' },
  { label: '换物管理', to: '/admin/exchange' },
  { label: '拼团管理', to: '/admin/team' },
  { label: '价格记录', to: '/admin/price' },
]

function isActive(path: string) {
  if (path === '/admin') return route.path === '/admin'
  return route.path.startsWith(path)
}
</script>

<template>
  <header class="admin-topbar">
    <div class="topbar-inner">
      <div class="logo" @click="router.push('/admin')">
        <span>A</span>
        <strong>谷购管理后台</strong>
      </div>
      <nav class="nav" aria-label="管理员导航">
        <button
          v-for="item in navItems"
          :key="item.to"
          type="button"
          :class="{ active: isActive(item.to) }"
          @click="router.push(item.to)"
        >
          {{ item.label }}
        </button>
      </nav>
      <button class="back-btn" type="button" @click="router.push('/')">返回前台</button>
    </div>
  </header>
  <main class="admin-page">
    <RouterView />
  </main>
</template>

<style scoped>
.admin-topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  border-bottom: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(16px);
}

.topbar-inner {
  width: min(1240px, calc(100% - 32px));
  min-height: 72px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  cursor: pointer;
}

.logo span {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  color: #fff;
  background: var(--accent);
  font-weight: 900;
}

.nav {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  overflow-x: auto;
  padding: 8px 0;
}

.nav button {
  min-width: max-content;
  min-height: 36px;
  border: 0;
  border-radius: 7px;
  padding: 0 12px;
  color: var(--muted);
  background: transparent;
  cursor: pointer;
  font: inherit;
}

.nav button:hover,
.nav button.active {
  color: var(--accent);
  background: #edf6f8;
}

.back-btn {
  flex: 0 0 auto;
  min-height: 34px;
  border: 1px solid var(--line);
  border-radius: 7px;
  padding: 0 14px;
  color: var(--muted);
  background: transparent;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font: inherit;
}

.back-btn:hover {
  color: var(--accent);
  border-color: var(--accent);
}

.admin-page {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 28px 0 44px;
}

@media (max-width: 980px) {
  .topbar-inner {
    align-items: flex-start;
    flex-direction: column;
    padding: 14px 0;
  }
  .nav {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (max-width: 620px) {
  .topbar-inner {
    width: min(100% - 20px, 1240px);
  }
  .admin-page {
    width: min(100% - 20px, 1180px);
  }
}
</style>
