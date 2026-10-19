<script setup>
defineProps({
  patient: { type: Object, required: true },
  risk: { type: String, default: null },
})
</script>

<template>
  <router-link :to="`/patients/${patient.id}`">
    <div class="card patient-card" :class="risk ? [`at-risk`, `risk-${risk}`] : ''">
      <strong>{{ patient.first_name }} {{ patient.last_name }}</strong>
      <div class="muted">{{ patient.mrn }} · {{ patient.bed_number || 'no bed' }}</div>
      <div v-if="risk" class="badge" :class="`sev-${risk}`" style="margin:.4rem 0">AT RISK</div>
      <div v-if="patient.episode_stage && patient.episode_outcome === 'ongoing'" class="muted">
        stage: {{ patient.episode_stage }}
      </div>
      <div class="muted" style="margin-top:.4rem">
        HR {{ patient.heart_rate ?? '–' }} · T {{ patient.temperature ?? '–' }} ·
        BP {{ patient.systolic_bp ?? '–' }}/{{ patient.diastolic_bp ?? '–' }} ·
        SpO₂ {{ patient.spo2 ?? '–' }} · Lac {{ patient.lactate ?? '–' }}
      </div>
    </div>
  </router-link>
</template>
