import axios from 'axios'

const apiBaseURL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api').replace(/\/$/, '')

const api = axios.create({
  baseURL: apiBaseURL,
  timeout: 10000,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

export const portalApi = {
  getProfile: () => api.get('/profile/').then(({ data }) => data),
  getMembers: () => api.get('/members/').then(({ data }) => data),
  getCurrentMembers: () => api.get('/members/current/').then(({ data }) => data),
  getActivities: () => api.get('/activities/').then(({ data }) => data),
  getFaqs: () => api.get('/faqs/').then(({ data }) => data),
  getMessages: () => api.get('/messages/').then(({ data }) => data),
  submitMessage: (payload) => api.post('/messages/', payload).then(({ data }) => data),
}

export function getApiErrorMessage(error, fallback = '请求失败，请稍后重试。') {
  if (!error?.response) {
    return error?.code === 'ECONNABORTED'
      ? '请求超时，请检查网络后重试。'
      : '暂时无法连接后端服务，请确认服务已启动后重试。'
  }
  if (error.response.status === 429) return '提交过于频繁，请稍后再试。'
  const data = error.response.data
  if (typeof data === 'string' && data.trim()) return data
  if (data?.detail) return data.detail
  if (data && typeof data === 'object') {
    const firstError = Object.values(data).flat()[0]
    if (firstError) return String(firstError)
  }
  return fallback
}

export default api
