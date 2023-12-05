<script setup lang="ts">
import { useMainStore } from '../stores/main'
const main = useMainStore()
</script>

<template>
  <h4>Package Popularity:</h4>
  <code>{{ main.getCurrentKpiValue(2001) }}</code>
</template>

<style scoped>
code {
  font-size: xx-small;
  line-height: 0;
}
</style>
