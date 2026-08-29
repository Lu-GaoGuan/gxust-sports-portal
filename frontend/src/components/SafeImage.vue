<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  src: { type: String, default: '' },
  alt: { type: String, required: true },
  eager: { type: Boolean, default: false },
})
const failed = ref(false)
const placeholder = '/media/content-placeholder.svg'
const displaySrc = computed(() => props.src && !failed.value ? props.src : placeholder)

watch(() => props.src, () => { failed.value = false })
</script>

<template>
  <img :src="displaySrc" :alt="failed || !src ? `${alt}（图片待补充）` : alt" :loading="eager ? 'eager' : 'lazy'" @error="failed = true">
</template>
