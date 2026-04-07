<template>
  <div class="space-y-6">
    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <StatCard v-for="card in statCards" :key="card.label" :label="card.label" :value="card.value" :helper="card.helper" :tone="card.tone">
        <span class="text-2xl">{{ card.icon }}</span>
      </StatCard>
    </section>

    <section class="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
      <BaseCard>
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-3xl font-semibold text-slate-900">Task Activity</h2>
            <p class="mt-2 text-sm text-slate-500">Biến biểu đồ sales trong mockup thành xu hướng task theo workspace.</p>
          </div>
          <div class="rounded-2xl border border-slate-200 px-4 py-2 text-sm text-slate-500">This week</div>
        </div>

        <div class="mt-8 rounded-[28px] bg-[#f5f8ff] p-5">
          <div class="flex h-[300px] items-end gap-3">
            <div v-for="point in chartPoints" :key="point.label" class="flex flex-1 flex-col items-center gap-3">
              <div class="w-full rounded-t-[18px] bg-[linear-gradient(180deg,#6f97ff_0%,#4f7df0_100%)]" :style="{ height: `${point.value}%` }"></div>
              <span class="text-xs text-slate-400">{{ point.label }}</span>
            </div>
          </div>
        </div>
      </BaseCard>

      <BaseCard>
        <h2 class="text-3xl font-semibold text-slate-900">Workspace Snapshot</h2>
        <div class="mt-6 space-y-4">
          <div v-for="workspace in workspaceHighlights" :key="workspace.workspace_id" class="rounded-[24px] border border-slate-200 p-4">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-base font-semibold text-slate-900">{{ workspace.workspace_name }}</p>
                <p class="mt-1 text-sm text-slate-500">{{ workspace.description || 'Không có mô tả' }}</p>
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
          </div>
          <p v-if="!workspaceHighlights.length" class="rounded-[24px] bg-[#f7f9ff] px-4 py-6 text-sm text-slate-500">Không có workspace khớp với từ khóa tìm kiếm hiện tại.</p>
        </div>
      </BaseCard>
    </section>

    <BaseCard>
      <div class="flex items-center justify-between gap-3">
        <div>
          <h2 class="text-3xl font-semibold text-slate-900">Latest Task Activity</h2>
          <p class="mt-2 text-sm text-slate-500">Bảng deals được chuyển thành bảng task gần đây.</p>
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
              <td class="px-4 py-4 text-slate-500">{{ task.assign_to || 'Unassigned' }}</td>
              <td class="px-4 py-4 text-slate-500">{{ formatDate(task.deadline) }}</td>
              <td class="px-4 py-4"><TaskStatusBadge :status="task.status" /></td>
            </tr>
          </tbody>
        </table>
        <p v-if="!recentTasks.length" class="px-4 py-6 text-sm text-slate-500">Không có task nào khớp với từ khóa tìm kiếm hiện tại.</p>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'

import BaseCard from '../components/BaseCard.vue'
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

onMounted(async () => {
  const workspaces = await workspaceStore.fetchWorkspaces()
  await taskStore.fetchDashboardTasks(workspaces)
})

const flattenedTasks = computed(() => taskStore.allTasks)
const createdCount = computed(() => workspaceStore.workspaces.filter((workspace) => workspace.created_by === authStore.user?.id).length)
const isManagerView = computed(() => createdCount.value > 0)

const scopedTasks = computed(() => {
  if (isManagerView.value) {
    return flattenedTasks.value.filter((task) => task.assign_from === authStore.user?.id)
  }

  return flattenedTasks.value.filter((task) => task.assign_to === authStore.user?.id)
})

const statCards = computed(() => {
  const completed = scopedTasks.value.filter((task) => task.status === 'done').length
  const inReview = scopedTasks.value.filter((task) => task.status === 'in_review').length
  const workspaceCount = isManagerView.value ? createdCount.value : workspaceStore.workspaces.length

  return [
    { label: isManagerView.value ? 'Managed Workspaces' : 'Related Workspaces', value: workspaceCount, helper: isManagerView.value ? 'Workspace do bạn tạo và quản lý' : 'Workspace bạn đang tham gia', tone: 'blue', icon: '▣' },
    { label: isManagerView.value ? 'Assigned Tasks' : 'My Tasks', value: scopedTasks.value.length, helper: isManagerView.value ? 'Số task bạn đã giao cho team' : 'Số task đang được giao cho bạn', tone: 'amber', icon: '☰' },
    { label: 'Completed Tasks', value: completed, helper: 'Tổng số task đã hoàn thành', tone: 'green', icon: '✓' },
    { label: isManagerView.value ? 'Need Review' : 'Waiting Review', value: inReview, helper: isManagerView.value ? 'Task đang chờ bạn duyệt' : 'Task bạn đã gửi đang chờ duyệt', tone: 'coral', icon: '◔' },
  ]
})

const chartPoints = computed(() => {
  const values = [18, 32, 40, 55, 48, 62, 70]
  return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((label, index) => ({ label, value: values[index] + Math.min(scopedTasks.value.length * 2, 18) }))
})

const filteredTasks = computed(() => scopedTasks.value.filter((task) => matchesSearch([
  task.title,
  task.description,
  task.status,
  task.assign_to,
  workspaceName(task.workspace),
], uiStore.normalizedSearch)))

const filteredWorkspaces = computed(() => workspaceStore.workspaces.filter((workspace) => matchesSearch([
  workspace.workspace_name,
  workspace.description,
  workspace.workspace_id,
], uiStore.normalizedSearch)))

const recentTasks = computed(() => filteredTasks.value.slice(0, 6))
const workspaceHighlights = computed(() => filteredWorkspaces.value.slice(0, 3))

function workspaceName(workspaceId) {
  return workspaceStore.workspaces.find((workspace) => workspace.workspace_id === workspaceId)?.workspace_name || workspaceId
}

function formatDate(value) {
  if (!value) return 'No deadline'
  return new Date(value).toLocaleDateString('en-GB')
}
</script>
