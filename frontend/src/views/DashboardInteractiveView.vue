<template>
  <div class="space-y-6">
    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <button
        v-for="card in statCards"
        :key="card.label"
        type="button"
        class="text-left transition hover:-translate-y-0.5"
        @click="openCardModal(card.type)"
      >
        <StatCard :label="card.label" :value="card.value" :helper="card.helper" :tone="card.tone">
          <span class="text-2xl">{{ card.icon }}</span>
        </StatCard>
      </button>
    </section>

    <BaseCard>
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-3xl font-semibold text-slate-900">Workspace Snapshot</h2>
          <p class="mt-2 text-sm text-slate-500">Chon mot workspace de di thang toi khong gian lam viec tuong ung.</p>
        </div>
        <p class="rounded-2xl bg-[#f5f8ff] px-4 py-3 text-sm text-slate-500">
          {{ workspaceHighlights.length }} workspace dang hien thi theo bo loc hien tai
        </p>
      </div>

      <div class="mt-6 grid gap-4 xl:grid-cols-3">
        <button
          v-for="workspace in workspaceHighlights"
          :key="workspace.workspace_id"
          type="button"
          class="block w-full rounded-[24px] border border-slate-200 p-4 text-left transition hover:border-[#4f7df0]/30 hover:bg-[#fbfcff]"
          @click="router.push(`/workspaces/${workspace.workspace_id}`)"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-base font-semibold text-slate-900">{{ workspace.workspace_name }}</p>
              <p class="mt-1 text-sm text-slate-500">{{ workspace.description || 'Khong co mo ta' }}</p>
              <p class="mt-2 text-xs uppercase tracking-[0.2em] text-slate-400">Creator: {{ creatorName(workspace) }}</p>
            </div>
            <TaskStatusBadge :status="workspace.completed_tasks === workspace.total_tasks && workspace.total_tasks > 0 ? 'done' : 'in_progress'" />
          </div>
          <div class="mt-4 grid grid-cols-2 gap-3 text-sm">
            <div class="rounded-2xl bg-[#f8faff] p-3">
              <p class="text-slate-400">Total Tasks</p>
              <p class="mt-2 text-lg font-semibold text-slate-900">{{ workspace.total_tasks }}</p>
            </div>
            <div class="rounded-2xl bg-[#f8faff] p-3">
              <p class="text-slate-400">Completed</p>
              <p class="mt-2 text-lg font-semibold text-slate-900">{{ workspace.completed_tasks }}</p>
            </div>
          </div>
        </button>
      </div>

      <p v-if="!workspaceHighlights.length" class="mt-6 rounded-[24px] bg-[#f7f9ff] px-4 py-6 text-sm text-slate-500">
        Khong co workspace khop voi tu khoa tim kiem hien tai.
      </p>
    </BaseCard>

    <BaseCard>
      <div class="flex items-center justify-between gap-3">
        <div>
          <h2 class="text-3xl font-semibold text-slate-900">Latest Task Activity</h2>
          <p class="mt-2 text-sm text-slate-500">Bang task gan day de ban ra nhanh tien do hien tai.</p>
        </div>
      </div>

      <div class="mt-6 overflow-x-auto">
        <table class="min-w-full text-left text-sm">
          <thead>
            <tr class="bg-[#f3f6fd] text-slate-500">
              <th class="rounded-l-2xl px-4 py-3 font-medium">Task</th>
              <th class="px-4 py-3 font-medium">Workspace</th>
              <th class="px-4 py-3 font-medium">Assignee</th>
              <th class="px-4 py-3 font-medium">Deadline</th>
              <th class="rounded-r-2xl px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in recentTasks" :key="task.id" class="border-b border-slate-100 last:border-b-0">
              <td class="px-4 py-4 font-medium text-slate-900">{{ task.title }}</td>
              <td class="px-4 py-4 text-slate-500">{{ workspaceName(task.workspace) }}</td>
              <td class="px-4 py-4 text-slate-500">{{ task.assign_to_username || task.assign_to || 'Unassigned' }}</td>
              <td class="px-4 py-4 text-slate-500">{{ formatDate(task.deadline) }}</td>
              <td class="px-4 py-4"><TaskStatusBadge :status="task.status" /></td>
            </tr>
          </tbody>
        </table>
        <p v-if="!recentTasks.length" class="px-4 py-6 text-sm text-slate-500">Khong co task nao khop voi tu khoa tim kiem hien tai.</p>
      </div>
    </BaseCard>

    <ModalShell v-if="activeModal" :title="activeModal.title" :description="activeModal.description" @close="activeModalType = ''">
      <div class="max-h-[65vh] space-y-4 overflow-y-auto pr-2">
        <template v-if="activeModalType === 'workspaces'">
          <div class="space-y-4">
            <div v-if="createdWorkspaces.length">
              <p class="text-sm font-semibold uppercase tracking-[0.22em] text-slate-400">Created by you</p>
              <button
                v-for="workspace in createdWorkspaces"
                :key="workspace.workspace_id"
                type="button"
                class="mt-3 block w-full rounded-[22px] border border-slate-200 p-4 text-left transition hover:border-[#4f7df0]/30 hover:bg-[#fbfcff]"
                @click="openWorkspace(workspace.workspace_id)"
              >
                <p class="text-base font-semibold text-slate-900">{{ workspace.workspace_name }}</p>
                <p class="mt-1 text-sm text-slate-500">Creator: {{ creatorName(workspace) }}</p>
                <p class="mt-1 text-sm text-slate-500">{{ workspace.description || 'Khong co mo ta' }}</p>
              </button>
            </div>

            <div v-if="joinedWorkspaces.length">
              <p class="text-sm font-semibold uppercase tracking-[0.22em] text-slate-400">Joined workspaces</p>
              <button
                v-for="workspace in joinedWorkspaces"
                :key="workspace.workspace_id"
                type="button"
                class="mt-3 block w-full rounded-[22px] border border-slate-200 p-4 text-left transition hover:border-[#4f7df0]/30 hover:bg-[#fbfcff]"
                @click="openWorkspace(workspace.workspace_id)"
              >
                <p class="text-base font-semibold text-slate-900">{{ workspace.workspace_name }}</p>
                <p class="mt-1 text-sm text-slate-500">Creator: {{ creatorName(workspace) }}</p>
                <p class="mt-1 text-sm text-slate-500">{{ workspace.description || 'Khong co mo ta' }}</p>
              </button>
            </div>
          </div>
        </template>

        <template v-else>
          <button
            v-for="task in activeModal.items"
            :key="task.id"
            type="button"
            class="block w-full rounded-[22px] border border-slate-200 p-4 text-left transition hover:border-[#4f7df0]/30 hover:bg-[#fbfcff]"
            @click="openTask(task)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="text-base font-semibold text-slate-900">{{ task.title }}</p>
                <p class="mt-1 text-sm text-slate-500">Workspace: {{ workspaceName(task.workspace) }}</p>
                <p class="mt-1 text-sm text-slate-500">Assignee: {{ task.assign_to_username || task.assign_to || 'Unassigned' }}</p>
              </div>
              <TaskStatusBadge :status="task.status" />
            </div>
          </button>
        </template>

        <p v-if="activeModal.empty" class="rounded-[22px] bg-[#f7f9ff] px-4 py-6 text-sm text-slate-500">Khong co du lieu phu hop de hien thi.</p>
      </div>
    </ModalShell>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import BaseCard from '../components/BaseCard.vue'
import ModalShell from '../components/ModalShell.vue'
import StatCard from '../components/StatCard.vue'
import TaskStatusBadge from '../components/TaskStatusBadge.vue'
import { useAuthStore } from '../stores/authStore'
import { useTaskStore } from '../stores/taskStore'
import { useUiStore } from '../stores/uiStore'
import { useWorkspaceStore } from '../stores/workspaceStore'
import { matchesSearch } from '../utils/search'

const authStore = useAuthStore()
const workspaceStore = useWorkspaceStore()
const taskStore = useTaskStore()
const uiStore = useUiStore()
const router = useRouter()

const activeModalType = ref('')

onMounted(async () => {
  const workspaces = await workspaceStore.fetchWorkspaces()
  await taskStore.fetchDashboardTasks(workspaces)
})

const flattenedTasks = computed(() => taskStore.allTasks)
const createdCount = computed(() => workspaceStore.workspaces.filter((workspace) => workspace.created_by === authStore.user?.id).length)
const assignedByMeTasks = computed(() => flattenedTasks.value.filter((task) => task.assign_from === authStore.user?.id))
const assignedToMeTasks = computed(() => flattenedTasks.value.filter((task) => task.assign_to === authStore.user?.id))
const relatedTasks = computed(() => {
  const uniqueTasks = new Map()

  for (const task of [...assignedByMeTasks.value, ...assignedToMeTasks.value]) {
    uniqueTasks.set(task.id, task)
  }

  return [...uniqueTasks.values()]
})
const isManagerView = computed(() => createdCount.value > 0 && assignedToMeTasks.value.length === 0)

const completedTaskList = computed(() => relatedTasks.value.filter((task) => task.status === 'done'))
const reviewTaskList = computed(() => relatedTasks.value.filter((task) => task.status === 'in_review'))

const filteredTasks = computed(() => relatedTasks.value.filter((task) => matchesSearch([
  task.title,
  task.description,
  task.status,
  task.assign_to,
  task.assign_to_username,
  workspaceName(task.workspace),
], uiStore.normalizedSearch)))

const filteredWorkspaces = computed(() => workspaceStore.workspaces.filter((workspace) => matchesSearch([
  workspace.workspace_name,
  workspace.description,
  workspace.workspace_id,
  creatorName(workspace),
], uiStore.normalizedSearch)))

const createdWorkspaces = computed(() => filteredWorkspaces.value.filter((workspace) => workspace.created_by === authStore.user?.id))
const joinedWorkspaces = computed(() => filteredWorkspaces.value.filter((workspace) => workspace.created_by !== authStore.user?.id))
const recentTasks = computed(() => filteredTasks.value.slice(0, 6))
const workspaceHighlights = computed(() => filteredWorkspaces.value.slice(0, 6))

const statCards = computed(() => {
  const completed = completedTaskList.value.length
  const inReview = reviewTaskList.value.length
  const workspaceCount = isManagerView.value ? createdCount.value : workspaceStore.workspaces.length
  const taskLabel = assignedByMeTasks.value.length > 0 && assignedToMeTasks.value.length > 0
    ? 'Related Tasks'
    : (assignedByMeTasks.value.length > 0 ? 'Assigned Tasks' : 'My Tasks')
  const taskHelper = assignedByMeTasks.value.length > 0 && assignedToMeTasks.value.length > 0
    ? 'Tong task ban giao hoac duoc giao'
    : (assignedByMeTasks.value.length > 0 ? 'So task ban da giao cho team' : 'So task dang duoc giao cho ban')
  const reviewLabel = assignedByMeTasks.value.length > 0 && assignedToMeTasks.value.length > 0
    ? 'Review Queue'
    : (assignedByMeTasks.value.length > 0 ? 'Need Review' : 'Waiting Review')
  const reviewHelper = assignedByMeTasks.value.length > 0 && assignedToMeTasks.value.length > 0
    ? 'Task lien quan dang o trang thai cho duyet'
    : (assignedByMeTasks.value.length > 0 ? 'Task dang cho ban duyet' : 'Task ban da gui dang cho duyet')

  return [
    { type: 'workspaces', label: isManagerView.value ? 'Managed Workspaces' : 'Related Workspaces', value: workspaceCount, helper: isManagerView.value ? 'Workspace do ban tao va quan ly' : 'Workspace ban dang tham gia', tone: 'blue', icon: '?' },
    { type: 'assigned', label: taskLabel, value: relatedTasks.value.length, helper: taskHelper, tone: 'amber', icon: '?' },
    { type: 'completed', label: 'Completed Tasks', value: completed, helper: 'Tong so task da hoan thanh', tone: 'green', icon: '?' },
    { type: 'review', label: reviewLabel, value: inReview, helper: reviewHelper, tone: 'coral', icon: '?' },
  ]
})

const activeModal = computed(() => {
  const modalMap = {
    workspaces: {
      title: isManagerView.value ? 'Managed & Joined Workspaces' : 'Your Workspaces',
      description: 'Danh sach workspace ban tao hoac dang tham gia.',
      empty: createdWorkspaces.value.length + joinedWorkspaces.value.length === 0,
    },
    assigned: {
      title: assignedByMeTasks.value.length > 0 && assignedToMeTasks.value.length > 0 ? 'Related Tasks' : (assignedByMeTasks.value.length > 0 ? 'Assigned Tasks' : 'My Tasks'),
      description: 'Danh sach task trong pham vi lam viec hien tai cua ban.',
      items: filteredTasks.value,
      empty: filteredTasks.value.length === 0,
    },
    completed: {
      title: 'Completed Tasks',
      description: 'Cac task da hoan thanh trong dashboard scope hien tai.',
      items: filteredTasks.value.filter((task) => task.status === 'done'),
      empty: filteredTasks.value.filter((task) => task.status === 'done').length === 0,
    },
    review: {
      title: assignedByMeTasks.value.length > 0 && assignedToMeTasks.value.length > 0 ? 'Review Queue' : (assignedByMeTasks.value.length > 0 ? 'Need Review' : 'Waiting Review'),
      description: 'Cac task dang o trang thai cho duyet.',
      items: filteredTasks.value.filter((task) => task.status === 'in_review'),
      empty: filteredTasks.value.filter((task) => task.status === 'in_review').length === 0,
    },
  }

  return modalMap[activeModalType.value] ?? null
})

function openCardModal(type) {
  activeModalType.value = type
}

function openTask(task) {
  activeModalType.value = ''
  router.push(`/workspaces/${task.workspace}/tasks/${task.id}`)
}

function openWorkspace(workspaceId) {
  activeModalType.value = ''
  router.push(`/workspaces/${workspaceId}`)
}

function workspaceName(workspaceId) {
  return workspaceStore.workspaces.find((workspace) => workspace.workspace_id === workspaceId)?.workspace_name || workspaceId
}

function creatorName(workspace) {
  if (workspace.created_by === authStore.user?.id) {
    return authStore.user?.username || authStore.user?.email || workspace.created_by
  }
  return workspace.created_by_username || workspace.created_by
}

function formatDate(value) {
  if (!value) return 'No deadline'
  return new Date(value).toLocaleDateString('en-GB')
}
</script>
