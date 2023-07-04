import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// Boostrap5
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

// VueRouter
import router from './router.js'

// Pinia
import { createPinia } from 'pinia'

// fontawesome
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faChevronCircleRight, faChevronCircleLeft, faCircleInfo, faSpinner } from '@fortawesome/free-solid-svg-icons'
library.add(faChevronCircleRight, faChevronCircleLeft, faCircleInfo, faSpinner)

const app = createApp(App)
app.component('font-awesome-icon', FontAwesomeIcon)
app.use(router)

const pinia = createPinia()
app.use(pinia)

app.mount('#app')
