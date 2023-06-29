<script setup>
import { useMainStore } from './stores/main'
const main = useMainStore()
</script>

<template>
  <div class="header d-flex align-items-center">
    <div class="spinner" v-if="main.is_loading">
      <font-awesome-icon icon="spinner" size="xl" spin />
    </div>
    <div class="title">Offspot Metrics</div>
  </div>
  <div class="content">
    <router-view></router-view>
  </div>
</template>

<style scoped>
div.header {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4em;
  background-color: #ffa256;
}

div.content {
  position: absolute;
  top: 6em;
  width: 100%;
  left: 0;
  padding-left: 2em;
  padding-right: 2em;
}

div.spinner {
  position: absolute;
  margin-left: 2em;
}

div.title {
  margin-left: 8em;
  font-weight: bold;
  color: white;
}
</style>
