import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { pinia } from './stores'
import { useUserStore } from './stores/user'
import { getUserInfo } from './api/user'

const app = createApp(App)
app.use(pinia)
app.use(router)

async function validateAuth() {
  const userStore = useUserStore()
  if (!userStore.access) {
    return
  }

  try {
    const res = await getUserInfo()
    userStore.setUserInfo(res.data)
  } catch {
    // Token invalid or refresh failed — store is already cleaned by 401 interceptor
  }
}

validateAuth().finally(() => {
  app.mount('#app')
})
