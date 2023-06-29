<script setup>
import { useMainStore } from '../stores/main'
import { onMounted } from "vue";
const main = useMainStore()

onMounted(() => {
  main.fetchUsers();
});

</script>

<template>
  An empty about page (count is {{ main.count }}, double is {{ main.doubleCount }})
  <br><router-link to="/">Go to home</router-link>
  <br><router-link to="/about2">Go to About 2</router-link>

  <div v-for="user in main.users" :key="user.id">
    {{ user.id }}: {{ user.name }} @ {{ user.address.city }}
  </div>
</template>

<style scoped></style>
