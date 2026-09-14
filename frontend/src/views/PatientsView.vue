<template>
  <div>
    <h1>Patients</h1>
    <table>
      <thead>
        <tr>
          <th>MRN</th>
          <th>Name</th>
          <th>Bed</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="patient in patients" :key="patient.id">
          <td>{{ patient.mrn }}</td>
          <td>{{ patient.first_name }} {{ patient.last_name }}</td>
          <td>{{ patient.bed_number }}</td>
          <td>{{ patient.status }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api/axios";

const patients = ref([]);

onMounted(async () => {
  const { data } = await api.get("/patients");
  patients.value = data;
});
</script>
