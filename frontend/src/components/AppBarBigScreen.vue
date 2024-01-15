<script setup lang="ts">
import { useMainStore } from '../stores/main'
const store = useMainStore()
</script>

<template>
  <v-col cols="12" class="d-flex py-2 align-center">
    <v-app-bar-nav-icon
      class="d-lg-none"
      @click="store.toggleDrawerVisibility()"
    ></v-app-bar-nav-icon>
    <div id="agg-selector" class="flex-0-1">
      <v-btn-toggle
        class="ml-6"
        divided
        mandatory
        density="compact"
        rounded
        :model-value="store.aggregationKind"
        @update:model-value="(newValue) => store.setAggregationKind(newValue)"
      >
        <v-btn value="D"> Day </v-btn>

        <v-btn value="W"> Week </v-btn>

        <v-btn value="M"> Month </v-btn>

        <v-btn value="Y"> Year </v-btn>
      </v-btn-toggle>
    </div>
    <div id="agg-value" class="flex-1-1">
      <span
        >{{ store.date_part_1 }}{{ store.date_part_2
        }}{{ store.date_part_3 }}</span
      >
    </div>
    <div id="prev-next" class="flex-0-1">
      <v-btn
        min-width="10em"
        prepend-icon="fas fa-arrow-left"
        variant="flat"
        :disabled="!store.hasPrevAggregationValue"
        @click="store.toPreviousAggregrationValue"
      >
        Previous
      </v-btn>
      <span>&nbsp;</span>
      <v-btn
        min-width="10em"
        append-icon="fas fa-arrow-right"
        variant="flat"
        :disabled="!store.hasNextAggregationValue"
        @click="store.toNextAggregationValue"
      >
        Next
      </v-btn>
    </div>
  </v-col>
</template>

<style scoped>
.hidden {
  display: none;
}

#agg-value {
  text-align: center;
}

#agg-selector .v-btn-group {
  border-radius: 20px;
}

#agg-selector .v-btn {
  text-transform: none;
  background-color: rgba(24, 24, 179, 0.34);
  color: #3858cc;
}

#agg-selector .v-btn--active {
  background-color: #dbdafb;
}

#prev-next .v-btn {
  border-radius: 30px;
  text-transform: none;
  background-color: #4f4bed;
  color: white;
}

#prev-next .v-btn--disabled {
  background-color: #d9d7e2;
}
</style>
