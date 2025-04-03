import { ref, computed } from 'vue'
import { getDistance } from "ol/sphere"

export function useMap() {
  const latitude = ref(28.400856773608965)
  const longitude = ref(-81.57923406710395)
  const center = ref([longitude.value, latitude.value])
  const zoom = ref(17)
  const drawEnabled = ref(false)
  
  // Change from single area to array of polygons
  const polygons = ref([])
  
  // Separate computed properties for each land use type
  const solarPanelArea = computed(() => {
    const solarPolygons = polygons.value.filter(polygon => polygon.type === 'solar')
    if (solarPolygons.length === 0) return null
    return solarPolygons.reduce((sum, polygon) => sum + polygon.area, 0)
  })
  
  const reforestationArea = computed(() => {
    const reforestationPolygons = polygons.value.filter(polygon => polygon.type === 'reforestation')
    if (reforestationPolygons.length === 0) return null
    return reforestationPolygons.reduce((sum, polygon) => sum + polygon.area, 0)
  })
  
  // Keep selectedArea for result calculations for now
  // TODO: use separate solar and reforestation areas for result calculations
  const selectedArea = computed(() => {
    if (polygons.value.length === 0) return null
    return polygons.value.reduce((sum, polygon) => sum + polygon.area, 0)
  })
  
  const landUseType = ref('solar') // Current active land use type
  
  // Function to toggle land use type
  const toggleLandUseType = () => {
    landUseType.value = landUseType.value === 'solar' ? 'reforestation' : 'solar'
    console.log('toggleLandUseType', landUseType.value)
  }

  // Track API call conditions
  const lastApiCallLocation = ref(null)
  const MWhPerYearPerHectare = ref(1850)
  const carbonOffsetPerYearPerHectare = ref(650)
  const kmDiff = ref(50) // Distance in kilometers before making a new API call

  const handleLocationUpdate = (loc) => {
    latitude.value = loc.latitude
    longitude.value = loc.longitude
    center.value = [loc.longitude, loc.latitude]
    calculatePotential(loc)
  }

  const toggleDraw = () => {
    drawEnabled.value = !drawEnabled.value
  }

  const handleDrawEnd = (area, geometry) => {
    drawEnabled.value = false
    
    // Add the new polygon to the array with current land use type
    polygons.value.push({
      geometry,
      area,
      type: landUseType.value
    })
    
    console.log('Added polygon', polygons.value.length, 'Total area:', selectedArea.value)
    
    // Update calculations with the new area using current coefficients
    if (selectedArea.value) {
      // Convert selected area to number of 1000 sqm units
      const areaHectares = selectedArea.value / 10000 // Convert to hectares
      console.log('updated calculations with coefficients:', MWhPerYearPerHectare.value, carbonOffsetPerYearPerHectare.value)
      return {
        energyProduction: areaHectares * MWhPerYearPerHectare.value,
        carbonOffset: areaHectares * carbonOffsetPerYearPerHectare.value
      }
    }
    
    return null
  }

  const clearPolygons = () => {
    polygons.value = []
  }

  const handleCenterChange = (newCenter) => {
    center.value = newCenter
    longitude.value = newCenter[0]
    latitude.value = newCenter[1]
  }

  const handleZoomChange = (newZoom) => {
    zoom.value = newZoom
  }

  const calculatePotential = async (loc) => {
    // if we have a lastApiCallLocation, we need to check if the new location is too close to the last one
    if (lastApiCallLocation.value) {
      const distance = getDistance(
        [lastApiCallLocation.value.longitude, lastApiCallLocation.value.latitude],
        [loc.longitude, loc.latitude]
      ) / 1000 // Convert meters to kilometers
      
      if (distance < kmDiff.value) {
        console.log('not recalculating because distance is too short', distance)
        return null
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
          area: 10000, // we always want to calculate the potential for one hectare
          landUseType: landUseType.value
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      lastApiCallLocation.value = loc
      MWhPerYearPerHectare.value = data.energyProduction
      carbonOffsetPerYearPerHectare.value = data.carbonOffset
      console.log('coefficients updated:', {
        MWh: MWhPerYearPerHectare.value,
        carbon: carbonOffsetPerYearPerHectare.value
      })
      return data
    } catch (e) {
      console.error('Calculation error:', e)
      throw new Error('Failed to calculate potential. Please try again.')
    }
  }

  return {
    // State
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
    
    // Methods
    handleLocationUpdate,
    toggleDraw,
    handleDrawEnd,
    clearPolygons,
    toggleLandUseType,
    handleCenterChange,
    handleZoomChange,
    calculatePotential
  }
}
