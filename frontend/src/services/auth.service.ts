import api from "./api";
import { User, Profile, AuthTokens } from "@/types/user.types";
import { RegisterRequest, LoginRequest } from "@/schemas/auth"; // We will map these schemas or define arguments directly

export const authService = {
  async login(payload: LoginRequest): Promise<AuthTokens> {
    const response = await api.post<AuthTokens>("/auth/login", payload);
    return response.data;
  },

  async register(payload: RegisterRequest): Promise<User> {
    const response = await api.post<User>("/auth/register", payload);
    return response.data;
  },

  async logout(refreshToken: string): Promise<void> {
    await api.post("/auth/logout", { refresh_token: refreshToken });
  },

  async googleAuth(token: string): Promise<AuthTokens> {
    const response = await api.post<AuthTokens>("/auth/google", { refresh_token: token });
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>("/users/me");
    return response.data;
  },

  async updateProfile(payload: Partial<Profile>): Promise<Profile> {
    const response = await api.put<Profile>("/users/me/profile", payload);
    return response.data;
  },
};
