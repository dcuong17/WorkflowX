<template>
  <div class="space-y-6">
    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
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
          <h2 class="text-3xl font-semibold text-slate-900">Tổng quan workspace</h2>
          <p class="mt-2 text-sm text-slate-500">Chọn một workspace để đi thẳng tới không gian làm việc tương ứng.</p>
        </div>
        <p class="rounded-2xl bg-[#f5f8ff] px-4 py-3 text-sm text-slate-500">
          {{ workspaceHighlights.length }} workspace đang hiển thị theo bộ lọc hiện tại
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
              <p class="mt-1 text-sm text-slate-500">{{ workspace.description || 'Không có mô tả' }}</p>
              <p class="mt-2 text-xs uppercase tracking-[0.2em] text-slate-400">Người tạo: {{ creatorName(workspace) }}</p>
            </div>
            <TaskStatusBadge :status="workspace.completed_tasks === workspace.total_tasks && workspace.total_tasks > 0 ? 'done' : 'in_progress'" />
          </div>
          <div class="mt-4 grid grid-cols-2 gap-3 text-sm">
            <div class="rounded-2xl bg-[#f8faff] p-3">
              <p class="text-slate-400">Tổng task</p>
              <p class="mt-2 text-lg font-semibold text-slate-900">{{ workspace.total_tasks }}</p>
            </div>
            <div class="rounded-2xl bg-[#f8faff] p-3">
              <p class="text-slate-400">Hoàn thành</p>
              <p class="mt-2 text-lg font-semibold text-slate-900">{{ workspace.completed_tasks }}</p>
            </div>
          </div>
        </button>
      </div>

      <p v-if="!workspaceHighlights.length" class="mt-6 rounded-[24px] bg-[#f7f9ff] px-4 py-6 text-sm text-slate-500">
        Không có workspace khớp với từ khóa tìm kiếm hiện tại.
      </p>
    </BaseCard>

    <BaseCard>
      <div class="flex items-center justify-between gap-3">
        <div>
          <h2 class="text-3xl font-semibold text-slate-900">Hoạt động task gần đây</h2>
          <p class="mt-2 text-sm text-slate-500">Bảng task gần đây để bạn rà nhanh tiến độ hiện tại.</p>
        </div>
      </div>

      <div class="mt-6 overflow-x-auto">
        <table class="min-w-full text-left text-sm">
          <thead>
            <tr class="bg-[#f3f6fd] text-slate-500">
              <th class="rounded-l-2xl px-4 py-3 font-medium">Tên task</th>
              <th class="px-4 py-3 font-medium">Workspace</th>
              <th class="px-4 py-3 font-medium">Người nhận</th>
              <th class="px-4 py-3 font-medium">Hạn chót</th>
              <th class="rounded-r-2xl px-4 py-3 font-medium">Trạng thái</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="task in recentTasks"
              :key="task.id"
              class="cursor-pointer border-b border-slate-100 transition hover:bg-[#fbfcff] last:border-b-0"
              @click="openTask(task)"
            >
              <td class="px-4 py-4 font-medium text-slate-900">{{ task.title }}</td>
              <td class="px-4 py-4 text-slate-500">{{ workspaceName(task.workspace) }}</td>
              <td class="px-4 py-4 text-slate-500">{{ displayUser(task.assign_to_username, task.assign_to, 'Chưa giao') }}</td>
              <td class="px-4 py-4 text-slate-500">{{ formatDate(task.deadline) }}</td>
              <td class="px-4 py-4"><TaskStatusBadge :status="task.status" /></td>
            </tr>
          </tbody>
        </table>
        <p v-if="!recentTasks.length" class="px-4 py-6 text-sm text-slate-500">Không có task nào khớp với từ khóa tìm kiếm hiện tại.</p>
      </div>
    </BaseCard>

    <ModalShell v-if="activeModal" :title="activeModal.title" :description="activeModal.description" @close="activeModalType = ''">
      <div class="max-h-[65vh] space-y-4 overflow-y-auto pr-2">
        <template v-if="activeModalType === 'workspaces'">
          <div class="space-y-4">
            <div v-if="createdWorkspaces.length">
              <p class="text-sm font-semibold uppercase tracking-[0.22em] text-slate-400">Bạn tạo</p>
              <button
                v-for="workspace in createdWorkspaces"
                :key="workspace.workspace_id"
                type="button"
                class="mt-3 block w-full rounded-[22px] border border-slate-200 p-4 text-left transition hover:border-[#4f7df0]/30 hover:bg-[#fbfcff]"
                @click="openWorkspace(workspace.workspace_id)"
              >
                <p class="text-base font-semibold text-slate-900">{{ workspace.workspace_name }}</p>
                <p class="mt-1 text-sm text-slate-500">Người tạo: {{ creatorName(workspace) }}</p>
                <p class="mt-1 text-sm text-slate-500">{{ workspace.description || 'Không có mô tả' }}</p>
              </button>
            </div>

            <div v-if="joinedWorkspaces.length">
              <p class="text-sm font-semibold uppercase tracking-[0.22em] text-slate-400">Đang tham gia</p>
              <button
                v-for="workspace in joinedWorkspaces"
                :key="workspace.workspace_id"
                type="button"
                class="mt-3 block w-full rounded-[22px] border border-slate-200 p-4 text-left transition hover:border-[#4f7df0]/30 hover:bg-[#fbfcff]"
                @click="openWorkspace(workspace.workspace_id)"
              >
                <p class="text-base font-semibold text-slate-900">{{ workspace.workspace_name }}</p>
                <p class="mt-1 text-sm text-slate-500">Người tạo: {{ creatorName(workspace) }}</p>
                <p class="mt-1 text-sm text-slate-500">{{ workspace.description || 'Không có mô tả' }}</p>
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
                <p class="mt-1 text-sm text-slate-500">Người nhận: {{ displayUser(task.assign_to_username, task.assign_to, 'Chưa giao') }}</p>
              </div>
              <TaskStatusBadge :status="task.status" />
            </div>
          </button>
        </template>

        <p v-if="activeModal.empty" class="rounded-[22px] bg-[#f7f9ff] px-4 py-6 text-sm text-slate-500">Không có dữ liệu phù hợp để hiển thị.</p>
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
import { useToastStore } from '../stores/toastStore'
import { useUiStore } from '../stores/uiStore'
import { useWorkspaceStore } from '../stores/workspaceStore'
import { matchesSearch } from '../utils/search'

const authStore = useAuthStore()
const workspaceStore = useWorkspaceStore()
const taskStore = useTaskStore()
const toastStore = useToastStore()
const uiStore = useUiStore()
const router = useRouter()

const activeModalType = ref('')

onMounted(async () => {
  const workspaces = await workspaceStore.fetchWorkspaces()
  await Promise.all(workspaces.map((workspace) => workspaceStore.fetchMembers(workspace.workspace_id)))
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
  displayUser(task.assign_to_username, task.assign_to, ''),
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
const recentTasks = computed(() => taskStore.combinedRecentTasks
  .filter((task) => matchesSearch([
    task.title,
    task.description,
    task.status,
    task.assign_to,
    task.assign_to_username,
    displayUser(task.assign_to_username, task.assign_to, ''),
    workspaceName(task.workspace, task.workspace_name_snapshot),
  ], uiStore.normalizedSearch))
  .slice(0, 6))
const workspaceHighlights = computed(() => filteredWorkspaces.value.slice(0, 6))
const myAssignedTasks = computed(() => filteredTasks.value.filter((task) => task.assign_to === authStore.user?.id))

const statCards = computed(() => {
  const completed = completedTaskList.value.length
  const inReview = reviewTaskList.value.length
  const workspaceCount = isManagerView.value ? createdCount.value : workspaceStore.workspaces.length
  const taskLabel = assignedByMeTasks.value.length > 0 && assignedToMeTasks.value.length > 0
    ? 'Task liên quan'
    : (assignedByMeTasks.value.length > 0 ? 'Task đã giao' : 'Task của tôi')
  const taskHelper = assignedByMeTasks.value.length > 0 && assignedToMeTasks.value.length > 0
    ? 'Tổng task bạn giao hoặc được giao'
    : (assignedByMeTasks.value.length > 0 ? 'Số task bạn đã giao cho team' : 'Số task đang được giao cho bạn')
  const reviewLabel = assignedByMeTasks.value.length > 0 && assignedToMeTasks.value.length > 0
    ? 'Hàng chờ duyệt'
    : (assignedByMeTasks.value.length > 0 ? 'Cần duyệt' : 'Đang chờ duyệt')
  const reviewHelper = assignedByMeTasks.value.length > 0 && assignedToMeTasks.value.length > 0
    ? 'Task liên quan đang ở trạng thái chờ duyệt'
    : (assignedByMeTasks.value.length > 0 ? 'Task đang chờ bạn duyệt' : 'Task bạn đã gửi đang chờ duyệt')

  return [
    { type: 'workspaces', label: isManagerView.value ? 'Workspace quản lý' : 'Workspace liên quan', value: workspaceCount, helper: isManagerView.value ? 'Workspace do bạn tạo và quản lý' : 'Workspace bạn đang tham gia', tone: 'blue', icon: '?' },
    { type: 'assigned', label: taskLabel, value: relatedTasks.value.length, helper: taskHelper, tone: 'amber', icon: '?' },
    { type: 'my-assigned', label: 'Task giao cho tôi', value: assignedToMeTasks.value.length, helper: 'Task đang và đã được giao trực tiếp cho bạn', tone: 'purple', icon: '?' },
    { type: 'completed', label: 'Task hoàn thành', value: completed, helper: 'Tổng số task đã hoàn thành', tone: 'green', icon: '?' },
    { type: 'review', label: reviewLabel, value: inReview, helper: reviewHelper, tone: 'coral', icon: '?' },
  ]
})

const activeModal = computed(() => {
  const modalMap = {
    workspaces: {
      title: isManagerView.value ? 'Workspace quản lý và tham gia' : 'Workspace của bạn',
      description: 'Danh sách workspace bạn tạo hoặc đang tham gia.',
      empty: createdWorkspaces.value.length + joinedWorkspaces.value.length === 0,
    },
    assigned: {
      title: assignedByMeTasks.value.length > 0 && assignedToMeTasks.value.length > 0 ? 'Task liên quan' : (assignedByMeTasks.value.length > 0 ? 'Task đã giao' : 'Task của tôi'),
      description: 'Danh sách task trong phạm vi làm việc hiện tại của bạn.',
      items: filteredTasks.value,
      empty: filteredTasks.value.length === 0,
    },
    'my-assigned': {
      title: 'Task giao cho bạn',
      description: 'Danh sách task đang và đã được giao trực tiếp cho tài khoản hiện tại.',
      items: myAssignedTasks.value,
      empty: myAssignedTasks.value.length === 0,
    },
    completed: {
      title: 'Task hoàn thành',
      description: 'Các task đã hoàn thành trong phạm vi dashboard hiện tại.',
      items: filteredTasks.value.filter((task) => task.status === 'done'),
      empty: filteredTasks.value.filter((task) => task.status === 'done').length === 0,
    },
    review: {
      title: assignedByMeTasks.value.length > 0 && assignedToMeTasks.value.length > 0 ? 'Hàng chờ duyệt' : (assignedByMeTasks.value.length > 0 ? 'Cần duyệt' : 'Đang chờ duyệt'),
      description: 'Các task đang ở trạng thái chờ duyệt.',
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
  if (task.workspace_missing || task.isArchivedWorkspaceActivity) {
    toastStore.warning('Workspace không còn tồn tại', `Workspace gốc của task "${task.title}" đã bị xóa khỏi hệ thống.`)
    return
  }
  router.push(`/workspaces/${task.workspace}/tasks/${task.id}`)
}

function openWorkspace(workspaceId) {
  activeModalType.value = ''
  router.push(`/workspaces/${workspaceId}`)
}

function workspaceName(workspaceId, fallbackName = '') {
  return workspaceStore.workspaces.find((workspace) => workspace.workspace_id === workspaceId)?.workspace_name || fallbackName || workspaceId
}

function displayUser(username, fallbackId, empty = 'Không xác định') {
  if (username) return username
  if (fallbackId === authStore.user?.id) {
    return authStore.user?.username || fallbackId || empty
  }
  return workspaceStore.memberDirectory[fallbackId] || fallbackId || empty
}

function creatorName(workspace) {
  if (workspace.created_by === authStore.user?.id) {
    return displayUser(authStore.user?.username, workspace.created_by, authStore.user?.email || workspace.created_by)
  }
  return displayUser(workspace.created_by_username, workspace.created_by)
}

function formatDate(value) {
  if (!value) return 'Không có hạn chót'
  return new Date(value).toLocaleDateString('vi-VN')
}
</script>
