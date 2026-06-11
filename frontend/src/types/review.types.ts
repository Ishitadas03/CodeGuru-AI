export interface ReviewIssue {
  category: "security" | "readability" | "performance" | "style";
  line: number;
  description: string;
  suggestion: string;
}

export interface ReviewBug {
  line: number;
  severity: "error" | "warning";
  description: string;
  fix: string;
}

export interface ReviewReport {
  id: string;
  submission_id: string;
  score: number;
  summary: string;
  issues: ReviewIssue[];
  refactored_code: string;
  has_bugs: boolean;
  bugs: ReviewBug[];
  created_at: string;
}
