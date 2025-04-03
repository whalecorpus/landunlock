<script setup>
import { ref, computed } from 'vue'
import { getDistance } from "ol/sphere";
import LocationForm from './components/LocationForm.vue'
import CalculationResults from './components/CalculationResults.vue'
import MapView from './components/MapView.vue'

const latitude = ref(41.3948)
const longitude = ref(-73.4540)
const center = computed(() => [longitude.value, latitude.value] )
const zoom = ref(17)
const calculationResult = ref(null)
const isLoading = ref(false)
const error = ref(null)
const drawEnabled = ref(false)
const selectedArea = ref(null)
const landUseType = 'solar'

// Track API call conditions
const lastApiCallLocation = ref(null)
const MWhPerYearPerHectare = ref(1850)
const carbonOffsetPerYearPerHectare = ref(650)
const kmDiff = ref(50) // Distance in kilometers before making a new API call

const calculatePotential = async (loc) => {
  isLoading.value = true
  error.value = null

  // if we have a lastApiCallLocation, we need to check if the new location is too close to the last one
  if (lastApiCallLocation.value) {
    const distance = getDistance(
      [lastApiCallLocation.value.longitude, lastApiCallLocation.value.latitude],
      [loc.longitude, loc.latitude]
    ) / 1000 // Convert meters to kilometers
    
    if (distance < kmDiff.value) {
      console.log('not recalculating because distance is too short', distance);
      return
    }
  }

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:3000/api/calculate'
  
  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        latitude: loc.latitude,
        longitude: loc.longitude,
        area: 10000 // we always want to calculate the potential for one hectare, and we'll calculate their selected area kWh / carbon offset based on that
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    calculationResult.value = data
    
    lastApiCallLocation.value = loc
    MWhPerYearPerHectare.value = data.energyProduction
    carbonOffsetPerYearPerHectare.value = data.carbonOffset
    console.log('coefficients updated:', {
      kWh: MWhPerYearPerHectare.value,
      carbon: carbonOffsetPerYearPerHectare.value
    })
  } catch (e) {
    console.error('Calculation error:', e)
    error.value = 'Failed to calculate solar potential. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const handleLocationUpdate = (loc) => {
  latitude.value = loc.latitude
  longitude.value = loc.longitude
  calculatePotential(loc)
}

const toggleDraw = () => {
  drawEnabled.value = !drawEnabled.value
}

const handleDrawEnd = (area) => {
  drawEnabled.value = false
  selectedArea.value = area
  console.log('selected area', selectedArea.value)
  
  // Update calculations with the new area using current coefficients
  if (selectedArea.value) {
    // Convert selected area to number of 1000 sqm units
    const areaHectares = selectedArea.value / 10000 // Convert to hectares
    calculationResult.value = {
      energyProduction: areaHectares * MWhPerYearPerHectare.value,
      carbonOffset: areaHectares * carbonOffsetPerYearPerHectare.value
    }
  }
}

const handleCenterChange = (newCenter) => {
  longitude.value = newCenter[0]
  latitude.value = newCenter[1]
  console.log('current coefficients', MWhPerYearPerHectare.value, carbonOffsetPerYearPerHectare.value)
}

const handleZoomChange = (newZoom) => {
  zoom.value = newZoom
}
</script>

<template>
  <div class="app">
    <header>
      <div class="header-content">
        <div class="logo-container">
          <img src="/logo.png" alt="Land Unlock Logo" class="logo">
          <h1>Land Unlock</h1>
        </div>
        <a href="/about.html" class="about-link">About</a>
      </div>
    </header>

    <main>
      <div class="content">
        <div class="sidebar">
          <LocationForm
            @update-location="handleLocationUpdate"
            v-model:latitude="latitude"
            v-model:longitude="longitude"
          />
          
          <div class="drawing-controls">
            <button @click="toggleDraw" class="draw-button">
              {{ drawEnabled ? 'Disable Drawing' : 'Manually Select a roof' }}
            </button>
            <p v-if="selectedArea" class="area-info">
              Selected area: {{ (selectedArea).toFixed(0) }} sq meters ({{ (selectedArea / 10000).toFixed(2) }} hectares)
            </p>
            <p v-if="drawEnabled" class="drawing-instructions">
              Click on the map to start drawing a polygon. Click each vertex position and double-click to finish.
            </p>
          </div>
          
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
              v-if="selectedArea"
              :area="selectedArea"
              :MWhPerYearPerHectare="MWhPerYearPerHectare"
              :carbon-offset-per-year-per-hectare="carbonOffsetPerYearPerHectare"
            />
          </div>
        </div>
        
        <MapView
          v-model:center="center"
          v-model:zoom="zoom"
          :draw-enabled="drawEnabled"
          :land-use-type="landUseType"
          @draw-end="handleDrawEnd"
          @update:center="handleCenterChange"
          @update:zoom="handleZoomChange"
        />
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
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.logo {
  height: 48px;
  width: auto;
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

.drawing-controls {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.draw-button {
  width: 100%;
  padding: 0.5rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.draw-button:hover {
  background: #45a049;
}

.area-info {
  margin-top: 0.5rem;
  font-weight: 500;
  color: #2c3e50;
}

.drawing-instructions {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #666;
  font-style: italic;
}

.about-link {
  color: #2c3e50;
  text-decoration: none;
  font-size: 1.1rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.about-link:hover {
  background-color: #f5f5f5;
}

@media (max-width: 768px) {
  .content {
    grid-template-columns: 1fr;
  }
}
</style>
