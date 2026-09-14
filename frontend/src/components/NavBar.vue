<template>
  <nav>
    <router-link to="/dashboard">Dashboard</router-link>
    <router-link to="/patients">Patients</router-link>
    <button @click="logout">Logout</button>
  </nav>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();

function logout() {
  auth.logout();
  router.push("/login");
}
</script>
