<template>
  <!-- Background -->
  <div class="silk-container">
    <Silk
      :speed="4"
      :scale="0.75"
      :color="'#171F26'"
      :noise-intensity="0.75"
      :rotation="0"
      class="silk"
    />
  </div>

  <!-- Foreground UI -->
  <div class="app-content">
    <Nav />
    <main class="pt-20">
      <Transition name="fade" mode="out-in">
        <router-view :key="$route.fullPath" />
      </Transition>
    </main>
  </div>
</template>

<script setup lang="ts">
import Silk from './Silk.vue'
import Nav from './views/Nav.vue'
</script>

<style scoped>
/* Background */
.silk-container {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  z-index: -1;
}

.silk {
  width: 100%;
  height: 100%;
}

/* Foreground */
.app-content {
  position: relative;
  min-height: 100vh;
  color: white;
}
</style>
