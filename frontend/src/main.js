import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// VueRouter
import router from './router.js'

// Pinia
import { createPinia } from 'pinia'

// fontawesome
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faUserSecret, faUmbrellaBeach } from '@fortawesome/free-solid-svg-icons'
library.add(faUserSecret, faUmbrellaBeach)

const app = createApp(App)
app.component('font-awesome-icon', FontAwesomeIcon)
app.use(router)

const pinia = createPinia()
app.use(pinia)

app.mount('#app')
