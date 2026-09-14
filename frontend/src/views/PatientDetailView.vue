<template>
  <div>
    <h1>Patient Details</h1>
    <p v-if="patient">Name: {{ patient.first_name }} {{ patient.last_name }}</p>
    <button @click="assess">Assess Sepsis</button>
    <pre v-if="assessment">{{ assessment }}</pre>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import api from "../api/axios";

const route = useRoute();
const patient = ref(null);
const assessment = ref(null);

onMounted(async () => {
  const { data } = await api.get(`/patients/${route.params.id}`);
  patient.value = data;
});

async function assess() {
  const { data } = await api.post(`/sepsis/assess/${route.params.id}`);
  assessment.value = data;
}
</script>
