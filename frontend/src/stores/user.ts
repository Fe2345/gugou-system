import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  const access = ref<string>(localStorage.getItem('access_token') || '')
  const refresh = ref<string>(localStorage.getItem('refresh_token') || '')
  const userInfo = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!access.value)

  function setTokens(accessToken: string, refreshToken: string) {
    access.value = accessToken
    refresh.value = refreshToken
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshToken)
  }

  function setAccess(accessToken: string) {
    access.value = accessToken
    localStorage.setItem('access_token', accessToken)
  }

  function setUserInfo(info: UserInfo) {
    userInfo.value = info
  }

  function logout() {
    access.value = ''
    refresh.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { access, refresh, userInfo, isLoggedIn, setTokens, setAccess, setUserInfo, logout }
})
