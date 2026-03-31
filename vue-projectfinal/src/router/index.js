import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/source-code'
  },
  {
    path: '/source-code',
    name: 'SourceCode',
    component: () => import('../views/SourceCode.vue')
  },
  {
    path: '/test-case',
    name: 'TestCase',
    component: () => import('../views/TestCaseGenerator.vue')
  },
  {
    path: '/data-resources',
    name: 'DataResource',
    component: () => import('../views/DataResourceConfig.vue')
  },
  {
    path: '/user-management',
    name: 'UserManagement',
    component: () => import('../views/UserManagement.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/SystemSettings.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router