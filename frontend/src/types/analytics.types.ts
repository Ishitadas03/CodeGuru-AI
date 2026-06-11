export interface DsaStats {
  total_solved: number;
  total_attempted: number;
  solved_by_difficulty: Record<string, number>;
  solved_by_topic: Record<string, number>;
}

export interface IssueCategoryCount {
  category: string;
  count: number;
}

export interface ScoreHistory {
  date: string;
  score: number;
}

export interface ReviewStats {
  total_reviews: number;
  average_score: number;
  common_issues: IssueCategoryCount[];
  score_history: ScoreHistory[];
}

export interface Streak {
  current_streak: number;
  longest_streak: number;
}

export interface HeatmapBlock {
  date: string;
  count: number;
}

export interface AnalyticsOverview {
  dsa_stats: DsaStats;
  review_stats: ReviewStats;
  streak: Streak;
  heatmap: HeatmapBlock[];
}

export interface DSAProgressUpdateRequest {
  problem_id: string;
  topic_slug: string;
  status: "solved" | "attempted";
  language: string;
  code: string;
}
