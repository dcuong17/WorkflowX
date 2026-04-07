<template>
  <BaseCard>
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="text-3xl font-semibold text-slate-900">Workspace Members</h2>
        <p class="mt-2 text-sm text-slate-500">Danh sách member/manager trong workspace theo route động từ backend.</p>
      </div>
      <BaseButton variant="secondary" @click="router.push(`/workspaces/${id}`)">Back to Workspace</BaseButton>
    </div>

    <div class="mt-6 overflow-x-auto">
      <table class="min-w-full text-left text-sm">
        <thead>
          <tr class="bg-[#f3f6fd] text-slate-500">
            <th class="rounded-l-2xl px-4 py-3 font-medium">Membership ID</th>
            <th class="px-4 py-3 font-medium">Username</th>
            <th class="px-4 py-3 font-medium">User ID</th>
            <th class="px-4 py-3 font-medium">Role</th>
            <th class="px-4 py-3 font-medium">Joined</th>
            <th class="rounded-r-2xl px-4 py-3 font-medium">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="member in filteredMembers" :key="member.id" class="border-b border-slate-100 last:border-b-0">
            <td class="px-4 py-4 font-medium text-slate-900">{{ member.id }}</td>
            <td class="px-4 py-4 text-slate-700">{{ member.user_username || '-' }}</td>
            <td class="px-4 py-4 text-slate-500">{{ member.user }}</td>
            <td class="px-4 py-4"><span class="rounded-full px-3 py-1 text-xs font-semibold" :class="member.role === 'manager' ? 'bg-[#eef3ff] text-[#4f7df0]' : 'bg-[#e8fbf2] text-[#18b16d]'">{{ member.role }}</span></td>
            <td class="px-4 py-4 text-slate-500">{{ new Date(member.joined_at).toLocaleString('en-GB') }}</td>
            <td class="px-4 py-4"><BaseButton v-if="isManager && member.role !== 'manager'" size="sm" variant="danger" @click="workspaceStore.removeMember(id, member.id)">Remove</BaseButton></td>
          </tr>
        </tbody>
      </table>
      <p v-if="!filteredMembers.length" class="px-4 py-6 text-sm text-slate-500">Không có thành viên nào khớp với từ khóa tìm kiếm hiện tại.</p>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import { useAuthStore } from '../stores/authStore'
import { useUiStore } from '../stores/uiStore'
import { useWorkspaceStore } from '../stores/workspaceStore'
import { matchesSearch } from '../utils/search'

const props = defineProps({ id: String })
const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUiStore()
const workspaceStore = useWorkspaceStore()

onMounted(async () => {
  await workspaceStore.fetchWorkspace(props.id)
  await workspaceStore.fetchMembers(props.id)
})

const isManager = computed(() => workspaceStore.currentWorkspace?.created_by === authStore.user?.id)
const filteredMembers = computed(() => workspaceStore.members.filter((member) => matchesSearch([
  member.id,
  member.user,
  member.user_username,
  member.role,
], uiStore.normalizedSearch)))
const { id } = props
</script>
