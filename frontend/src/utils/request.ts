import axios from 'axios'
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import router from '@/router'

const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

// 请求拦截器：注入 Token
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Token ${userStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error) => {
    const appStore = useAppStore()

    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 401:
          const userStore = useUserStore()
          userStore.logout()
          router.push('/login')
          appStore.showError('登录已过期，请重新登录')
          break
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
  }
)

export default request
