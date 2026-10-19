<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'

const route = useRoute()
const data = ref(null)
const message = ref('')

async function load() {
  data.value = (await api.get(`/patients/${route.params.id}/summary`)).data
}

async function assess() {
  try {
    const r = (await api.post(`/sepsis/assess/${route.params.id}`)).data
    message.value = r.sepsis_detected
      ? `Detected: ${r.message}`
      : `Not detected (SIRS ${r.sirs_score}, qSOFA ${r.qsofa_score})`
    await load()
  } catch (e) {
    message.value = e.response?.data?.error || 'Assessment failed'
  }
}

async function ackLatest() {
  const alert = data.value.alerts.find((a) => !a.acknowledged)
  if (!alert) return (message.value = 'No unacknowledged alerts')
  await api.put(`/alerts/${alert.id}/acknowledge`)
  message.value = `Alert #${alert.id} acknowledged`
  await load()
}

onMounted(load)
</script>

<template>
  <div v-if="data">
    <h2>{{ data.patient.first_name }} {{ data.patient.last_name }}
      <span class="muted">{{ data.patient.mrn }} · {{ data.patient.bed_number }}</span></h2>
    <div style="display:flex;gap:.5rem;margin-bottom:1rem">
      <button @click="assess">Assess sepsis now</button>
      <button class="secondary" @click="ackLatest">Acknowledge latest alert</button>
    </div>
    <p v-if="message" class="muted">{{ message }}</p>

    <div class="layout">
      <section class="card">
        <h3>Latest vitals</h3>
        <p v-if="!data.vitals.length" class="muted">No vitals yet.</p>
        <table v-else>
          <thead><tr><th>Time</th><th>T</th><th>HR</th><th>RR</th><th>BP</th><th>SpO₂</th><th>GCS</th></tr></thead>
          <tbody>
            <tr v-for="v in data.vitals" :key="v.id">
              <td>{{ new Date(v.recorded_at).toLocaleTimeString() }}</td>
              <td>{{ v.temperature }}</td><td>{{ v.heart_rate }}</td><td>{{ v.respiratory_rate }}</td>
              <td>{{ v.systolic_bp }}/{{ v.diastolic_bp }}</td><td>{{ v.spo2 }}</td><td>{{ v.gcs }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section>
        <div class="card" style="margin-bottom:1rem">
          <h3>Last labs</h3>
          <table>
            <thead><tr><th>Time</th><th>WBC</th><th>Lac</th><th>CRP</th></tr></thead>
            <tbody>
              <tr v-for="l in data.labs" :key="l.id">
                <td>{{ new Date(l.recorded_at).toLocaleTimeString() }}</td>
                <td>{{ l.wbc }}</td><td>{{ l.lactate }}</td><td>{{ l.crp }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="card">
          <h3>Episode history</h3>
          <p v-if="!data.episodes.length" class="muted">No episodes.</p>
          <div v-for="e in data.episodes" :key="e.id" style="margin-bottom:.5rem">
            <strong>{{ e.stage }}</strong> · {{ e.outcome }}
            <div class="muted">SIRS {{ e.sirs_score }} · qSOFA {{ e.qsofa_score }} ·
              conf {{ e.confidence_score }} · {{ new Date(e.detected_at).toLocaleString() }}</div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
