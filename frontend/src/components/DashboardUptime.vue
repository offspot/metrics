<script setup lang="ts">
import VueApexCharts from 'vue3-apexcharts'
import { useUptimeStore } from '../stores/uptime'
import { useMainStore } from '../stores/main'
import { computed } from 'vue'
const uptimeStore = useUptimeStore()
const mainStore = useMainStore()

const chartOptions = computed(() => {
  return {
    chart: { type: 'radialBar' },
    plotOptions: {
      radialBar: {
        offsetY: 10,
        startAngle: -140,
        endAngle: 140,
        hollow: { size: '50%' },
        track: {
          show: false,
        },
        dataLabels: {
          name: {
            show: false,
          },
          value: {
            offsetY: 10,
            fontSize: '32px',
            fontWeight: '600',
            fontFamily: 'Avenir',
            formatter: () => uptimeStore.legend,
          },
        },
      },
    },
    fill: {
      type: 'gradient',
      gradient: {
        type: 'horizontal',
        colorStops: [
          {
            offset: 0,
            color: 'rgb(59,233,159)',
            opacity: 0.4,
          },
          {
            offset: 100,
            color: 'rgb(125,255,75)',
            opacity: 1,
          },
        ],
      },
    },
    stroke: { dashArray: 10 },
  }
})
</script>

<template>
  <v-card-title>Uptime</v-card-title>
  <div v-if="uptimeStore.kpiValue" class="container data">
    <VueApexCharts
      id="box"
      :options="chartOptions"
      :series="uptimeStore.series"
      height="250px"
    />

    <v-card-subtitle class="pt-2">During selected period</v-card-subtitle>
    <v-card-text>
      <span class="text-subtitle-1 font-weight-medium">{{
        mainStore.date_part_1
      }}</span>
      <span class="text-h5 font-weight-bold">{{ mainStore.date_part_2 }}</span>
      <span class="text-subtitle-1 font-weight-medium">{{
        mainStore.date_part_3
      }}</span>
    </v-card-text>
  </div>

  <div v-else class="container">
    <v-card-text>No data</v-card-text>
  </div>
</template>

<style scoped>
.container {
  min-height: 152px;
}
#box {
  position: absolute;
  top: -20px;
  right: -50px;
}
.data .v-card-text {
  position: absolute;
  bottom: 0px;
}
</style>
