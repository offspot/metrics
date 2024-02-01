<script setup lang="ts">
import VueApexCharts from 'vue3-apexcharts'
import { useSharedFilesStore } from '../stores/sharedFiles'
import { computed } from 'vue'
const sharedFilesStore = useSharedFilesStore()

const chartOptions = computed(() => {
  return {
    chart: {
      height: 220,
      type: 'line',
      zoom: {
        enabled: false,
      },
      animations: {
        enabled: false,
      },
      toolbar: {
        show: false,
      },
    },
    legend: {
      horizontalAlign: 'left',
      markers: {
        width: 25,
        height: 3,
        offsetY: -2,
        offsetX: -6,
      },
      itemMargin: {
        horizontal: 15,
      },
    },
    stroke: {
      width: [3, 3],
      curve: 'straight',
    },
    colors: ['#28c56f', '#ca0033'],
    labels: sharedFilesStore.labels,
    markers: {
      size: 3,
      colors: 'white',
      strokeColors: ['#28c56f', '#ca0033'],
      strokeWidth: 3,
      strokeOpacity: 1,
      hover: {
        sizeOffset: 2,
      },
    },
    xaxis: {
      axisBorder: {
        show: false,
      },
      labels: {
        show: false,
      },
      tooltip: {
        enabled: false,
      },
    },
    yaxis: {
      labels: {
        show: false,
      },
    },
    grid: {
      strokeDashArray: 7,
      xaxis: {
        lines: {
          show: true,
        },
      },
      yaxis: {
        lines: {
          show: false,
        },
      },
    },
  }
})

const series = computed(() => {
  return [
    {
      name: 'Added',
      data: sharedFilesStore.values?.map((value) =>
        value ? value.filesCreated : null,
      ),
    },
    {
      name: 'Removed',
      data: sharedFilesStore.values?.map((value) =>
        value ? value.filesDeleted : null,
      ),
    },
  ]
})
</script>

<template>
  <v-card-title>Shared Files</v-card-title>
  <div v-if="sharedFilesStore.hasData">
    <VueApexCharts
      id="box"
      :options="chartOptions"
      :series="series"
      height="220px"
    />
  </div>
  <div v-else>
    <v-card-text>No data</v-card-text>
  </div>
</template>

<style scoped>
.v-card-title {
  font-size: 1.3rem;
  padding-top: 1.2rem;
}
</style>
