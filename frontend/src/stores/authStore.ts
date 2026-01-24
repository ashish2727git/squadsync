import { create } from "zustand";
import { getMe } from "../api/auth";

interface AuthState {
  accessToken: string | null;
  user: any | null;
  setToken: (token: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem("access_token"),
  user: null,

  setToken: async (token) => {
    localStorage.setItem("access_token", token);
    const user = await getMe();
    set({ accessToken: token, user });
  },

  logout: () => {
    localStorage.removeItem("access_token");
    set({ accessToken: null, user: null });
  },
}));
