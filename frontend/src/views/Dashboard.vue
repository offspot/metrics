<script setup>
import Kpi1 from '../components/Kpi1.vue'
import Kpi2 from '../components/Kpi2.vue'
import Selector from '../components/Selector.vue'


import { onMounted, ref } from "vue";
import { useMainStore } from '../stores/main'
const main = useMainStore()

onMounted(() => {
  main.fetchAggregations();
});

</script>

<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-md-4 col-lg-3">
        <Selector @valueUpdated="main.update_kpi" :values="['Top contents', 'Top 50 resources']" />
        <Selector @valueUpdated="main.update_agg_kind" :values="['Daily', 'Weekly', 'Monthly', 'Yearly']" />
        <Selector @valueUpdated="main.update_agg_value" :values="main.agg_values_for_selected_agg_kind" :start_from_last="true" />
      </div>
      <div class="col-md-8 col-lg-9">
        <div class="container-fluid">
          <div class="row" v-if="main.is_loading">
            Loading ...
          </div>
          <div class="row" v-if="!main.is_loading">
            <div v-if="main.value_for_selected_kpi_id">
              <Kpi1 v-if="main.selected_kpi_id === 1" :value="main.value_for_selected_kpi_id" />
              <Kpi2 v-if="main.selected_kpi_id === 2" :value="main.value_for_selected_kpi_id" />
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped></style>
