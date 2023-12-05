<script setup lang="ts">
import { useMainStore } from '../stores/main'
const main = useMainStore()
</script>

<template>
  <h4>Total Usage:</h4>
  <code>{{ main.getCurrentKpiValue(2003) }}</code>
</template>

<style scoped>
code {
  font-size: xx-small;
  line-height: 0;
}
</style>
