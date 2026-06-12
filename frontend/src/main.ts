import './assets/main.css'
import 'element-plus/dist/index.css'

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
    // 获取用户信息失败，清除 token 保持状态一致
    userStore.logout()
  }
}

validateAuth().finally(() => {
  app.mount('#app')
})
