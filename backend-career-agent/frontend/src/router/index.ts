import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'landing',
    component: () => import('@/views/Landing.vue'),
    meta: { title: '后端职途', public: true }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/role-select',
    name: 'roleSelect',
    component: () => import('@/views/RoleCardSelect.vue'),
    meta: { title: '选择面试方向', public: true }
  },
  {
    path: '/dashboard',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台' }
      }
    ]
  },
  {
    path: '/job-matcher',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'jobMatcher',
        component: () => import('@/views/JobMatcher.vue'),
        meta: { title: '岗位匹配' }
      }
    ]
  },
  {
    path: '/resume-optimizer',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'resumeOptimizer',
        component: () => import('@/views/ResumeOptimizer.vue'),
        meta: { title: '项目分析' }
      }
    ]
  },
  {
    path: '/question-bank',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'questionBank',
        component: () => import('@/views/QuestionBank.vue'),
        meta: { title: '题库刷题' }
      }
    ]
  },
  {
    path: '/interview',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'interview',
        component: () => import('@/views/Interview.vue'),
        meta: { title: '模拟面试' }
      }
    ]
  },
  {
    path: '/history',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'history',
        component: () => import('@/views/History.vue'),
        meta: { title: '历史记录' }
      }
    ]
  },
  {
    path: '/profile',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人资料', requireAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：未登录时跳转到登录页（游客模式放行）
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('career-agent-token')
  const guestMode = localStorage.getItem('career-agent-guest') === 'true'
  const isPublic = to.meta?.public === true
  const requireAuth = to.meta?.requireAuth === true

  // 需要登录的页面，游客不可访问
  if (requireAuth && !token) {
    next('/login')
    return
  }

  // 游客模式 或 已登录 或 公开页面 → 放行
  if (token || guestMode || isPublic) {
    next()
  } else {
    next('/login')
  }
})

router.afterEach((to) => {
  const title = (to.meta?.title as string) || '后端职途'
  document.title = `${title} · 后端职途`
})

export default router
