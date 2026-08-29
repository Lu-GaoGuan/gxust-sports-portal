<script setup>
import { onMounted, ref } from 'vue'
import BananaCatScene from '../components/BananaCatScene.vue'
import SafeImage from '../components/SafeImage.vue'
import { getApiErrorMessage, portalApi } from '../services/api'

const profile = ref(null)
const activities = ref([])
const profileLoading = ref(true)
const activitiesLoading = ref(true)
const profileError = ref('')
const activitiesError = ref('')

const formatDate = (value) => value || '日期待公布'
const activityImage = (activity) => activity.cover || activity.media?.find((item) => item.media_type === 'image')?.file || ''
const featuredActivities = () => activities.value.filter((activity) => activityImage(activity)).slice(0, 4)

async function loadProfile() {
  profileLoading.value = true
  profileError.value = ''
  try { profile.value = await portalApi.getProfile() }
  catch (error) { profileError.value = getApiErrorMessage(error, '体育部资料加载失败，请稍后重试。') }
  finally { profileLoading.value = false }
}

async function loadActivities() {
  activitiesLoading.value = true
  activitiesError.value = ''
  try { activities.value = await portalApi.getActivities() }
  catch (error) { activitiesError.value = getApiErrorMessage(error, '活动资料加载失败，请稍后重试。') }
  finally { activitiesLoading.value = false }
}

onMounted(() => { loadProfile(); loadActivities() })
</script>

<template>
  <main>
    <section class="home-hero banana-home-hero">
      <BananaCatScene class="hero-cat-background" />
      <div class="home-hero-copy">
        <p class="eyebrow">广西科技大学电子工程学院学生会体育部</p>
        <h1>{{ profile?.welcome_slogan || '以热爱集结，为青春开赛' }}</h1>
        <p v-if="profile">{{ profile.recruitment_info || profile.introduction || '招新信息将由体育部通过管理后台发布。' }}</p>
        <p v-else>这里有热烈的赛场，也有并肩前行的伙伴。欢迎了解体育部，与我们一起见证成长。</p>
        <p v-if="profileLoading" class="inline-api-status">正在读取体育部资料…</p>
        <p v-else-if="profileError" class="inline-api-status error">{{ profileError }}</p>
        <div class="hero-actions"><RouterLink class="button button-orange" to="/department">了解体育部</RouterLink><RouterLink class="button button-glass" to="/team-six">查看现任成员</RouterLink></div>
      </div>
    </section>

    <section class="content-section intro-layout">
      <div><p class="section-kicker">ABOUT US / 关于我们</p><h2>把每一场赛事，<br>办得有声有色</h2></div>
      <div class="lead-copy">
        <div v-if="profileLoading" class="data-state compact"><span class="state-spinner"></span><p>正在加载部门简介…</p></div>
        <div v-else-if="profileError" class="data-state compact error"><p>{{ profileError }}</p><button type="button" @click="loadProfile">重新加载</button></div>
        <template v-else-if="profile"><p>{{ profile.introduction || '体育部简介暂未填写。' }}</p><p v-if="profile.contact_info"><b>联系方式：</b>{{ profile.contact_info }}</p><RouterLink class="intro-more" to="/department">了解体育部的工作与生活 <span>→</span></RouterLink></template>
        <div v-else class="data-state compact empty"><p>后台暂未发布体育部简介和招新资料。</p></div>
      </div>
      <div class="value-grid"><article><span>01</span><h3>组织赛事</h3><p>策划、协调、执行与复盘，让热爱有序发生。</p></article><article><span>02</span><h3>服务同学</h3><p>关注现场的每一个细节，为参与者做好保障。</p></article><article><span>03</span><h3>传承成长</h3><p>学长学姐传帮带，让每一届都能独当一面。</p></article></div>
    </section>

    <section class="blue-section">
      <div class="section-heading"><div><p class="section-kicker light">FEATURED MOMENTS</p><h2>一起做过的事，<br>都是青春的注脚</h2></div><RouterLink class="text-link" to="/activities">浏览全部活动 →</RouterLink></div>
      <div v-if="activitiesLoading" class="data-state dark"><span class="state-spinner"></span><p>正在加载活动资料…</p></div>
      <div v-else-if="activitiesError" class="data-state dark error"><p>{{ activitiesError }}</p><button type="button" @click="loadActivities">重新加载</button></div>
      <div v-else-if="featuredActivities().length" class="featured-grid">
        <article v-for="(activity, index) in featuredActivities()" :key="activity.id" :class="{ featured: index === 0 }"><SafeImage :src="activityImage(activity)" :alt="activity.name" /><div><small>{{ activity.category_label }} · {{ formatDate(activity.activity_date) }}</small><h3>{{ activity.name }}</h3><p>{{ activity.introduction || '活动简介待补充。' }}</p></div></article>
      </div>
      <div v-else class="data-state dark empty"><p>后台暂未发布可展示的活动资料。</p></div>
    </section>

    <section class="content-section video-section">
      <div><p class="section-kicker">VIDEO / 换届影像</p><h2>接过接力棒，<br>继续并肩前行</h2><p>回顾2025年体育部换届大会，记录工作交接与团队传承的重要时刻。</p></div>
      <video controls preload="metadata" poster="/media/handover-2025.jpg"><source src="/media/handover-2025.mp4" type="video/mp4">浏览器不支持视频播放。</video>
    </section>

    <section class="home-cta"><div><p class="section-kicker light">WELCOME 2026</p><h2>{{ profile?.welcome_slogan || '下一棒，期待与你一起跑' }}</h2><p>{{ profile?.recruitment_info || '具体招新时间、地点和联系方式请等待后台发布。' }}</p></div><div class="home-cta-actions"><SafeImage v-if="profile?.qq_group_qr_code" class="qr-code" :src="profile.qq_group_qr_code" alt="体育部QQ群二维码" /><RouterLink class="round-link" to="/messages">来聊聊 <span>→</span></RouterLink></div></section>
  </main>
</template>
