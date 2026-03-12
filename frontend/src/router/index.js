// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { supabase } from '@/lib/supabase'

const routes = [
  { path: '/login',    name: 'Login',    component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  { path: '/',         name: 'Dashboard', component: () => import('@/views/DashboardView.vue') },
  { path: '/review',   name: 'Review',   component: () => import('@/views/ReviewView.vue') },
  { path: '/quiz',     name: 'Quiz',     component: () => import('@/views/QuizSetupView.vue') },
  { path: '/quiz/play',name: 'QuizPlay', component: () => import('@/views/QuizPlayView.vue') },
  { path: '/history',  name: 'History',  component: () => import('@/views/HistoryView.vue') },
  { path: '/history/:id', name: 'HistoryDetail', component: () => import('@/views/HistoryDetailView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Guard: redirect to /login if not authenticated
router.beforeEach(async (to) => {
  if (to.meta.public) return true
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) return { name: 'Login' }
  return true
})

export default router
