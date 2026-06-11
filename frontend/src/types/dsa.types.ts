export interface DSATopic {
  id: string;
  name: string;
  slug: string;
  description: string;
}

export interface DSAProblem {
  id: string;
  topic_slug: string;
  title: string;
  difficulty: "easy" | "medium" | "hard";
  description: string;
  starter_code: Record<string, string>;
}

export interface DryRunStep {
  step: number;
  line_number: number;
  description: string;
  variables_state: string;
}

export interface Complexity {
  time_complexity: string;
  time_explanation: string;
  space_complexity: string;
  space_explanation: string;
}

export interface DSAExplanation {
  concept_name: string;
  explanation: string;
  complexity: Complexity;
  dry_run: DryRunStep[];
}
