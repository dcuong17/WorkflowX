import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginPage.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/signup',
    name: 'Signup',
    component: () => import('../views/SignupPage.vue'),
    meta: { requiresGuest: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const accessToken = localStorage.getItem('access_token')
  const isAuthenticated = !!accessToken

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.meta.requiresGuest && isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
