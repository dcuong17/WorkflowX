<template>
  <header class="sticky top-0 z-20 border-b border-slate-200/70 bg-white/90 backdrop-blur-xl">
    <div class="flex min-h-[88px] flex-wrap items-center justify-between gap-x-4 gap-y-3 px-4 py-4 sm:px-6 lg:flex-nowrap lg:px-8">
      <div class="flex min-w-0 flex-1 items-center gap-3">
        <button class="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 text-slate-700 lg:hidden" @click="$emit('toggle-sidebar')">
          ☰
        </button>
        <div class="min-w-0">
          <p class="text-[11px] uppercase tracking-[0.3em] text-slate-400">WorkflowX</p>
          <h1 class="truncate text-2xl font-semibold leading-tight text-slate-900">{{ route.meta.title ?? 'Dashboard' }}</h1>
          <p v-if="route.meta.subtitle" class="truncate text-sm leading-6 text-slate-500">{{ route.meta.subtitle }}</p>
        </div>
      </div>

      <div class="flex w-full items-stretch justify-end gap-3 lg:w-auto lg:flex-none">
        <label class="hidden h-14 w-[340px] max-w-full items-center gap-3 rounded-2xl border border-slate-200 bg-[#f8faff] px-4 text-sm text-slate-400 xl:flex">
          <span>⌕</span>
          <input
            v-model="uiStore.searchQuery"
            type="text"
            class="w-full border-0 bg-transparent p-0 text-sm text-slate-700 outline-none placeholder:text-slate-400"
            placeholder="Search workspace or task"
          />
          <button
            v-if="uiStore.hasSearch"
            type="button"
            class="inline-flex h-8 w-8 items-center justify-center rounded-full text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
            @click="uiStore.clearSearch()"
          >
            ✕
          </button>
        </label>

        <div class="relative flex" data-header-menu>
          <button
            type="button"
            class="flex h-14 min-w-[292px] max-w-full items-center gap-3 rounded-2xl border border-slate-200 bg-white px-3 text-left shadow-sm transition hover:border-[#4f7df0]/30 hover:bg-[#fbfcff]"
            @click="toggleMenu"
          >
            <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#eef3ff] font-semibold text-[#4f7df0]">
              {{ initials }}
            </div>
            <div class="min-w-0 flex-1 pr-1 text-left">
              <p class="truncate text-sm font-medium leading-5 text-slate-900">{{ authStore.user?.email }}</p>
              <p class="text-xs leading-5 text-slate-500">{{ workspaceStore.createdWorkspaceCount > 0 ? 'Manager' : 'Member' }}</p>
            </div>
            <span class="text-xs text-slate-400">{{ menuOpen ? '▲' : '▼' }}</span>
          </button>

          <div v-if="menuOpen" class="absolute right-0 top-[calc(100%+0.75rem)] z-30 w-56 rounded-[22px] border border-slate-200 bg-white p-2 shadow-[0_20px_50px_rgba(15,23,42,0.12)]">
            <button type="button" class="flex w-full items-center justify-between rounded-2xl px-4 py-3 text-left text-sm text-slate-700 transition hover:bg-[#f6f9ff]" @click="goToProfile">
              <span>View profile</span>
              <span>→</span>
            </button>
            <button type="button" class="mt-1 flex w-full items-center justify-between rounded-2xl px-4 py-3 text-left text-sm text-[#d64b4b] transition hover:bg-[#fff5f5]" @click="handleLogout">
              <span>Logout</span>
              <span>↗</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '../stores/authStore'
import { useUiStore } from '../stores/uiStore'
import { useWorkspaceStore } from '../stores/workspaceStore'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUiStore()
const workspaceStore = useWorkspaceStore()
const menuOpen = ref(false)

defineEmits(['toggle-sidebar'])

const initials = computed(() => {
  const email = authStore.user?.email ?? 'WX'
  return email.slice(0, 2).toUpperCase()
})

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}

function handleOutsideClick(event) {
  if (!(event.target instanceof HTMLElement)) return
  if (event.target.closest('[data-header-menu]')) return
  menuOpen.value = false
}

function goToProfile() {
  menuOpen.value = false
  router.push('/profile')
}

async function handleLogout() {
  menuOpen.value = false
  await authStore.signOut()
  uiStore.clearSearch()
  router.push('/login')
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
})
</script>
