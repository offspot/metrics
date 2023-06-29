import { createRouter, createWebHistory } from 'vue-router'

import Home from './views/Home.vue'
import About from './views/About.vue'
import About2 from './views/About2.vue'

const routes = [
    {
        path: '/',
        name: 'root',
        redirect: { name: 'home' }
    },
    {
        path: '/home',
        name: 'home',
        component: Home
    },
    {
        path: '/about',
        name: 'about',
        component: About
    },
    {
        path: '/about2',
        name: 'about2',
        component: About2
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router