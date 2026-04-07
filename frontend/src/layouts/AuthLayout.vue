<template>
  <div class="auth-shell min-h-screen overflow-hidden bg-[linear-gradient(180deg,#5a86f8_0%,#4d79ee_100%)] px-4 py-8 text-slate-900">
    <div class="auth-blob auth-blob-one"></div>
    <div class="auth-blob auth-blob-two"></div>
    <div class="auth-blob auth-blob-three"></div>
    <div class="relative z-10 mx-auto flex min-h-[calc(100vh-4rem)] max-w-7xl items-center justify-center">
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>
