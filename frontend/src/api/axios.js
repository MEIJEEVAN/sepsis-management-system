import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })
let refreshing = null

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) config.headers.Authorization = `Bearer ${auth.accessToken}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    const auth = useAuthStore()
    if (error.response?.status === 401 && !original._retried && auth.refreshToken) {
      original._retried = true
      try {
        refreshing = refreshing || auth.refresh().finally(() => (refreshing = null))
        const token = await refreshing
        original.headers.Authorization = `Bearer ${token}`
        return api(original)
      } catch (e) {
        /* fall through to logout */
      }
    }
    if (error.response?.status === 401) {
      auth.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default api
