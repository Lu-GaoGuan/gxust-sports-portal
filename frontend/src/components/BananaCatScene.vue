<script setup>
import { onBeforeUnmount, ref } from 'vue'

const scene = ref(null)
const video = ref(null)
const ready = ref(false)
const failed = ref(false)
const scrubbing = ref(false)
const progress = ref(0)
let duration = 0
let pendingClientX = 0
let frameId = 0

const clamp = (value, min, max) => Math.min(Math.max(value, min), max)

function syncDuration() {
  duration = video.value?.duration || 0
  ready.value = duration > 0
  if (video.value) {
    video.value.pause()
    video.value.currentTime = 0
  }
}

function seekFromClientX(clientX) {
  if (!duration || !scene.value || !video.value) return
  const bounds = scene.value.getBoundingClientRect()
  const nextProgress = clamp((clientX - bounds.left) / bounds.width, 0, 1)
  const nextTime = clamp(nextProgress * duration, 0, Math.max(0, duration - .02))
  progress.value = nextProgress
  if (Math.abs(video.value.currentTime - nextTime) > .018) video.value.currentTime = nextTime
}

function scheduleSeek(clientX) {
  pendingClientX = clientX
  if (frameId) return
  frameId = requestAnimationFrame(() => {
    frameId = 0
    seekFromClientX(pendingClientX)
  })
}

function handlePointerDown(event) {
  scrubbing.value = true
  scene.value?.setPointerCapture?.(event.pointerId)
  video.value?.pause()
  scheduleSeek(event.clientX)
}

function handlePointerMove(event) {
  if (event.pointerType === 'mouse' || scrubbing.value) scheduleSeek(event.clientX)
}

function stopScrubbing(event) {
  scrubbing.value = false
  if (event?.pointerId !== undefined && scene.value?.hasPointerCapture?.(event.pointerId)) scene.value.releasePointerCapture(event.pointerId)
}

function handleKeyboard(event) {
  if (!duration || !video.value) return
  const direction = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0
  if (!direction) return
  event.preventDefault()
  progress.value = clamp(progress.value + direction * .05, 0, 1)
  video.value.currentTime = clamp(progress.value * duration, 0, Math.max(0, duration - .02))
}

onBeforeUnmount(() => {
  if (frameId) cancelAnimationFrame(frameId)
})
</script>

<template>
  <section
    ref="scene"
    class="banana-cat-scene"
    :class="{ ready, failed, scrubbing }"
    tabindex="0"
    aria-label="香蕉猫新队员全屏环视场景，左右移动鼠标或使用方向键控制画面"
    @pointerdown="handlePointerDown"
    @pointermove="handlePointerMove"
    @pointerup="stopScrubbing"
    @pointercancel="stopScrubbing"
    @lostpointercapture="stopScrubbing"
    @keydown="handleKeyboard"
  >
    <video ref="video" muted playsinline preload="auto" @loadedmetadata="syncDuration" @durationchange="syncDuration" @error="failed = true">
      <source src="/media/banana-cat-interactive-mobile.mp4" type="video/mp4" media="(max-width: 700px)">
      <source src="/media/banana-cat-interactive.mp4" type="video/mp4">
    </video>
    <div class="banana-cat-shade" aria-hidden="true"></div>
    <div v-if="!ready && !failed" class="banana-cat-loading" role="status"><i></i><span>猫咪正在入场…</span></div>
    <div v-if="failed" class="banana-cat-error" role="status"><b>互动视频暂时无法加载</b><span>首页其他内容仍可正常浏览</span></div>
    <div class="banana-cat-control">
      <span class="banana-cat-track"><i :style="{ width: `${progress * 100}%` }"></i></span>
      <p><b>左右移动鼠标</b><span>查看香蕉猫环视动作</span></p>
      <small>{{ String(Math.round(progress * 100)).padStart(2, '0') }}%</small>
    </div>
  </section>
</template>
