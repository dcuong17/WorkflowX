<template>
  <BaseCard class="h-full min-h-[146px] w-full">
    <div class="flex h-full items-start justify-between gap-4">
      <div class="flex min-h-[90px] flex-1 flex-col">
        <p class="text-sm text-slate-400">{{ label }}</p>
        <p class="mt-2 text-3xl font-semibold text-slate-900">{{ value }}</p>
        <p class="mt-auto pt-3 text-sm" :class="trendColor">{{ helper }}</p>
      </div>
      <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl" :class="iconBg">
        <slot />
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import BaseCard from './BaseCard.vue'

const props = defineProps({
  label: String,
  value: [String, Number],
  helper: String,
  tone: { type: String, default: 'blue' },
})

const palettes = {
  blue: { iconBg: 'bg-[#edf3ff] text-[#4f7df0]', trend: 'text-[#4f7df0]' },
  green: { iconBg: 'bg-[#ebfbf3] text-[#18b16d]', trend: 'text-[#18b16d]' },
  amber: { iconBg: 'bg-[#fff5e8] text-[#f59e0b]', trend: 'text-[#f59e0b]' },
  coral: { iconBg: 'bg-[#fff1ef] text-[#f9736a]', trend: 'text-[#f9736a]' },
  purple: { iconBg: 'bg-[#f4efff] text-[#7c4dff]', trend: 'text-[#7c4dff]' },
}

const iconBg = computed(() => palettes[props.tone]?.iconBg ?? palettes.blue.iconBg)
const trendColor = computed(() => palettes[props.tone]?.trend ?? palettes.blue.trend)
</script>
