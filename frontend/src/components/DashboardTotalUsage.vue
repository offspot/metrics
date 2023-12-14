<script setup lang="ts">
import { useMainStore } from '../stores/main'
import { kpiIds } from '../constants'
const store = useMainStore()
</script>

<template>
  <h4>Total Usage:</h4>
  <code>{{ store.getCurrentKpiValue(kpiIds.totalUsage) }}</code>
</template>

<style scoped>
code {
  font-size: xx-small;
  line-height: 0;
}
</style>
