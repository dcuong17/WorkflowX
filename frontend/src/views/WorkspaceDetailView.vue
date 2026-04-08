<template>
  <div class="space-y-6" v-if="workspaceStore.currentWorkspace">
    <section class="grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">
      <BaseCard>
        <div class="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p class="text-sm uppercase tracking-[0.28em] text-[#4f7df0]">Workspace overview</p>
            <h2 class="mt-3 text-4xl font-semibold text-slate-900">{{ workspaceStore.currentWorkspace.workspace_name }}</h2>
            <p class="mt-3 max-w-2xl text-sm leading-7 text-slate-500">{{ workspaceStore.currentWorkspace.description || 'Workspace này đang chờ bạn bổ sung mô tả.' }}</p>
          </div>
          <div class="flex flex-wrap gap-3">
            <BaseButton v-if="isManager" variant="secondary" @click="showEditModal = true">Edit</BaseButton>
            <BaseButton v-if="isManager" variant="danger" @click="handleDeleteWorkspace">Delete</BaseButton>
            <BaseButton variant="soft" @click="router.push(`/workspaces/${id}/members`)">Members</BaseButton>
          </div>
        </div>

        <div class="mt-6 grid gap-4 md:grid-cols-3">
          <div class="rounded-[24px] bg-[#f7f9ff] p-5"><p class="text-sm text-slate-400">Members</p><p class="mt-2 text-3xl font-semibold text-slate-900">{{ workspaceStore.members.length }}</p></div>
          <div class="rounded-[24px] bg-[#f7f9ff] p-5"><p class="text-sm text-slate-400">Tasks</p><p class="mt-2 text-3xl font-semibold text-slate-900">{{ visibleTasks.length }}</p></div>
          <div class="rounded-[24px] bg-[#f7f9ff] p-5"><p class="text-sm text-slate-400">Completed</p><p class="mt-2 text-3xl font-semibold text-slate-900">{{ completedTasks }}</p></div>
        </div>
      </BaseCard>

      <BaseCard>
        <h2 class="text-2xl font-semibold text-slate-900">Action Center</h2>
        <div class="mt-5 space-y-3">
          <BaseButton v-if="isManager" block @click="openAddMemberModal">Add Member</BaseButton>
          <BaseButton v-if="isManager" block variant="secondary" @click="showTaskModal = true">Create Task</BaseButton>
          <BaseButton block variant="soft" @click="refreshWorkspace">Refresh Data</BaseButton>
        </div>
        <div class="mt-6 rounded-[24px] bg-[#f7f9ff] p-4 text-sm text-slate-500">
          <p class="font-medium text-slate-700">Current role in this workspace</p>
          <p class="mt-2">{{ isManager ? 'Manager: có thể tạo task, thêm thành viên, duyệt bài.' : 'Member: chỉ thấy task được giao và có thể submit khi hoàn thành.' }}</p>
        </div>
      </BaseCard>
    </section>

    <BaseCard>
      <div class="flex items-center justify-between gap-3">
        <div>
          <h2 class="text-3xl font-semibold text-slate-900">Task Board</h2>
          <p class="mt-2 text-sm text-slate-500">Danh sách task theo đúng flow manager/member từ backend.</p>
        </div>
        <TaskStatusBadge :status="pendingBadgeStatus" />
      </div>

      <div class="mt-6 space-y-4">
        <article v-for="task in visibleTasks" :key="task.id" class="rounded-[24px] border border-slate-200 px-5 py-5 transition hover:border-[#4f7df0]/30 hover:bg-[#fbfcff]">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div class="flex items-center gap-3">
                <TaskStatusBadge :status="task.status" />
                <RouterLink :to="`/workspaces/${id}/tasks/${task.id}`" class="text-xl font-semibold text-slate-900 hover:text-[#4f7df0]">{{ task.title }}</RouterLink>
              </div>
              <p class="mt-3 max-w-3xl text-sm leading-7 text-slate-500">{{ task.description || 'Task chưa có mô tả.' }}</p>
              <div class="mt-4 flex flex-wrap gap-3 text-xs text-slate-400">
                <span class="rounded-full bg-slate-100 px-3 py-1">Người nhận: {{ displayUser(task.assign_to_username, task.assign_to, 'Chưa giao') }}</span>
                <span class="rounded-full bg-slate-100 px-3 py-1">Hạn chót: {{ task.deadline ? new Date(task.deadline).toLocaleDateString('vi-VN') : 'Không có hạn chót' }}</span>
              </div>
            </div>

            <div class="flex flex-wrap gap-2 lg:max-w-[320px] lg:justify-end">
              <BaseButton v-if="canSubmit(task)" size="sm" @click="handleSubmitTask(task.id)">Submit</BaseButton>
              <RouterLink v-else-if="canUpload(task)" :to="`/workspaces/${id}/tasks/${task.id}`" class="inline-flex items-center justify-center rounded-2xl bg-[#eef3ff] px-3 py-2 text-sm font-medium text-[#4f7df0] transition hover:bg-[#e2ebff]">
                Upload File
              </RouterLink>
              <BaseButton v-if="canApprove(task)" size="sm" @click="handleApproveTask(task.id)">Approve</BaseButton>
              <BaseButton v-if="canReject(task)" size="sm" variant="secondary" @click="handleRejectTask(task.id)">Reject</BaseButton>
              <BaseButton v-if="isManager" size="sm" variant="soft" @click="openEditTask(task)">Edit</BaseButton>
              <BaseButton v-if="isManager" size="sm" variant="danger" @click="handleDeleteTask(task.id)">Delete</BaseButton>
            </div>
          </div>
        </article>
        <p v-if="!visibleTasks.length" class="rounded-[24px] bg-[#f7f9ff] px-4 py-6 text-sm text-slate-500">Không có task nào khớp với từ khóa tìm kiếm hiện tại.</p>
      </div>
    </BaseCard>

    <ModalShell v-if="showAddMemberModal" title="Add member" description="Chọn user trong hệ thống để thêm vào workspace" @close="closeAddMemberModal">
      <form class="space-y-4" @submit.prevent="handleAddMember">
        <label class="block text-sm font-medium text-slate-600">
          Select user
          <select v-model="memberForm.user" required class="app-input mt-2 appearance-none bg-[right_1rem_center] bg-no-repeat pr-10" style="background-image: url(&quot;data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 20 20' fill='none'%3E%3Cpath d='M5 7.5L10 12.5L15 7.5' stroke='%2394A3B8' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E&quot;);">
            <option value="">Choose a member</option>
            <option v-for="user in selectableUsers" :key="user.id" :value="user.id">
              {{ user.username || user.email }}
            </option>
          </select>
        </label>
        <p v-if="selectedCandidate" class="rounded-[20px] bg-[#f7f9ff] px-4 py-3 text-sm text-slate-500">
          Selected user: <span class="font-medium text-slate-900">{{ selectedCandidate.username || selectedCandidate.id }}</span>
        </p>
        <p v-if="memberError" class="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-600">{{ memberError }}</p>
        <div class="flex justify-end gap-3"><BaseButton variant="secondary" @click="closeAddMemberModal">Cancel</BaseButton><BaseButton type="submit">Add Member</BaseButton></div>
      </form>
    </ModalShell>

    <ModalShell v-if="showTaskModal" :title="editingTaskId ? 'Edit task' : 'Create task'" description="Manager có thể giao task cho member thuộc workspace" @close="closeTaskModal">
      <form class="space-y-4" @submit.prevent="handleSaveTask">
        <label class="block text-sm font-medium text-slate-600">Title<input v-model="taskForm.title" maxlength="50" required class="app-input mt-2" /></label>
        <label class="block text-sm font-medium text-slate-600">Description<textarea v-model="taskForm.description" rows="4" class="app-input mt-2"></textarea></label>
        <div class="grid gap-4 sm:grid-cols-2">
          <label class="block text-sm font-medium text-slate-600">Assign to member<select v-model="taskForm.assign_to" class="app-input mt-2"><option value="">Assign later</option><option v-for="member in memberOnlyOptions" :key="member.id" :value="member.user">{{ member.user_username || member.user_email || member.user }}</option></select></label>
          <label class="block text-sm font-medium text-slate-600">Deadline<input v-model="taskForm.deadline" type="datetime-local" class="app-input mt-2" /></label>
        </div>
        <p class="text-xs text-slate-400">Task có thể tạo trước khi có member. Sau đó bạn có thể dùng Edit để gán lại cho member bất kỳ trong workspace.</p>
        <p v-if="taskError" class="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-600">{{ taskError }}</p>
        <div class="flex justify-end gap-3"><BaseButton variant="secondary" @click="closeTaskModal">Cancel</BaseButton><BaseButton type="submit">{{ editingTaskId ? 'Save Changes' : 'Create Task' }}</BaseButton></div>
      </form>
    </ModalShell>

    <ModalShell v-if="showEditModal" title="Edit workspace" description="Cập nhật tên và mô tả workspace" @close="showEditModal = false">
      <form class="space-y-4" @submit.prevent="handleUpdateWorkspace">
        <label class="block text-sm font-medium text-slate-600">Workspace name<input v-model="workspaceForm.workspace_name" required class="app-input mt-2" /></label>
        <label class="block text-sm font-medium text-slate-600">Description<textarea v-model="workspaceForm.description" rows="4" class="app-input mt-2"></textarea></label>
        <div class="flex justify-end gap-3"><BaseButton variant="secondary" @click="showEditModal = false">Cancel</BaseButton><BaseButton type="submit">Update Workspace</BaseButton></div>
      </form>
    </ModalShell>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import ModalShell from '../components/ModalShell.vue'
import TaskStatusBadge from '../components/TaskStatusBadge.vue'
import { useAuthStore } from '../stores/authStore'
import { useTaskStore } from '../stores/taskStore'
import { useToastStore } from '../stores/toastStore'
import { useUiStore } from '../stores/uiStore'
import { useWorkspaceStore } from '../stores/workspaceStore'
import { matchesSearch } from '../utils/search'

const props = defineProps({ id: String })
const router = useRouter()
const authStore = useAuthStore()
const workspaceStore = useWorkspaceStore()
const taskStore = useTaskStore()
const toastStore = useToastStore()
const uiStore = useUiStore()

const showAddMemberModal = ref(false)
const showTaskModal = ref(false)
const showEditModal = ref(false)
const editingTaskId = ref('')
const memberError = ref('')
const taskError = ref('')

const memberForm = reactive({ user: '' })
const workspaceForm = reactive({ workspace_name: '', description: '' })
const taskForm = reactive({ title: '', description: '', assign_to: '', deadline: '' })

onMounted(refreshWorkspace)
watch(() => props.id, refreshWorkspace)
watch(() => workspaceStore.currentWorkspace, (workspace) => {
  if (!workspace) return
  workspaceForm.workspace_name = workspace.workspace_name
  workspaceForm.description = workspace.description
}, { immediate: true })

const isManager = computed(() => workspaceStore.currentWorkspace?.created_by === authStore.user?.id)
const workspaceTasks = computed(() => taskStore.tasksForWorkspace(props.id))
const visibleTasks = computed(() => {
  const scopedTasks = isManager.value ? workspaceTasks.value : workspaceTasks.value.filter((task) => task.assign_to === authStore.user?.id)

  return scopedTasks.filter((task) => matchesSearch([
    task.title,
    task.description,
    task.status,
    task.assign_to,
    task.assign_to_username,
    task.assign_from,
    task.assign_from_username,
  ], uiStore.normalizedSearch))
})
const completedTasks = computed(() => visibleTasks.value.filter((task) => task.status === 'done').length)
const pendingBadgeStatus = computed(() => visibleTasks.value.some((task) => task.status === 'in_review') ? 'in_review' : 'in_progress')
const memberOnlyOptions = computed(() => workspaceStore.members.filter((member) => member.role === 'member'))
const selectableUsers = computed(() => workspaceStore.availableUsers.filter((user) => user.username || user.email))
const selectedCandidate = computed(() => selectableUsers.value.find((user) => user.id === memberForm.user) ?? null)

async function refreshWorkspace() {
  try {
    await Promise.all([workspaceStore.fetchWorkspace(props.id), workspaceStore.fetchMembers(props.id), taskStore.fetchTasks(props.id)])
  } catch (error) {
    const message = error.response?.status === 404
      ? 'Workspace này không còn tồn tại.'
      : 'Không thể tải dữ liệu workspace.'
    toastStore.warning('Không thể mở workspace', message)
    router.push('/workspaces')
  }
}

const canSubmit = (task) => !isManager.value && task.status === 'in_progress' && task.assign_to === authStore.user?.id && Boolean(task.submission_file_name || task.submission_file_url)
const canUpload = (task) => !isManager.value && task.status === 'in_progress' && task.assign_to === authStore.user?.id && !task.submission_file_name && !task.submission_file_url
const canApprove = (task) => isManager.value && task.status === 'in_review'
const canReject = (task) => isManager.value && task.status === 'in_review'

async function handleAddMember() {
  memberError.value = ''
  try {
    await workspaceStore.addMember(props.id, memberForm.user)
    await workspaceStore.fetchAvailableUsers(props.id)
    closeAddMemberModal()
  } catch (error) {
    memberError.value = error.response?.data?.user?.[0] || error.response?.data?.non_field_errors?.[0] || 'Không thể thêm member.'
  }
}

async function openAddMemberModal() {
  memberError.value = ''
  memberForm.user = ''
  await workspaceStore.fetchAvailableUsers(props.id)
  showAddMemberModal.value = true
}

function closeAddMemberModal() {
  memberError.value = ''
  memberForm.user = ''
  showAddMemberModal.value = false
}

async function handleSaveTask() {
  taskError.value = ''
  const payload = {
    title: taskForm.title,
    description: taskForm.description,
    assign_to: taskForm.assign_to,
    deadline: taskForm.deadline ? new Date(taskForm.deadline).toISOString() : null,
  }

  try {
    if (editingTaskId.value) {
      await taskStore.updateTask(props.id, editingTaskId.value, payload)
    } else {
      await taskStore.createTask(props.id, payload)
    }
    closeTaskModal()
  } catch (error) {
    taskError.value = error.response?.data?.assign_to?.[0] || error.response?.data?.title?.[0] || 'Không thể lưu task.'
  }
}

function openEditTask(task) {
  editingTaskId.value = task.id
  taskForm.title = task.title
  taskForm.description = task.description
  taskForm.assign_to = task.assign_to
  taskForm.deadline = task.deadline ? new Date(task.deadline).toISOString().slice(0, 16) : ''
  showTaskModal.value = true
}

function closeTaskModal() {
  editingTaskId.value = ''
  taskError.value = ''
  taskForm.title = ''
  taskForm.description = ''
  taskForm.assign_to = ''
  taskForm.deadline = ''
  showTaskModal.value = false
}

async function handleUpdateWorkspace() {
  await workspaceStore.updateWorkspace(props.id, workspaceForm)
  showEditModal.value = false
}

async function handleDeleteWorkspace() {
  await workspaceStore.deleteWorkspace(props.id)
  router.push('/workspaces')
}

function displayUser(username, fallbackId, empty = 'Không xác định') {
  if (username) return username
  if (fallbackId === authStore.user?.id) {
    return authStore.user?.username || fallbackId || empty
  }
  return workspaceStore.memberDirectory[fallbackId] || fallbackId || empty
}

async function handleDeleteTask(taskId) { await taskStore.deleteTask(props.id, taskId) }
async function handleSubmitTask(taskId) { await taskStore.submitTask(props.id, taskId) }
async function handleApproveTask(taskId) { await taskStore.approveTask(props.id, taskId) }
async function handleRejectTask(taskId) { await taskStore.rejectTask(props.id, taskId) }
</script>
