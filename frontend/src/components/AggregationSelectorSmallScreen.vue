<script setup lang="ts">
import { computed, ref } from 'vue'
import { useMainStore } from '../stores/main'

const mainStore = useMainStore()
const isOpen = ref(false)

const toggleOpen = () => {
  isOpen.value = !isOpen.value
}

const height = computed(() => (isOpen.value ? '200px' : '15px'))
</script>

<template>
  <div id="selector1" :style="{ height: height }">
    <div v-if="isOpen">
      <div id="select-timeline" class="pt-2 pb-2">Select timeline</div>
      <div id="agg-selector">
        <v-btn-toggle
          divided
          mandatory
          density="compact"
          rounded
          :model-value="mainStore.aggregationKind"
          @update:model-value="
            (newValue) => mainStore.setAggregationKind(newValue)
          "
        >
          <v-btn value="D"> Day </v-btn>

          <v-btn value="W"> Week </v-btn>

          <v-btn value="M"> Month </v-btn>

          <v-btn value="Y"> Year </v-btn>
        </v-btn-toggle>
      </div>
      <div class="pt-4 pb-4 font-weight-bold">
        <div v-if="mainStore.hasAggregationValues">
          <span class="text-subtitle-1 font-weight-medium">{{
            mainStore.date_part_1
          }}</span>
          <span class="text-h5 font-weight-bold">{{
            mainStore.date_part_2
          }}</span>
          <span class="text-subtitle-1 font-weight-medium">{{
            mainStore.date_part_3
          }}</span>
        </div>
        <span v-else>No data</span>
      </div>
      <div id="prev-next">
        <v-btn
          min-width="10em"
          prepend-icon="fas fa-arrow-left"
          variant="flat"
          :disabled="!mainStore.hasPrevAggregationValue"
          @click="mainStore.toPreviousAggregrationValue"
        >
          Previous
        </v-btn>
        <span>&nbsp;</span>
        <v-btn
          min-width="10em"
          append-icon="fas fa-arrow-right"
          variant="flat"
          :disabled="!mainStore.hasNextAggregationValue"
          @click="mainStore.toNextAggregationValue"
        >
          Next
        </v-btn>
      </div>
    </div>
  </div>
  <div id="selector2" @click="toggleOpen">
    <div v-if="isOpen" id="apply-btn">APPLY</div>
    <div v-else-if="mainStore.hasAggregationValues">
      <span class="text-subtitle-1 font-weight-medium">{{
        mainStore.date_part_1
      }}</span>
      <span class="text-h5 font-weight-bold">{{ mainStore.date_part_2 }}</span>
      <span class="text-subtitle-1 font-weight-medium">{{
        mainStore.date_part_3
      }}</span>
    </div>
    <div v-else>No data</div>
  </div>
</template>

<style scoped>
#selector1 {
  background-color: #7266ed;
  text-align: center;
  color: white;
}
#selector2 {
  background-color: #7266ed;
  width: 220px;
  color: white;
  text-align: center;
  margin-left: auto;
  margin-right: auto;
  border-radius: 0 0 6px 6px;
}
#selector2 div {
  padding-top: 0.5em;
  padding-bottom: 0.5em;
}
#select-timeline {
  width: 300px;
  text-align: left;
  margin-left: auto;
  margin-right: auto;
  font-size: 0.9rem !important;
}

#apply-btn {
  letter-spacing: 0.1em;
  font-weight: bold;
}

#agg-selector .v-btn-group {
  border-radius: 20px;
}

#agg-selector .v-btn {
  text-transform: none;
  background-color: #4f4ad6;
  color: white;
}

#agg-selector .v-btn--active {
  background-color: #2d2f90;
}

#prev-next .v-btn {
  border-radius: 30px;
  text-transform: none;
  background-color: #4f4bed;
  color: white;
}

#prev-next .v-btn--disabled {
  background-color: #e2e1e4;
}
</style>
