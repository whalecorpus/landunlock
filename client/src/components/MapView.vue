<template>
  <div class="map-container">
    <Map.OlMap
      style="width: 800px; height: 600px;"
      ref="mapRef">
      <Map.OlView
        :center="center"
        :zoom="zoom"
        :projection="projection"
        @change:center="handleCenterChange"
      />
      <Layers.OlTileLayer>
        <Sources.OlSourceOsm />
      </Layers.OlTileLayer>
      
      <!-- Vector layer for drawn features -->
      <Layers.OlVectorLayer 
        :style="landUseType === 'solar' 
          ? { 
              'stroke-color': '#FFD700',
              'stroke-width': 3,
              'fill-color': 'rgba(0, 0, 0, 0.5)'
            } 
          : { 
              'stroke-color': '#228B22',
              'stroke-width': 3,
              'fill-color': 'rgba(34, 139, 34, 0.5)'
            }"
        ref="vectorLayerRef"
      >
        <Sources.OlSourceVector ref="sourceRef">
          <!-- Draw interaction -->
          <Interactions.OlInteractionDraw
            v-if="drawEnabled"
            type="Polygon"
            @drawend="handleDrawEnd"
            :style="landUseType === 'solar' 
              ? { 
                  'stroke-color': '#FFD700',
                  'stroke-width': 3,
                  'fill-color': 'rgba(0, 0, 0, 0.5)'
                } 
              : { 
                  'stroke-color': '#228B22',
                  'stroke-width': 3,
                  'fill-color': 'rgba(34, 139, 34, 0.5)'
                }"
          >
          </Interactions.OlInteractionDraw>
        </Sources.OlSourceVector>
      </Layers.OlVectorLayer>
      
      <MapControls.OlScalelineControl bar/>
    </Map.OlMap>
    
    <div class="controls">
      <button @click="clearPolygons" class="clear-button" v-if="hasPolygons">Clear All Polygons</button>
    </div>
  </div>
</template>

<script setup>
import { Map, Layers, Sources, Interactions, MapControls } from "vue3-openlayers"
import { getArea } from "ol/sphere"
import { ref, computed } from 'vue'

const props = defineProps({
  center: {
    type: Array,
    required: true
  },
  zoom: {
    type: Number,
    required: true
  },
  drawEnabled: {
    type: Boolean,
    required: true
  },
  landUseType: {
    type: String,
    default: 'solar'
  },
  polygons: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:center', 'update:zoom', 'drawEnd', 'clearPolygons'])

const projection = 'EPSG:4326'
const mapRef = ref(null)
const vectorLayerRef = ref(null)
const sourceRef = ref(null)

const hasPolygons = computed(() => props.polygons && props.polygons.length > 0)

// Handle the drawing finish event
const handleDrawEnd = (event) => {
  const feature = event.feature
  const geometry = feature.getGeometry()
  const area = getArea(geometry, {projection: projection})
  
  // Pass both the area and the geometry to the parent
  emit('drawEnd', area, geometry)
}

const handleCenterChange = (event) => {
  emit('update:center', event.target.getCenter())
  emit('update:zoom', event.target.getZoom())
}

const clearPolygons = () => {
  if (sourceRef.value && sourceRef.value.source) {
    sourceRef.value.source.clear()
    emit('clearPolygons')
  }
}
</script>

<style scoped>
.map-container {
  border: 1px solid #ccc;
  border-radius: 4px;
  position: relative;
}

.controls {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.clear-button {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.clear-button:hover {
  background-color: #d32f2f;
}
</style>
