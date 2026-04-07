import { defineStore } from 'pinia'

export const useWorkspaceStore = defineStore('workspace', {
  state: () => ({
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1',
    stats: [
      { label: 'System Role', value: 'member', caption: 'Default role after authentication.' },
      { label: 'Workspace Role', value: 'manager', caption: 'Assigned to the workspace creator.' },
      { label: 'Review Flow', value: '3 steps', caption: 'Submit, review, approve or reject.' },
    ],
    reviewSteps: [
      {
        title: '1. In Progress',
        description: 'A manager creates a task inside a workspace and assigns it to a workspace member.',
      },
      {
        title: '2. In Review',
        description: 'Only the assigned member can submit the task for review when their work is ready.',
      },
      {
        title: '3. Done or Rework',
        description: 'The workspace manager approves the task to done or rejects it back to in progress.',
      },
    ],
  }),
})
