<template>
  <form @submit.prevent="handleLogin">
    <h1>Login</h1>
    <input v-model="email" type="email" placeholder="Email" required />
    <input v-model="password" type="password" placeholder="Password" required />
    <button type="submit">Login</button>
    <p v-if="error" style="color: red">{{ error }}</p>
  </form>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const email = ref("");
const password = ref("");
const error = ref("");
const router = useRouter();
const auth = useAuthStore();

async function handleLogin() {
  try {
    await auth.login({ email: email.value, password: password.value });
    router.push("/dashboard");
  } catch (err) {
    error.value = err.response?.data?.message || "Login failed";
  }
}
</script>
