import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/help/create'
  },
  {
    path: '/help/create',
    name: 'HelpCreate',
    component: () => import('@/views/HelpCreate.vue'),
    meta: { title: '发起求助', icon: '📞' }
  },
  {
    path: '/guidance',
    name: 'Guidance',
    component: () => import('@/views/GuidanceRecords.vue'),
    meta: { title: '远程指导', icon: '💬' }
  },
  {
    path: '/stepcards',
    name: 'StepCards',
    component: () => import('@/views/StepCards.vue'),
    meta: { title: '步骤卡整理', icon: '📋' }
  },
  {
    path: '/library',
    name: 'Library',
    component: () => import('@/views/ProblemLibrary.vue'),
    meta: { title: '高频问题库', icon: '📚' }
  },
  {
    path: '/library/:cardId',
    name: 'LibraryDetail',
    component: () => import('@/views/ProblemLibrary.vue'),
    meta: { title: '高频问题库', icon: '📚' }
  },
  {
    path: '/stats',
    name: 'Stats',
    component: () => import('@/views/Statistics.vue'),
    meta: { title: '数据统计', icon: '📊' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
