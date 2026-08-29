<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import PageBanner from '../components/PageBanner.vue'
import { getApiErrorMessage, portalApi } from '../services/api'

const faqItems = ref([])
const loading = ref(true)
const errorMessage = ref('')
const query = ref('')
const opened = ref(null)
const filteredItems = computed(() => {
  const keyword = query.value.trim().toLowerCase()
  if (!keyword) return faqItems.value
  return faqItems.value.filter((item) => `${item.question} ${item.answer}`.toLowerCase().includes(keyword))
})

async function loadFaqs() {
  loading.value = true
  errorMessage.value = ''
  try {
    faqItems.value = await portalApi.getFaqs()
    opened.value = faqItems.value[0]?.id ?? null
  } catch (error) { errorMessage.value = getApiErrorMessage(error, '问答资料加载失败，请稍后重试。') }
  finally { loading.value = false }
}

watch(query, () => { opened.value = filteredItems.value[0]?.id ?? null })
onMounted(loadFaqs)
</script>

<template>
  <main><PageBanner eyebrow="FRESHMAN FAQ" title="新生问答" description="关于学生会、第二课堂与体育部，你可能想知道的事情。" number="05" />
    <section class="content-section faq-layout"><aside><p class="section-kicker">BEFORE YOU ASK</p><h2>先了解，<br>再做选择</h2><p>政策和执行口径可能更新，请以学院当期正式通知及个人培养要求为准。</p><label v-if="!loading && !errorMessage && faqItems.length" class="faq-search interactive-field"><span>搜索问题</span><span class="search-input-wrap"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m21 21-4.35-4.35m2.35-5.65a8 8 0 1 1-16 0 8 8 0 0 1 16 0Z"/></svg><input v-model="query" type="search" placeholder="例如：综测、志愿服务、第二课堂" aria-label="搜索新生问答"></span><small>找到 {{ filteredItems.length }} 条相关问答</small></label></aside>
      <div class="accordion">
        <div v-if="loading" class="data-state page-state"><span class="state-spinner"></span><h2>正在加载新生问答</h2><p>请稍候，正在读取后台发布的内容。</p></div>
        <div v-else-if="errorMessage" class="data-state page-state error"><h2>问答资料暂时无法加载</h2><p>{{ errorMessage }}</p><button type="button" @click="loadFaqs">重新加载</button></div>
        <div v-else-if="!faqItems.length" class="data-state page-state empty"><h2>暂无问答内容</h2><p>后台尚未发布允许展示的新生问答。</p></div>
        <template v-else><article v-for="(item, index) in filteredItems" :key="item.id"><button type="button" :aria-expanded="opened === item.id" @click="opened = opened === item.id ? null : item.id"><span>{{ String(index + 1).padStart(2, '0') }}</span><b>{{ item.question }}</b><i>{{ opened === item.id ? '−' : '+' }}</i></button><div class="faq-answer" :class="{ open: opened === item.id }" :aria-hidden="opened !== item.id"><div><p>{{ item.answer }}</p></div></div></article><div v-if="!filteredItems.length" class="faq-empty"><b>暂未找到相关问题</b><p>可以换一个关键词，或到留言交流页告诉我们你想了解的内容。</p></div></template>
        <div class="policy-source"><b>政策核对说明</b><p>涉及综合测评和第二课堂的回答应由管理员依据学校、学院当前有效文件维护。</p><small>具体执行要求及不同年级培养要求可能调整，请以当年正式通知和个人培养要求为准。</small></div>
      </div>
    </section>
  </main>
</template>
