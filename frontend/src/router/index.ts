import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue')
  },
  {
    path: '/trade',
    name: 'Trading',
    component: () => import('@/views/TradingView.vue')
  },
  {
    path: '/graph',
    name: 'Charts',
    component: () => import('@/views/ChartsView.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue')
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('@/views/LogView.vue')
  },
  {
    path: '/settings/api',
    name: 'ApiSettings',
    component: () => import('@/views/ApiSettings.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/Error404View.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!sessionStorage.getItem('bot_token')

  if (to.name === 'Login' || to.path === '/') {
    if (isAuthenticated) {
      next({ name: 'Dashboard' })
    } else {
      next()
    }
  } else {
    // Protected routes
    if (!isAuthenticated && to.name !== 'Login') {
      next({ name: 'Home' })
    } else {
      next() // make sure to always call next()!
    }
  }
})

export default router
