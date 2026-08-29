<script setup>
import { computed, onMounted, ref } from 'vue'
import PageBanner from '../components/PageBanner.vue'
import SafeImage from '../components/SafeImage.vue'
import { getApiErrorMessage, portalApi } from '../services/api'

const members = ref([])
const loading = ref(true)
const errorMessage = ref('')
const selectedRole = ref('全部')
const generation = computed(() => members.value[0]?.generation || 6)
const roles = computed(() => ['全部', ...new Set(members.value.map((member) => member.position))])
const filteredMembers = computed(() => selectedRole.value === '全部' ? members.value : members.value.filter((member) => member.position === selectedRole.value))

async function loadMembers() {
  loading.value = true
  errorMessage.value = ''
  try { members.value = await portalApi.getCurrentMembers() }
  catch (error) { errorMessage.value = getApiErrorMessage(error, '现任成员加载失败，请稍后重试。') }
  finally { loading.value = false }
}

onMounted(loadMembers)
</script>

<template>
  <main><PageBanner :eyebrow="`GENERATION ${String(generation).padStart(2, '0')}`" :title="`第${generation}届成员`" description="此刻并肩工作的团队，在赛事组织与日常协作中延续体育部的认真与担当。" number="03" />
    <section class="content-section">
      <div v-if="loading" class="data-state page-state"><span class="state-spinner"></span><h2>正在加载现任成员</h2><p>请稍候，正在从后台读取公开资料。</p></div>
      <div v-else-if="errorMessage" class="data-state page-state error"><h2>成员资料暂时无法加载</h2><p>{{ errorMessage }}</p><button type="button" @click="loadMembers">重新加载</button></div>
      <div v-else-if="!members.length" class="data-state page-state empty"><h2>暂无现任成员资料</h2><p>后台尚未发布允许展示的成员数据。</p></div>
      <template v-else>
        <div class="notice-card"><b>公开资料</b><p>当前页面仅展示后台标记为“允许展示”的成员；缺失照片和介绍会显示待补充状态。</p></div>
        <div class="team-toolbar"><div class="filter-tabs" role="group" aria-label="按职务筛选成员"><button v-for="role in roles" :key="role" type="button" :class="{ active: selectedRole === role }" :aria-pressed="selectedRole === role" @click="selectedRole = role">{{ role }}</button></div><p>当前显示 <b>{{ filteredMembers.length }}</b> 位成员</p></div>
        <TransitionGroup name="cards" tag="div" class="team-grid"><article v-for="member in filteredMembers" :key="member.id"><div class="member-photo"><SafeImage :src="member.photo" :alt="`${member.name}的成员照片`" /></div><div><small>第{{ member.generation }}届 · {{ member.position }}</small><h3>{{ member.name }}</h3><p>{{ member.major_class || '专业班级待补充' }}</p><p v-if="member.introduction" class="member-introduction">{{ member.introduction }}</p><blockquote v-if="member.welcome_message">“{{ member.welcome_message }}”</blockquote></div></article></TransitionGroup>
      </template>
    </section>
  </main>
</template>
