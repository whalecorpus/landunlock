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
  solarPanelArea,
  reforestationArea,
  polygons,
  landUseType,
  MWhPerYearPerHectare,
  carbonOffsetPerYearPerHectare,
  toggleDraw,
  handleDrawEnd,
  toggleLandUseType,
  clearPolygons,
  handleCenterChange,
  handleZoomChange,
  calculateSolarPotential,
  calculateForestPotential
} = useMap()

const solarCalculationResult = ref(null)
const forestCalculationResult = ref(null)
const isLoading = ref(false)
const error = ref(null)

const handleLocationUpdateWithLoading = async (loc) => {
  isLoading.value = true
  error.value = null
  try {
    solarCalculationResult.value = await calculateSolarPotential(loc)
    // forestCalculationResult.value = await calculateForestPotential(loc)
    await calculateForestPotential(loc)
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
}

const handleDrawEndWithResults = (area, geometry) => {
  const results = handleDrawEnd(area, geometry)
  if (results) {
    solarCalculationResult.value = results
  }
}

const handleClearPolygons = () => {
  clearPolygons()
  solarCalculationResult.value = null
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
            <!-- Land use type toggle buttons -->
            <div class="toggle-container">
              <button 
                @click="toggleLandUseType" 
                class="toggle-button"
                :class="{ 'active': landUseType === 'solar' }"
                :disabled="drawEnabled"
              >
                Solar Panels
              </button>
              <button 
                @click="toggleLandUseType" 
                class="toggle-button"
                :class="{ 'active': landUseType === 'reforestation' }"
                :disabled="drawEnabled"
              >
                Reforestation
              </button>
            </div>
            
            <button @click="toggleDraw" class="draw-button">
              {{ drawEnabled 
                ? 'Cancel Drawing' 
                : (landUseType === 'solar' ? 'Add Solar Panel Area' : 'Add Reforestation Area') 
              }}
            </button>
            
            <div v-if="polygons.length > 0" class="polygons-info">
              <p class="polygons-count">
                {{ polygons.length }} polygon{{ polygons.length !== 1 ? 's' : '' }} drawn
              </p>
              <p v-if="solarPanelArea" class="area-info">
                Solar panel area: {{ (solarPanelArea).toFixed(0) }} sq meters
              </p>
              <p v-if="reforestationArea" class="area-info">
                Reforestation area: {{ (reforestationArea).toFixed(0) }} sq meters
              </p>
              <p class="area-info total-area" v-if="solarPanelArea && reforestationArea">
                Total area: {{ (selectedArea).toFixed(0) }} sq meters
              </p>
              <button @click="handleClearPolygons" class="clear-button">Clear All</button>
            </div>
            
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
        </div>
        
        <div class="map-container">
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

        <!-- Results panel moved to the right -->
        <div v-if="solarCalculationResult && solarPanelArea" class="results-panel">
          <CalculationResults 
            :area="solarPanelArea"
            :MWhPerYearPerHectare="MWhPerYearPerHectare"
            :carbon-offset-per-year-per-hectare="carbonOffsetPerYearPerHectare"
          />
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
  width: 100%;
  padding: 2rem;
  min-height: 100vh;
}

header {
  margin-bottom: 2rem;
  width: 100%;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
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

main {
  width: 100%;
}

.content {
  display: grid;
  grid-template-columns: 300px 1fr 300px;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
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

.drawing-controls {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.toggle-container {
  display: flex;
  margin-bottom: 10px;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.toggle-button {
  flex: 1;
  padding: 8px 12px;
  background: #f5f5f5;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
}

.toggle-button.active {
  background-color: #2c3e50;
  color: white;
  font-weight: 500;
}

.toggle-button:first-child {
  border-right: 1px solid #e0e0e0;
}

.toggle-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.polygons-info {
  margin-top: 0.5rem;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.polygons-count {
  margin: 0 0 5px 0;
  font-size: 0.9rem;
  color: #2c3e50;
}

.area-info {
  margin: 5px 0;
  font-weight: 500;
  color: #2c3e50;
}

.total-area {
  margin-top: 10px;
  padding-top: 5px;
  border-top: 1px solid #ddd;
}

.clear-button {
  margin-top: 10px;
  width: 100%;
  padding: 5px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.clear-button:hover {
  background: #d32f2f;
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

.map-container {
  position: relative;
  height: 100%;
  min-height: 600px;
}

.results-panel {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  height: fit-content;
  position: sticky;
  top: 2rem;
}

@media (max-width: 1200px) {
  .content {
    grid-template-columns: 300px 1fr;
  }
  
  .results-panel {
    grid-column: 1 / -1;
    position: static;
  }
}

@media (max-width: 768px) {
  .content {
    grid-template-columns: 1fr;
  }
}
</style>
