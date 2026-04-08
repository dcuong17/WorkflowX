import { defineStore } from 'pinia'
import { ref } from 'vue'

let toastSeed = 0

export const useToastStore = defineStore('toastStore', () => {
  const toasts = ref([])

  function push({ title, message = '', tone = 'success', duration = 3200 }) {
    const id = ++toastSeed
    toasts.value = [...toasts.value, { id, title, message, tone }]

    if (duration > 0) {
      window.setTimeout(() => dismiss(id), duration)
    }

    return id
  }

  function success(title, message = '') {
    return push({ title, message, tone: 'success' })
  }

  function warning(title, message = '') {
    return push({ title, message, tone: 'warning', duration: 4200 })
  }

  function error(title, message = '') {
    return push({ title, message, tone: 'error', duration: 4800 })
  }

  function dismiss(id) {
    toasts.value = toasts.value.filter((toast) => toast.id !== id)
  }

  return {
    toasts,
    push,
    success,
    warning,
    error,
    dismiss,
  }
})
