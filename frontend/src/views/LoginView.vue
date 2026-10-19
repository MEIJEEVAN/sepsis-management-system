<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const email = ref('admin@sepsis.local')
const password = ref('')
const error = ref('')

async function submit() {
  error.value = ''
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.error || 'Login failed'
  }
}
</script>

<template>
  <form class="card form" style="max-width:380px;margin:4rem auto" @submit.prevent="submit">
    <h2>Sign in</h2>
    <label>Email<input v-model="email" type="email" required /></label>
    <label>Password<input v-model="password" type="password" required /></label>
    <p v-if="error" class="error">{{ error }}</p>
    <button type="submit">Login</button>
  </form>
</template>
