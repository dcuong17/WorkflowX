<script setup>
import { useAuthStore } from '../stores/authStore'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Top bar -->
    <nav class="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
      <h1 class="text-xl font-bold text-gray-800">WorkflowX</h1>
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-600">{{ authStore.userEmail }}</span>
        <button
          @click="handleLogout"
          class="px-4 py-2 text-sm bg-red-500 text-white rounded-md hover:bg-red-600"
        >
          Đăng xuất
        </button>
      </div>
    </nav>

    <!-- Main content -->
    <main class="max-w-7xl mx-auto py-8 px-4">
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold mb-4">Chào mừng đến với WorkflowX</h2>
        <p class="text-gray-600">Chọn workspace để bắt đầu quản lý công việc.</p>
        <!-- Workspaces list and task management will be added here -->
      </div>
    </main>
  </div>
</template>
