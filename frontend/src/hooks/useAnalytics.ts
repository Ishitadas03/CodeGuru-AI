import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/services/api";
import { AnalyticsOverview, DSAProgressUpdateRequest } from "@/types/analytics.types";

export function useAnalytics() {
  const queryClient = useQueryClient();

  const useOverviewQuery = () =>
    useQuery({
      queryKey: ["analytics", "overview"],
      queryFn: async () => {
        const response = await api.get<AnalyticsOverview>("/analytics/overview");
        return response.data;
      },
    });

  const updateProgressMutation = useMutation({
    mutationFn: async (payload: DSAProgressUpdateRequest) => {
      const response = await api.post("/analytics/dsa/progress", payload);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate the overview query to update stats dynamically
      queryClient.invalidateQueries({ queryKey: ["analytics", "overview"] });
      queryClient.invalidateQueries({ queryKey: ["dsa", "problems"] });
    },
  });

  return {
    useOverview: useOverviewQuery,
    updateProgress: updateProgressMutation.mutateAsync,
    isUpdatingProgress: updateProgressMutation.isPending,
  };
}
