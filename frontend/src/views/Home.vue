<script setup>
import HelloWorld from '../components/HelloWorld.vue'
</script>

<template>

  <div class="container text-center">
    <div class="row  justify-content-center">
      <div class="col-3">
        <a href="https://vitejs.dev" target="_blank">
          <img src="/vite.svg" class="logo" alt="Vite logo" />
        </a>
      </div>
      <div class="col-3">
        <a href="https://vuejs.org/" target="_blank">
          <img src="../assets/vue.svg" class="logo vue" alt="Vue logo" />
        </a>
      </div>
    </div>
  </div>
  <HelloWorld msg="Vite + Vue" />
  <font-awesome-icon icon="fa-solid fa-user-secret" />&nbsp;
  <font-awesome-icon icon="fa-solid fa-umbrella-beach" /><br>
  <router-link to="/about">Go to About </router-link><br>
  <router-link to="/about2">Go to About2 </router-link>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}

.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}

.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
