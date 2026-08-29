<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import AppLoader from './components/AppLoader.vue'
import SiteFooter from './components/SiteFooter.vue'
import SiteHeader from './components/SiteHeader.vue'
import SwarmCursor from './components/SwarmCursor.vue'

const loading = ref(true)
let loaderTimer

function finishLoading(delay = 520) {
  window.clearTimeout(loaderTimer)
  loaderTimer = window.setTimeout(() => { loading.value = false }, delay)
}

onMounted(() => finishLoading(480))
onBeforeUnmount(() => window.clearTimeout(loaderTimer))
</script>

<template>
  <AppLoader :visible="loading" />
  <SwarmCursor color="#1689f5" accent-color="#ffffff" :count="6" :size="4" :speed="3.8" :spread="42" :trail="0.42" scatter-on-click />
  <SiteHeader />
  <RouterView v-slot="{ Component }"><component :is="Component" /></RouterView>
  <SiteFooter />
</template>
