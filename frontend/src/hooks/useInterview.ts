import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { interviewService } from "@/services/interview.service";
import { InterviewSession } from "@/types/interview.types";

export function useInterview() {
  const queryClient = useQueryClient();

  const startMutation = useMutation({
    mutationFn: ({ topic, difficulty }: { topic: string; difficulty: string }) =>
      interviewService.startSession(topic, difficulty),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["interviews", "history"] });
    },
  });

  const sendMessageMutation = useMutation({
    mutationFn: ({ sessionId, message }: { sessionId: string; message: string }) =>
      interviewService.sendMessage(sessionId, message),
    onSuccess: (data: InterviewSession, variables: { sessionId: string; message: string }) => {
      // Optimistically update or invalidate detail queries
      queryClient.invalidateQueries({ queryKey: ["interviews", "detail", variables.sessionId] });
    },
  });

  const endMutation = useMutation({
    mutationFn: (sessionId: string) => interviewService.endSession(sessionId),
    onSuccess: (data: InterviewSession) => {
      queryClient.invalidateQueries({ queryKey: ["interviews", "history"] });
      queryClient.invalidateQueries({ queryKey: ["interviews", "detail", data.id] });
    },
  });

  const useSessionsQuery = (skip = 0, limit = 20) =>
    useQuery({
      queryKey: ["interviews", "history", skip, limit],
      queryFn: () => interviewService.getSessions(skip, limit),
    });

  const useSessionDetailsQuery = (sessionId: string | null) =>
    useQuery({
      queryKey: ["interviews", "detail", sessionId],
      queryFn: () => interviewService.getSession(sessionId!),
      enabled: !!sessionId,
    });

  return {
    startSession: startMutation.mutateAsync,
    isStarting: startMutation.isPending,
    startError: startMutation.error,

    sendMessage: sendMessageMutation.mutateAsync,
    isSending: sendMessageMutation.isPending,
    sendError: sendMessageMutation.error,

    endSession: endMutation.mutateAsync,
    isEnding: endMutation.isPending,
    endError: endMutation.error,

    useSessions: useSessionsQuery,
    useSessionDetails: useSessionDetailsQuery,
  };
}
