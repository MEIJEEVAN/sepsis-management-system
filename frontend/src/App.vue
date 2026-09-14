<template>
  <div>
    <NavBar v-if="auth.isAuthenticated" />
    <router-view />
  </div>
</template>

<script setup>
import { useAuthStore } from "./stores/auth";
import NavBar from "./components/NavBar.vue";

const auth = useAuthStore();
</script>
