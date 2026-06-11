import { useMutation, useQuery } from "@tanstack/react-query";
import api from "@/services/api";
import { DSATopic, DSAProblem, DSAExplanation } from "@/types/dsa.types";

export function useDSA() {
  const useTopicsQuery = () =>
    useQuery({
      queryKey: ["dsa", "topics"],
      queryFn: async () => {
        const response = await api.get<DSATopic[]>("/dsa/topics");
        return response.data;
      },
    });

  const useProblemsQuery = (topicSlug?: string) =>
    useQuery({
      queryKey: ["dsa", "problems", topicSlug],
      queryFn: async () => {
        const response = await api.get<DSAProblem[]>("/dsa/problems", {
          params: topicSlug ? { topic_slug: topicSlug } : {},
        });
        return response.data;
      },
    });

  const useProblemDetailsQuery = (problemId: string | null) =>
    useQuery({
      queryKey: ["dsa", "problem", problemId],
      queryFn: async () => {
        const response = await api.get<DSAProblem>(`/dsa/problems/${problemId}`);
        return response.data;
      },
      enabled: !!problemId,
    });

  const explainSolutionMutation = useMutation({
    mutationFn: async ({
      problemId,
      code,
      language,
    }: {
      problemId: string;
      code: string;
      language: string;
    }) => {
      const response = await api.post<DSAExplanation>(
        `/dsa/problems/${problemId}/explain`,
        { code, language }
      );
      return response.data;
    },
  });

  return {
    useTopics: useTopicsQuery,
    useProblems: useProblemsQuery,
    useProblemDetails: useProblemDetailsQuery,
    explainSolution: explainSolutionMutation.mutateAsync,
    isExplaining: explainSolutionMutation.isPending,
    explainError: explainSolutionMutation.error,
  };
}
