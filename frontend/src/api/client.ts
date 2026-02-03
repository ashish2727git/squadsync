// import axios from "axios";
import { useAuthStore } from "../stores/authStore";

import axios from "axios";

// Backend API port
const API_PORT = 8000;

// Determine API base URL based on current location
const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return `http://localhost:${API_PORT}/api/v1`;
    }
    return `http://${hostname}:${API_PORT}/api/v1`;
  }
  return `http://localhost:${API_PORT}/api/v1`;
};

export const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  withCredentials: false,
});


apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
