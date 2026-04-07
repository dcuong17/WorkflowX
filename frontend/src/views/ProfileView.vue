<template>
  <div class="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
    <BaseCard>
      <div>
        <p class="text-sm uppercase tracking-[0.28em] text-[#4f7df0]">Account profile</p>
        <h2 class="mt-3 text-4xl font-semibold text-slate-900">Personal Details</h2>
        <p class="mt-3 max-w-2xl text-sm leading-7 text-slate-500">Cập nhật email đăng nhập và giữ đồng bộ session hiện tại.</p>
      </div>

      <form class="mt-8 space-y-4" @submit.prevent="handleProfileUpdate">
        <label class="block text-sm font-medium text-slate-600">
          Email address
          <input v-model="profileForm.email" type="email" required class="app-input mt-2" />
        </label>
        <label class="block text-sm font-medium text-slate-600">
          Username
          <input v-model="profileForm.username" type="text" class="app-input mt-2" placeholder="Nhập username để hiển thị trong workspace và task" />
        </label>
        <p class="rounded-[24px] bg-[#f7f9ff] px-4 py-4 text-sm text-slate-500">
          System role: <span class="font-semibold text-slate-900">{{ authStore.user?.role ?? 'member' }}</span>
        </p>
        <p v-if="profileMessage" class="rounded-2xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ profileMessage }}</p>
        <p v-if="profileError" class="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-600">{{ profileError }}</p>
        <div class="flex justify-end">
          <BaseButton type="submit" :loading="profileLoading">Save Profile</BaseButton>
        </div>
      </form>
    </BaseCard>

    <BaseCard>
      <div>
        <p class="text-sm uppercase tracking-[0.28em] text-[#4f7df0]">Security</p>
        <h2 class="mt-3 text-4xl font-semibold text-slate-900">Change Password</h2>
        <p class="mt-3 max-w-2xl text-sm leading-7 text-slate-500">Mật khẩu mới phải có ít nhất 8 ký tự và xác nhận trùng khớp.</p>
      </div>

      <form class="mt-8 space-y-4" @submit.prevent="handlePasswordChange">
        <label class="block text-sm font-medium text-slate-600">
          Current password
          <input v-model="passwordForm.old_password" type="password" required class="app-input mt-2" />
        </label>
        <p class="rounded-[20px] bg-[#f7f9ff] px-4 py-3 text-sm leading-6 text-slate-500">
          Vì lý do bảo mật, mật khẩu hiện tại không thể tự động điền. Hệ thống chỉ lưu password dạng băm nên bạn cần nhập lại thủ công khi đổi mật khẩu.
        </p>
        <label class="block text-sm font-medium text-slate-600">
          New password
          <input v-model="passwordForm.new_password" type="password" required class="app-input mt-2" />
        </label>
        <label class="block text-sm font-medium text-slate-600">
          Confirm new password
          <input v-model="passwordForm.new_password_confirm" type="password" required class="app-input mt-2" />
        </label>
        <p v-if="passwordMessage" class="rounded-2xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ passwordMessage }}</p>
        <p v-if="passwordError" class="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-600">{{ passwordError }}</p>
        <div class="flex justify-end">
          <BaseButton type="submit" :loading="passwordLoading">Update Password</BaseButton>
        </div>
      </form>
    </BaseCard>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import { useAuthStore } from '../stores/authStore'

const authStore = useAuthStore()

const profileLoading = ref(false)
const passwordLoading = ref(false)
const profileMessage = ref('')
const passwordMessage = ref('')
const profileError = ref('')
const passwordError = ref('')

const profileForm = reactive({
  email: authStore.user?.email ?? '',
  username: authStore.user?.username ?? '',
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  new_password_confirm: '',
})

async function handleProfileUpdate() {
  profileLoading.value = true
  profileMessage.value = ''
  profileError.value = ''

  try {
    await authStore.updateProfile({ email: profileForm.email, username: profileForm.username })
    profileMessage.value = 'Thông tin cá nhân đã được cập nhật.'
  } catch (error) {
    profileError.value = error.response?.data?.email?.[0] || 'Không thể cập nhật hồ sơ.'
  } finally {
    profileLoading.value = false
  }
}

async function handlePasswordChange() {
  passwordLoading.value = true
  passwordMessage.value = ''
  passwordError.value = ''

  try {
    await authStore.changePassword(passwordForm)
    passwordMessage.value = 'Mật khẩu đã được thay đổi thành công.'
    passwordForm.old_password = ''
    passwordForm.new_password = ''
    passwordForm.new_password_confirm = ''
  } catch (error) {
    passwordError.value =
      error.response?.data?.old_password?.[0] ||
      error.response?.data?.new_password?.[0] ||
      error.response?.data?.new_password_confirm?.[0] ||
      'Không thể đổi mật khẩu.'
  } finally {
    passwordLoading.value = false
  }
}
</script>
