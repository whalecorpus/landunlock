<template>
  <div class="map-container">
    <Map.OlMap
      style="width: 800px; height: 600px;">
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
      >
        <Sources.OlSourceVector>
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
  </div>
</template>

<script setup>
import { Map, Layers, Sources, Interactions, MapControls } from "vue3-openlayers"
import { getArea } from "ol/sphere";

defineProps({
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
  }
})

const emit = defineEmits(['update:center', 'update:zoom', 'drawEnd'])

const projection = 'EPSG:4326'

const handleDrawEnd = (event) => {
  const feature = event.feature
  const geometry = feature.getGeometry()
  const area = getArea(geometry, {projection: projection})
  emit('drawEnd', area)
}

const handleCenterChange = (event) => {
  emit('update:center', event.target.getCenter())
  emit('update:zoom', event.target.getZoom())
}
</script>

<style scoped>
.map-container {
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style> 