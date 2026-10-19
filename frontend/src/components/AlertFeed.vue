<script setup>
defineProps({ alerts: { type: Array, required: true } })
</script>

<template>
  <div class="alert-list">
    <p v-if="!alerts.length" class="muted">No alerts yet.</p>
    <div v-for="a in alerts" :key="a.alert_id" class="alert-item" :class="`sev-${a.severity}`">
      <span class="badge" :class="`sev-${a.severity}`">{{ a.severity }}</span>
      <strong> {{ a.patient_name }}</strong>
      <div>{{ a.message }}</div>
      <div class="muted">{{ new Date(a.created_at).toLocaleTimeString() }}</div>
    </div>
  </div>
</template>
