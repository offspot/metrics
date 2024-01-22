<script setup lang="ts">
import { usePackagePopularityStore } from '../stores/packagePopularity'
const packagePopularityStore = usePackagePopularityStore()
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

const props = withDefaults(
  defineProps<{
    package: string
    visits: number
    total: number
    inverted: boolean
  }>(),
  { inverted: false },
)

const percentage = computed(() => {
  const value = (100.0 * props.visits) / props.total
  if (value < 10) {
    return value.toFixed(1)
  } else {
    return value.toFixed(0)
  }
})

const chartOptions = computed(() => {
  return {
    chart: { type: 'radialBar', height: '180px' },
    plotOptions: {
      radialBar: {
        track: {
          opacity: 0.1,
          background: '#020202',
          strokeWidth: '50%',
        },
        dataLabels: {
          name: {
            show: false,
          },
          value: {
            offsetY: 10,
            fontSize: '1.8em',
            fontWeight: '600',
            formatter: () => `${percentage.value} %`,
          },
        },
      },
    },
    fill: {
      type: 'solid',
      opacity: 1,
      colors: [
        props.inverted
          ? '#000000'
          : packagePopularityStore.packageColor(props.package),
      ],
    },
    stroke: {
      lineCap: 'round',
    },
  }
})

const cardStyle = computed(() =>
  props.inverted
    ? {
        'background-color': packagePopularityStore.packageColor(props.package),
      }
    : {},
)
</script>

<template>
  <v-card :style="cardStyle">
    <div class="d-flex">
      <div class="chart-container">
        <VueApexCharts
          :options="chartOptions"
          :series="[percentage]"
          height="180px"
        />
      </div>
      <div class="ml-4 mt-4">
        <div class="package-name">{{ props.package }}</div>
        <div class="nb-visits">
          <span>{{ props.visits }}</span> sessions
        </div>
      </div>
    </div>
  </v-card>
</template>

<style scoped>
.nb-visits {
  position: absolute;
  bottom: 30px;
  font-size: 0.9em;
}
.nb-visits span {
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  border-width: 4px;
  border-color: rgba(0, 0, 0, 0);
  border-style: solid;
  padding: 2px 4px;
}

.package-name {
  font-size: 1.2em;
  font-weight: bold;
}

.chart-container {
  position: relative;
  top: -10px;
  height: 130px;
  width: 130px;
}
</style>
