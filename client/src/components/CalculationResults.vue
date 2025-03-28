<template>
  <div v-if="result" class="calculation-results">
    <div class="main-result">
      <p>
        With your <span class="highlight">{{ formatArea(result.areaHectares * 10000) }}</span> of solar panels,
        you would produce <span class="highlight">{{ result.energyProduction.toFixed(2) }} MWh</span> per year.
      </p>
    </div>

    <div class="context">
      <p class="carbon-offset">
        Carbon offset: {{ result.carbonOffset.toFixed(1) }} tons CO₂e per year
      </p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  result: {
    type: Object,
    required: true
  }
})

const formatArea = (areaInSqMeters) => {
  if (areaInSqMeters >= 10000) {
    return `${(areaInSqMeters / 10000).toFixed(2)} hectares`
  }
  return `${areaInSqMeters.toFixed(0)} sq. meters`
}

</script>

<style scoped>
.calculation-results {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.main-result {
  font-size: 1.2rem;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.context {
  color: #4a5568;
  margin-bottom: 1rem;
}

.highlight {
  color: #42b983;
  font-weight: 600;
}

.carbon-offset {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #edf2f7;
  color: #2c5282;
  font-weight: 500;
}

</style> 