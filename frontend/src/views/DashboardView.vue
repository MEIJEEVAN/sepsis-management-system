<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'
import { useAuthStore } from '../stores/auth'
import AlertFeed from '../components/AlertFeed.vue'
import PatientCard from '../components/PatientCard.vue'

const auth = useAuthStore()
const router = useRouter()
const patients = ref([])
const alerts = ref([])
const risk = reactive({})
const received = ref(0)
const lastAt = ref('–')
const state = ref('connecting')
const rank = { critical: 3, high: 2, medium: 1 }
let es = null
let stopped = false

function normalize(a) {
  return {
    ...a,
    patient_name: a.patient_name || `${a.mrn} ${a.first_name} ${a.last_name}`,
    stage: a.stage || a.episode_stage,
  }
}

function markRisk(a) {
  if (!risk[a.patient_id] || rank[a.severity] >= rank[risk[a.patient_id]]) {
    risk[a.patient_id] = a.severity
  }
}

function connect() {
  if (stopped) return
  const url = `${import.meta.env.VITE_API_URL}/stream/alerts?token=${encodeURIComponent(auth.accessToken)}`
  es = new EventSource(url)
  es.onopen = () => (state.value = 'live')
  es.onmessage = (ev) => {
    const a = normalize(JSON.parse(ev.data))
    alerts.value.unshift(a)
    alerts.value.splice(100)
    received.value++
    lastAt.value = new Date().toLocaleTimeString()
    markRisk(a)
    const p = patients.value.find((x) => x.id === a.patient_id)
    if (p) {
      p.episode_stage = a.stage
      p.episode_outcome = 'ongoing'
    }
  }
  es.onerror = async () => {
    state.value = 'reconnecting'
    if (es.readyState === EventSource.CLOSED && !stopped) {
      try {
        await auth.refresh()
      } catch {
        auth.logout()
        router.push('/login')
        return
      }
      setTimeout(connect, 1000)
    }
  }
}

onMounted(async () => {
  const [p, a] = await Promise.all([api.get('/patients'), api.get('/alerts?acknowledged=false&limit=30')])
  patients.value = p.data
  alerts.value = a.data.map(normalize)
  alerts.value.forEach(markRisk)
  connect()
})

onBeforeUnmount(() => {
  stopped = true
  es?.close()
})
</script>

<template>
  <h2>ICU Dashboard</h2>
  <div class="status-line card">
    <span>Alert stream: <strong :class="{ live: state === 'live' }">{{ state }}</strong></span>
    <span>Alerts this session: <strong>{{ received }}</strong></span>
    <span>Last received: <strong>{{ lastAt }}</strong></span>
  </div>
  <div class="layout">
    <section class="grid">
      <PatientCard v-for="p in patients" :key="p.id" :patient="p" :risk="risk[p.id] || null" />
    </section>
    <aside class="card">
      <h3>Live alerts</h3>
      <AlertFeed :alerts="alerts" />
    </aside>
  </div>
</template>
