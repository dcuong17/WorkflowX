import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { apiClient } from '../plugins/axios'
import { useToastStore } from './toastStore'

const ACCESS_TOKEN_KEY = 'workflowx_access_token'
const REFRESH_TOKEN_KEY = 'workflowx_refresh_token'
const USER_KEY = 'workflowx_user'

export const useAuthStore = defineStore('authStore', () => {
  const toastStore = useToastStore()
  const accessToken = ref(localStorage.getItem(ACCESS_TOKEN_KEY) ?? '')
  const refreshToken = ref(localStorage.getItem(REFRESH_TOKEN_KEY) ?? '')
  const user = ref(loadStoredUser())
  const initialized = ref(false)
  const loading = ref(false)

  const isAuthenticated = computed(() => Boolean(accessToken.value))

  function persistSession(payload) {
    accessToken.value = payload.accessToken ?? ''
    refreshToken.value = payload.refreshToken ?? ''
    user.value = payload.user ?? null

    persistValue(ACCESS_TOKEN_KEY, accessToken.value)
    persistValue(REFRESH_TOKEN_KEY, refreshToken.value)
    persistValue(USER_KEY, user.value ? JSON.stringify(user.value) : '')
  }

  function clearSession() {
    persistSession({
      accessToken: '',
      refreshToken: '',
      user: null,
    })
  }

  async function initialize() {
    if (!accessToken.value) {
      initialized.value = true
      return
    }

    try {
      await fetchProfile()
    } catch {
      try {
        await refreshAccessToken()
        await fetchProfile()
      } catch {
        clearSession()
      }
    } finally {
      initialized.value = true
    }
  }

  async function signIn(credentials) {
    loading.value = true
    try {
      const { data } = await apiClient.post('/auth/signin', credentials)
      persistSession({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        user: {
          id: data.id,
          email: data.email,
          username: data.username,
          role: data.role,
        },
      })
      return data
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  async function signUp(payload) {
    loading.value = true
    try {
      await apiClient.post('/auth/signup', payload)
      return await signIn({
        email: payload.email,
        password: payload.password,
      })
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  async function fetchProfile() {
    const { data } = await apiClient.get('/auth/profile')
    persistSession({
      accessToken: accessToken.value,
      refreshToken: refreshToken.value,
      user: data,
    })
    return data
  }

  async function updateProfile(payload) {
    const { data } = await apiClient.put('/auth/profile', payload)
    persistSession({
      accessToken: accessToken.value,
      refreshToken: refreshToken.value,
      user: data,
    })
    toastStore.success('Profile updated', 'Thông tin cá nhân đã được cập nhật.')
    return data
  }

  async function changePassword(payload) {
    const { data } = await apiClient.post('/auth/change-password', payload)
    toastStore.success('Password changed', 'Mật khẩu đã được thay đổi thành công.')
    return data
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) {
      throw new Error('Missing refresh token')
    }

    const { data } = await apiClient.post('/auth/token/refresh', {
      refresh: refreshToken.value,
    })

    persistSession({
      accessToken: data.access,
      refreshToken: refreshToken.value,
      user: user.value,
    })

    return data.access
  }

  async function signOut() {
    try {
      if (refreshToken.value) {
        await apiClient.post('/auth/signout', {
          refresh_token: refreshToken.value,
        })
      }
    } finally {
      clearSession()
      toastStore.success('Signed out', 'Bạn đã đăng xuất khỏi hệ thống.')
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    initialized,
    loading,
    isAuthenticated,
    initialize,
    signIn,
    signUp,
    fetchProfile,
    updateProfile,
    changePassword,
    refreshAccessToken,
    signOut,
    clearSession,
  }
})

function loadStoredUser() {
  const rawUser = localStorage.getItem(USER_KEY)
  if (!rawUser) return null

  try {
    return JSON.parse(rawUser)
  } catch {
    localStorage.removeItem(USER_KEY)
    return null
  }
}

function persistValue(key, value) {
  if (!value) {
    localStorage.removeItem(key)
    return
  }

  localStorage.setItem(key, value)
}
