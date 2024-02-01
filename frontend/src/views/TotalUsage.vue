<script setup lang="ts">
import PackageElement from '../components/PackageElement.vue'

import { useTotalUsageStore } from '../stores/totalUsage'
const totalUsageStore = useTotalUsageStore()
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
        return totalUsageStore.kpiValue.items[opt.dataPointIndex].package
      },
      style: {
        colors: ['#000'],
      },
    },
    xaxis: {
      labels: {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        formatter: function (val: any, _: any) {
          return `${val} %`
        },
      },
      axisTicks: {
        color: '#333333',
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
    colors: totalUsageStore.kpiValue.items.map((item) =>
      totalUsageStore.packageColor(item.package),
    ),
  }
})

const series = computed(() => {
  return [
    {
      data: totalUsageStore.kpiValue.items.map(
        (item) =>
          (100 * item.minutesActivity) /
          totalUsageStore.kpiValue.totalMinutesActivity,
      ),
    },
  ]
})
</script>

<template>
  <v-container class="pa-4">
    <v-row>
      <v-col cols="12" md="6" lg="4" class="d-flex flex-column pt-0">
        <div v-if="lgAndUp" id="total-usage" class="title">Total usage</div>
        <div v-if="lgAndUp" id="total-hours">
          Total of
          {{
            totalUsageStore.valueInHours(
              totalUsageStore.kpiValue.totalMinutesActivity,
            )
          }}
          hours
        </div>
        <div id="first-package">
          <PackageElement
            v-if="totalUsageStore.kpiValue.items.length > 0 && lgAndUp"
            :value="
              totalUsageStore.valueInHours(
                totalUsageStore.kpiValue.items[0].minutesActivity,
              )
            "
            :package="totalUsageStore.kpiValue.items[0].package"
            :total="
              totalUsageStore.valueInHours(
                totalUsageStore.kpiValue.totalMinutesActivity,
              )
            "
            label="hours"
          />
        </div>
      </v-col>
      <v-col cols="12" lg="8">
        <v-card>
          <div class="mt-4 ml-6">
            <div v-if="!lgAndUp" id="package-popularity" class="title">
              Total usage
            </div>
            <div v-if="!lgAndUp" id="total-hours">
              Total of
              {{ totalUsageStore.kpiValue.totalMinutesActivity }} hours
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
        v-if="totalUsageStore.kpiValue.items.length > 0 && !lgAndUp"
        cols="12"
        md="6"
        lg="4"
      >
        <PackageElement
          v-if="totalUsageStore.kpiValue.items.length > 0"
          :value="
            totalUsageStore.valueInHours(
              totalUsageStore.kpiValue.items[0].minutesActivity,
            )
          "
          :package="totalUsageStore.kpiValue.items[0].package"
          :total="
            totalUsageStore.valueInHours(
              totalUsageStore.kpiValue.totalMinutesActivity,
            )
          "
          label="hours"
        />
      </v-col>
      <v-col v-for="item_no in 10" :key="item_no" cols="12" md="6" lg="4">
        <PackageElement
          v-if="totalUsageStore.kpiValue.items.length > item_no"
          :value="
            totalUsageStore.valueInHours(
              totalUsageStore.kpiValue.items[item_no].minutesActivity,
            )
          "
          :package="totalUsageStore.kpiValue.items[item_no].package"
          :total="
            totalUsageStore.valueInHours(
              totalUsageStore.kpiValue.totalMinutesActivity,
            )
          "
          label="hours"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
#total-usage {
  margin-top: 1.4rem;
  font-size: 1.4rem;
}

.title {
  font-size: 1.4rem;
  font-weight: bold;
  color: #4b465c;
}

#total-hours {
  margin-top: 1em;
  font-size: 1rem;
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
