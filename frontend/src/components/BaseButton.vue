<template>
  <button :type="type" :class="classes" :disabled="disabled || loading">
    <span v-if="loading" class="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/50 border-t-white"></span>
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: { type: String, default: 'button' },
  variant: { type: String, default: 'primary' },
  size: { type: String, default: 'md' },
  disabled: Boolean,
  loading: Boolean,
  block: Boolean,
})

const classes = computed(() => {
  const base = 'inline-flex items-center justify-center rounded-2xl font-medium transition focus:outline-none focus:ring-2 focus:ring-[#4f7df0]/50 disabled:cursor-not-allowed disabled:opacity-60'
  const variants = {
    primary: 'bg-[#4f7df0] text-white shadow-[0_12px_30px_rgba(79,125,240,0.28)] hover:bg-[#3c6de7]',
    secondary: 'bg-white text-slate-700 ring-1 ring-slate-200 hover:bg-slate-50',
    soft: 'bg-[#eef3ff] text-[#4f7df0] hover:bg-[#e2ebff]',
    danger: 'bg-[#fff1f1] text-[#d64b4b] hover:bg-[#ffe2e2]',
  }
  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-3 text-sm',
    lg: 'px-5 py-3.5 text-base',
  }

  return [base, variants[props.variant], sizes[props.size], props.block ? 'w-full' : ''].join(' ')
})
</script>
