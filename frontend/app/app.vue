<template>
  <div class="app-root">
    <NuxtPage />
    <UiToasts />
  </div>
</template>

<style>
/* Global resets or transitions if needed */
.app-root {
  min-height: 100vh;
}

.page-enter-active,
.page-leave-active {
  transition: all 0.2s;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
  filter: blur(1rem);
}
</style>
