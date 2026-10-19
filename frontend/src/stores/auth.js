import { defineStore } from 'pinia'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('access_token'),
    refreshToken: localStorage.getItem('refresh_token'),
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),
  getters: { isAuthenticated: (s) => !!s.accessToken },
  actions: {
    async login(email, password) {
      const { data } = await axios.post(`${API}/auth/login`, { email, password })
      this.accessToken = data.access_token
      this.refreshToken = data.refresh_token
      this.user = data.user
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user', JSON.stringify(data.user))
    },
    async refresh() {
      const { data } = await axios.post(`${API}/auth/refresh`, null, {
        headers: { Authorization: `Bearer ${this.refreshToken}` },
      })
      this.accessToken = data.access_token
      localStorage.setItem('access_token', data.access_token)
      return data.access_token
    },
    logout() {
      this.accessToken = this.refreshToken = this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    },
  },
})
