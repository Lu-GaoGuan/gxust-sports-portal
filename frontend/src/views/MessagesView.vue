<script setup>
import { computed, onMounted, ref } from 'vue'
import PageBanner from '../components/PageBanner.vue'
import { getApiErrorMessage, portalApi } from '../services/api'

const form = ref({ nickname: '', content: '' })
const messages = ref([])
const loading = ref(true)
const listError = ref('')
const submitting = ref(false)
const submitError = ref('')
const successMessage = ref('')
const canSubmit = computed(() => form.value.nickname.trim().length > 0 && form.value.content.trim().length >= 2 && !submitting.value)
const contentProgress = computed(() => Math.min(100, form.value.content.length / 10))

function formatTime(value) {
  if (!value) return '时间未知'
  return new Intl.DateTimeFormat('zh-CN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
}

function resetSubmitNotice() {
  submitError.value = ''
  successMessage.value = ''
}

async function loadMessages() {
  loading.value = true
  listError.value = ''
  try { messages.value = await portalApi.getMessages() }
  catch (error) { listError.value = getApiErrorMessage(error, '公开留言加载失败，请稍后重试。') }
  finally { loading.value = false }
}

async function submit() {
  if (!canSubmit.value) return
  submitting.value = true
  resetSubmitNotice()
  try {
    const result = await portalApi.submitMessage({ nickname: form.value.nickname.trim(), content: form.value.content.trim() })
    form.value = { nickname: '', content: '' }
    successMessage.value = `留言已发布（编号 ${result.id}）。`
    await loadMessages()
  } catch (error) {
    submitError.value = getApiErrorMessage(error, '留言提交失败，请稍后重试。')
  } finally { submitting.value = false }
}

onMounted(loadMessages)
</script>

<template>
  <main><PageBanner eyebrow="MESSAGE BOARD" title="留言交流" description="有问题、有想法，或者只是想说声你好，都欢迎留在这里。" number="06" />
    <section class="content-section message-layout"><form @submit.prevent="submit"><p class="section-kicker">LEAVE A MESSAGE</p><h2>给体育部留句话</h2><label class="interactive-field"><span class="field-heading">你的昵称<small>{{ form.nickname.length }} / 50</small></span><input v-model="form.nickname" required maxlength="50" placeholder="怎么称呼你" @input="resetSubmitNotice"></label><label class="interactive-field"><span class="field-heading">留言内容<small>{{ form.content.length }} / 1000</small></span><textarea v-model="form.content" required minlength="2" maxlength="1000" rows="6" placeholder="想问的问题或想说的话" @input="resetSubmitNotice"></textarea><i class="content-meter" aria-hidden="true"><span :style="{ width: `${contentProgress}%` }"></span></i></label><p class="form-hint">留言提交后会立即公开。请勿提交联系方式、身份证号等个人敏感信息。</p><button class="button button-blue" type="submit" :disabled="!canSubmit">{{ submitting ? '正在发布…' : '发布留言' }}</button><p v-if="successMessage" class="success-message" role="status">{{ successMessage }}</p><p v-if="submitError" class="submit-error" role="alert">{{ submitError }}</p></form>
      <div class="message-list-area"><div v-if="loading" class="data-state"><span class="state-spinner"></span><p>正在加载留言…</p></div><div v-else-if="listError" class="data-state error"><p>{{ listError }}</p><button type="button" @click="loadMessages">重新加载</button></div><div v-else-if="!messages.length" class="data-state empty"><h3>暂无公开留言</h3><p>还没有留言，欢迎提交第一条。</p></div><TransitionGroup v-else name="message-list" tag="div" class="message-wall"><article v-for="message in messages" :key="message.id"><div class="avatar">{{ message.nickname.slice(0, 1) }}</div><div><header><b>{{ message.nickname }}</b><small>{{ formatTime(message.submitted_at) }}</small></header><p>{{ message.content }}</p></div></article></TransitionGroup></div>
    </section>
  </main>
</template>
