import { createApp } from 'vue'

import './style.css'
import App from './App.vue'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'

const app = createApp(App)

// VueRouter
import router from './router.js'

// Pinia
import { createPinia } from 'pinia'

// fontawesome
import { aliases, fa } from 'vuetify/iconsets/fa-svg'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { far } from '@fortawesome/free-regular-svg-icons'
library.add(fas)
library.add(far)
// eslint-disable-next-line vue/component-definition-name-casing
app.component('font-awesome-icon', FontAwesomeIcon)

app.use(router)

const vuetify = createVuetify({
  icons: {
    defaultSet: 'fa',
    aliases,
    sets: {
      fa,
    },
  },
})
app.use(vuetify)

const pinia = createPinia()
app.use(pinia)

import VueApexCharts from 'vue3-apexcharts'
app.use(VueApexCharts)

app.mount('#app')
