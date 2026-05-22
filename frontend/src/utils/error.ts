import { useAppStore } from '@/stores/app'

export function handleError(error: any) {
  const appStore = useAppStore()

  if (error.response) {
    const { status, data } = error.response
    switch (status) {
      case 400:
        appStore.showError(data?.message || '请求参数错误')
        break
      case 401:
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
        appStore.showError(data?.message || '未知错误')
    }
  } else if (error.request) {
    appStore.showError('网络连接失败，请检查网络')
  } else {
    appStore.showError(error.message || '操作失败')
  }
}
