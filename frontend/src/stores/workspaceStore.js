import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { apiClient } from '../plugins/axios'
import { useToastStore } from './toastStore'

function normalizeCollection(payload) {
  return Array.isArray(payload) ? payload : (payload?.results ?? [])
}

export const useWorkspaceStore = defineStore('workspaceStore', () => {
  const toastStore = useToastStore()
  const workspaces = ref([])
  const currentWorkspace = ref(null)
  const currentWorkspaceId = ref('')
  const members = ref([])
  const availableUsers = ref([])
  const loading = ref(false)

  const createdWorkspaceCount = computed(() => {
    return workspaces.value.filter((workspace) => workspace.created_by === currentUserId()).length
  })

  async function fetchWorkspaces() {
    loading.value = true
    try {
      const { data } = await apiClient.get('/workspace/')
      workspaces.value = normalizeCollection(data)
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
    return members.value
  }

  async function fetchAvailableUsers(workspaceId) {
    const { data } = await apiClient.get('/auth/users', {
      params: { workspace_id: workspaceId },
    })
    availableUsers.value = normalizeCollection(data)
    return availableUsers.value
  }

  async function createWorkspace(payload) {
    const { data } = await apiClient.post('/workspace/', payload)
    workspaces.value = [data, ...workspaces.value]
    toastStore.success('Workspace created', `Workspace "${data.workspace_name}" đã được tạo.`)
    return data
  }

  async function updateWorkspace(workspaceId, payload) {
    const { data } = await apiClient.put(`/workspace/${workspaceId}/`, payload)
    currentWorkspace.value = data
    patchWorkspace(data)
    toastStore.success('Workspace updated', `Workspace "${data.workspace_name}" đã được cập nhật.`)
    return data
  }

  async function deleteWorkspace(workspaceId) {
    const workspaceName = workspaces.value.find((workspace) => workspace.workspace_id === workspaceId)?.workspace_name || 'Workspace'
    await apiClient.delete(`/workspace/${workspaceId}/`)
    workspaces.value = workspaces.value.filter((workspace) => workspace.workspace_id !== workspaceId)
    if (currentWorkspaceId.value === workspaceId) {
      currentWorkspace.value = null
      currentWorkspaceId.value = ''
    }
    toastStore.success('Workspace deleted', `"${workspaceName}" đã được xóa.`)
  }

  async function addMember(workspaceId, userId) {
    const { data } = await apiClient.post(`/workspace/${workspaceId}/members/`, { user: userId })
    members.value = [...members.value, data]
    toastStore.success('Member added', 'Thành viên đã được thêm vào workspace.')
    return data
  }

  async function removeMember(workspaceId, memberId) {
    await apiClient.delete(`/workspace/${workspaceId}/members/${memberId}/`)
    members.value = members.value.filter((member) => member.id !== memberId)
    toastStore.success('Member removed', 'Thành viên đã được xóa khỏi workspace.')
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

  return {
    workspaces,
    currentWorkspace,
    currentWorkspaceId,
    members,
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
  try {
    const user = JSON.parse(localStorage.getItem('workflowx_user') ?? 'null')
    return user?.id ?? ''
  } catch {
    return ''
  }
}
