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
  const lastSolarApiCallLocation = ref(null)
  const lastForestApiCallLocation = ref(null)
  const MWhPerYearPerHectare = ref(1850)
  const carbonOffsetPerYearPerHectare = ref(650)
  const kmDiff = ref(50) // Distance in kilometers before making a new API call

  const handleLocationUpdate = (loc) => {
    latitude.value = loc.latitude
    longitude.value = loc.longitude
    center.value = [loc.longitude, loc.latitude]
    calculateSolarPotential(loc)
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
      
      if (landUseType.value === 'solar') {
        return {
          energyProduction: areaHectares * MWhPerYearPerHectare.value,
          carbonOffset: areaHectares * carbonOffsetPerYearPerHectare.value
        }
      } else {
        // For forest, we'll return null since the results will come from the API
        return null
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

  const calculateSolarPotential = async (loc) => {
    // if we have a lastSolarApiCallLocation, we need to check if the new location is too close to the last one
    if (lastSolarApiCallLocation.value) {
      const distance = getDistance(
        [lastSolarApiCallLocation.value.longitude, lastSolarApiCallLocation.value.latitude],
        [loc.longitude, loc.latitude]
      ) / 1000 // Convert meters to kilometers
      
      if (distance < kmDiff.value) {
        console.log('not recalculating solar potential because distance is too short', distance)
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
          landUseType: 'solar'
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      lastSolarApiCallLocation.value = loc
      
      // Ensure we have valid numbers before updating
      if (typeof data.energyProduction === 'number' && !isNaN(data.energyProduction)) {
        MWhPerYearPerHectare.value = data.energyProduction
      } else {
        console.error('Invalid energy production data:', data.energyProduction)
      }
      if (typeof data.carbonOffset === 'number' && !isNaN(data.carbonOffset)) {
        carbonOffsetPerYearPerHectare.value = data.carbonOffset
      } else {
        console.error('Invalid carbon offset data:', data.carbonOffset)
      }
      
      console.log('coefficients updated:', {
        MWh: MWhPerYearPerHectare.value,
        carbon: carbonOffsetPerYearPerHectare.value
      })
      return data
    } catch (e) {
      console.error('Calculation error:', e)
      // Return default values on error
      return {
        energyProduction: MWhPerYearPerHectare.value,
        carbonOffset: carbonOffsetPerYearPerHectare.value
      }
    }
  }

  const calculateForestPotential = async (loc) => {
    // if we have a lastForestApiCallLocation, we need to check if the new location is too close to the last one
    if (lastForestApiCallLocation.value) {
      const distance = getDistance(
        [lastForestApiCallLocation.value.longitude, lastForestApiCallLocation.value.latitude],
        [loc.longitude, loc.latitude]
      ) / 1000 // Convert meters to kilometers
      
      if (distance < kmDiff.value) {
        console.log('not recalculating forest potential because distance is too short', distance)
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
          landUseType: 'reforestation'
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      lastForestApiCallLocation.value = loc
      return consolidateData(data)
    } catch (e) {
      console.error('Calculation error:', e)
      throw new Error('Failed to calculate potential. Please try again.')
    }
  }

  /**
   * Consolidates the data from the API into an array of objects with a type and its first-year and twenty year carbon potential
   * A lot of room for expansion here; and user input could be used to select the type of tree
   * @param {*} data 
   * @returns 
   */
  const consolidateData = (data) => {
    let forestResults = []
  
    const addForestType = (type, potential) => {
      if (potential === 'N/A') return
      const oneYear = potential.potential_removal_one_year_tCO2e
      if (oneYear === 'N/A') return
      const twentyYear = potential.cumulative_removal_tCO2e[19]
      forestResults.push({
        type: type,
        oneYearPotential: oneYear,
        twentyYearPotential: twentyYear
      })
    }
  
    // Add all non-N/A forest types in both categories
    Object.entries(data.forestResults['Plantations and Woodlots']).forEach(([type, potential]) => {
      addForestType(type, potential)
    })
  
    Object.entries(data.forestResults['Other Forest Types']).forEach(([type, potential]) => {
      addForestType(type, potential)
    })
  
    console.log('forestResults', forestResults)
    return forestResults
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
    calculateSolarPotential,
    calculateForestPotential
  }
}
