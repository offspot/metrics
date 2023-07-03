<script setup>
import { useMainStore } from './stores/main'
const main = useMainStore()
</script>

<template>
  <div class="header d-flex align-items-center">
    <div class="container-fluid">
      <div class="row">
        <div class="col-2 col-md-1">
          <div class="spinner" v-if="main.is_loading">
            <font-awesome-icon icon="spinner" size="xl" spin />
          </div>
        </div>
        <div class="col-10 col-md-3 title">
          Offspot Metrics
        </div>
        <div class="col-12 col-md-8 error">
          <div class="">{{ main.error }}</div>
        </div>
      </div>
    </div>
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

div.title {
  font-weight: bold;
  color: white;
  text-align: left;
}

div.error {
  color: red;
  text-align: right;
}
</style>
