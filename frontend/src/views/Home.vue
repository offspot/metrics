<!-- eslint-disable vue/multi-word-component-names -->
<script setup lang="ts">
import DrawerItem from '../components/DrawerItem.vue'
import AppBarSmallScreen from '../components/AppBarSmallScreen.vue'
import AppBarBigScreen from '../components/AppBarBigScreen.vue'
import Dashboard from '../views/Dashboard.vue'
import PackagePopularity from '../views/PackagePopularity.vue'
import TotalUsage from '../views/TotalUsage.vue'

import { onMounted } from 'vue'
import { useMainStore, Page } from '../stores/main'
import { useDisplay } from 'vuetify'
import ViewInfo from '@/types/ViewInfo'

const { mdAndUp, lgAndUp } = useDisplay()
const store = useMainStore()
onMounted(() => {
  store.fetchAggregationDetails()
  store.setDrawerVisibility(lgAndUp.value) // at startutp, close drawer on small screens
})

const views: ViewInfo[] = [
  {
    title: 'Dashboard',
    value: Page.Dashboard,
    icon: 'far fa-envelope-open',
  },
  {
    title: 'Package popularity',
    value: Page.PackagePopularity,
    icon: 'fas fa-chart-column',
  },
  {
    title: 'Total usage',
    value: Page.TotalUsage,
    icon: 'far fa-clock',
  },
]
</script>

<template>
  <v-app v-if="store.aggregationsDetails" id="home">
    <v-navigation-drawer
      v-if="mdAndUp"
      v-model="store.drawerVisible"
      class="pa-2"
      location="left"
    >
      <div class="d-flex ma-4 mb-0 align-center">
        <v-img width="60" src="./Kiwix-logo.png"></v-img>
        <div class="pl-2 flex-1-1-100">
          <span class="float-left font-weight-black hotspot">Metrics</span>
        </div>
      </div>
      <div class="my-6"></div>
      <DrawerItem
        v-for="view in views"
        :key="view.value"
        :title="view.title"
        :value="view.value"
        :icon="view.icon"
        active-class="active-big"
      />
    </v-navigation-drawer>

    <v-navigation-drawer
      v-if="!mdAndUp"
      v-model="store.drawerVisible"
      class="small-drawer py-8 px-4"
      location="right"
    >
      <div class="pb-4 px-2 font-weight-bold">Menu</div>
      <v-icon
        id="close-drawer"
        icon="fas fa-xmark"
        @click="store.toggleDrawerVisibility()"
      ></v-icon>
      <DrawerItem
        v-for="view in views"
        :key="view.value"
        class="py-6"
        :title="view.title"
        :value="view.value"
        :icon="view.icon"
      />
    </v-navigation-drawer>

    <v-app-bar flat height="undefined">
      <AppBarBigScreen v-if="mdAndUp" />
      <AppBarSmallScreen v-if="!mdAndUp" />
    </v-app-bar>

    <v-main>
      <!-- <AggregationSelectorSmallScreen v-if="!mdAndUp" />   -->
      <Dashboard v-if="store.currentPage == Page.Dashboard" />
      <PackagePopularity v-if="store.currentPage == Page.PackagePopularity" />
      <TotalUsage v-if="store.currentPage == Page.TotalUsage" />
    </v-main>
  </v-app>
</template>

<style scoped>
.v-main {
  background-color: rgb(243, 239, 245);
  padding-top: 120px;
}

.v-toolbar {
  background: transparent;
}

.hotspot {
  font-size: 1.5rem;
}

#close-drawer {
  position: absolute;
  top: 24px;
  right: 24px;
  font-size: medium;
}
</style>
