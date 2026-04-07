<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 px-4 py-6 backdrop-blur-sm" @click.self="$emit('close')">
      <div class="w-full max-w-xl rounded-[28px] bg-white p-6 shadow-[0_30px_80px_rgba(15,23,42,0.25)] sm:p-7">
        <div class="mb-5 flex items-start justify-between gap-4">
          <div>
            <h3 class="text-2xl font-semibold text-slate-900">{{ title }}</h3>
            <p v-if="description" class="mt-1 text-sm text-slate-500">{{ description }}</p>
          </div>
          <button class="rounded-full p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700" @click="$emit('close')">✕</button>
        </div>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({ title: String, description: String })
defineEmits(['close'])
</script>
