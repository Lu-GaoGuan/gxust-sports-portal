<script setup>
defineProps({ eyebrow: String, title: String, description: String, number: String })
</script>
<template>
  <section class="page-banner">
    <div class="circuit-grid"></div>
    <div class="page-banner-copy"><p class="eyebrow">{{ eyebrow }}</p><h1>{{ title }}</h1><p>{{ description }}</p></div>
    <span class="page-number">{{ number }}</span>
  </section>
</template>
