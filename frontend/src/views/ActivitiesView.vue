<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import PageBanner from '../components/PageBanner.vue'
import SafeImage from '../components/SafeImage.vue'
import { getApiErrorMessage, portalApi } from '../services/api'

const activities = ref([])
const loading = ref(true)
const errorMessage = ref('')
const selected = ref('全部')
const selectedImage = ref(null)
const categories = computed(() => ['全部', ...new Set(activities.value.map((item) => item.category_label))])
const filtered = computed(() => selected.value === '全部' ? activities.value : activities.value.filter((item) => item.category_label === selected.value))

function activityAssets(activity) {
  const assets = [...(activity.media || [])]
  if (activity.cover && !assets.some((item) => item.file === activity.cover)) {
    assets.unshift({ id: `cover-${activity.id}`, file: activity.cover, media_type: 'image', description: `${activity.name}封面` })
  }
  return assets
}
function mediaLayout(media, index) {
  if (media.media_type === 'video') return ['media-video', { 'media-featured': index === 0 }]
  const ratio = media.width && media.height ? media.width / media.height : 4 / 3
  return [
    ratio >= 1.85 ? 'media-wide' : ratio <= 0.82 ? 'media-portrait' : 'media-landscape',
    { 'media-featured': index === 0 },
  ]
}
const formatDate = (value) => value ? value.replaceAll('-', '.') : '日期待公布'
const closeLightbox = () => { selectedImage.value = null }
const handleKeydown = (event) => { if (event.key === 'Escape') closeLightbox() }

async function loadActivities() {
  loading.value = true
  errorMessage.value = ''
  try { activities.value = await portalApi.getActivities() }
  catch (error) { errorMessage.value = getApiErrorMessage(error, '活动资料加载失败，请稍后重试。') }
  finally { loading.value = false }
}

watch(selectedImage, (image) => { document.body.classList.toggle('lightbox-open', Boolean(image)) })
onMounted(() => { window.addEventListener('keydown', handleKeydown); loadActivities() })
onBeforeUnmount(() => { window.removeEventListener('keydown', handleKeydown); document.body.classList.remove('lightbox-open') })
</script>

<template>
  <main><PageBanner eyebrow="ACTIVITY ARCHIVE" title="活动回顾" description="赛场、团建、迎新与生日会——那些认真投入的瞬间，汇成了部门共同的青春档案。" number="04" />
    <section class="content-section">
      <div v-if="loading" class="data-state page-state"><span class="state-spinner"></span><h2>正在加载活动资料</h2><p>活动照片和视频正在从后台读取。</p></div>
      <div v-else-if="errorMessage" class="data-state page-state error"><h2>活动资料暂时无法加载</h2><p>{{ errorMessage }}</p><button type="button" @click="loadActivities">重新加载</button></div>
      <div v-else-if="!activities.length" class="data-state page-state empty"><h2>暂无活动资料</h2><p>后台尚未发布允许展示的活动和媒体。</p></div>
      <template v-else>
        <div class="activity-toolbar"><div class="filter-tabs" role="group" aria-label="按活动分类筛选"><button v-for="category in categories" :key="category" type="button" :class="{ active: selected === category }" :aria-pressed="selected === category" @click="selected = category">{{ category }}</button></div><p>共 <b>{{ filtered.length }}</b> 项记录</p></div>
        <TransitionGroup name="cards" tag="div" class="activity-gallery"><article v-for="activity in filtered" :key="activity.id">
          <div v-if="activityAssets(activity).length" class="activity-media-stack">
            <template v-for="(media, mediaIndex) in activityAssets(activity)" :key="media.id">
              <video v-if="media.media_type === 'video'" :class="mediaLayout(media, mediaIndex)" controls preload="none"><source :src="media.file">浏览器不支持视频播放。</video>
              <button v-else class="activity-image-button" :class="mediaLayout(media, mediaIndex)" type="button" :aria-label="`查看${activity.name}${mediaIndex ? `第${mediaIndex + 1}张` : ''}大图`" @click="selectedImage = { ...media, activity }"><SafeImage :src="media.file" :alt="media.description || activity.name" /><span>查看大图</span></button>
            </template>
          </div>
          <div v-else class="activity-media-empty"><SafeImage src="" :alt="activity.name" /></div>
          <div><small>{{ activity.category_label }} / {{ formatDate(activity.activity_date) }}</small><h2>{{ activity.name }}</h2><p>{{ activity.introduction || '活动简介待补充。' }}</p><p v-if="activity.media?.length" class="media-count">包含 {{ activity.media.length }} 项活动媒体</p></div>
        </article></TransitionGroup>
        <p class="material-note">页面只展示后台标记为允许公开的活动数据。正式上线前仍应统一核对照片、视频及肖像授权。</p>
      </template>
    </section>
    <Teleport to="body"><Transition name="lightbox"><div v-if="selectedImage" class="image-lightbox" role="dialog" aria-modal="true" :aria-label="selectedImage.activity.name" @click.self="closeLightbox"><figure><SafeImage :src="selectedImage.file" :alt="selectedImage.description || selectedImage.activity.name" /><figcaption><div><small>{{ selectedImage.activity.category_label }} · {{ formatDate(selectedImage.activity.activity_date) }}</small><b>{{ selectedImage.description || selectedImage.activity.name }}</b></div><button type="button" aria-label="关闭大图" @click="closeLightbox">×</button></figcaption></figure></div></Transition></Teleport>
  </main>
</template>
