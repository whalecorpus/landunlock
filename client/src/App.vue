<script setup>
import HelloWorld from './components/HelloWorld.vue'
import TheWelcome from './components/TheWelcome.vue'
import { Map, Layers, Sources } from "vue3-openlayers";
</script>

<template>
  <header>
    <img alt="Vue logo" class="logo" src="./assets/logo.svg" width="125" height="125" />

    <h2>Map</h2>
    <div class="wrapper">
      <Map.OlMap style="min-width: 400px; min-height: 400px;">
        <Map.OlView :center="[40, 40]" :zoom="5" projection="EPSG:4326" />
        <Layers.OlTileLayer>
          <Sources.OlSourceOsm />
        </Layers.OlTileLayer>
      </Map.OlMap>
    </div>
  </header>

  <main>
  </main>
</template>

<style scoped>
</style>
