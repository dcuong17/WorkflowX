<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  email: '',
  password: '',
  acceptTerms: false,
})

const formError = ref('')
const passwordError = ref('')

function validatePassword() {
  if (form.password.length < 8) {
    passwordError.value = 'Password must be at least 8 characters'
    return false
  }
  passwordError.value = ''
  return true
}

function validateForm() {
  formError.value = ''
  passwordError.value = ''

  if (!form.acceptTerms) {
    formError.value = 'You must accept the terms and conditions'
    return false
  }

  if (!validatePassword()) {
    return false
  }

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailPattern.test(form.email)) {
    formError.value = 'Please enter a valid email address'
    return false
  }

  return true
}

async function handleSignup() {
  if (!validateForm()) return

  try {
    await authStore.signup({ email: form.email, password: form.password })
    router.push({ path: '/login', query: { signedUp: 'true' } })
  } catch (err) {
    const data = err.response?.data
    if (typeof data === 'object') {
      formError.value = Object.values(data).flat().join('\n')
    } else {
      formError.value = 'Registration failed. Please try again.'
    }
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-[#5B8AFF]">
    <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md mx-4 p-10">
      <h1 class="text-2xl font-bold text-center text-gray-900 mb-2">Create an Account</h1>
      <p class="text-center text-gray-600 mb-8">Create an account to continue</p>

      <form @submit.prevent="handleSignup" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email address:</label>
          <input
            v-model="form.email"
            type="email"
            required
            placeholder="you@gmail.com"
            class="w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#5B8AFF] focus:border-transparent placeholder-gray-400"
          />
        </div>

        <div class="relative">
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            v-model="form.password"
            type="password"
            required
            minlength="8"
            @blur="validatePassword"
            placeholder="••••••••"
            class="w-full px-4 py-3 bg-gray-100 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#5B8AFF] focus:border-transparent placeholder-gray-400"
          />
          <p v-if="passwordError" class="text-red-500 text-xs mt-1">{{ passwordError }}</p>
        </div>

        <div class="flex items-center">
          <input
            v-model="form.acceptTerms"
            type="checkbox"
            id="terms"
            required
            class="w-4 h-4 text-[#5B8AFF] border-gray-300 rounded focus:ring-[#5B8AFF]"
          />
          <label for="terms" class="ml-2 text-sm text-gray-600">I accept terms and conditions</label>
        </div>

        <p v-if="formError" class="text-red-500 text-sm whitespace-pre-line">{{ formError }}</p>

        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full bg-[#5B8AFF] text-white py-3 rounded-lg text-base font-medium hover:bg-[#4A7AFF] disabled:opacity-50 transition-colors"
        >
          {{ authStore.loading ? 'Signing up...' : 'Sign Up' }}
        </button>
      </form>

      <p class="text-center text-sm text-gray-600 mt-6">
        Already have an account?
        <router-link to="/login" class="text-[#5B8AFF] hover:underline font-medium">Login</router-link>
      </p>
    </div>
  </div>
</template>
