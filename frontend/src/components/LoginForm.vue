<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const rememberPassword = ref(false)
const formError = ref('')

async function handleLogin() {
  formError.value = ''
  try {
    await authStore.login({ email: email.value, password: password.value })
    if (rememberPassword.value) {
      localStorage.setItem('remember_email', email.value)
    }
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (err) {
    const data = err.response?.data
    formError.value = data?.non_field_errors?.[0] || 'Invalid credentials'
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-[#5B8AFF]">
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md mx-4 p-10">
      <h1 class="text-2xl font-bold text-center text-gray-900 mb-2">Login to Account</h1>
      <p class="text-center text-gray-600 mb-8">Please enter your email and password to continue</p>

      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email address:</label>
          <input
            v-model="email"
            type="email"
            required
            placeholder="you@gmail.com"
            class="w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#5B8AFF] focus:border-transparent placeholder-gray-400"
          />
        </div>

        <div>
          <div class="flex justify-between items-center mb-1">
            <label class="block text-sm font-medium text-gray-700">Password</label>
            <span class="text-sm text-gray-400">Forget Password?</span>
          </div>
          <input
            v-model="password"
            type="password"
            required
            placeholder="••••••••"
            class="w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#5B8AFF] focus:border-transparent placeholder-gray-400"
          />
        </div>

        <div class="flex items-center">
          <input
            v-model="rememberPassword"
            type="checkbox"
            id="remember"
            class="w-4 h-4 text-[#5B8AFF] border-gray-300 rounded focus:ring-[#5B8AFF]"
          />
          <label for="remember" class="ml-2 text-sm text-gray-600">Remember Password</label>
        </div>

        <p v-if="formError" class="text-red-500 text-sm">{{ formError }}</p>

        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full bg-[#5B8AFF] text-white py-3 rounded-lg text-base font-medium hover:bg-[#4A7AFF] disabled:opacity-50 transition-colors"
        >
          {{ authStore.loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <p class="text-center text-sm text-gray-600 mt-6">
        Don't have an account?
        <router-link to="/signup" class="text-[#5B8AFF] hover:underline font-medium">Create Account</router-link>
      </p>
    </div>
  </div>
</template>
