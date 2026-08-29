<script setup>
import { ref } from 'vue'

const status = ref('')

async function sharePage() {
  const data = { title: document.title, text: '广西科技大学电子工程学院团委学生会体育部迎新网站', url: window.location.href }
  try {
    if (navigator.share) {
      await navigator.share(data)
      status.value = '分享面板已打开'
    } else {
      await navigator.clipboard.writeText(data.url)
      status.value = '链接已复制'
    }
  } catch (error) {
    if (error?.name !== 'AbortError') status.value = '暂时无法分享，请复制浏览器地址'
  }
  window.setTimeout(() => { status.value = '' }, 2400)
}
</script>

<template>
  <div class="share-control">
    <button type="button" class="share-trigger" @click="sharePage">
      <span>分享网站</span>
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 16.1c-.76 0-1.44.3-1.96.77L8.91 12.7a3 3 0 0 0 0-1.4l7.05-4.11A3 3 0 1 0 15 5c0 .23.03.45.08.66L8.03 9.77a3 3 0 1 0 0 4.46l7.12 4.16A3 3 0 1 0 18 16.1Z"/></svg>
    </button>
    <span class="share-status" role="status">{{ status }}</span>
  </div>
</template>
