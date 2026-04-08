import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { apiClient } from '../plugins/axios'
import { useToastStore } from './toastStore'
import { useWorkspaceStore } from './workspaceStore'

const ARCHIVE_STORAGE_PREFIX = 'workflowx_deleted_task_activity_'

function normalizeCollection(payload) {
  return Array.isArray(payload) ? payload : (payload?.results ?? [])
}

export const useTaskStore = defineStore('taskStore', () => {
  const toastStore = useToastStore()
  const tasksByWorkspace = ref({})
  const currentTask = ref(null)
  const loading = ref(false)
  const deletedWorkspaceActivity = ref(loadDeletedWorkspaceActivity())

  const allTasks = computed(() => Object.values(tasksByWorkspace.value).flat())
  const combinedRecentTasks = computed(() => {
    const archived = deletedWorkspaceActivity.value.map((task) => ({
      ...task,
      isArchivedWorkspaceActivity: true,
    }))

    const active = allTasks.value.map((task) => ({
      ...task,
      isArchivedWorkspaceActivity: false,
    }))

    return [...active, ...archived].sort((left, right) => {
      const leftTime = new Date(left.updated_at || left.created_at || 0).getTime()
      const rightTime = new Date(right.updated_at || right.created_at || 0).getTime()
      return rightTime - leftTime
    })
  })

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
    pruneDeletedWorkspaceActivity(ids)
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
    toastStore.success('Tạo task thành công', `Task "${data.title}" đã được tạo.`)
    return data
  }

  async function updateTask(workspaceId, taskId, payload) {
    const { data } = await apiClient.put(`/workspace/${workspaceId}/tasks/${taskId}/`, payload)
    currentTask.value = data
    upsertTask(workspaceId, data)
    await syncWorkspaceSnapshots(workspaceId)
    toastStore.success('Cập nhật task thành công', `Task "${data.title}" đã được cập nhật.`)
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
    toastStore.success('Xóa task thành công', `"${taskTitle}" đã được xóa.`)
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
    toastStore.success('Tải file thành công', 'File bài nộp đã được tải lên thành công.')
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
    toastStore.success('Cập nhật trạng thái task', messages[status] || 'Trạng thái task đã được cập nhật.')
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

  function archiveDeletedWorkspaceTasks(workspaceId, workspaceName) {
    const snapshot = tasksForWorkspace(workspaceId)
    if (!snapshot.length) {
      clearWorkspaceTasks(workspaceId)
      return
    }

    const archived = snapshot.map((task) => ({
      ...task,
      workspace: workspaceId,
      workspace_name_snapshot: workspaceName,
      workspace_missing: true,
      archived_at: new Date().toISOString(),
    }))

    const merged = [...archived, ...deletedWorkspaceActivity.value.filter((task) => task.workspace !== workspaceId)]
      .reduce((collection, task) => {
        if (!collection.some((item) => item.id === task.id)) {
          collection.push(task)
        }
        return collection
      }, [])

    deletedWorkspaceActivity.value = merged
    persistDeletedWorkspaceActivity()
    clearWorkspaceTasks(workspaceId)
  }

  function pruneDeletedWorkspaceActivity(activeWorkspaceIds = []) {
    const activeSet = new Set(activeWorkspaceIds)
    deletedWorkspaceActivity.value = deletedWorkspaceActivity.value.filter((task) => !activeSet.has(task.workspace))
    persistDeletedWorkspaceActivity()
  }

  function clearWorkspaceTasks(workspaceId) {
    const nextState = { ...tasksByWorkspace.value }
    delete nextState[workspaceId]
    tasksByWorkspace.value = nextState

    if (currentTask.value?.workspace === workspaceId) {
      currentTask.value = null
    }
  }

  async function syncWorkspaceSnapshots(workspaceId) {
    const workspaceStore = useWorkspaceStore()
    await workspaceStore.fetchWorkspaces()
    if (workspaceStore.currentWorkspaceId === workspaceId) {
      await workspaceStore.fetchWorkspace(workspaceId)
    }
  }

  function persistDeletedWorkspaceActivity() {
    const key = deletedWorkspaceStorageKey()
    if (!key) return
    localStorage.setItem(key, JSON.stringify(deletedWorkspaceActivity.value))
  }

  function loadDeletedWorkspaceActivity() {
    const key = deletedWorkspaceStorageKey()
    if (!key) return []

    try {
      return JSON.parse(localStorage.getItem(key) ?? '[]')
    } catch {
      localStorage.removeItem(key)
      return []
    }
  }

  function deletedWorkspaceStorageKey() {
    const user = JSON.parse(localStorage.getItem('workflowx_user') ?? 'null')
    return user?.id ? `${ARCHIVE_STORAGE_PREFIX}${user.id}` : ''
  }

  return {
    tasksByWorkspace,
    currentTask,
    loading,
    deletedWorkspaceActivity,
    allTasks,
    combinedRecentTasks,
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
    archiveDeletedWorkspaceTasks,
    clearWorkspaceTasks,
  }
})
