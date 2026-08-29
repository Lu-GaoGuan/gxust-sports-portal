<script setup>
import { onMounted, ref } from 'vue'
import PageBanner from '../components/PageBanner.vue'
import { getApiErrorMessage, portalApi } from '../services/api'

const token = ref('')
const messages = ref([])
const loading = ref(false)
const errorMessage = ref('')
const deletingId = ref(null)
const authenticated = ref(false)

function formatTime(value) {
  return value
    ? new Intl.DateTimeFormat('zh-CN', {
        dateStyle: 'medium',
        timeStyle: 'short',
      }).format(new Date(value))
    : '时间未知'
}

async function loadMessages() {
  if (!token.value.trim()) return
  loading.value = true
  errorMessage.value = ''
  try {
    messages.value = await portalApi.getAdminMessages(token.value.trim())
    authenticated.value = true
    sessionStorage.setItem('commentsAdminToken', token.value.trim())
  } catch (error) {
    authenticated.value = false
    messages.value = []
    errorMessage.value = getApiErrorMessage(error, '无法进入评论管理。')
  } finally {
    loading.value = false
  }
}

async function removeMessage(message) {
  if (!window.confirm(`确定删除“${message.nickname}”的这条评论吗？`)) return
  deletingId.value = message.id
  errorMessage.value = ''
  try {
    await portalApi.deleteAdminMessage(message.id, token.value.trim())
    messages.value = messages.value.filter((item) => item.id !== message.id)
  } catch (error) {
    errorMessage.value = getApiErrorMessage(error, '删除评论失败。')
  } finally {
    deletingId.value = null
  }
}

function logout() {
  sessionStorage.removeItem('commentsAdminToken')
  token.value = ''
  messages.value = []
  authenticated.value = false
  errorMessage.value = ''
}

onMounted(() => {
  token.value = sessionStorage.getItem('commentsAdminToken') || ''
  if (token.value) loadMessages()
})
</script>

<template>
  <main>
    <PageBanner
      eyebrow="COMMENT ADMIN"
      title="评论管理"
      description="管理网站当前公开显示的留言。"
      number="A"
    />
    <section class="content-section admin-comments">
      <form v-if="!authenticated" class="admin-login" @submit.prevent="loadMessages">
        <h2>管理员验证</h2>
        <label class="interactive-field">
          <span>管理员口令</span>
          <input v-model="token" type="password" autocomplete="current-password" required>
        </label>
        <button class="button button-blue" type="submit" :disabled="loading">
          {{ loading ? '正在验证…' : '进入管理' }}
        </button>
      </form>
      <template v-else>
        <header class="admin-toolbar">
          <div><h2>公开评论</h2><p>共 {{ messages.length }} 条</p></div>
          <button class="button admin-logout" type="button" @click="logout">退出</button>
        </header>
        <div v-if="!messages.length" class="data-state empty"><p>当前没有公开评论。</p></div>
        <div v-else class="admin-comment-list">
          <article v-for="message in messages" :key="message.id">
            <div>
              <header><b>{{ message.nickname }}</b><small>{{ formatTime(message.submitted_at) }}</small></header>
              <p>{{ message.content }}</p>
            </div>
            <button
              class="admin-delete"
              type="button"
              :disabled="deletingId === message.id"
              @click="removeMessage(message)"
            >
              {{ deletingId === message.id ? '删除中…' : '删除' }}
            </button>
          </article>
        </div>
      </template>
      <p v-if="errorMessage" class="submit-error" role="alert">{{ errorMessage }}</p>
    </section>
  </main>
</template>
