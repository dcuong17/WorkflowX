<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/authStore'

const authStore = useAuthStore()

onMounted(() => {
  authStore.restoreSession()
})
</script>

<template>
  <router-view />
</template>
