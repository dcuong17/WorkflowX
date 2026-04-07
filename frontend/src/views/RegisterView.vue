<template>
  <div class="w-full max-w-[500px] rounded-[30px] bg-white px-8 py-10 shadow-[0_30px_120px_rgba(31,56,128,0.25)] sm:px-10">
    <div class="text-center">
      <h1 class="text-4xl font-bold text-slate-900">Create Workspace Account</h1>
      <p class="mt-3 text-sm text-slate-500">Đăng ký nhanh để tạo workspace riêng hoặc tham gia workspace được mời.</p>
    </div>

    <form class="mt-10 space-y-6" @submit.prevent="handleSubmit">
      <label class="block text-sm font-medium text-slate-600">
        Email address
        <input v-model="form.email" type="email" required class="auth-input mt-3" placeholder="manager@workflowx.app" />
      </label>

      <label class="block text-sm font-medium text-slate-600">
        Password
        <input v-model="form.password" type="password" required class="auth-input mt-3" placeholder="Ít nhất 8 ký tự" />
      </label>

      <label class="block text-sm font-medium text-slate-600">
        Confirm password
        <input v-model="form.password_confirm" type="password" required class="auth-input mt-3" placeholder="Nhập lại mật khẩu" />
      </label>

      <p v-if="errorMessage" class="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-600">{{ errorMessage }}</p>

      <BaseButton type="submit" size="lg" block :loading="authStore.loading">Sign Up</BaseButton>
    </form>

    <p class="mt-6 text-center text-sm text-slate-500">
      Đã có tài khoản?
      <RouterLink class="font-semibold text-[#4f7df0]" to="/login">Đăng nhập</RouterLink>
    </p>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import BaseButton from '../components/BaseButton.vue'
import { useAuthStore } from '../stores/authStore'
import { useToastStore } from '../stores/toastStore'

const authStore = useAuthStore()
const toastStore = useToastStore()
const router = useRouter()
const errorMessage = ref('')

const form = reactive({ email: '', password: '', password_confirm: '' })

async function handleSubmit() {
  errorMessage.value = ''

  try {
    await authStore.signUp(form)
    toastStore.success('Account created', 'Đăng ký tài khoản thành công.')
    router.push('/dashboard')
  } catch (error) {
    const data = error.response?.data ?? {}
    errorMessage.value = data.password_confirm?.[0] || data.password?.[0] || data.email?.[0] || 'Đăng ký thất bại. Vui lòng kiểm tra lại thông tin.'
  }
}
</script>
