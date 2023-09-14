import { createRouter, createWebHistory } from 'vue-router'

import Dashboard from './views/Dashboard.vue'

const routes = [{
  path: '/',
  name: 'root',
  redirect: { name: 'dashboard' }
},
{
  path: '/dashboard',
  name: 'dashboard',
  component: Dashboard
},
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router