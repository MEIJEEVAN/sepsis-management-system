import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import PatientsView from '../views/PatientsView.vue'
import PatientDetailView from '../views/PatientDetailView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    { path: '/', component: DashboardView, meta: { auth: true } },
    { path: '/patients', component: PatientsView, meta: { auth: true } },
    { path: '/patients/:id', component: PatientDetailView, meta: { auth: true } },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.auth && !auth.isAuthenticated) return '/login'
})

export default router
