<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  color: { type: String, default: '#1689f5' },
  accentColor: { type: String, default: '#ffffff' },
  count: { type: Number, default: 6 },
  size: { type: Number, default: 4 },
  speed: { type: Number, default: 3.8 },
  spread: { type: Number, default: 42 },
  trail: { type: Number, default: 0.42 },
  scatterOnClick: { type: Boolean, default: true },
})

const canvas = ref(null)
const pointer = { x: 0, y: 0, active: false }
const particles = []
let context
let frameId = 0
let lastTime = 0
let enabled = false
let burst = 0

function resize() {
  if (!canvas.value || !context) return
  canvas.value.width = window.innerWidth
  canvas.value.height = window.innerHeight
  canvas.value.style.width = `${window.innerWidth}px`
  canvas.value.style.height = `${window.innerHeight}px`
}

function createParticle(index) {
  const angle = (Math.PI * 2 * index) / Math.max(1, props.count)
  const radius = 8 + (index % 3) * 6
  return { x: pointer.x, y: pointer.y, vx: 0, vy: 0, angle, radius, trail: [] }
}

function updatePointer(event) {
  pointer.x = event.clientX
  pointer.y = event.clientY
  if (!pointer.active) {
    pointer.active = true
    particles.length = 0
    for (let index = 0; index < props.count; index += 1) particles.push(createParticle(index))
  }
}

function scatter(event) {
  if (!props.scatterOnClick) return
  updatePointer(event)
  burst = 1
  particles.forEach((particle, index) => {
    const angle = particle.angle + index * 0.7
    particle.vx += Math.cos(angle) * (240 + index * 16)
    particle.vy += Math.sin(angle) * (240 + index * 16)
  })
}

function drawParticle(particle, index) {
  const maxTrail = Math.max(3, Math.round(3 + props.trail * 9))
  particle.trail.unshift({ x: particle.x, y: particle.y })
  particle.trail.length = Math.min(particle.trail.length, maxTrail)
  if (particle.trail.length > 1) {
    context.globalAlpha = 0.18
    context.strokeStyle = props.color
    context.lineWidth = Math.max(1, props.size * 0.45)
    context.lineCap = 'round'
    context.beginPath()
    particle.trail.forEach((point, pointIndex) => pointIndex ? context.lineTo(point.x, point.y) : context.moveTo(point.x, point.y))
    context.stroke()
  }
  context.globalAlpha = 0.62 + (index % 3) * 0.1
  context.fillStyle = index === 0 ? props.accentColor : props.color
  context.beginPath()
  context.arc(particle.x, particle.y, props.size * (0.65 + (index % 2) * 0.16), 0, Math.PI * 2)
  context.fill()
}

function render(now) {
  frameId = requestAnimationFrame(render)
  const delta = Math.min((now - lastTime) / 1000 || 0.016, 0.032)
  lastTime = now
  context.clearRect(0, 0, canvas.value.width, canvas.value.height)
  if (!enabled || !pointer.active) return
  burst = Math.max(0, burst - delta * 3.2)
  const response = Math.min(1, delta * (18 + props.speed * 3.7))
  const time = now * 0.005

  particles.forEach((particle, index) => {
    const orbit = particle.angle + time * (index % 2 ? 1 : -1)
    const radius = Math.min(props.spread, particle.radius + index)
    const targetX = pointer.x + Math.cos(orbit) * radius
    const targetY = pointer.y + Math.sin(orbit) * radius
    particle.vx += (targetX - particle.x) * delta * 8
    particle.vy += (targetY - particle.y) * delta * 8
    const damping = Math.max(0.72, 1 - delta * (burst ? 2.2 : 9))
    particle.vx *= damping
    particle.vy *= damping
    particle.x += (targetX - particle.x) * response + particle.vx * delta
    particle.y += (targetY - particle.y) * response + particle.vy * delta
    drawParticle(particle, index)
  })

  context.globalAlpha = 0.22
  context.fillStyle = props.color
  context.beginPath()
  context.arc(pointer.x, pointer.y, props.size * 2.4, 0, Math.PI * 2)
  context.fill()
  context.globalAlpha = 1
  context.fillStyle = props.accentColor
  context.beginPath()
  context.arc(pointer.x, pointer.y, Math.max(1.8, props.size * 0.62), 0, Math.PI * 2)
  context.fill()
}

const deactivatePointer = () => { pointer.active = false }

onMounted(() => {
  enabled = window.matchMedia('(hover: hover) and (pointer: fine)').matches
    && !window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (!enabled || !canvas.value) return
  context = canvas.value.getContext('2d', { alpha: true, desynchronized: true })
  resize()
  window.addEventListener('resize', resize, { passive: true })
  window.addEventListener('pointermove', updatePointer, { passive: true })
  window.addEventListener('pointerdown', scatter, { passive: true })
  window.addEventListener('blur', deactivatePointer)
  frameId = requestAnimationFrame(render)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(frameId)
  window.removeEventListener('resize', resize)
  window.removeEventListener('pointermove', updatePointer)
  window.removeEventListener('pointerdown', scatter)
  window.removeEventListener('blur', deactivatePointer)
})
</script>

<template><canvas ref="canvas" class="swarm-cursor-canvas" aria-hidden="true"></canvas></template>
