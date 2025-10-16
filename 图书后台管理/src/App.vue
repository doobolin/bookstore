<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <transition name="fade" mode="out-in">
    <RouterView />
  </transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
