<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const navItems = [
  { label: '产品库', to: '/goods' },
  { label: '交易市场', to: '/market' },
  { label: '我的资产', to: '/assets' },
  { label: '价格分析', to: '/price' },
  { label: '交换交易', to: '/swap' },
  { label: '拼团项目', to: '/group' },
  { label: '我的订单', to: '/my-orders' },
  { label: '用户中心', to: '/profile' },
]

function isActive(path: string) {
  return route.path === path
}
</script>

<template>
  <header class="topbar">
    <div class="topbar-inner">
      <div class="logo" @click="router.push('/')">
        <span>G</span>
        <strong>谷子交易系统</strong>
      </div>
      <nav class="nav" aria-label="主导航">
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
    </div>
  </header>
</template>

<style scoped>
.topbar {
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
  color: #172126;
  background: var(--gold);
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
}
</style>
