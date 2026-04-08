<template>
  <div class="w-full max-w-[470px] rounded-[30px] bg-white px-8 py-10 shadow-[0_30px_120px_rgba(31,56,128,0.25)] sm:px-10">
    <div class="text-center">
      <h1 class="text-4xl font-bold text-slate-900">Đăng nhập WorkflowX</h1>
      <p class="mt-3 text-sm text-slate-500">Dùng email và mật khẩu để truy cập dashboard workspace của bạn.</p>
    </div>

    <form class="mt-10 space-y-6" @submit.prevent="handleSubmit">
      <label class="block text-sm font-medium text-slate-600">
        Địa chỉ email
        <input v-model="form.email" type="email" required class="auth-input mt-3" placeholder="member@workflowx.app" />
      </label>

      <label class="block text-sm font-medium text-slate-600">
        Mật khẩu
        <input v-model="form.password" type="password" required class="auth-input mt-3" placeholder="••••••••" />
      </label>

      <p v-if="errorMessage" class="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-600">{{ errorMessage }}</p>

      <BaseButton type="submit" size="lg" block :loading="authStore.loading">Đăng nhập</BaseButton>
    </form>

    <p class="mt-6 text-center text-sm text-slate-500">
      Chưa có tài khoản?
      <RouterLink class="font-semibold text-[#4f7df0]" to="/register">Tạo tài khoản</RouterLink>
    </p>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import BaseButton from '../components/BaseButton.vue'
import { useAuthStore } from '../stores/authStore'
import { useToastStore } from '../stores/toastStore'

const authStore = useAuthStore()
const toastStore = useToastStore()
const route = useRoute()
const router = useRouter()
const errorMessage = ref('')

const form = reactive({ email: '', password: '' })

async function handleSubmit() {
  errorMessage.value = ''

  try {
    await authStore.signIn(form)
    toastStore.success('Signed in', 'Đăng nhập thành công.')
    router.push(route.query.redirect?.toString() || '/dashboard')
  } catch (error) {
    errorMessage.value = error.response?.data?.non_field_errors?.[0] || 'Đăng nhập thất bại. Vui lòng thử lại.'
  }
}
</script>
