// import axios from "axios";
import { useAuthStore } from "../stores/authStore";

import axios from "axios";

export const apiClient = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  withCredentials: true,
});


apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
