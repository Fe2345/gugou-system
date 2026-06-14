import axios from 'axios'
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import router from '@/router'

const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

let isRefreshing = false
let pendingRequests: Array<{ resolve: (token: string) => void; reject: (err: unknown) => void }> = []

function onRefreshSuccess(newToken: string) {
  pendingRequests.forEach(({ resolve }) => resolve(newToken))
  pendingRequests = []
}

function onRefreshFailure(err: unknown) {
  pendingRequests.forEach(({ reject }) => reject(err))
  pendingRequests = []
}

request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (config.url === '/auth/refresh/') {
      return config
    }
    const userStore = useUserStore()
    if (userStore.access) {
      config.headers.Authorization = `Bearer ${userStore.access}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

request.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  async (error) => {
    const appStore = useAppStore()
    const userStore = useUserStore()
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (originalRequest.url === '/auth/refresh/') {
        userStore.logout()
        router.push('/login')
        appStore.showError('登录已过期，请重新登录')
        return Promise.reject(error)
      }

      if (!userStore.refresh) {
        userStore.logout()
        router.push('/login')
        appStore.showError('登录已过期，请重新登录')
        return Promise.reject(error)
      }

      originalRequest._retry = true

      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          pendingRequests.push({ resolve, reject })
        }).then((newToken) => {
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return request(originalRequest)
        })
      }

      isRefreshing = true

      try {
        const resp = await axios.post(
          `${import.meta.env.VITE_API_BASE_URL || '/api'}/auth/refresh/`,
          { refresh: userStore.refresh },
        )

        const newAccess = resp.data.data.access
        const newRefresh = resp.data.data.refresh

        if (newRefresh) {
          userStore.setTokens(newAccess, newRefresh)
        } else {
          userStore.setAccess(newAccess)
        }

        onRefreshSuccess(newAccess)

        originalRequest.headers.Authorization = `Bearer ${newAccess}`
        return request(originalRequest)
      } catch (refreshError) {
        onRefreshFailure(refreshError)
        userStore.logout()
        router.push('/login')
        appStore.showError('登录已过期，请重新登录')
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 403:
          appStore.showError('没有权限执行此操作')
          break
        case 404:
          appStore.showError('请求的资源不存在')
          break
        case 500:
          appStore.showError('服务器内部错误，请稍后重试')
          break
        default:
          appStore.showError(data?.message || '请求失败')
      }
    } else if (error.request) {
      appStore.showError('网络连接失败，请检查网络')
    } else {
      appStore.showError(error.message || '操作失败')
    }

    return Promise.reject(error)
  },
)

export default request
