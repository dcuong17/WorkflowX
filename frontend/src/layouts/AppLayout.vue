<template>
  <div class="min-h-screen overflow-x-hidden bg-[#f7f9ff] text-slate-900 lg:flex">
    <AppSidebar :open="sidebarOpen" @close="sidebarOpen = false" />

    <div class="app-shell-content flex min-h-screen flex-1 flex-col lg:ml-[270px]">
      <AppHeader @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <main class="flex-1 bg-[#f4f7ff] px-4 py-5 sm:px-6 lg:px-8">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterView } from 'vue-router'

import AppHeader from '../components/AppHeader.vue'
import AppSidebar from '../components/AppSidebar.vue'

const sidebarOpen = ref(false)
</script>

<style scoped>
@media (min-width: 1024px) {
  .app-shell-content {
    width: calc(100vw - 270px);
    max-width: calc(100vw - 270px);
  }
}
</style>
