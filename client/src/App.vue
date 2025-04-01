<script setup>
import { ref, computed } from 'vue'
import { Map, Layers, Sources, Interactions, MapControls } from "vue3-openlayers"
import { getArea } from "ol/sphere";
import LocationForm from './components/LocationForm.vue'
import CalculationResults from './components/CalculationResults.vue'

const latitude = ref(-73.4540)
const longitude = ref(41.3948)
const center = computed(() => [latitude.value, longitude.value] )
const projection = 'EPSG:4326'
const calculationResult = ref(null)
const isLoading = ref(false)
const error = ref(null)
const drawEnabled = ref(false)
const selectedArea = ref(null)

const calculatePotential = async (loc) => {
  isLoading.value = true
  error.value = null

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:3000/api/calculate'
  
  try {
    console.log("fetch", loc)
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        latitude: loc.latitude,
        longitude: loc.longitude,
        area: selectedArea.value || 1000 // Use selected area if available, otherwise default
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
  // console.log(loc, loc.latitude, loc.longitude)
  console.log(loc);
  console.log("lat", loc.latitude); console.log("long", loc.longitude)
  latitude.value = loc.latitude
  longitude.value = loc.longitude
  calculatePotential(loc)
}

const toggleDraw = () => {
  drawEnabled.value = !drawEnabled.value
}

const handleDrawEnd = (event) => {
  drawEnabled.value = false;
  const feature = event.feature
  
  // Get the geometry and calculate area (in square meters)
  const geometry = feature.getGeometry()
  const area = getArea(geometry, {projection: projection})
  
  // Update the selected area (convert to hectares as that's what the backend expects)
  selectedArea.value = area
  
  // Recalculate with the new area
  if (center.value) {
    console.log('would have calculated potential at', center.value)
    // calculatePotential({
    //   latitude: center.value[1],
    //   longitude: center.value[0]
    // })
  }
}

const handleCenterChange = (event) => {
    latitude.value = event.target.getCenter()[0];
    longitude.value = event.target.getCenter()[1];
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
              Selected area: {{ (selectedArea * 10000).toFixed(0) }} sq meters ({{ selectedArea.toFixed(2) }} hectares)
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
              :result="calculationResult"
            />
          </div>
        </div>
        
        <div class="map-container">
          <Map.OlMap
            style="width: 800px; height: 600px;">
            <Map.OlView
                :center="center"
                :zoom="15"
                :projection="projection"
                @change:center="handleCenterChange"
                />
            <Layers.OlTileLayer>
              <Sources.OlSourceOsm />
            </Layers.OlTileLayer>
            
            <!-- Vector layer for drawn features -->
            <Layers.OlVectorLayer>
              <Sources.OlSourceVector>
                <!-- Draw interaction -->
                <Interactions.OlInteractionDraw
                  v-if="drawEnabled"
                  type="Polygon"
                  @drawend="handleDrawEnd"
                >
                </Interactions.OlInteractionDraw>
              </Sources.OlSourceVector>
            </Layers.OlVectorLayer>
            <MapControls.OlScalelineControl bar/>
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

@media (max-width: 768px) {
  .content {
    grid-template-columns: 1fr;
  }
}
</style>
