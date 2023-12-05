<script setup lang="ts">
import { useMainStore } from '../stores/main'
const main = useMainStore()
</script>

<template>
  <h4>Shared Files:</h4>
  <code>{{ main.getAllKpiValues(2005) }}</code>
</template>

<style scoped>
code {
  font-size: xx-small;
  line-height: 0;
}
</style>
