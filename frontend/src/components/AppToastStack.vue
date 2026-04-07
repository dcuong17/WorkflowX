<template>
  <Teleport to="body">
    <div class="pointer-events-none fixed right-4 top-4 z-[80] flex w-full max-w-sm flex-col gap-3 sm:right-6 sm:top-6">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toastStore.toasts"
          :key="toast.id"
          class="pointer-events-auto rounded-[24px] border border-emerald-100 bg-white/95 p-4 shadow-[0_20px_60px_rgba(15,23,42,0.14)] backdrop-blur"
        >
          <div class="flex items-start gap-3">
            <div class="mt-0.5 flex h-9 w-9 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
              ✓
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-slate-900">{{ toast.title }}</p>
              <p v-if="toast.message" class="mt-1 text-sm leading-6 text-slate-500">{{ toast.message }}</p>
            </div>
            <button class="rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600" @click="toastStore.dismiss(toast.id)">
              ✕
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
</script>
