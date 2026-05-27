# 谷子交易系统 - 前端完善指南

> 项目名称：gugou-front-end
> 技术栈：Vue 3 + TypeScript + Vite + Vue Router
> 文档更新日期：2026-05-22

---

## 一、当前项目状态

### ✅ 已完成模块

| 模块 | 文件路径 | 说明 |
|------|----------|------|
| 基础架构 | `package.json`, `vite.config.ts`, `tsconfig.json` | Vue 3 + TS + Vite 配置完整 |
| 路由系统 | `src/router/index.ts` | 用户端 9 条 + 管理端 8 条路由 |
| 用户端布局 | `src/layouts/TopBar.vue` | 顶部导航栏，8 个导航项 |
| 管理端布局 | `src/layouts/AdminLayout.vue` | 管理后台布局，7 个导航项 |
| 用户端页面 | `src/views/user/*.vue` | 9 个页面组件 |
| 管理端页面 | `src/views/admin/*.vue` | 8 个页面组件 |
| 全局样式 | `src/assets/base.css`, `src/assets/main.css` | CSS 变量体系 |

### ❌ 缺失模块

| 模块 | 优先级 | 说明 |
|------|--------|------|
| 状态管理 | P0 | 无 Pinia，数据无法跨组件共享 |
| HTTP 请求 | P0 | 无 axios/fetch 封装，无法调用后端 API |
| API 接口定义 | P0 | 无 `src/api/` 目录 |
| 路由守卫 | P0 | 无登录态检查和权限控制 |
| 类型定义 | P1 | 无 `src/types/` 目录 |
| 工具函数 | P1 | 无 `src/utils/` 目录 |
| 环境变量 | P1 | 无 `.env` 文件 |
| 订单页面 | P1 | TopBar 引用 `/my-orders` 但路由未定义 |
| 全局错误处理 | P2 | 无统一错误处理机制 |
| 全局 Loading | P2 | 无加载状态管理 |

---

## 二、P0 - 必须完成（核心功能）

### 2.1 添加 Pinia 状态管理

**目的**：实现用户登录态、购物车、全局配置等跨组件状态共享。

**安装依赖**：
```bash
npm install pinia
```

**目录结构**：
```
src/
└── stores/
    ├── index.ts          # createPinia() 导出
    ├── user.ts           # 用户状态（登录态、Token、用户信息）
    └── app.ts            # 应用全局状态（loading、错误信息等）
```

**实现要点**：

```typescript
// src/stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const userInfo = ref<any>(null)

  const isLoggedIn = computed(() => !!token.value)

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return { token, userInfo, isLoggedIn, setToken, logout }
})
```

```typescript
// src/stores/index.ts
import { createPinia } from 'pinia'
export const pinia = createPinia()
```

```typescript
// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { pinia } from './stores'

createApp(App).use(pinia).use(router).mount('#app')
```

---

### 2.2 封装 HTTP 请求

**目的**：统一管理 API 请求、Token 注入、错误处理、响应拦截。

**安装依赖**：
```bash
npm install axios
```

**目录结构**：
```
src/
└── utils/
    └── request.ts        # axios 实例封装
```

**实现要点**：

```typescript
// src/utils/request.ts
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

// 请求拦截器：注入 Token
request.interceptors.request.use((config) => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default request
```

---

### 2.3 定义 API 接口

**目的**：集中管理所有后端 API 调用，便于维护和 mock。

**目录结构**：
```
src/
└── api/
    ├── index.ts          # 统一导出
    ├── user.ts           # 用户相关接口
    ├── goods.ts          # 商品相关接口
    ├── order.ts          # 订单相关接口
    ├── market.ts         # 交易市场接口
    ├── swap.ts           # 交换交易接口
    └── group.ts          # 拼团相关接口
```

**实现要点**：

```typescript
// src/api/user.ts
import request from '@/utils/request'

export interface LoginParams {
  account: string
  password: string
}

export interface LoginResult {
  token: string
  user: {
    id: string
    phone: string
    nickname: string
    avatar: string
  }
}

export function login(params: LoginParams): Promise<LoginResult> {
  return request.post('/auth/login', params)
}

export function register(params: {
  phone: string
  password: string
}): Promise<void> {
  return request.post('/auth/register', params)
}

export function getUserInfo(): Promise<LoginResult['user']> {
  return request.get('/user/info')
}

export function logout(): Promise<void> {
  return request.post('/auth/logout')
}
```

```typescript
// src/api/goods.ts
import request from '@/utils/request'

export interface GoodsItem {
  id: string
  name: string
  price: number
  image: string
  ip: string
  role: string
  category: string
  description: string
}

export function getGoodsList(params?: {
  keyword?: string
  category?: string
  page?: number
  pageSize?: number
}): Promise<{ list: GoodsItem[]; total: number }> {
  return request.get('/goods', { params })
}

export function addGoods(data: Partial<GoodsItem>): Promise<void> {
  return request.post('/goods', data)
}
```

---

### 2.4 实现路由守卫

**目的**：保护需要登录的页面，未登录用户跳转到登录页。

**文件**：`src/router/index.ts`

**实现要点**：

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ... 现有路由
  ]
})

// 白名单：不需要登录的页面
const publicPaths = ['/', '/login', '/admin/login']

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 管理后台路由单独判断
  if (to.path.startsWith('/admin') && to.path !== '/admin/login') {
    // 这里可以检查管理员登录态
    // 暂时放行，后续需要单独的管理员认证
    next()
    return
  }

  // 公开页面直接放行
  if (publicPaths.includes(to.path)) {
    next()
    return
  }

  // 需要登录的页面检查登录态
  if (!userStore.isLoggedIn) {
    next('/login')
    return
  }

  next()
})

export default router
```

---

## 三、P1 - 重要完善

### 3.1 添加环境变量配置

**目的**：区分开发/测试/生产环境的 API 地址和其他配置。

**文件结构**：
```
gugou-front-end/
├── .env                  # 通用配置
├── .env.development      # 开发环境
├── .env.production       # 生产环境
└── .env.staging          # 测试环境（可选）
```

**实现要点**：

```env
# .env.development
VITE_API_BASE_URL=http://localhost:3000/api
VITE_APP_TITLE=谷子交易系统（开发）
VITE_APP_ENV=development
```

```env
# .env.production
VITE_API_BASE_URL=https://api.gugou.com/api
VITE_APP_TITLE=谷子交易系统
VITE_APP_ENV=production
```

```typescript
// src/env.d.ts 补充类型声明
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_ENV: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

---

### 3.2 创建类型定义目录

**目的**：统一管理 TypeScript 接口类型，避免重复定义。

**目录结构**：
```
src/
└── types/
    ├── index.ts          # 统一导出
    ├── user.ts           # 用户相关类型
    ├── goods.ts          # 商品相关类型
    ├── order.ts          # 订单相关类型
    └── api.ts            # API 响应通用类型
```

**实现要点**：

```typescript
// src/types/api.ts
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}
```

```typescript
// src/types/user.ts
export interface UserInfo {
  id: string
  phone: string
  nickname: string
  avatar: string
  role: 'user' | 'admin'
  createdAt: string
}

export interface LoginForm {
  account: string
  password: string
}

export interface RegisterForm {
  phone: string
  password: string
  confirmPassword: string
}
```

```typescript
// src/types/goods.ts
export interface GoodsItem {
  id: string
  name: string
  price: number
  image: string
  ip: string
  role: string
  category: string
  description: string
  status: 'pending' | 'approved' | 'rejected'
  createdAt: string
}
```

---

### 3.3 创建工具函数目录

**目的**：存放通用工具函数，如日期格式化、表单验证、本地存储封装等。

**目录结构**：
```
src/
└── utils/
    ├── request.ts        # HTTP 请求封装（已在 2.2 定义）
    ├── storage.ts        # localStorage 封装
    ├── format.ts         # 格式化工具（日期、金额等）
    └── validate.ts       # 表单验证规则
```

**实现要点**：

```typescript
// src/utils/storage.ts
export const storage = {
  get<T>(key: string): T | null {
    const value = localStorage.getItem(key)
    if (!value) return null
    try {
      return JSON.parse(value)
    } catch {
      return value as T
    }
  },

  set(key: string, value: any): void {
    localStorage.setItem(key, JSON.stringify(value))
  },

  remove(key: string): void {
    localStorage.removeItem(key)
  },

  clear(): void {
    localStorage.clear()
  }
}
```

```typescript
// src/utils/format.ts
export function formatDate(date: string | Date, format = 'YYYY-MM-DD'): string {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hour = String(d.getHours()).padStart(2, '0')
  const minute = String(d.getMinutes()).padStart(2, '0')
  const second = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('mm', minute)
    .replace('ss', second)
}

export function formatPrice(price: number): string {
  return `¥ ${price.toFixed(2)}`
}

export function formatPhone(phone: string): string {
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}
```

```typescript
// src/utils/validate.ts
export function isPhone(value: string): boolean {
  return /^1[3-9]\d{9}$/.test(value)
}

export function isPassword(value: string): boolean {
  return value.length >= 6
}

export function isEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
}
```

---

### 3.4 补充"我的订单"页面

**问题**：TopBar.vue 中有"我的订单"导航项指向 `/my-orders`，但路由未定义。

**实现步骤**：

1. 创建页面组件：
```vue
<!-- src/views/user/OrdersView.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import TopBar from '@/layouts/TopBar.vue'

const orders = ref([])
</script>

<template>
  <TopBar />
  <main class="page">
    <h1>我的订单</h1>
    <!-- 订单列表 -->
  </main>
</template>
```

2. 添加路由配置：
```typescript
// src/router/index.ts
{
  path: '/my-orders',
  name: 'orders',
  component: () => import('@/views/user/OrdersView.vue'),
}
```

---

## 四、P2 - 优化提升

### 4.1 全局错误处理

**目的**：统一处理 API 错误、网络异常，给用户友好提示。

**实现要点**：

```typescript
// src/utils/error.ts
import { useAppStore } from '@/stores/app'

export function handleError(error: any) {
  const appStore = useAppStore()
  
  if (error.response) {
    // 服务器返回错误
    const { status, data } = error.response
    switch (status) {
      case 400:
        appStore.showError(data.message || '请求参数错误')
        break
      case 401:
        appStore.showError('登录已过期，请重新登录')
        // 跳转登录页
        break
      case 403:
        appStore.showError('没有权限执行此操作')
        break
      case 404:
        appStore.showError('请求的资源不存在')
        break
      case 500:
        appStore.showError('服务器内部错误，请稍后重试')
        break
      default:
        appStore.showError(data.message || '未知错误')
    }
  } else if (error.request) {
    // 网络错误
    appStore.showError('网络连接失败，请检查网络')
  } else {
    appStore.showError(error.message || '操作失败')
  }
}
```

---

### 4.2 全局 Loading 状态

**目的**：统一管理页面和请求的加载状态。

**实现要点**：

```typescript
// src/stores/app.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const loading = ref(false)
  const loadingText = ref('')
  const errorMessage = ref('')

  function showLoading(text = '加载中...') {
    loading.value = true
    loadingText.value = text
  }

  function hideLoading() {
    loading.value = false
    loadingText.value = ''
  }

  function showError(message: string) {
    errorMessage.value = message
    setTimeout(() => {
      errorMessage.value = ''
    }, 3000)
  }

  return { loading, loadingText, errorMessage, showLoading, hideLoading, showError }
})
```

---

### 4.3 清理未使用的脚手架文件

**需要删除的文件**：
```
src/components/HelloWorld.vue
src/components/TheWelcome.vue
src/components/WelcomeItem.vue
src/components/icons/
src/assets/logo.svg          # 如果未使用
```

---

## 五、目录结构参考

完善后的项目目录结构：

```
gugou-front-end/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── .env
├── .env.development
├── .env.production
└── src/
    ├── main.ts
    ├── App.vue
    ├── assets/
    │   ├── base.css
    │   └── main.css
    ├── router/
    │   └── index.ts
    ├── stores/
    │   ├── index.ts
    │   ├── user.ts
    │   └── app.ts
    ├── api/
    │   ├── index.ts
    │   ├── user.ts
    │   ├── goods.ts
    │   ├── order.ts
    │   ├── market.ts
    │   ├── swap.ts
    │   └── group.ts
    ├── types/
    │   ├── index.ts
    │   ├── user.ts
    │   ├── goods.ts
    │   ├── order.ts
    │   └── api.ts
    ├── utils/
    │   ├── request.ts
    │   ├── storage.ts
    │   ├── format.ts
    │   ├── validate.ts
    │   └── error.ts
    ├── layouts/
    │   ├── TopBar.vue
    │   └── AdminLayout.vue
    ├── components/
    │   └── ... (业务组件)
    └── views/
        ├── user/
        │   ├── HomeView.vue
        │   ├── AuthView.vue
        │   ├── GoodsView.vue
        │   ├── MarketView.vue
        │   ├── AssetsView.vue
        │   ├── PriceView.vue
        │   ├── SwapView.vue
        │   ├── GroupView.vue
        │   ├── OrdersView.vue      # 新增
        │   └── ProfileView.vue
        └── admin/
            ├── AdminLoginView.vue
            ├── AdminDashboardView.vue
            ├── AdminUsersView.vue
            ├── AdminGoodsView.vue
            ├── AdminOrdersView.vue
            ├── AdminExchangeView.vue
            ├── AdminTeamView.vue
            └── AdminPriceView.vue
```

---

## 六、实施建议

### 实施顺序

```
阶段一（核心功能）：
  1. 安装 Pinia + axios
  2. 创建 stores/user.ts
  3. 创建 utils/request.ts
  4. 修改 main.ts 注册 Pinia
  5. 修改 AuthView.vue 接入真实登录

阶段二（接口对接）：
  1. 创建 api/ 目录，定义各模块接口
  2. 创建 types/ 目录，统一类型定义
  3. 修改各页面组件，接入 API

阶段三（路由守卫）：
  1. 添加路由守卫逻辑
  2. 补充 OrdersView.vue 页面
  3. 修复 TopBar 导航问题

阶段四（优化完善）：
  1. 添加环境变量配置
  2. 创建 utils/ 工具函数
  3. 添加全局错误处理
  4. 添加全局 Loading
  5. 清理无用文件
```

### 注意事项

1. **渐进式改造**：不要一次性修改所有文件，逐个模块改造并测试
2. **保持兼容**：改造过程中保持现有功能可用
3. **类型安全**：充分利用 TypeScript 类型检查
4. **代码复用**：提取公共逻辑到 utils/ 和 components/

---

## 七、相关命令

```bash
# 安装新增依赖
npm install pinia axios

# 启动开发服务器
npm run dev

# 类型检查
npm run type-check

# 构建生产版本
npm run build
```

---

*文档生成时间：2026-05-22*
*项目版本：v0.0.0*
