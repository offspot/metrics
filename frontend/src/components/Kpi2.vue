<script setup>
import Kpi from '../components/Kpi.vue'

defineProps({
  value: String,
})
</script>

<template>
  <Kpi>
    <template #info>
      <p>
        Top 50 resources is the list of the 50 most viewed resources on a given period, ordered from most to least viewed.
      </p>
    </template>
    <table class="table table-striped">
      <thead>
        <tr>
          <th scope="col">Resource</th>
          <th scope="col">Content</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="res in JSON.parse(value)">
          <td>{{ res.object }}</td>
          <td>{{ res.content }}</td>
        </tr>
      </tbody>
    </table>
  </Kpi>
</template>

<style scoped>
div.parent {
  position: relative;
}

div.info-button {
  position: absolute;
  right: 0em;
}

div.info-button button {
  color: grey;
}

div.offcanvas-body {
  text-align: justify;
}
</style>