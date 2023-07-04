<script setup>
defineProps({
  value: String,
})
</script>

<template>
  <div class="parent">
    <div class="info-button">
      <button class="btn btn-light" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasInfo"
        aria-controls="offcanvasInfo">
        <font-awesome-icon icon="circle-info" />
      </button>
    </div>

    <div class="offcanvas offcanvas-start" tabindex="-1" id="offcanvasInfo" aria-labelledby="offcanvasLabel">
      <div class="offcanvas-header">
        <h5 class="offcanvas-title" id="offcanvasLabel">Top contents</h5>
        <button type="button" class="btn-close text-reset" data-bs-dismiss="offcanvas" aria-label="Close"></button>
      </div>
      <div class="offcanvas-body">
        <slot name="info"></slot>
      </div>
    </div>
    <slot></slot>
  </div>
</template>

<style scoped>
div.parent {
  position: relative;
}

div.info-button {
  position: absolute;
  left: 0em;
}

div.info-button button {
  color: grey;
}

div.offcanvas-body {
  text-align: justify;
}</style>
