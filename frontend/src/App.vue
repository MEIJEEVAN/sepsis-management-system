<script setup>
import NavBar from './components/NavBar.vue'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
</script>

<template>
  <NavBar v-if="auth.isAuthenticated" />
  <main class="container"><router-view /></main>
</template>
