import { defineStore } from "pinia";
import api from "../api/axios";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    accessToken: localStorage.getItem("access_token") || null,
    refreshToken: localStorage.getItem("refresh_token") || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },
  actions: {
    async login(credentials) {
      const { data } = await api.post("/auth/login", credentials);
      this.accessToken = data.access_token;
      this.refreshToken = data.refresh_token;
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      await this.fetchMe();
    },
    async fetchMe() {
      const { data } = await api.get("/auth/me");
      this.user = data;
    },
    logout() {
      this.user = null;
      this.accessToken = null;
      this.refreshToken = null;
      localStorage.clear();
    },
  },
});
