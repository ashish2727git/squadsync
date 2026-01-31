import { apiClient } from "./client";

export const login = async (email: string, password: string) => {
  const res = await apiClient.post("/api/v1/auth/login", {
    email,
    password,
  });
  return res.data;
};

export const register = async (
  username: string,
  email: string,
  password: string,
  role: string
) => {
  const res = await apiClient.post("/api/v1/auth/register", {
    username,
    email,
    password,
    role,
  });
  return res.data;
};

export const getMe = async () => {
  const res = await apiClient.get("/api/v1/auth/me");
  return res.data;
};
