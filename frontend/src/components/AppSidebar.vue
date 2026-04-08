<template>
  <aside>
    <div v-if="open" class="fixed inset-0 z-30 bg-slate-950/20 lg:hidden" @click="$emit('close')"></div>
    <div :class="sidebarClasses">
      <div class="flex min-h-0 flex-1 flex-col overflow-hidden">
        <div class="flex items-center justify-between px-7 pb-8 pt-7">
          <RouterLink to="/dashboard" class="text-2xl font-bold tracking-tight text-[#4f7df0]">Workflow<span class="text-slate-900">X</span></RouterLink>
          <button class="rounded-full p-2 text-slate-500 lg:hidden" @click="$emit('close')">✕</button>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto px-4 pb-6">
          <nav class="space-y-2">
            <RouterLink
              v-for="item in navItems"
              :key="item.to"
              :to="item.to"
              class="flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition"
              :class="isActive(item.match) ? 'bg-[#4f7df0] text-white shadow-[0_18px_40px_rgba(79,125,240,0.28)]' : 'text-slate-600 hover:bg-slate-100'"
              @click="$emit('close')"
            >
              <span class="inline-flex h-9 w-9 items-center justify-center rounded-xl" :class="isActive(item.match) ? 'bg-white/15' : 'bg-slate-100'">
                {{ item.icon }}
              </span>
              <span>{{ item.label }}</span>
            </RouterLink>
          </nav>
        </div>

        <div class="shrink-0 border-t border-slate-100 px-6 py-5">
          <div class="rounded-[24px] bg-[#f4f7ff] p-4">
            <p class="text-xs uppercase tracking-[0.25em] text-slate-400">Đang đăng nhập</p>
            <p class="mt-3 break-all text-base font-semibold leading-7 text-slate-900">{{ authStore.user?.email }}</p>
            <p class="mt-1 text-sm leading-6 text-slate-500">{{ managerHint }}</p>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import { useAuthStore } from '../stores/authStore'
import { useWorkspaceStore } from '../stores/workspaceStore'

const props = defineProps({ open: Boolean })
defineEmits(['close'])

const route = useRoute()
const authStore = useAuthStore()
const workspaceStore = useWorkspaceStore()

const navItems = [
  { to: '/dashboard', label: 'Bảng điều khiển', match: '/dashboard', icon: '◫' },
  { to: '/workspaces', label: 'Workspace', match: '/workspaces', icon: '▣' },
  { to: '/tasks', label: 'Công việc', match: '/tasks', icon: '◩' },
]

const sidebarClasses = computed(() => [
  'fixed inset-y-0 left-0 z-40 flex h-screen w-[270px] flex-col overflow-hidden border-r border-slate-100 bg-white transition-transform duration-300 lg:translate-x-0',
  props.open ? 'translate-x-0' : '-translate-x-full',
].join(' '))

const managerHint = computed(() => workspaceStore.createdWorkspaceCount > 0 ? 'Có quyền quản lý workspace' : 'Đang ở chế độ thành viên')

function isActive(match) {
  return route.path.startsWith(match)
}
</script>
