<script setup lang="ts">
import { useMainStore } from '../stores/main'
const store = useMainStore()
</script>

<template>
  <v-col cols="12" class="d-flex py-2 align-center">
    <div class="d-flex ma-2 mb-0 align-center">
      <v-img :height="30" width="30" src="./Kiwix_logo_v3.svg"></v-img>
      <div class="pl-2 flex-1-1-100">
        <span class="float-left font-weight-black text-h6">Metrics</span>
      </div>
    </div>
    <div class="flex-1-1"></div>
    <v-app-bar-nav-icon
      class="d-lg-none"
      @click="store.toggleDrawerVisibility()"
    ></v-app-bar-nav-icon>
  </v-col>
</template>

<style scoped></style>
