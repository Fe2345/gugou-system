import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/user/HomeView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/user/AuthView.vue'),
    },
    {
      path: '/goods',
      name: 'goods',
      component: () => import('@/views/user/GoodsView.vue'),
    },
    {
      path: '/market',
      name: 'market',
      component: () => import('@/views/user/MarketView.vue'),
    },
    {
      path: '/price',
      name: 'price',
      component: () => import('@/views/user/PriceView.vue'),
    },
    {
      path: '/swap',
      name: 'swap',
      component: () => import('@/views/user/SwapView.vue'),
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/user/ProfileView.vue'),
    },
    {
      path: '/group',
      name: 'group',
      component: () => import('@/views/user/GroupView.vue'),
    },
    {
      path: '/assets',
      name: 'assets',
      component: () => import('@/views/user/AssetsView.vue'),
    },
    {
      path: '/my-orders',
      name: 'orders',
      component: () => import('@/views/user/OrdersView.vue'),
    },
    {
      path: '/market/publish',
      name: 'market-publish',
      component: () => import('@/views/user/MarketPublishView.vue'),
    },
    {
      path: '/market/my',
      name: 'market-my',
      component: () => import('@/views/user/MyMarketView.vue'),
    },
    {
      path: '/market/:id',
      name: 'market-detail',
      component: () => import('@/views/user/MarketDetailView.vue'),
      props: true,
    },
    {
      path: '/my-orders/create',
      name: 'order-create',
      component: () => import('@/views/user/OrderCreateView.vue'),
    },
    {
      path: '/my-orders/:id',
      name: 'order-detail',
      component: () => import('@/views/user/OrderDetailView.vue'),
      props: true,
    },
    {
      path: '/swap/publish',
      name: 'swap-publish',
      component: () => import('@/views/user/SwapPublishView.vue'),
    },
    {
      path: '/swap/my',
      name: 'swap-my',
      component: () => import('@/views/user/MySwapView.vue'),
    },
    {
      path: '/swap/:id',
      name: 'swap-detail',
      component: () => import('@/views/user/SwapDetailView.vue'),
      props: true,
    },
    {
      path: '/group/publish',
      name: 'group-publish',
      component: () => import('@/views/user/GroupPublishView.vue'),
    },
    {
      path: '/group/my',
      name: 'group-my',
      component: () => import('@/views/user/MyGroupView.vue'),
    },
    {
      path: '/group/:id',
      name: 'group-detail',
      component: () => import('@/views/user/GroupDetailView.vue'),
      props: true,
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/admin/AdminLoginView.vue'),
    },
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      children: [
        {
          path: '',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/AdminDashboardView.vue'),
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('@/views/admin/AdminUsersView.vue'),
        },
        {
          path: 'goods',
          name: 'admin-goods',
          component: () => import('@/views/admin/AdminGoodsView.vue'),
        },
        {
          path: 'orders',
          name: 'admin-orders',
          component: () => import('@/views/admin/AdminOrdersView.vue'),
        },
        {
          path: 'exchange',
          name: 'admin-exchange',
          component: () => import('@/views/admin/AdminExchangeView.vue'),
        },
        {
          path: 'team',
          name: 'admin-team',
          component: () => import('@/views/admin/AdminTeamView.vue'),
        },
        {
          path: 'price',
          name: 'admin-price',
          component: () => import('@/views/admin/AdminPriceView.vue'),
        },
      ],
    },
  ],
})

// 白名单：不需要登录的页面
const publicPaths = ['/', '/login', '/admin/login']

router.beforeEach((to, from, next) => {
  // 管理后台路由单独判断
  if (to.path.startsWith('/admin') && to.path !== '/admin/login') {
    // 管理后台暂时放行，后续需要单独的管理员认证
    next()
    return
  }

  // 公开页面直接放行
  if (publicPaths.includes(to.path)) {
    next()
    return
  }

  // 需要登录的页面检查登录态
  const userStore = useUserStore()
  if (!userStore.isLoggedIn) {
    next('/login')
    return
  }

  next()
})

export default router
