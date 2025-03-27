<script setup>
import { ref } from 'vue'
import { Map, Layers, Sources } from "vue3-openlayers"
import LocationForm from './components/LocationForm.vue'

const center = ref([-73.4540, 41.3948]) // Danbury, CT coordinates
</script>

<template>
  <div class="app">
    <header>
      <h1>Land Unlock</h1>
    </header>

    <main>
      <div class="content">
        <LocationForm @update-location="(loc) => center = [loc.longitude, loc.latitude]" />
        
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

.map-container {
  border: 1px solid #ccc;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .content {
    grid-template-columns: 1fr;
  }
}
</style>