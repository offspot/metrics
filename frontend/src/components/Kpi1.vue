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
        Top contents is the list of all contents used on a given period, order from most to least viewed.
      </p>
      <p>
        Content not displayed have not been used on the period.
      </p>
      <p>
        Only display of the content home page is considered to count the usage, i.e. activity within the
        content is
        not considered.
      </p>
    </template>
    <table class="table table-striped">
      <thead>
        <tr>
          <th scope="col">Content</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="res in JSON.parse(value)">
          <td>{{ res }}</td>
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
