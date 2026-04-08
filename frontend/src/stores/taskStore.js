import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { apiClient } from '../plugins/axios'
import { useToastStore } from './toastStore'
import { useWorkspaceStore } from './workspaceStore'

function normalizeCollection(payload) {
  return Array.isArray(payload) ? payload : (payload?.results ?? [])
}

export const useTaskStore = defineStore('taskStore', () => {
  const toastStore = useToastStore()
  const tasksByWorkspace = ref({})
  const currentTask = ref(null)
  const loading = ref(false)

  const allTasks = computed(() => Object.values(tasksByWorkspace.value).flat())

  function tasksForWorkspace(workspaceId) {
    return tasksByWorkspace.value[workspaceId] ?? []
  }

  async function fetchTasks(workspaceId) {
    loading.value = true
    try {
      const { data } = await apiClient.get(`/workspace/${workspaceId}/tasks/`)
      tasksByWorkspace.value = {
        ...tasksByWorkspace.value,
        [workspaceId]: normalizeCollection(data),
      }
      return tasksForWorkspace(workspaceId)
    } finally {
      loading.value = false
    }
  }

  async function fetchDashboardTasks(workspaces) {
    const ids = [...new Set(workspaces.map((workspace) => workspace.workspace_id))]
    await Promise.all(ids.map((workspaceId) => fetchTasks(workspaceId)))
  }

  async function fetchTask(workspaceId, taskId) {
    const { data } = await apiClient.get(`/workspace/${workspaceId}/tasks/${taskId}/`)
    currentTask.value = data
    upsertTask(workspaceId, data)
    return data
  }

  async function createTask(workspaceId, payload) {
    const { data } = await apiClient.post(`/workspace/${workspaceId}/tasks/`, payload)
    upsertTask(workspaceId, data)
    await syncWorkspaceSnapshots(workspaceId)
    toastStore.success('Task created', `Task "${data.title}" đã được tạo.`)
    return data
  }

  async function updateTask(workspaceId, taskId, payload) {
    const { data } = await apiClient.put(`/workspace/${workspaceId}/tasks/${taskId}/`, payload)
    currentTask.value = data
    upsertTask(workspaceId, data)
    await syncWorkspaceSnapshots(workspaceId)
    toastStore.success('Task updated', `Task "${data.title}" đã được cập nhật.`)
    return data
  }

  async function deleteTask(workspaceId, taskId) {
    const taskTitle = tasksForWorkspace(workspaceId).find((task) => task.id === taskId)?.title || 'Task'
    await apiClient.delete(`/workspace/${workspaceId}/tasks/${taskId}/`)
    tasksByWorkspace.value = {
      ...tasksByWorkspace.value,
      [workspaceId]: tasksForWorkspace(workspaceId).filter((task) => task.id !== taskId),
    }
    await syncWorkspaceSnapshots(workspaceId)
    toastStore.success('Task deleted', `"${taskTitle}" đã được xóa.`)
  }

  async function submitTask(workspaceId, taskId) {
    return patchTaskStatus(workspaceId, taskId, 'in_review')
  }

  async function uploadSubmission(workspaceId, taskId, file) {
    const formData = new FormData()
    formData.append('submission_file', file)

    const { data } = await apiClient.post(`/workspace/${workspaceId}/tasks/${taskId}/submission/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    currentTask.value = data
    upsertTask(workspaceId, data)
    toastStore.success('File uploaded', 'File submission đã được tải lên thành công.')
    return data
  }

  async function downloadSubmission(workspaceId, taskId, filename = 'submission-file') {
    const response = await apiClient.get(`/workspace/${workspaceId}/tasks/${taskId}/submission/download/`, {
      responseType: 'blob',
    })

    const downloadUrl = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  }

  async function approveTask(workspaceId, taskId) {
    return patchTaskStatus(workspaceId, taskId, 'done')
  }

  async function rejectTask(workspaceId, taskId) {
    return patchTaskStatus(workspaceId, taskId, 'in_progress')
  }

  async function patchTaskStatus(workspaceId, taskId, status) {
    const { data } = await apiClient.patch(`/workspace/${workspaceId}/tasks/${taskId}/status/`, { status })
    currentTask.value = data
    upsertTask(workspaceId, data)
    await syncWorkspaceSnapshots(workspaceId)
    const messages = {
      in_review: 'Task đã được gửi lên để chờ duyệt.',
      done: 'Task đã được phê duyệt hoàn thành.',
      in_progress: 'Task đã được trả lại trạng thái đang thực hiện.',
    }
    toastStore.success('Task status updated', messages[status] || 'Trạng thái task đã được cập nhật.')
    return data
  }

  function upsertTask(workspaceId, task) {
    const list = [...tasksForWorkspace(workspaceId)]
    const index = list.findIndex((item) => item.id === task.id)

    if (index === -1) {
      list.unshift(task)
    } else {
      list.splice(index, 1, { ...list[index], ...task })
    }

    tasksByWorkspace.value = {
      ...tasksByWorkspace.value,
      [workspaceId]: list,
    }
  }

  async function syncWorkspaceSnapshots(workspaceId) {
    const workspaceStore = useWorkspaceStore()
    await workspaceStore.fetchWorkspaces()
    if (workspaceStore.currentWorkspaceId === workspaceId) {
      await workspaceStore.fetchWorkspace(workspaceId)
    }
  }

  return {
    tasksByWorkspace,
    currentTask,
    loading,
    allTasks,
    tasksForWorkspace,
    fetchTasks,
    fetchDashboardTasks,
    fetchTask,
    createTask,
    updateTask,
    deleteTask,
    uploadSubmission,
    downloadSubmission,
    submitTask,
    approveTask,
    rejectTask,
  }
})
