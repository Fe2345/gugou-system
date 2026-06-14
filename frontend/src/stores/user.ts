import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  const access = ref<string>(localStorage.getItem('access_token') || '')
  const refresh = ref<string>(localStorage.getItem('refresh_token') || '')
  const userInfo = ref<UserInfo | null>(null)
  const authInitialized = ref(false)
  let resolveAuthInitialized: (() => void) | null = null
  const authInitializedPromise = new Promise<void>((resolve) => {
    resolveAuthInitialized = resolve
  })

  const isLoggedIn = computed(() => !!access.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')

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

  function finishAuthInitialization() {
    if (authInitialized.value) {
      return
    }
    authInitialized.value = true
    resolveAuthInitialized?.()
    resolveAuthInitialized = null
  }

  function waitForAuthInitialized() {
    if (authInitialized.value) {
      return Promise.resolve()
    }
    return authInitializedPromise
  }

  return {
    access,
    refresh,
    userInfo,
    authInitialized,
    isLoggedIn,
    isAdmin,
    setTokens,
    setAccess,
    setUserInfo,
    logout,
    finishAuthInitialization,
    waitForAuthInitialized,
  }
})
