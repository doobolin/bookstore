<template>
  <div class="container">
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
// App容器组件，用于布局包装
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}
</style>