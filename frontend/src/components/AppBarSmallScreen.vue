<script setup lang="ts">
import { computed, ref } from 'vue'
import { useMainStore } from '../stores/main'
const store = useMainStore()

const selectorOpen = ref(false)

const toggleOpen = () => {
  selectorOpen.value = !selectorOpen.value
}

const selectorHeight = computed(() => (selectorOpen.value ? '260px' : '15px'))
</script>

<template>
  <div class="main">
    <v-col cols="12" class="d-flex py-2 align-center menu">
      <div class="d-flex ma-2 mb-0 align-center">
        <v-img height="30" width="30" src="./Kiwix-logo.png"></v-img>
        <div class="pl-2 flex-1-1-100">
          <span class="float-left font-weight-black text-h6">Metrics</span>
        </div>
      </div>
      <div class="flex-1-1"></div>
      <v-app-bar-nav-icon
        class="d-lg-none"
        @click="store.toggleDrawerVisibility()"
      ></v-app-bar-nav-icon>
    </v-col>
    <div class="selector">
      <div id="selector1" :style="{ height: selectorHeight }">
        <div v-if="selectorOpen">
          <div id="select-timeline" class="pt-4 pb-4">Select timeline</div>
          <div id="agg-selector">
            <v-btn-toggle
              divided
              mandatory
              rounded
              :model-value="store.aggregationKind"
              @update:model-value="
                (newValue) => store.setAggregationKind(newValue)
              "
            >
              <v-btn size="large" value="D"> Day </v-btn>

              <v-btn size="large" value="W"> Week </v-btn>

              <v-btn size="large" value="M"> Month </v-btn>

              <v-btn size="large" value="Y"> Year </v-btn>
            </v-btn-toggle>
          </div>
          <div class="pt-6 pb-6 font-weight-bold">
            <div v-if="store.hasAggregationValues">
              <span class="text-subtitle-1 font-weight-medium">{{
                store.date_part_1
              }}</span>
              <span class="text-h5 font-weight-bold">{{
                store.date_part_2
              }}</span>
              <span class="text-subtitle-1 font-weight-medium">{{
                store.date_part_3
              }}</span>
            </div>
            <span v-else>No data</span>
          </div>
          <div id="prev-next">
            <v-btn
              min-width="10em"
              prepend-icon="fas fa-arrow-left"
              variant="flat"
              size="large"
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
              size="large"
              :disabled="!store.hasNextAggregationValue"
              @click="store.toNextAggregationValue"
            >
              Next
            </v-btn>
          </div>
        </div>
      </div>
      <div id="selector2" @click="toggleOpen">
        <div v-if="selectorOpen" id="apply-btn">APPLY</div>
        <div v-else-if="store.hasAggregationValues">
          <span class="text-subtitle-1 font-weight-medium">{{
            store.date_part_1
          }}</span>
          <span class="text-h5 font-weight-bold">{{ store.date_part_2 }}</span>
          <span class="text-subtitle-1 font-weight-medium">{{
            store.date_part_3
          }}</span>
        </div>
        <div v-else>No data</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.main {
  width: 100%;
}

.menu {
  background-color: #f9f8fb;
}

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
  color: #7266ed;
}
</style>
