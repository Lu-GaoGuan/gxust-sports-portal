<script setup>
import { computed, onMounted, ref } from 'vue'
import PageBanner from '../components/PageBanner.vue'
import SafeImage from '../components/SafeImage.vue'
import { getApiErrorMessage, portalApi } from '../services/api'

const members = ref([])
const loading = ref(true)
const errorMessage = ref('')
const selectedGeneration = ref(null)
const legacyGenerations = computed(() => {
  const groups = new Map()
  members.value.filter((member) => member.generation >= 1 && member.generation <= 5).forEach((member) => {
    if (!groups.has(member.generation)) groups.set(member.generation, [])
    groups.get(member.generation).push(member)
  })
  return [...groups.entries()].sort(([a], [b]) => a - b).map(([generation, generationMembers]) => ({
    generation,
    years: generationMembers.find((member) => member.tenure)?.tenure || '任期待确认',
    members: generationMembers,
  }))
})

async function loadMembers() {
  loading.value = true
  errorMessage.value = ''
  try {
    members.value = await portalApi.getMembers()
    selectedGeneration.value = legacyGenerations.value[0]?.generation ?? null
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error, '历届成员加载失败，请稍后重试。')
  } finally { loading.value = false }
}

function goToGeneration(generation) {
  selectedGeneration.value = generation
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  document.getElementById(`generation-${generation}`)?.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'start' })
}

onMounted(loadMembers)
</script>

<template>
  <main><PageBanner eyebrow="OUR LEGACY" title="历届风采" description="回望第一届到第五届的传承，记录并肩同行的伙伴，也把认真与担当传递给现任团队。" number="02" />
    <div v-if="loading" class="content-section data-state page-state"><span class="state-spinner"></span><h2>正在加载历届成员</h2><p>请稍候，正在从后台读取公开资料。</p></div>
    <div v-else-if="errorMessage" class="content-section data-state page-state error"><h2>成员资料暂时无法加载</h2><p>{{ errorMessage }}</p><button type="button" @click="loadMembers">重新加载</button></div>
    <div v-else-if="!legacyGenerations.length" class="content-section data-state page-state empty"><h2>暂无历届成员资料</h2><p>后台尚未发布第一届至第五届可展示的成员数据。</p></div>
    <template v-else>
      <nav class="legacy-generation-index content-section" aria-label="历届成员快速定位">
        <div><p class="section-kicker">QUICK NAVIGATION</p><h2>选择届次</h2></div>
        <div class="generation-buttons"><button v-for="generation in legacyGenerations" :key="generation.generation" type="button" :class="{ active: selectedGeneration === generation.generation }" :aria-pressed="selectedGeneration === generation.generation" @click="goToGeneration(generation.generation)">第{{ generation.generation }}届<span>{{ generation.years }}</span></button></div>
      </nav>
      <section class="content-section legacy-generations">
        <article v-for="generation in legacyGenerations" :id="`generation-${generation.generation}`" :key="generation.generation" v-reveal class="generation-block">
          <header><div><small>{{ generation.years }}</small><h2>第{{ generation.generation }}届成员</h2></div><p>以下为后台已审核并允许公开展示的成员资料。</p></header>
          <div class="legacy-member-grid">
            <article v-for="member in generation.members" :key="member.id" class="legacy-member-card">
              <div class="member-photo"><SafeImage :src="member.photo" :alt="`${member.name}的成员照片`" /></div>
              <div><small>第{{ generation.generation }}届 · {{ member.position }}</small><h3>{{ member.name }}</h3><p>{{ member.major_class || '专业班级待补充' }}</p><p v-if="member.introduction" class="member-introduction">{{ member.introduction }}</p></div>
            </article>
          </div>
        </article>
      </section>
    </template>
  </main>
</template>
