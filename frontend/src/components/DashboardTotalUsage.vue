<script setup lang="ts">
import { useTotalUsageStore } from '../stores/totalUsage'
const totalUsageStore = useTotalUsageStore()
import DashboardRadialGraph from './DashboardRadialGraph.vue'
</script>

<template>
  <v-card-title>Total usage</v-card-title>
  <div v-if="totalUsageStore.kpiValue">
    <v-card-subtitle class="pt-2"
      >Total of {{ totalUsageStore.totalValue }} hours</v-card-subtitle
    >
    <span id="legend" class="text-disabled">TIME</span>
    <v-card-text class="ps-0 pb-0">
      <v-list>
        <v-list-item
          v-for="item in totalUsageStore.firstItems"
          :key="item.package"
        >
          <div class="d-flex align-center">
            <div class="flex-0-0 chart-container">
              <DashboardRadialGraph
                :package="item.package"
                :value="item.minutesActivity"
                :total="totalUsageStore.kpiValue.totalMinutesActivity"
              />
            </div>
            <div class="flex-1-1 mx-4 my-5 package">
              {{ item.package }}
            </div>
            <div class="flex-0-0 ms-2 value">
              {{ totalUsageStore.itemLabel(item) }}
            </div>
          </div>
        </v-list-item>
      </v-list>
    </v-card-text>
  </div>
  <div v-else>
    <v-card-text> No data </v-card-text>
  </div>
</template>

<style scoped>
.chart-container {
  max-height: 60px;
  margin-top: -30px;
  margin-left: -10px;
  width: 80px;
}

.v-card-title {
  font-size: 1.3rem;
  padding-top: 1.2rem;
}

.v-card-subtitle {
  font-size: 0.95rem;
}

.package {
  hyphens: auto;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  word-break: normal;
  word-wrap: break-word;
  padding: 0;
  font-size: 1.1rem;
}

.value {
  font-size: 1.2rem;
}

#legend {
  position: absolute;
  top: 7em;
  right: 2.4em;
  font-size: small;
  z-index: 2;
}
</style>
