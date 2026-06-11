import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { authService } from "@/services/auth.service";
import { useAuthStore } from "@/store/authStore";
import { LoginRequest, RegisterRequest } from "@/schemas/auth";
import { Profile } from "@/types/user.types";
import { ROUTES } from "@/lib/constants";

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const loginState = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: async (payload: LoginRequest) => {
      const tokens = await authService.login(payload);
      // Temporarily write token to store for getCurrentUser call in next step
      loginState.setTokens(tokens.access_token, tokens.refresh_token);
      
      const user = await authService.getCurrentUser();
      loginState.login(user, tokens);
      return { user, tokens };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user"] });
      router.push(ROUTES.DASHBOARD);
    },
  });

  const googleLoginMutation = useMutation({
    mutationFn: async (token: string) => {
      const tokens = await authService.googleAuth(token);
      loginState.setTokens(tokens.access_token, tokens.refresh_token);
      
      const user = await authService.getCurrentUser();
      loginState.login(user, tokens);
      return { user, tokens };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user"] });
      router.push(ROUTES.DASHBOARD);
    },
  });

  const registerMutation = useMutation({
    mutationFn: async (payload: RegisterRequest) => {
      return await authService.register(payload);
    },
    onSuccess: () => {
      router.push(ROUTES.LOGIN);
    },
  });

  const logoutMutation = useMutation({
    mutationFn: async () => {
      const refreshToken = loginState.refreshToken;
      if (refreshToken) {
        await authService.logout(refreshToken);
      }
    },
    onSettled: () => {
      loginState.logout();
      queryClient.clear();
      router.push(ROUTES.LOGIN);
    },
  });

  const profileQuery = useQuery({
    queryKey: ["user", "me"],
    queryFn: () => authService.getCurrentUser(),
    enabled: loginState.isAuthenticated,
    retry: false,
  });

  const updateProfileMutation = useMutation({
    mutationFn: (payload: Partial<Profile>) => authService.updateProfile(payload),
    onSuccess: (updatedProfile: Profile) => {
      if (loginState.user) {
        loginState.setUser({
          ...loginState.user,
          profile: updatedProfile,
        });
      }
      queryClient.setQueryData(["user", "me"], (oldData: any) => {
        if (!oldData) return oldData;
        return {
          ...oldData,
          profile: updatedProfile,
        };
      });
    },
  });

  return {
    user: loginState.user,
    isAuthenticated: loginState.isAuthenticated,
    login: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error,
    googleLogin: googleLoginMutation.mutateAsync,
    isLoggingInWithGoogle: googleLoginMutation.isPending,
    register: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    registerError: registerMutation.error,
    logout: logoutMutation.mutate,
    isLoggingOut: logoutMutation.isPending,
    profile: profileQuery.data,
    isLoadingProfile: profileQuery.isLoading,
    updateProfile: updateProfileMutation.mutateAsync,
    isUpdatingProfile: updateProfileMutation.isPending,
  };
}
