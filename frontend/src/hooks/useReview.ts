import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { reviewService } from "@/services/review.service";

export function useReview() {
  const queryClient = useQueryClient();

  const submitReviewMutation = useMutation({
    mutationFn: ({ code, language }: { code: string; language: string }) =>
      reviewService.submitReview(code, language),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reviews", "history"] });
    },
  });

  const useHistoryQuery = (skip = 0, limit = 20) =>
    useQuery({
      queryKey: ["reviews", "history", skip, limit],
      queryFn: () => reviewService.getHistory(skip, limit),
    });

  const useReviewDetailsQuery = (reviewId: string | null) =>
    useQuery({
      queryKey: ["reviews", "detail", reviewId],
      queryFn: () => reviewService.getReview(reviewId!),
      enabled: !!reviewId,
    });

  return {
    submitReview: submitReviewMutation.mutateAsync,
    isSubmitting: submitReviewMutation.isPending,
    submitError: submitReviewMutation.error,
    useHistory: useHistoryQuery,
    useReviewDetails: useReviewDetailsQuery,
  };
}
