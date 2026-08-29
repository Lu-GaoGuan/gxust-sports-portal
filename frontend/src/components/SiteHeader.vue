<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'

const route = useRoute()
const open = ref(false)
const scrolled = ref(false)
const links = [
  ['/', '首页'], ['/department', '部门介绍'], ['/legacy', '历届风采'], ['/team-six', '第六届成员'],
  ['/activities', '活动回顾'], ['/faq', '新生问答'], ['/messages', '留言交流'],
]
const updateScrollState = () => { scrolled.value = window.scrollY > 12 }
onMounted(() => {
  updateScrollState()
  window.addEventListener('scroll', updateScrollState, { passive: true })
})
onBeforeUnmount(() => window.removeEventListener('scroll', updateScrollState))
</script>

<template>
  <header class="site-header" :class="{ scrolled }">
    <RouterLink class="brand" to="/" @click="open = false">
      <span class="brand-icon">E</span><span><b>电子工程学院</b><small>团委学生会体育部</small></span>
    </RouterLink>
    <button class="menu-toggle" type="button" :aria-expanded="open" aria-label="切换导航" @click="open = !open">{{ open ? '×' : '☰' }}</button>
    <nav :class="{ open }">
      <RouterLink v-for="link in links" :key="link[0]" :to="link[0]" :class="{ active: route.path === link[0] }" @click="open = false">{{ link[1] }}</RouterLink>
      <ThemeToggle />
    </nav>
  </header>
</template>
