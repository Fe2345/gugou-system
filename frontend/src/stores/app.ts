import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const loading = ref(false)
  const loadingText = ref('')
  const errorMessage = ref('')

  function showLoading(text = '加载中...') {
    loading.value = true
    loadingText.value = text
  }

  function hideLoading() {
    loading.value = false
    loadingText.value = ''
  }

  function showError(message: string) {
    errorMessage.value = message
    setTimeout(() => {
      errorMessage.value = ''
    }, 3000)
  }

  function clearError() {
    errorMessage.value = ''
  }

  return { loading, loadingText, errorMessage, showLoading, hideLoading, showError, clearError }
})
