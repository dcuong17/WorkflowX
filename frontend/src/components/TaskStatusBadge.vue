<template>
  <span class="inline-flex rounded-full px-3 py-1 text-xs font-semibold" :class="classes">
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ status: { type: String, default: 'in_progress' } })

const classes = computed(() => ({
  in_progress: 'bg-[#eef3ff] text-[#4f7df0]',
  in_review: 'bg-[#fff5e7] text-[#f59e0b]',
  done: 'bg-[#e8fbf2] text-[#13a362]',
}[props.status] ?? 'bg-[#eef3ff] text-[#4f7df0]'))

const label = computed(() => ({
  in_progress: 'In Progress',
  in_review: 'In Review',
  done: 'Done',
}[props.status] ?? props.status))
</script>
