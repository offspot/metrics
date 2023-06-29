<script setup>

import { onBeforeUpdate, onMounted, ref, watch } from 'vue'

const props = defineProps({
  values: Array,
  init_val: String,
  start_from_last: Boolean,
})

const emit = defineEmits(['valueUpdated'])

const cur_idx = ref(-1)
const val = ref('')

watch(props, () => {
  if (props.start_from_last) {
    cur_idx.value = props.values.length - 1
  }
  else {
    cur_idx.value = 0
  }
  val.value = props.values[cur_idx.value]
})

onMounted(() => {
  if (props.init_val) {
    val.value = props.init_val
    cur_idx.value = props.values.indexOf(props.init_val)
  } else {
    if (props.start_from_last) {
      cur_idx.value = props.values.length - 1
    }
    else {
      cur_idx.value = 0
    }
    val.value = props.values[cur_idx.value]
  }
  emit('valueUpdated', val.value)
})

function move(delta) {
  cur_idx.value = (cur_idx.value + delta) % props.values.length
  if (cur_idx.value < 0) {
    cur_idx.value += props.values.length
  }
  val.value = props.values[cur_idx.value]
  emit('valueUpdated', val.value)
}

function prev(event) {
  move(-1)
}

function next(event) {
  move(1)
}

</script>

<template>
  <div class="mt-4 mb-4 p-2 shadow rounded container d-flex justify-content-center align-items-center">
    <font-awesome-icon icon="fa-solid fa-chevron-circle-left" @click="prev" />
    <div class="fg-1">{{ val }}</div>
    <font-awesome-icon icon="fa-solid fa-chevron-circle-right" @click="next" />
  </div>
</template>

<style scoped>
.fg-1 {
  flex-grow: 1
}

div.container {
  background-color: #ffa256;
}
</style>