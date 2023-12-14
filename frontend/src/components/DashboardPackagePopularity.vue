<script setup lang="ts">
import { useMainStore } from '../stores/main'
import { kpiIds } from '../constants'
const store = useMainStore()
</script>

<template>
  <h4>Package Popularity:</h4>
  <code>{{ store.getCurrentKpiValue(kpiIds.packagePopularity) }}</code>
</template>

<style scoped>
code {
  font-size: xx-small;
  line-height: 0;
}
</style>
