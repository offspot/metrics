<script setup>
import { useMainStore } from '../stores/main'

const main = useMainStore()

</script>

<template>
  An empty about page (count is {{ main.count }}, double is {{ main.doubleCount }})
  <router-link to="/">Go to home</router-link>
  <router-link to="/about2">Go to About 2</router-link>
</template>

<style scoped>
</style>
