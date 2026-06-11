export const API_URL = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  DASHBOARD: "/dashboard",
  REVIEW: "/review",
  DSA: "/dsa",
  INTERVIEW: "/interview",
  ROADMAP: "/roadmap",
  ANALYTICS: "/analytics",
  DOCUMENTS: "/documents",
  SETTINGS: "/settings",
};

export const LANGUAGES = [
  { value: "python", label: "Python" },
  { value: "javascript", label: "JavaScript" },
  { value: "typescript", label: "TypeScript" },
  { value: "java", label: "Java" },
  { value: "cpp", label: "C++" },
] as const;

export const DSA_TOPICS = [
  "Arrays & Hashing",
  "Two Pointers",
  "Sliding Window",
  "Stack & Queue",
  "Binary Search",
  "Linked List",
  "Trees & Graphs",
  "Dynamic Programming",
  "Backtracking",
  "Greedy Algorithms",
] as const;
