<script setup>
import { onMounted, ref } from 'vue'

const energetic = ref(true)
const themeVersion = '2'

function applyTheme() {
  document.documentElement.dataset.theme = energetic.value ? 'energetic' : 'college'
  localStorage.setItem('portal-theme', energetic.value ? 'energetic' : 'college')
}

onMounted(() => {
  const storedVersion = localStorage.getItem('portal-theme-version')
  energetic.value = storedVersion === themeVersion
    ? localStorage.getItem('portal-theme') !== 'college'
    : true
  localStorage.setItem('portal-theme-version', themeVersion)
  applyTheme()
})
</script>

<template>
  <label class="theme-toggle" title="切换网站主题">
    <input v-model="energetic" type="checkbox" role="switch" :aria-label="energetic ? '切换为学院蓝橙主题' : '切换为活力夜场主题'" @change="applyTheme">
    <span class="theme-slider" aria-hidden="true"><i class="theme-cosmos"></i><i class="theme-orb"><b></b></i><i class="theme-energy e1"></i><i class="theme-energy e2"></i><i class="theme-energy e3"></i></span>
    <small>{{ energetic ? '夜场' : '日场' }}</small>
  </label>
</template>
