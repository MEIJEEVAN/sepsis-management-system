<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'

const router = useRouter()
const patients = ref([])
onMounted(async () => (patients.value = (await api.get('/patients')).data))
</script>

<template>
  <h2>Patients</h2>
  <div class="card">
    <table>
      <thead>
        <tr><th>MRN</th><th>Name</th><th>Bed</th><th>Status</th><th>Stage</th></tr>
      </thead>
      <tbody>
        <tr v-for="p in patients" :key="p.id" class="clickable" @click="router.push(`/patients/${p.id}`)">
          <td>{{ p.mrn }}</td>
          <td>{{ p.first_name }} {{ p.last_name }}</td>
          <td>{{ p.bed_number }}</td>
          <td>{{ p.status }}</td>
          <td>{{ p.episode_outcome === 'ongoing' ? p.episode_stage : '–' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
