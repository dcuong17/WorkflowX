import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1'

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('workflowx_access_token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const status = error.response?.status

    if (
      status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/auth/signin') &&
      !originalRequest.url?.includes('/auth/signup') &&
      !originalRequest.url?.includes('/auth/token/refresh')
    ) {
      originalRequest._retry = true

      try {
        const { useAuthStore } = await import('../stores/authStore')
        const authStore = useAuthStore()
        const nextToken = await authStore.refreshAccessToken()
        originalRequest.headers.Authorization = `Bearer ${nextToken}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        const { useAuthStore } = await import('../stores/authStore')
        const authStore = useAuthStore()
        authStore.clearSession()
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  },
)
