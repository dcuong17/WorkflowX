<template>
  <div v-if="taskStore.currentTask && workspaceStore.currentWorkspace" class="space-y-6">
    <BaseCard>
      <div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div class="flex items-center gap-3">
            <TaskStatusBadge :status="taskStore.currentTask.status" />
            <h2 class="text-4xl font-semibold text-slate-900">{{ taskStore.currentTask.title }}</h2>
          </div>
          <p class="mt-4 max-w-3xl text-sm leading-7 text-slate-500">{{ taskStore.currentTask.description || 'Task chưa có mô tả chi tiết.' }}</p>
        </div>
        <BaseButton variant="secondary" @click="router.push(`/workspaces/${id}`)">Quay lại workspace</BaseButton>
      </div>

      <div class="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div class="rounded-[24px] bg-[#f7f9ff] p-5"><p class="text-sm text-slate-400">Workspace</p><p class="mt-2 text-lg font-semibold text-slate-900">{{ workspaceStore.currentWorkspace.workspace_name }}</p></div>
        <div class="rounded-[24px] bg-[#f7f9ff] p-5"><p class="text-sm text-slate-400">Người nhận</p><p class="mt-2 break-all text-lg font-semibold text-slate-900">{{ displayUser(taskStore.currentTask.assign_to_username, taskStore.currentTask.assign_to, 'Chưa giao') }}</p></div>
        <div class="rounded-[24px] bg-[#f7f9ff] p-5"><p class="text-sm text-slate-400">Người giao</p><p class="mt-2 break-all text-lg font-semibold text-slate-900">{{ displayUser(taskStore.currentTask.assign_from_username, taskStore.currentTask.assign_from, 'Không xác định') }}</p></div>
        <div class="rounded-[24px] bg-[#f7f9ff] p-5"><p class="text-sm text-slate-400">Hạn chót</p><p class="mt-2 text-lg font-semibold text-slate-900">{{ taskStore.currentTask.deadline ? new Date(taskStore.currentTask.deadline).toLocaleString('vi-VN') : 'Không có hạn chót' }}</p></div>
      </div>
    </BaseCard>

    <BaseCard>
      <h3 class="text-2xl font-semibold text-slate-900">Thao tác workflow của task</h3>
      <div class="mt-6 rounded-[24px] bg-[#f7f9ff] p-5">
        <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p class="text-sm font-medium text-slate-700">Submission file</p>
            <p class="mt-2 text-sm text-slate-500">
              {{ taskStore.currentTask.submission_file_name || 'Chưa có file đính kèm' }}
            </p>
          </div>
          <button v-if="taskStore.currentTask.submission_file_name" type="button" @click="handleDownload" class="inline-flex items-center rounded-2xl bg-white px-4 py-2 text-sm font-medium text-slate-700 ring-1 ring-slate-200 hover:bg-slate-50">
            Xem file
          </button>
        </div>

        <form v-if="canUploadSubmission" class="mt-5 space-y-3" @submit.prevent="handleUpload">
          <input ref="submissionInput" type="file" accept=".doc,.docx,.xls,.xlsx" class="app-input" @change="handleFileChange" />
          <p class="text-xs text-slate-400">Chỉ chấp nhận file Word hoặc Excel. Thành viên phải tải file lên trước khi gửi duyệt.</p>
          <p v-if="uploadError" class="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-600">{{ uploadError }}</p>
          <div class="flex justify-end">
            <BaseButton type="submit" :disabled="!selectedFile" :loading="uploading">Tải bài nộp lên</BaseButton>
          </div>
        </form>
      </div>

      <div class="mt-6 flex flex-wrap gap-3">
        <BaseButton v-if="canSubmit" @click="taskStore.submitTask(id, task_id)">Gửi duyệt</BaseButton>
        <BaseButton v-if="canApprove" @click="taskStore.approveTask(id, task_id)">Phê duyệt</BaseButton>
        <BaseButton v-if="canReject" variant="secondary" @click="taskStore.rejectTask(id, task_id)">Từ chối</BaseButton>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import TaskStatusBadge from '../components/TaskStatusBadge.vue'
import { useAuthStore } from '../stores/authStore'
import { useTaskStore } from '../stores/taskStore'
import { useWorkspaceStore } from '../stores/workspaceStore'

const props = defineProps({ id: String, task_id: String })
const router = useRouter()
const authStore = useAuthStore()
const taskStore = useTaskStore()
const workspaceStore = useWorkspaceStore()
const selectedFile = ref(null)
const submissionInput = ref(null)
const uploadError = ref('')
const uploading = ref(false)

onMounted(async () => {
  await Promise.all([
    workspaceStore.fetchWorkspace(props.id),
    workspaceStore.fetchMembers(props.id),
    taskStore.fetchTask(props.id, props.task_id),
  ])
})

const isManager = computed(() => workspaceStore.currentWorkspace?.created_by === authStore.user?.id)
const canUploadSubmission = computed(() => !isManager.value && taskStore.currentTask?.status === 'in_progress' && taskStore.currentTask?.assign_to === authStore.user?.id)
const canSubmit = computed(() => !isManager.value && taskStore.currentTask?.status === 'in_progress' && taskStore.currentTask?.assign_to === authStore.user?.id && Boolean(taskStore.currentTask?.submission_file_name || taskStore.currentTask?.submission_file_url))
const canApprove = computed(() => isManager.value && taskStore.currentTask?.status === 'in_review')
const canReject = computed(() => isManager.value && taskStore.currentTask?.status === 'in_review')

const { id, task_id } = props

function handleFileChange(event) {
  selectedFile.value = event.target.files?.[0] ?? null
}

function displayUser(username, fallbackId, empty = 'Không xác định') {
  if (username) return username
  if (fallbackId === authStore.user?.id) {
    return authStore.user?.username || fallbackId || empty
  }
  return workspaceStore.memberDirectory[fallbackId] || fallbackId || empty
}

async function handleUpload() {
  if (!selectedFile.value) return

  uploadError.value = ''
  uploading.value = true
  try {
    await taskStore.uploadSubmission(id, task_id, selectedFile.value)
    selectedFile.value = null
    if (submissionInput.value) {
      submissionInput.value.value = ''
    }
  } catch (error) {
    uploadError.value = error.response?.data?.submission_file?.[0] || 'Không thể tải file lên.'
  } finally {
    uploading.value = false
  }
}

async function handleDownload() {
  const filename = taskStore.currentTask?.submission_file_name || 'submission-file'
  await taskStore.downloadSubmission(id, task_id, filename)
}
</script>
