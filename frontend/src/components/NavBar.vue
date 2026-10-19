<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <nav class="container" style="display:flex;gap:1rem;align-items:center">
    <strong style="color:var(--purple)">Sepsis MS</strong>
    <router-link to="/">Dashboard</router-link>
    <router-link to="/patients">Patients</router-link>
    <span style="flex:1"></span>
    <span class="muted">{{ auth.user?.username }} ({{ auth.user?.role }})</span>
    <button class="secondary" @click="logout">Logout</button>
  </nav>
</template>
