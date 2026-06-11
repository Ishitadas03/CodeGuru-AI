export interface InterviewMessage {
  role: "interviewer" | "user";
  content: string;
}

export interface InterviewEvaluation {
  score: number;
  summary: string;
  strengths: string[];
  weakness_areas: string[];
  correct_code_suggestions: string;
  improvement_tips: string[];
}

export interface InterviewSession {
  id: string;
  user_id: string;
  topic: string;
  difficulty: string;
  messages: InterviewMessage[];
  score: number | null;
  feedback: InterviewEvaluation | null;
  is_completed: boolean;
  created_at: string;
}

export interface InterviewStartRequest {
  topic: string;
  difficulty: string;
}

export interface InterviewMessageRequest {
  message: string;
}
