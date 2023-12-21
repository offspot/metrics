<script setup lang="ts">
import { usePackagePopularityStore } from '../stores/packagePopularity'
const packagePopularityStore = usePackagePopularityStore()
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
        >
          <v-list-item-title class="font-weight-medium text-body-2 mx-4 my-5">
            {{ item.package }}
          </v-list-item-title>

          <template #prepend>
            <v-progress-circular
              :rotate="360"
              :size="55"
              :width="4"
              :model-value="packagePopularityStore.itemPercentage(item)"
              :color="packagePopularityStore.itemColor(item)"
            >
              <template #default>
                <span class="percentage">{{
                  packagePopularityStore.itemPercentageLabel(item)
                }}</span></template
              >
            </v-progress-circular>
          </template>
          <template #append>
            <div class="d-flex align-center">
              <span class="activity font-weight-medium text-body-1">{{
                packagePopularityStore.itemLabel(item)
              }}</span>
            </div>
          </template>
        </v-list-item>
      </v-list>
    </v-card-text>
  </div>
  <div v-else>
    <v-card-text> No data </v-card-text>
  </div>
</template>

<style scoped>
#legend {
  position: absolute;
  top: 9.3em;
  right: 3.4em;
  font-size: x-small;
  z-index: 2;
}
span.activity {
  min-width: 2.5em;
  text-align: right;
  font-size: 1.1rem !important;
}

.percentage {
  color: rgba(0, 0, 0, 0.87);
}
</style>
