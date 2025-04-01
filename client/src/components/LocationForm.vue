<!-- LocationForm.vue -->
<template>
    <form @submit.prevent="handleSubmit" class="location-form">
      <div class="form-group">
          <label for="Address">Address</label>
          <input
            type="string"
            id="address"
            v-model="address"
          />
      </div>

      <div class="form-group">
        <label for="latitude">Latitude:</label>
        <input 
          type="number" 
          id="latitude" 
          v-model="latitude" 
          step="any"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="longitude">Longitude:</label>
        <input 
          type="number" 
          id="longitude" 
          v-model="longitude" 
          step="any"
          required
        />
      </div>
  
      <button type="submit" class="submit-button">Update Location</button>
    </form>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  
  const emit = defineEmits(['update-location'])
  
  const latitude = defineModel('latitude');
  const longitude = defineModel('longitude');
  
  const handleSubmit = () => {
    // geocodeAddress(address.value);
    
    emit('update-location', {
      latitude: parseFloat(latitude.value),
      longitude: parseFloat(longitude.value)
    })
  }
  </script>
  
  <style scoped>
  .location-form {
    padding: 1rem;
    background: white;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }
  
  input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  .submit-button {
    width: 100%;
    padding: 0.5rem;
    background: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .submit-button:hover {
    background: #45a049;
  }
  </style>
