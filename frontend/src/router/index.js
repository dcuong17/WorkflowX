import { createRouter, createWebHistory } from 'vue-router'

import AppLayout from '../layouts/AppLayout.vue'
import AuthLayout from '../layouts/AuthLayout.vue'
import { useAuthStore } from '../stores/authStore'
import DashboardView from '../views/DashboardInteractiveView.vue'
import LoginView from '../views/LoginView.vue'
import ProfileView from '../views/ProfileView.vue'
import RegisterView from '../views/RegisterView.vue'
import TaskListView from '../views/TaskListView.vue'
import TaskDetailView from '../views/TaskDetailView.vue'
import WorkspaceDetailView from '../views/WorkspaceDetailView.vue'
import WorkspaceListView from '../views/WorkspaceListView.vue'
import WorkspaceMembersView from '../views/WorkspaceMembersView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    {
      path: '/',
      component: AuthLayout,
      meta: { guestOnly: true },
      children: [
        {
          path: 'login',
          name: 'login',
          component: LoginView,
          meta: { title: 'Đăng nhập' },
        },
        {
          path: 'register',
          name: 'register',
          component: RegisterView,
          meta: { title: 'Đăng ký' },
        },
      ],
    },
    {
      path: '/',
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: DashboardView,
          meta: { title: 'Bảng điều khiển', subtitle: 'Tổng quan hoạt động workspace và task' },
        },
        {
          path: 'workspaces',
          name: 'workspaces',
          component: WorkspaceListView,
          meta: { title: 'Workspace', subtitle: 'Theo dõi workspace bạn quản lý hoặc tham gia' },
        },
        {
          path: 'workspaces/:id',
          name: 'workspace-detail',
          component: WorkspaceDetailView,
          props: true,
          meta: { title: 'Chi tiết workspace', subtitle: 'Quản lý thành viên, task và tiến độ' },
        },
        {
          path: 'workspaces/:id/members',
          name: 'workspace-members',
          component: WorkspaceMembersView,
          props: true,
          meta: { title: 'Thành viên workspace', subtitle: 'Danh sách thành viên và vai trò nội bộ' },
        },
        {
          path: 'workspaces/:id/tasks/:task_id',
          name: 'task-detail',
          component: TaskDetailView,
          props: true,
          meta: { title: 'Chi tiết task', subtitle: 'Xem và cập nhật trạng thái task trong workspace' },
        },
        {
          path: 'tasks',
          name: 'tasks',
          component: TaskListView,
          meta: { title: 'Công việc', subtitle: 'Theo dõi task theo từng workspace và xử lý ngay trên danh sách' },
        },
        {
          path: 'profile',
          name: 'profile',
          component: ProfileView,
          meta: { title: 'Hồ sơ', subtitle: 'Cập nhật email và đổi mật khẩu của bạn' },
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (!authStore.initialized) {
    await authStore.initialize()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      name: 'login',
      query: { redirect: to.fullPath },
    }
  }

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return { name: 'dashboard' }
  }

  return true
})

export default router
