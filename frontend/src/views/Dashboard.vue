<!-- eslint-disable vue/multi-word-component-names -->
<script setup lang="ts">
import DashboardPackagePopularity from '../components/DashboardPackagePopularity.vue'
import DashboardTotalUsage from '../components/DashboardTotalUsage.vue'
import DashboardSharedFiles from '../components/DashboardSharedFiles.vue'
import DashboardUptime from '../components/DashboardUptime.vue'

import { useMainStore, Page } from '../stores/main'

const mainStore = useMainStore()
</script>

<template>
  <v-container class="pt-6">
    <v-row>
      <v-col cols="12" md="6" lg="4">
        <v-container class="pa-0">
          <v-row>
            <v-col cols="12">
              <v-card elevation="0">
                <DashboardUptime />
              </v-card>
            </v-col>
            <v-col cols="12">
              <v-card elevation="0" class="shared-files">
                <DashboardSharedFiles />
              </v-card>
            </v-col>
            <v-col cols="12" class="d-lg-none">
              <v-card
                elevation="0"
                class="total-usage"
                @click="mainStore.currentPage = Page.TotalUsage"
              >
                <DashboardTotalUsage />
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </v-col>
      <v-col cols="12" md="6" lg="8">
        <v-container class="pa-0">
          <v-row>
            <v-col cols="12" lg="6">
              <v-card
                elevation="0"
                class="package-popularity"
                @click="mainStore.currentPage = Page.PackagePopularity"
              >
                <DashboardPackagePopularity />
              </v-card>
            </v-col>
            <v-col cols="12" lg="6" class="d-md-none d-lg-flex">
              <v-card
                elevation="0"
                class="total-usage"
                @click="mainStore.currentPage = Page.TotalUsage"
              >
                <DashboardTotalUsage />
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.shared-files {
  min-height: 320px;
}
.package-popularity {
  min-height: 544px;
}

.total-usage {
  min-height: 544px;
  width: 100%;
}
</style>
