<template>
  <div class="space-y-6">
    <BaseCard>
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p class="text-sm uppercase tracking-[0.28em] text-[#4f7df0]">Danh mục task</p>
          <h2 class="mt-3 text-4xl font-semibold text-slate-900">Task theo workspace</h2>
          <p class="mt-3 max-w-2xl text-sm leading-7 text-slate-500">
            Chọn một workspace để xem toàn bộ task, trạng thái hiện tại và thao tác nhanh ngay trên danh sách.
          </p>
        </div>

        <div class="w-full max-w-md lg:w-[360px]">
          <label class="block text-sm font-medium text-slate-600">
            Workspace
            <select
              v-model="selectedWorkspaceId"
              class="app-input mt-2 appearance-none bg-[right_1rem_center] bg-no-repeat pr-10"
              style="background-image: url(&quot;data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 20 20' fill='none'%3E%3Cpath d='M5 7.5L10 12.5L15 7.5' stroke='%2394A3B8' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E&quot;);"
            >
              <option value="">Chọn workspace</option>
              <option
                v-for="workspace in workspaceStore.workspaces"
                :key="workspace.workspace_id"
                :value="workspace.workspace_id"
              >
                {{ workspace.workspace_name }}
              </option>
            </select>
          </label>
        </div>
      </div>
    </BaseCard>

    <BaseCard v-if="selectedWorkspace">
      <div class="grid gap-4 md:grid-cols-3">
        <div class="rounded-[24px] bg-[#f7f9ff] p-5">
          <p class="text-sm text-slate-400">Workspace</p>
          <p class="mt-2 text-2xl font-semibold text-slate-900">{{ selectedWorkspace.workspace_name }}</p>
        </div>
        <div class="rounded-[24px] bg-[#f7f9ff] p-5">
          <p class="text-sm text-slate-400">Task đang hiển thị</p>
          <p class="mt-2 text-2xl font-semibold text-slate-900">{{ visibleTasks.length }}</p>
        </div>
        <div class="rounded-[24px] bg-[#f7f9ff] p-5">
          <p class="text-sm text-slate-400">Đang chờ duyệt</p>
          <p class="mt-2 text-2xl font-semibold text-slate-900">
            {{ visibleTasks.filter((task) => task.status === 'in_review').length }}
          </p>
        </div>
      </div>
    </BaseCard>

    <div v-if="selectedWorkspace" class="space-y-4">
      <article
        v-for="task in visibleTasks"
        :key="task.id"
        class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-[0_18px_50px_rgba(40,66,120,0.08)]"
      >
        <div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-3">
              <TaskStatusBadge :status="task.status" />
              <RouterLink
                :to="`/workspaces/${selectedWorkspaceId}/tasks/${task.id}`"
                class="text-2xl font-semibold text-slate-900 hover:text-[#4f7df0]"
              >
                {{ task.title }}
              </RouterLink>
            </div>

            <p class="mt-3 max-w-3xl text-sm leading-7 text-slate-500">
              {{ task.description || 'Task chưa có mô tả.' }}
            </p>

            <div class="mt-4 flex flex-wrap gap-3 text-xs text-slate-400">
              <span class="rounded-full bg-slate-100 px-3 py-1">
                Người nhận: {{ displayUser(task.assign_to_username, task.assign_to, 'Chưa giao') }}
              </span>
              <span class="rounded-full bg-slate-100 px-3 py-1">
                Người giao: {{ displayUser(task.assign_from_username, task.assign_from, 'Không xác định') }}
              </span>
              <span class="rounded-full bg-slate-100 px-3 py-1">Hạn chót: {{ formatDate(task.deadline) }}</span>
            </div>

            <div class="mt-5 rounded-[22px] bg-[#f7f9ff] p-4">
              <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p class="text-sm font-medium text-slate-700">Tệp bài nộp</p>
                  <p class="mt-1 text-sm text-slate-500">{{ task.submission_file_name || 'Chưa có file đính kèm' }}</p>
                </div>
                <button
                  v-if="task.submission_file_name"
                  type="button"
                  @click="handleDownload(task)"
                  class="inline-flex items-center justify-center rounded-2xl bg-white px-4 py-2 text-sm font-medium text-slate-700 ring-1 ring-slate-200 hover:bg-slate-50"
                >
                  Xem file
                </button>
              </div>

              <form v-if="canUpload(task)" class="mt-4 space-y-3" @submit.prevent="handleInlineUpload(task.id)">
                <input
                  :ref="(el) => setFileInputRef(task.id, el)"
                  type="file"
                  accept=".doc,.docx,.xls,.xlsx"
                  class="app-input"
                  @change="handleInlineFileChange(task.id, $event)"
                />
                <p class="text-xs text-slate-400">Chỉ chấp nhận file Word hoặc Excel.</p>
                <p
                  v-if="uploadErrors[task.id]"
                  class="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-600"
                >
                  {{ uploadErrors[task.id] }}
                </p>
                <div class="flex justify-end">
                  <BaseButton
                    type="submit"
                    :disabled="!selectedFiles[task.id]"
                    :loading="uploadingTaskIds[task.id]"
                  >
                    Tải file lên
                  </BaseButton>
                </div>
              </form>
            </div>
          </div>

          <div class="flex flex-wrap gap-2 lg:max-w-[340px] lg:justify-end">
            <BaseButton v-if="canSubmit(task)" size="sm" @click="handleSubmit(task.id)">Nộp duyệt</BaseButton>
            <BaseButton v-if="canApprove(task)" size="sm" @click="handleApprove(task.id)">Phê duyệt</BaseButton>
            <BaseButton v-if="canReject(task)" size="sm" variant="secondary" @click="handleReject(task.id)">Từ chối</BaseButton>
            <RouterLink
              :to="`/workspaces/${selectedWorkspaceId}/tasks/${task.id}`"
              class="inline-flex items-center justify-center rounded-2xl bg-[#eef3ff] px-3 py-2 text-sm font-medium text-[#4f7df0] transition hover:bg-[#e2ebff]"
            >
              Mở chi tiết
            </RouterLink>
          </div>
        </div>
      </article>

      <BaseCard v-if="!visibleTasks.length" class="text-center text-sm text-slate-500">
        Không có task nào khớp với workspace hoặc từ khóa tìm kiếm hiện tại.
      </BaseCard>
    </div>

    <BaseCard v-else class="text-center text-sm text-slate-500">
      Chọn một workspace để xem danh sách task.
    </BaseCard>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import TaskStatusBadge from '../components/TaskStatusBadge.vue'
import { useAuthStore } from '../stores/authStore'
import { useTaskStore } from '../stores/taskStore'
import { useUiStore } from '../stores/uiStore'
import { useWorkspaceStore } from '../stores/workspaceStore'
import { matchesSearch } from '../utils/search'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const taskStore = useTaskStore()
const uiStore = useUiStore()
const workspaceStore = useWorkspaceStore()

const selectedWorkspaceId = ref('')
const selectedFiles = reactive({})
const fileInputRefs = reactive({})
const uploadErrors = reactive({})
const uploadingTaskIds = reactive({})

onMounted(async () => {
  await workspaceStore.fetchWorkspaces()
  initializeWorkspaceSelection()
})

watch(() => route.query.workspace, (workspaceId) => {
  if (workspaceId && workspaceId !== selectedWorkspaceId.value) {
    selectedWorkspaceId.value = String(workspaceId)
  }
})

watch(selectedWorkspaceId, async (workspaceId) => {
  if (!workspaceId) return

  if (route.query.workspace !== workspaceId) {
    router.replace({ path: '/tasks', query: { workspace: workspaceId } })
  }

  await Promise.all([
    taskStore.fetchTasks(workspaceId),
    workspaceStore.fetchMembers(workspaceId),
  ])
})

const selectedWorkspace = computed(() => workspaceStore.workspaces.find((workspace) => workspace.workspace_id === selectedWorkspaceId.value) ?? null)
const isManagerView = computed(() => selectedWorkspace.value?.created_by === authStore.user?.id)
const workspaceTasks = computed(() => selectedWorkspaceId.value ? taskStore.tasksForWorkspace(selectedWorkspaceId.value) : [])
const visibleTasks = computed(() => {
  const scopedTasks = isManagerView.value
    ? workspaceTasks.value
    : workspaceTasks.value.filter((task) => task.assign_to === authStore.user?.id)

  return scopedTasks.filter((task) => matchesSearch([
    task.title,
    task.description,
    task.status,
    task.assign_to,
    task.assign_to_username,
    task.assign_from,
    task.assign_from_username,
    displayUser(task.assign_to_username, task.assign_to, ''),
    displayUser(task.assign_from_username, task.assign_from, ''),
  ], uiStore.normalizedSearch))
})

function initializeWorkspaceSelection() {
  const routeWorkspace = String(route.query.workspace ?? '')
  if (routeWorkspace && workspaceStore.workspaces.some((workspace) => workspace.workspace_id === routeWorkspace)) {
    selectedWorkspaceId.value = routeWorkspace
    return
  }

  selectedWorkspaceId.value = workspaceStore.workspaces[0]?.workspace_id ?? ''
}

function displayUser(username, fallbackId, empty = 'Không xác định') {
  if (username) return username
  if (fallbackId === authStore.user?.id) {
    return authStore.user?.username || fallbackId || empty
  }
  return workspaceStore.memberDirectory[fallbackId] || fallbackId || empty
}

function canUpload(task) {
  return !isManagerView.value && task.status === 'in_progress' && task.assign_to === authStore.user?.id && !task.submission_file_name && !task.submission_file_url
}

function canSubmit(task) {
  return !isManagerView.value && task.status === 'in_progress' && task.assign_to === authStore.user?.id && Boolean(task.submission_file_name || task.submission_file_url)
}

function canApprove(task) {
  return isManagerView.value && task.status === 'in_review'
}

function canReject(task) {
  return isManagerView.value && task.status === 'in_review'
}

function formatDate(value) {
  if (!value) return 'Không có hạn chót'
  return new Date(value).toLocaleDateString('vi-VN')
}

function setFileInputRef(taskId, element) {
  if (element) {
    fileInputRefs[taskId] = element
  }
}

function handleInlineFileChange(taskId, event) {
  selectedFiles[taskId] = event.target.files?.[0] ?? null
}

async function handleInlineUpload(taskId) {
  const file = selectedFiles[taskId]
  if (!file || !selectedWorkspaceId.value) return

  uploadErrors[taskId] = ''
  uploadingTaskIds[taskId] = true
  try {
    await taskStore.uploadSubmission(selectedWorkspaceId.value, taskId, file)
    selectedFiles[taskId] = null
    if (fileInputRefs[taskId]) {
      fileInputRefs[taskId].value = ''
    }
  } catch (error) {
    uploadErrors[taskId] = error.response?.data?.submission_file?.[0] || 'Không thể tải file lên.'
  } finally {
    uploadingTaskIds[taskId] = false
  }
}

async function handleSubmit(taskId) {
  if (!selectedWorkspaceId.value) return
  await taskStore.submitTask(selectedWorkspaceId.value, taskId)
}

async function handleApprove(taskId) {
  if (!selectedWorkspaceId.value) return
  await taskStore.approveTask(selectedWorkspaceId.value, taskId)
}

async function handleReject(taskId) {
  if (!selectedWorkspaceId.value) return
  await taskStore.rejectTask(selectedWorkspaceId.value, taskId)
}

async function handleDownload(task) {
  if (!selectedWorkspaceId.value) return
  const filename = task.submission_file_name || 'submission-file'
  await taskStore.downloadSubmission(selectedWorkspaceId.value, task.id, filename)
}
</script>
