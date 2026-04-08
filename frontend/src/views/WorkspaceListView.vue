<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-4 rounded-[30px] bg-white p-6 shadow-[0_18px_50px_rgba(40,66,120,0.08)] lg:flex-row lg:items-center lg:justify-between">
      <div>
        <h2 class="text-3xl font-semibold text-slate-900">Danh sách workspace</h2>
        <p class="mt-2 text-sm text-slate-500">Danh sách workspace theo dạng thẻ để bạn theo dõi nhanh.</p>
      </div>
      <BaseButton @click="showCreateModal = true">Tạo workspace</BaseButton>
    </div>

    <div class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
      <RouterLink v-for="workspace in filteredWorkspaces" :key="workspace.workspace_id" :to="`/workspaces/${workspace.workspace_id}`" class="group">
        <BaseCard>
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-2xl font-semibold text-slate-900">{{ workspace.workspace_name }}</p>
              <p class="mt-2 line-clamp-2 text-sm leading-6 text-slate-500">{{ workspace.description || 'Workspace chưa có mô tả.' }}</p>
            </div>
            <div class="rounded-2xl bg-[#eef3ff] px-3 py-2 text-sm font-medium text-[#4f7df0] group-hover:bg-[#4f7df0] group-hover:text-white">Mở</div>
          </div>

          <div class="mt-6 grid grid-cols-2 gap-3 text-sm">
            <div class="rounded-2xl bg-[#f6f9ff] p-4">
              <p class="text-slate-400">Total Tasks</p>
              <p class="mt-2 text-lg font-semibold text-slate-900">{{ workspace.total_tasks }}</p>
            </div>
            <div class="rounded-2xl bg-[#f6f9ff] p-4">
              <p class="text-slate-400">Completed</p>
              <p class="mt-2 text-lg font-semibold text-slate-900">{{ workspace.completed_tasks }}</p>
            </div>
          </div>
        </BaseCard>
      </RouterLink>
    </div>
    <BaseCard v-if="!filteredWorkspaces.length" class="text-center text-sm text-slate-500">
      Không có workspace nào khớp với từ khóa tìm kiếm hiện tại.
    </BaseCard>

    <ModalShell v-if="showCreateModal" title="Tạo workspace mới" description="Tạo workspace mới theo đúng flow backend" @close="showCreateModal = false">
      <form class="space-y-4" @submit.prevent="handleCreate">
        <label class="block text-sm font-medium text-slate-600">Tên workspace<input v-model="workspaceForm.workspace_name" required class="app-input mt-2" /></label>
        <label class="block text-sm font-medium text-slate-600">Mô tả<textarea v-model="workspaceForm.description" rows="4" class="app-input mt-2"></textarea></label>
        <p v-if="errorMessage" class="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-600">{{ errorMessage }}</p>
        <div class="flex justify-end gap-3">
          <BaseButton variant="secondary" @click="showCreateModal = false">Hủy</BaseButton>
          <BaseButton type="submit">Tạo workspace</BaseButton>
        </div>
      </form>
    </ModalShell>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'

import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import ModalShell from '../components/ModalShell.vue'
import { useUiStore } from '../stores/uiStore'
import { useWorkspaceStore } from '../stores/workspaceStore'
import { matchesSearch } from '../utils/search'

const workspaceStore = useWorkspaceStore()
const uiStore = useUiStore()
const showCreateModal = ref(false)
const errorMessage = ref('')
const workspaceForm = reactive({ workspace_name: '', description: '' })

onMounted(() => {
  workspaceStore.fetchWorkspaces()
})

const filteredWorkspaces = computed(() => workspaceStore.workspaces.filter((workspace) => matchesSearch([
  workspace.workspace_name,
  workspace.description,
  workspace.workspace_id,
], uiStore.normalizedSearch)))

async function handleCreate() {
  errorMessage.value = ''
  try {
    await workspaceStore.createWorkspace(workspaceForm)
    workspaceForm.workspace_name = ''
    workspaceForm.description = ''
    showCreateModal.value = false
  } catch (error) {
    errorMessage.value = error.response?.data?.workspace_name?.[0] || 'Không thể tạo workspace.'
  }
}
</script>
