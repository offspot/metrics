<script setup lang="ts">
import { PropType } from 'vue'
import { useMainStore, Page } from '../stores/main'
const store = useMainStore()

defineProps({
  title: {
    type: String,
    required: true,
  },
  value: {
    type: Number as PropType<Page>,
    required: true,
  },
  icon: {
    type: String,
    required: true,
  },
})
</script>

<template>
  <v-list-item
    :active="store.currentPage == value"
    link
    class="rounded-lg mx-2 py-0"
    @click="store.currentPage = value"
  >
    <div class="d-flex align-center">
      <v-icon :icon="icon" size="xs" start />
      <div class="flex-1-1-100">
        <span class="float-left">{{ title }}</span>
      </div>
    </div>
  </v-list-item>
</template>

<style scoped></style>
