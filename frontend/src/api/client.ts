// import axios from "axios";
import { useAuthStore } from "../stores/authStore";

import axios from "axios";

// Determine API base URL based on current location
const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    // Always use port 8000 for backend API
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:8000/api/v1';
    }
    // If accessing from network IP, use same IP for backend on port 8000
    return `http://${hostname}:8000/api/v1`;
  }
  return 'http://localhost:8000/api/v1';
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
