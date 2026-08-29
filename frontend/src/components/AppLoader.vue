<script setup>
defineProps({ visible: Boolean })
</script>

<template>
  <Transition name="app-loader">
    <div v-if="visible" class="app-loader" role="status" aria-live="polite" aria-label="页面正在加载">
      <div class="runner-wheel" aria-hidden="true">
        <span class="runner-wheel-ring"></span>
        <span class="runner-body"><i class="runner-head"></i><i class="runner-leg one"></i><i class="runner-leg two"></i></span>
        <span class="runner-spoke"></span>
      </div>
      <div class="loader-copy"><b>体育部正在热身</b><span>准备进入下一页…</span></div>
    </div>
  </Transition>
</template>
