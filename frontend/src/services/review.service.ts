import api from "./api";
import { ReviewReport } from "@/types/review.types";

export const reviewService = {
  async submitReview(code: string, language: string): Promise<ReviewReport> {
    const response = await api.post<ReviewReport>("/reviews", { code, language });
    return response.data;
  },

  async getReview(reviewId: string): Promise<ReviewReport> {
    const response = await api.get<ReviewReport>(`/reviews/${reviewId}`);
    return response.data;
  },

  async getHistory(skip = 0, limit = 20): Promise<ReviewReport[]> {
    const response = await api.get<ReviewReport[]>("/reviews/history", {
      params: { skip, limit },
    });
    return response.data;
  },
};
