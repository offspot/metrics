<script setup lang="ts">
import { useMainStore } from '../stores/main'
const main = useMainStore()
</script>

<template>
  <v-col cols="12" class="py-2 d-flex align-center">
    <div class="flex-0-1">
      <v-btn-toggle
        color="deep-purple-accent-2"
        divided
        mandatory
        density="compact"
        :model-value="main.aggregationKind"
        @update:model-value="(newValue) => main.setAggregationKind(newValue)"
      >
        <v-btn value="D"> Day </v-btn>

        <v-btn value="W"> Week </v-btn>

        <v-btn value="M"> Month </v-btn>

        <v-btn value="Y"> Year </v-btn>
      </v-btn-toggle>
    </div>
    <div class="flex-1-1">
      <span>{{ main.aggregationValue }}</span>
    </div>
    <div class="flex-0-1">
      <v-btn
        color="indigo-darken-1"
        min-width="10em"
        prepend-icon="fas fa-arrow-left"
        variant="flat"
        :disabled="!main.hasPrevAggregationValue"
        @click="main.toPreviousAggregrationValue"
      >
        Previous
      </v-btn>
      <span>&nbsp;</span>
      <v-btn
        color="indigo-darken-1"
        min-width="10em"
        append-icon="fas fa-arrow-right"
        variant="flat"
        :disabled="!main.hasNextAggregationValue"
        @click="main.toNextAggregationValue"
      >
        Next
      </v-btn>
    </div>
  </v-col>
</template>

<style scoped></style>
