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
              'fill-color': 'rgba(34, 139, 34, 0.4)'
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
                  'fill-color': 'rgba(34, 139, 34, 0.4)'
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
import { getArea } from "ol/sphere"
import { ref, watch } from 'vue'

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
const vectorLayerRef = ref(null)
const sourceRef = ref(null)

// Add the new shape to our list of shapes
const handleDrawEnd = (event) => {
  console.log('Drawing with landUseType:', props.landUseType)
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

watch(() => props.polygons, (newPolygons) => {
  if (newPolygons.length === 0 && sourceRef.value && sourceRef.value.source) {
    sourceRef.value.source.clear()
  }
}, { deep: true })

</script>

<style scoped>
.map-container {
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>
