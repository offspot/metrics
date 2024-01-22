<script setup lang="ts">
import PackagePopularityElement from '../components/PackagePopularityElement.vue'

import { usePackagePopularityStore } from '../stores/packagePopularity'
const packagePopularityStore = usePackagePopularityStore()
import { useDisplay } from 'vuetify'
const { lgAndUp } = useDisplay()
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

const chartOptions = computed(() => {
  return {
    chart: { type: 'bar', height: '600px', toolbar: { show: false } },
    plotOptions: {
      bar: {
        horizontal: true,
        distributed: true,
      },
    },
    dataLabels: {
      textAnchor: 'start',
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      formatter: function (_: any, opt: any) {
        return packagePopularityStore.kpiValue.items[opt.dataPointIndex].package
      },
      style: {
        colors: ['#000'],
      },
    },
    xaxis: {
      labels: {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        formatter: function (val: any, _: any) {
          return val + ' %'
        },
      },
    },
    yaxis: {
      labels: {
        show: false,
      },
    },
    legend: {
      show: false,
    },
    tooltip: {
      enabled: false,
    },
    colors: packagePopularityStore.kpiValue.items.map((item) =>
      packagePopularityStore.packageColor(item.package),
    ),
  }
})

const series = computed(() => {
  return [
    {
      data: packagePopularityStore.kpiValue.items.map(
        (item) =>
          (100 * item.visits) / packagePopularityStore.kpiValue.totalVisits,
      ),
    },
  ]
})
</script>

<template>
  <v-container class="pa-6">
    <v-row>
      <v-col cols="12" md="6" lg="4" class="d-flex flex-column pt-0">
        <div v-if="lgAndUp" id="package-popularity" class="title">
          Package popularity
        </div>
        <div v-if="lgAndUp" id="total-sessions">
          Total of {{ packagePopularityStore.kpiValue.totalVisits }} sessions
        </div>
        <div id="first-package">
          <PackagePopularityElement
            v-if="packagePopularityStore.kpiValue.items.length > 0 && lgAndUp"
            :visits="packagePopularityStore.kpiValue.items[0].visits"
            :package="packagePopularityStore.kpiValue.items[0].package"
            :total="packagePopularityStore.kpiValue.totalVisits"
            :inverted="true"
          />
        </div>
      </v-col>
      <v-col cols="12" lg="8">
        <v-card>
          <div class="mt-4 ml-6">
            <div v-if="!lgAndUp" id="package-popularity" class="title">
              Package popularity
            </div>
            <div v-if="!lgAndUp" id="total-sessions">
              Total of
              {{ packagePopularityStore.kpiValue.totalVisits }} sessions
            </div>
            <div :class="{ title: true, centered: !lgAndUp }">Top 10</div>
          </div>
          <div class="chart-container">
            <VueApexCharts
              :options="chartOptions"
              :series="series"
              height="600px"
            />
          </div>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col
        v-if="packagePopularityStore.kpiValue.items.length > 0 && !lgAndUp"
        cols="12"
        md="6"
        lg="4"
      >
        <PackagePopularityElement
          v-if="packagePopularityStore.kpiValue.items.length > 0"
          :visits="packagePopularityStore.kpiValue.items[0].visits"
          :package="packagePopularityStore.kpiValue.items[0].package"
          :total="packagePopularityStore.kpiValue.totalVisits"
          :inverted="true"
        />
      </v-col>
      <v-col v-for="item_no in 10" :key="item_no" cols="12" md="6" lg="4">
        <PackagePopularityElement
          v-if="packagePopularityStore.kpiValue.items.length > item_no"
          :visits="packagePopularityStore.kpiValue.items[item_no].visits"
          :package="packagePopularityStore.kpiValue.items[item_no].package"
          :total="packagePopularityStore.kpiValue.totalVisits"
          :inverted="false"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
#package-popularity {
  margin-top: 1.4em;
}

.title {
  font-size: 1.2em;
  font-weight: bold;
  color: #4b465c;
}

#total-sessions {
  margin-top: 1em;
  font-size: 0.8em;
  color: #908ca3;
}

#first-package {
  margin-top: auto;
}

.chart-container {
  position: relative;
  top: -10px;
}

.centered {
  text-align: center;
  margin-top: 1em;
}
</style>
