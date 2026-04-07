import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1/'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
    loading: false,
    error: null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.accessToken,
    userEmail: (state) => state.user?.email || null,
    userId: (state) => state.user?.id || null,
  },

  actions: {
    persistAuth(user, accessToken, refreshToken) {
      this.user = user
      this.accessToken = accessToken
      this.refreshToken = refreshToken
      this.isAuthenticated = true

      localStorage.setItem('access_token', accessToken)
      localStorage.setItem('refresh_token', refreshToken)
      localStorage.setItem('user', JSON.stringify(user))
    },

    restoreSession() {
      const accessToken = localStorage.getItem('access_token')
      const refreshToken = localStorage.getItem('refresh_token')
      const user = localStorage.getItem('user')

      if (accessToken && refreshToken && user) {
        this.accessToken = accessToken
        this.refreshToken = refreshToken
        this.user = JSON.parse(user)
        this.isAuthenticated = true
        return true
      }

      return false
    },

    clearAuth() {
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      this.isAuthenticated = false
      this.error = null

      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    },

    async signup(credentials) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(`${API_URL}auth/signup`, {
          email: credentials.email,
          password: credentials.password,
        })
        return response.data
      } catch (error) {
        this.error = error.response?.data || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async login(credentials) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(`${API_URL}auth/signin`, {
          email: credentials.email,
          password: credentials.password,
        })

        const { id, email, access_token, refresh_token } = response.data

        this.persistAuth({ id, email }, access_token, refresh_token)
        return response.data
      } catch (error) {
        this.error = error.response?.data || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        const refreshToken = this.refreshToken
        await axios.post(`${API_URL}auth/signout`, {
          refresh_token: refreshToken,
        })
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.clearAuth()
      }
    },
  },
})
