import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// VueRouter
import router from './router.js'

// Pinia
import { createPinia } from 'pinia'

const app = createApp(App)
app.use(router)

const pinia = createPinia()
app.use(pinia)

app.mount('#app')
