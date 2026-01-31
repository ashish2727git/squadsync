import { create } from "zustand";
import { getMe } from "../api/auth";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: any | null;
  isAuthenticated: boolean;
  setToken: (token: string) => Promise<void>;
  setAuth: (accessToken: string, refreshToken: string, user: any) => void;
  updateAccessToken: (token: string) => void;
  clearAuth: () => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem("access_token"),
  refreshToken: localStorage.getItem("refresh_token"),
  user: null,
  isAuthenticated: !!localStorage.getItem("access_token"),

  setToken: async (token) => {
    localStorage.setItem("access_token", token);
    const user = await getMe();
    set({ accessToken: token, user, isAuthenticated: true });
  },

  setAuth: (accessToken, refreshToken, user) => {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    set({ accessToken, refreshToken, user, isAuthenticated: true });
  },

  updateAccessToken: (token) => {
    localStorage.setItem("access_token", token);
    set({ accessToken: token });
  },

  clearAuth: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ accessToken: null, refreshToken: null, user: null, isAuthenticated: false });
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ accessToken: null, refreshToken: null, user: null, isAuthenticated: false });
  },
}));
