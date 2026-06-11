import api from "./api";
import { InterviewSession } from "@/types/interview.types";

export const interviewService = {
  async startSession(topic: string, difficulty: string): Promise<InterviewSession> {
    const response = await api.post<InterviewSession>("/interview/start", {
      topic,
      difficulty,
    });
    return response.data;
  },

  async sendMessage(sessionId: string, message: string): Promise<InterviewSession> {
    const response = await api.post<InterviewSession>(`/interview/${sessionId}/message`, {
      message,
    });
    return response.data;
  },

  async endSession(sessionId: string): Promise<InterviewSession> {
    const response = await api.post<InterviewSession>(`/interview/${sessionId}/end`);
    return response.data;
  },

  async getSession(sessionId: string): Promise<InterviewSession> {
    const response = await api.get<InterviewSession>(`/interview/${sessionId}`);
    return response.data;
  },

  async getSessions(skip = 0, limit = 20): Promise<InterviewSession[]> {
    const response = await api.get<InterviewSession[]>("/interview/sessions", {
      params: { skip, limit },
    });
    return response.data;
  },
};
