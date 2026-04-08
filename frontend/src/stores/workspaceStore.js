import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { apiClient } from '../plugins/axios'
import { useToastStore } from './toastStore'

const WORKSPACE_SNAPSHOT_PREFIX = 'workflowx_workspace_ids_'

function normalizeCollection(payload) {
  return Array.isArray(payload) ? payload : (payload?.results ?? [])
}

export const useWorkspaceStore = defineStore('workspaceStore', () => {
  const toastStore = useToastStore()
  const workspaces = ref([])
  const currentWorkspace = ref(null)
  const currentWorkspaceId = ref('')
  const members = ref([])
  const memberDirectory = ref({})
  const availableUsers = ref([])
  const loading = ref(false)
  const deletedWorkspaceNotifications = ref([])

  const createdWorkspaceCount = computed(() => {
    return workspaces.value.filter((workspace) => workspace.created_by === currentUserId()).length
  })

  async function fetchWorkspaces() {
    loading.value = true
    try {
      const previousWorkspaces = [...workspaces.value]
      const { data } = await apiClient.get('/workspace/')
      workspaces.value = normalizeCollection(data)
      syncRemovedWorkspaces(previousWorkspaces, workspaces.value)
      persistWorkspaceIds(workspaces.value)
      return workspaces.value
    } finally {
      loading.value = false
    }
  }

  async function fetchWorkspace(workspaceId) {
    loading.value = true
    try {
      const { data } = await apiClient.get(`/workspace/${workspaceId}/`)
      currentWorkspace.value = data
      currentWorkspaceId.value = workspaceId
      patchWorkspace(data)
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchMembers(workspaceId) {
    const { data } = await apiClient.get(`/workspace/${workspaceId}/members/`)
    members.value = normalizeCollection(data)
    const directoryPatch = {}
    for (const member of members.value) {
      directoryPatch[member.user] = member.user_username || member.user_email || member.user
    }
    memberDirectory.value = {
      ...memberDirectory.value,
      ...directoryPatch,
    }
    return members.value
  }

  async function fetchAvailableUsers(workspaceId) {
    const { data } = await apiClient.get('/auth/users', {
      params: { workspace_id: workspaceId },
    })
    availableUsers.value = normalizeCollection(data)
    const directoryPatch = {}
    for (const user of availableUsers.value) {
      directoryPatch[user.id] = user.username || user.email || user.id
    }
    memberDirectory.value = {
      ...memberDirectory.value,
      ...directoryPatch,
    }
    return availableUsers.value
  }

  async function createWorkspace(payload) {
    const { data } = await apiClient.post('/workspace/', payload)
    workspaces.value = [data, ...workspaces.value]
    persistWorkspaceIds(workspaces.value)
    toastStore.success('Tạo workspace thành công', `Workspace "${data.workspace_name}" đã được tạo.`)
    return data
  }

  async function updateWorkspace(workspaceId, payload) {
    const { data } = await apiClient.put(`/workspace/${workspaceId}/`, payload)
    currentWorkspace.value = data
    patchWorkspace(data)
    persistWorkspaceIds(workspaces.value)
    toastStore.success('Cập nhật workspace thành công', `Workspace "${data.workspace_name}" đã được cập nhật.`)
    return data
  }

  async function deleteWorkspace(workspaceId) {
    const workspace = workspaces.value.find((item) => item.workspace_id === workspaceId)
    const workspaceName = workspace?.workspace_name || 'Workspace'
    await apiClient.delete(`/workspace/${workspaceId}/`)

    const { useTaskStore } = await import('./taskStore')
    useTaskStore().archiveDeletedWorkspaceTasks(workspaceId, workspaceName)

    workspaces.value = workspaces.value.filter((item) => item.workspace_id !== workspaceId)
    persistWorkspaceIds(workspaces.value)
    if (currentWorkspaceId.value === workspaceId) {
      currentWorkspace.value = null
      currentWorkspaceId.value = ''
    }
    toastStore.success('Xóa workspace thành công', `"${workspaceName}" đã được xóa.`)
  }

  async function addMember(workspaceId, userId) {
    const { data } = await apiClient.post(`/workspace/${workspaceId}/members/`, { user: userId })
    members.value = [...members.value, data]
    memberDirectory.value = {
      ...memberDirectory.value,
      [data.user]: data.user_username || data.user_email || data.user,
    }
    toastStore.success('Thêm thành viên thành công', 'Thành viên đã được thêm vào workspace.')
    return data
  }

  async function removeMember(workspaceId, memberId) {
    await apiClient.delete(`/workspace/${workspaceId}/members/${memberId}/`)
    members.value = members.value.filter((member) => member.id !== memberId)
    toastStore.success('Xóa thành viên thành công', 'Thành viên đã được xóa khỏi workspace.')
  }

  function patchWorkspace(workspace) {
    const snapshot = [...workspaces.value]
    const index = snapshot.findIndex((item) => item.workspace_id === workspace.workspace_id)

    if (index === -1) {
      snapshot.unshift(workspace)
    } else {
      snapshot.splice(index, 1, { ...snapshot[index], ...workspace })
    }

    workspaces.value = snapshot
  }

  function syncRemovedWorkspaces(previousWorkspaces, nextWorkspaces) {
    const storedWorkspaceIds = loadStoredWorkspaceIds()
    const mergedPrevious = [
      ...previousWorkspaces,
      ...storedWorkspaceIds
        .filter((workspaceId) => !previousWorkspaces.some((workspace) => workspace.workspace_id === workspaceId))
        .map((workspaceId) => ({ workspace_id: workspaceId, workspace_name: 'Workspace đã bị xoá', created_by: '' })),
    ]
    const nextIds = new Set(nextWorkspaces.map((workspace) => workspace.workspace_id))
    const removed = mergedPrevious.filter((workspace) => !nextIds.has(workspace.workspace_id))

    if (!removed.length) {
      return
    }

    const currentUser = loadCurrentUser()
    for (const workspace of removed) {
      const deletedByCurrentUser = workspace.created_by === currentUser?.id
      if (deletedByCurrentUser || deletedWorkspaceNotifications.value.includes(workspace.workspace_id)) {
        continue
      }

      deletedWorkspaceNotifications.value = [...deletedWorkspaceNotifications.value, workspace.workspace_id]
      toastStore.warning(
        'Workspace không còn tồn tại',
        `Workspace "${workspace.workspace_name}" mà bạn từng tham gia đã bị xóa khỏi hệ thống.`,
      )
    }

    import('./taskStore').then(({ useTaskStore }) => {
      const taskStore = useTaskStore()
      for (const workspace of removed) {
        taskStore.archiveDeletedWorkspaceTasks(workspace.workspace_id, workspace.workspace_name)
      }
    })
  }

  function persistWorkspaceIds(nextWorkspaces) {
    const key = workspaceSnapshotKey()
    if (!key) return
    localStorage.setItem(key, JSON.stringify(nextWorkspaces.map((workspace) => workspace.workspace_id)))
  }

  return {
    workspaces,
    currentWorkspace,
    currentWorkspaceId,
    members,
    memberDirectory,
    availableUsers,
    loading,
    createdWorkspaceCount,
    fetchWorkspaces,
    fetchWorkspace,
    fetchMembers,
    fetchAvailableUsers,
    createWorkspace,
    updateWorkspace,
    deleteWorkspace,
    addMember,
    removeMember,
  }
})

function currentUserId() {
  return loadCurrentUser()?.id ?? ''
}

function loadCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem('workflowx_user') ?? 'null')
  } catch {
    return null
  }
}

function workspaceSnapshotKey() {
  const user = loadCurrentUser()
  return user?.id ? `${WORKSPACE_SNAPSHOT_PREFIX}${user.id}` : ''
}

function loadStoredWorkspaceIds() {
  const key = workspaceSnapshotKey()
  if (!key) return []

  try {
    return JSON.parse(localStorage.getItem(key) ?? '[]')
  } catch {
    localStorage.removeItem(key)
    return []
  }
}
