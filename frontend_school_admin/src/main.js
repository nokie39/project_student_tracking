import { createApp } from 'vue'
import App from './App.vue'

// 1. Import Vuetify & Icons
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css' // ໄອຄອນ

// 2. Import Router
import router from './router'

import './style.css'

// ✅ 3. Import PWA Register (ເພີ່ມໃໝ່)
import { registerSW } from 'virtual:pwa-register'

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
  },
})

const app = createApp(App)
app.use(vuetify)
app.use(router)
app.mount('#app')

// ✅ 4. Register Service Worker (ຈຸດສຳຄັນໃຫ້ປຸ່ມ Install ຂຶ້ນ)
const updateSW = registerSW({
  onNeedRefresh() {
    // ເມື່ອມີການອັບເດດ Code ໃໝ່ ມັນຈະຖາມໃຫ້ Reload
    if (confirm('ມີການອັບເດດລະບົບໃໝ່! ຕ້ອງການໂຫຼດໜ້າເວັບໃໝ່ບໍ່?')) {
      updateSW(true)
    }
  },
  onOfflineReady() {
    console.log('ແອັບພ້ອມໃຊ້ງານແບບ Offline ແລ້ວ!')
  },
})