<template>
  <Teleport to="body">
    <div class="pointer-events-none fixed right-4 top-4 z-[80] flex w-full max-w-sm flex-col gap-3 sm:right-6 sm:top-6">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toastStore.toasts"
          :key="toast.id"
          class="pointer-events-auto rounded-[24px] border bg-white/95 p-4 shadow-[0_20px_60px_rgba(15,23,42,0.14)] backdrop-blur"
          :class="toneCardClass(toast.tone)"
        >
          <div class="flex items-start gap-3">
            <div class="mt-0.5 flex h-9 w-9 items-center justify-center rounded-2xl text-lg font-semibold" :class="toneIconClass(toast.tone)">
              {{ toneIcon(toast.tone) }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-slate-900">{{ toast.title }}</p>
              <p v-if="toast.message" class="mt-1 text-sm leading-6 text-slate-500">{{ toast.message }}</p>
            </div>
            <button class="rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600" @click="toastStore.dismiss(toast.id)">
              ×
            </button>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToastStore } from '../stores/toastStore'

const toastStore = useToastStore()

function toneCardClass(tone) {
  return {
    success: 'border-emerald-100',
    warning: 'border-amber-100',
    error: 'border-red-100',
  }[tone] || 'border-slate-200'
}

function toneIconClass(tone) {
  return {
    success: 'bg-emerald-50 text-emerald-600',
    warning: 'bg-amber-50 text-amber-600',
    error: 'bg-red-50 text-red-600',
  }[tone] || 'bg-slate-100 text-slate-600'
}

function toneIcon(tone) {
  return {
    success: '✓',
    warning: '!',
    error: '×',
  }[tone] || 'i'
}
</script>
