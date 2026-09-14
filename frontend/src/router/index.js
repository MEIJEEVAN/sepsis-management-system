import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/LoginView.vue"),
  },
  { path: "/", redirect: "/dashboard" },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: () => import("../views/DashboardView.vue"),
  },
  {
    path: "/patients",
    name: "Patients",
    component: () => import("../views/PatientsView.vue"),
  },
  {
    path: "/patients/:id",
    name: "PatientDetail",
    component: () => import("../views/PatientDetailView.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const auth = useAuthStore();
  if (to.name !== "Login" && !auth.isAuthenticated) {
    next({ name: "Login" });
  } else {
    next();
  }
});

export default router;
