<script setup lang="ts">
import { useMainStore } from '../stores/main'
const mainStore = useMainStore()
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

const props = withDefaults(
  defineProps<{
    package: string
    value: number
    total: number
  }>(),
  {},
)

const percentage = computed(() => {
  const value = (100.0 * props.value) / props.total
  if (value < 10) {
    return value.toFixed(1)
  } else {
    return value.toFixed(0)
  }
})

const chartOptions = computed(() => {
  return {
    chart: { type: 'radialBar', height: '110px' },
    plotOptions: {
      radialBar: {
        track: {
          opacity: 0.1,
          background: '#020202',
          strokeWidth: '50%',
          margin: 3,
        },
        dataLabels: {
          name: {
            show: false,
          },
          value: {
            offsetY: 6,
            fontSize: '1.05rem',
            fontWeight: '400',
            formatter: () => `${percentage.value}%`,
          },
        },
      },
    },
    fill: {
      type: 'solid',
      opacity: 1,
      colors: [mainStore.getPackageColor(props.package)],
    },
    stroke: {
      lineCap: 'round',
    },
  }
})
</script>

<template>
  <VueApexCharts
    :options="chartOptions"
    :series="[percentage]"
    height="110px"
  />
</template>

<style scoped></style>
