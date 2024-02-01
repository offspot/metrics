<script setup lang="ts">
import { usePackagePopularityStore } from '../stores/packagePopularity'
const packagePopularityStore = usePackagePopularityStore()
import DashboardRadialGraph from './DashboardRadialGraph.vue'
</script>

<template>
  <v-card-title>Package popularity</v-card-title>
  <div v-if="packagePopularityStore.kpiValue">
    <v-card-subtitle class="pt-2"
      >Total of
      {{ packagePopularityStore.kpiValue.totalVisits }}
      sessions</v-card-subtitle
    >
    <span id="legend" class="text-disabled">SESSIONS</span>
    <v-card-text class="ps-0 pb-0">
      <v-list>
        <v-list-item
          v-for="item in packagePopularityStore.firstItems"
          :key="item.package"
          class="my-3"
        >
          <div class="d-flex align-center">
            <div class="flex-0-0 chart-container">
              <DashboardRadialGraph
                :package="item.package"
                :value="item.visits"
                :total="packagePopularityStore.kpiValue.totalVisits"
              />
            </div>
            <div class="flex-1-1 mx-4 my-5 package">
              {{ item.package }}
            </div>
            <div class="flex-0-0 ms-2 value">
              {{ packagePopularityStore.itemLabel(item) }}
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
  top: 9.3em;
  right: 3.4em;
  font-size: x-small;
  z-index: 2;
}
</style>
