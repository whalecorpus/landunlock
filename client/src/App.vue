<script setup>
import { ref } from 'vue'
import { Map, Layers, Sources } from "vue3-openlayers"
import LocationForm from './components/LocationForm.vue'
import CalculationResults from './components/CalculationResults.vue'

const center = ref([-73.4540, 41.3948]) // Danbury, CT coordinates
const calculationResult = ref(null)
const isLoading = ref(false)
const error = ref(null)

const calculatePotential = async (loc) => {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await fetch('http://localhost:5000/api/calculate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        latitude: loc.latitude,
        longitude: loc.longitude,
        area: 1000 // Default 1000 sq meters for now
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    calculationResult.value = data
  } catch (e) {
    console.error('Calculation error:', e)
    error.value = 'Failed to calculate solar potential. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const handleLocationUpdate = (loc) => {
  center.value = [loc.longitude, loc.latitude]
  calculatePotential(loc)
}
</script>

<template>
  <div class="app">
    <header>
      <h1>Land Unlock</h1>
    </header>

    <main>
      <div class="content">
        <div class="sidebar">
          <LocationForm @update-location="handleLocationUpdate" />
          
          <!-- Loading state -->
          <div v-if="isLoading" class="status-message loading">
            Calculating potential...
          </div>

          <!-- Error state -->
          <div v-if="error" class="status-message error">
            {{ error }}
          </div>

          <!-- Results -->
          <div v-if="calculationResult" class="results">
            <CalculationResults 
              :result="calculationResult"
            />
          </div>
        </div>
        
        <div class="map-container">
          <Map.OlMap style="width: 800px; height: 600px;">
            <Map.OlView :center="center" :zoom="15" projection="EPSG:4326" />
            <Layers.OlTileLayer>
              <Sources.OlSourceOsm />
            </Layers.OlTileLayer>
          </Map.OlMap>
        </div>
      </div>
    </main>
  </div>
</template>

<style>
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
}

.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

header {
  margin-bottom: 2rem;
  text-align: center;
}

h1 {
  color: #2c3e50;
  font-size: 2.5rem;
}

.content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.map-container {
  border: 1px solid #ccc;
  border-radius: 4px;
}

.status-message {
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}

.status-message.loading {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status-message.error {
  background-color: #ffebee;
  color: #d32f2f;
}

.results {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}

.results h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.results pre {
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .content {
    grid-template-columns: 1fr;
  }
}
</style>