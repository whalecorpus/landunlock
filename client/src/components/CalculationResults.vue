<template>
  <div class="results-container">
    <div v-if="area" class="calculation-results">
      <div class="main-result">
        <p>
          With your <span class="highlight">{{ formatArea(area) }}</span> of solar panels,
          you would produce <span class="highlight">{{ (area / 10000 * MWhPerYearPerHectare).toFixed(2) }} MWh</span> per year.
        </p>
      </div>

      <div class="context">
        <p class="carbon-offset">
          Carbon offset: {{ (area /10000 * carbonOffsetPerYearPerHectare).toFixed(1) }} tons CO₂e per year. <br> <span id="carbon-metaphor">Equivalent to {{ carbonMetaphor(area / 10000 * carbonOffsetPerYearPerHectare) }}. </span>
        </p>
      </div>
    </div>

    <div v-if="forestArea && forestResults" class="forest-calculation-results">
      <div class="main-result">
        <p>
          With <span class="highlight">{{ formatArea(forestArea) }}</span> of {{ mapForestType(forestResults.type) }} forest,
          you would sequester about <span class="highlight">{{ ((forestArea / 10000) * forestResults.oneYearPotential).toFixed(1) }} tons CO₂e</span> in the first year and,
          and <span class="highlight">{{ ((forestArea / 10000) * forestResults.twentyYearPotential).toFixed(1) }} tons CO₂e</span> over 20 years.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  area: {
    type: Number,
    required: false
  },
  MWhPerYearPerHectare: {
    type: Number,
    required: false
  },
  carbonOffsetPerYearPerHectare: {
    type: Number,
    required: false
  },
  forestArea: {
    type: Number,
    required: false
  },
  forestResults: {
    type: Object,
    required: false,
    validator: (value) => {
      if (!value) return true
      return 'type' in value && 'oneYearPotential' in value && 'twentyYearPotential' in value
    }
  }
})

const formatArea = (areaInSqMeters) => {
  if (areaInSqMeters >= 10000) {
    return `${(areaInSqMeters / 10000).toFixed(2)} hectares`
  }
  return `${areaInSqMeters.toFixed(5)} sq. meters`
}

const mapForestType = (type) => {
  switch (type) {
    case 'other broadleaf':
      return 'broadleaf'
    case 'other conifer':
      return 'conifer'
    case 'Mangrove Restoration - shrub':
      return 'mangrove shrub'
    case 'Mangrove Restoration - tree':
      return 'mangrove tree'
    case 'Natural Regeneration':
      return 'generic native'
    default:
      return type
  }
}

const carbonMetaphor = (effectiveCarbon) => {
  // Array of carbon equivalencies with their coefficients and descriptions
  const carbonEquivalencies = [
    {
      verb: 'stopping',
      activity: 'transatlantic flights',
      coefficient: 250, // source: Jae
    },
    {
      verb: 'taking',
      activity: 'cars off the road for one year',
      coefficient: 4.6, // tons CO2 per car per year; https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle
    },
    {
      verb: 'offsetting',
      activity: 'US households\' annual energy usage',
      coefficient: 4.798, // tons CO2 per avg US household per year; https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references; "Home electricity use"
    },
    {
      verb: 'offsetting',
      activity: 'barrels of oil',
      coefficient: 0.43, // tons CO2 per barrel of oil; https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references; "Barrels of oil consumed"
    },
    {
      verb: 'recycling',
      activity: 'tons of waste instead of putting in landfill',
      coefficient: 2.83, // tons CO2e per ton of waste; https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references; "Tons of waste recycled instead of landfilled"
    },
    {
      verb: 'avoiding',
      activity: 'kilograms of beef consumption',
      coefficient: 0.071, // tons CO2e difference between beef-heavy and plant-based diet; https://ourworldindata.org/carbon-footprint-food-methane
    },
    {
      verb: 'eliminating',
      activity: 'smartphone productions',
      coefficient: 0.07, // tons CO2e per smartphone; https://www.apple.com/environment/pdf/products/iphone/iPhone_12_PER_Oct2020.pdf
    },
    {
      verb: "cancelling out USA's 2020 emissions",
      activity: 'times',
      coefficient: 4230000, // tons CO2 emitted by US in 2020
    },
  ]

  // Find an appropriate equivalency, from random sorting
  const getEquivalency = (carbonAmount) => {
    // Shuffle array copy to randomize order
    for (const eq of [...carbonEquivalencies].sort(() => Math.random() - 0.5)) {
      const number = Math.round(carbonAmount / eq.coefficient)
      if (number >= 1 && number <= 1000) { // Reasonable range for comparison
        return `${eq.verb} ${number} ${eq.activity}`
      }
    }
    // Fallback to flights if no other good comparison found
    const flights = Math.round(carbonAmount / carbonEquivalencies[0].coefficient)
    return `${carbonEquivalencies[0].verb} ${flights} ${carbonEquivalencies[0].activity}`
  }

  return getEquivalency(effectiveCarbon)
}

</script>

<style scoped>
.results-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.calculation-results,
.forest-calculation-results {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.main-result {
  font-size: 1.2rem;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.context {
  color: #4a5568;
  margin-bottom: 1rem;
}

.highlight {
  color: #42b983;
  font-weight: 600;
}

.carbon-offset {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #edf2f7;
  color: #2c5282;
  font-weight: 500;
}

#carbon-metaphor {
  font-size: 0.8rem;
  color: #4a5568;
}

/* .forest-calculation-results .highlight {
  color: #2c5282;
} */
</style> 
