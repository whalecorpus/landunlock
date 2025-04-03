<script setup>
import { ref } from 'vue'
import LocationForm from './components/LocationForm.vue'
import CalculationResults from './components/CalculationResults.vue'
import MapView from './components/MapView.vue'
import { useMap } from './composables/useMap'

const {
  latitude,
  longitude,
  center,
  zoom,
  drawEnabled,
  selectedArea,
  polygons,
  landUseType,
  MWhPerYearPerHectare,
  carbonOffsetPerYearPerHectare,
  toggleDraw,
  handleDrawEnd,
  clearPolygons,
  handleCenterChange,
  handleZoomChange,
  calculatePotential
} = useMap()

const calculationResult = ref(null)
const isLoading = ref(false)
const error = ref(null)

const handleLocationUpdateWithLoading = async (loc) => {
  isLoading.value = true
  error.value = null
  try {
    calculationResult.value = await calculatePotential(loc)
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
}

const handleDrawEndWithResults = (area, geometry) => {
  const results = handleDrawEnd(area, geometry)
  if (results) {
    calculationResult.value = results
  }
}

const handleClearPolygons = () => {
  clearPolygons()
  calculationResult.value = null
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
            @update-location="handleLocationUpdateWithLoading"
            v-model:latitude="latitude"
            v-model:longitude="longitude"
          />
          
          <div class="drawing-controls">
            <button @click="toggleDraw" class="draw-button">
              {{ drawEnabled ? 'Disable Drawing' : 'Manually Select a roof' }}
            </button>
            
            <p v-if="drawEnabled" class="drawing-instructions">
              Click on the map to start drawing your solar panel or reforestation area. Click each vertex position and complete the shape to finish.
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
          <div v-if="calculationResult && selectedArea" class="results">
            <CalculationResults 
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
          :polygons="polygons"
          @draw-end="handleDrawEndWithResults"
          @clear-polygons="handleClearPolygons"
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