<!-- eslint-disable vue/multi-word-component-names -->
<script setup lang="ts">
import DrawerItem from '../components/DrawerItem.vue'
import AggregationSelector from '../components/AggregationSelector.vue'
import Dashboard from '../views/Dashboard.vue'
import PackagePopularity from '../views/PackagePopularity.vue'
import TotalUsage from '../views/TotalUsage.vue'

import { onMounted, ref } from 'vue'
import { useMainStore, Page } from '../stores/main'
const store = useMainStore()
const drawer = ref(true)
onMounted(() => {
  store.fetchAggregationDetails()
})
</script>

<template>
  <v-app v-if="store.aggregationsDetails" id="home">
    <v-navigation-drawer v-model="drawer" class="pa-2">
      <div class="d-flex ma-4 mb-0 align-center">
        <v-img :width="60" src="./Kiwix_logo_v3.svg"></v-img>
        <div class="pl-2 flex-1-1-100">
          <span class="float-left font-weight-black text-h4">Metrics</span>
        </div>
      </div>
      <div class="my-6"></div>
      <DrawerItem
        title="Dashboard"
        :value="Page.Dashboard"
        icon="far fa-envelope-open"
      />
      <DrawerItem
        title="Package popularity"
        :value="Page.PackagePopularity"
        icon="fas fa-chart-column"
      />
      <DrawerItem
        title="Total usage"
        :value="Page.TotalUsage"
        icon="far fa-clock"
      />
    </v-navigation-drawer>

    <v-app-bar flat height="100">
      <v-app-bar-nav-icon
        class="d-lg-none"
        @click="drawer = !drawer"
      ></v-app-bar-nav-icon>
      <AggregationSelector />
    </v-app-bar>

    <v-main>
      <Dashboard v-if="store.currentPage == Page.Dashboard" />
      <PackagePopularity v-if="store.currentPage == Page.PackagePopularity" />
      <TotalUsage v-if="store.currentPage == Page.TotalUsage" />
      <v-footer app class="text-caption">
        <span class="font-weight-bold me-auto">© 2023 Kiwix Association</span>
        <span class="me-8">Support</span>
        <a href="https://www.kiwix.org" target="_blank"
          ><span class="font-weight-bold flex-d-1-1-100">www.kiwix.org</span></a
        >
      </v-footer>
    </v-main>
  </v-app>
</template>

<style scoped>
.v-app-bar.v-toolbar {
  background-color: rgb(248, 247, 250);
}

.v-footer {
  background-color: rgb(243, 239, 245);
}

.v-footer a {
  color: rgba(var(--v-theme-on-surface), var(--v-high-emphasis-opacity));
}

.v-main {
  background-color: rgb(243, 239, 245);
}
</style>
