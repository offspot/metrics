<script setup lang="ts">
import { useTotalUsageStore } from '../stores/totalUsage'
const totalUsageStore = useTotalUsageStore()
</script>

<template>
  <v-card-title>Total usage</v-card-title>
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
        <v-list-item-title class="font-weight-medium text-body-2 mx-4 my-5">
          {{ item.package }}
        </v-list-item-title>

        <template #append>
          <div class="d-flex align-center">
            <div class="me-2" style="inline-size: 4.875rem">
              <v-progress-linear
                :model-value="totalUsageStore.itemPercentage(item)"
                :color="totalUsageStore.itemColor(item)"
                bg-color="blue-grey"
                height="8"
                rounded-bar
                rounded
              />
            </div>
            <span class="activity text-body-1">{{
              totalUsageStore.itemLabel(item)
            }}</span>
          </div>
        </template>
      </v-list-item>
    </v-list>
  </v-card-text>
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
  min-width: 3em;
  text-align: right;
}
</style>
