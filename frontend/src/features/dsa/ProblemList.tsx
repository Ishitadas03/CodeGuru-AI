"use client";

import React, { useState } from "react";
import { DSAProblem } from "@/types/dsa.types";
import { ArrowRight, Code } from "lucide-react";

interface ProblemListProps {
  problems: DSAProblem[];
  selectedProblemId: string | null;
  onSelectProblem: (problem: DSAProblem) => void;
}

export default function ProblemList({
  problems,
  selectedProblemId,
  onSelectProblem,
}: ProblemListProps) {
  const [difficultyFilter, setDifficultyFilter] = useState<string>("all");

  const filteredProblems = problems.filter((prob) => {
    if (difficultyFilter === "all") return true;
    return prob.difficulty === difficultyFilter;
  });

  const getDifficultyBadge = (difficulty: DSAProblem["difficulty"]) => {
    switch (difficulty) {
      case "easy":
        return "bg-aether-emerald/10 text-[#6EE7B7] border-aether-emerald/20";
      case "medium":
        return "bg-aether-amber/10 text-[#FCD34D] border-aether-amber/20";
      case "hard":
        return "bg-aether-rose/10 text-[#F9A8D4] border-aether-rose/20";
    }
  };

  return (
    <div className="space-y-4">
      {/* Filtering Header */}
      <div className="flex items-center justify-between border-b border-aether pb-3">
        <h4 className="font-bold text-foreground text-base">Coding Challenges</h4>
        
        <div className="flex gap-1 bg-obsidian p-1 rounded-xl border border-aether">
          {["all", "easy", "medium", "hard"].map((diff) => (
            <button
              key={diff}
              onClick={() => setDifficultyFilter(diff)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg capitalize transition-colors ${
                difficultyFilter === diff
                  ? "bg-obsidian-depth text-foreground border border-aether shadow-sm"
                  : "text-[#8892B0] hover:text-foreground"
              }`}
            >
              {diff}
            </button>
          ))}
        </div>
      </div>

      {/* Problems Directory Grid */}
      {filteredProblems.length === 0 ? (
        <div className="text-center py-8 text-xs text-[#8892B0]">
          No coding challenges found matching filter.
        </div>
      ) : (
        <div className="space-y-3">
          {filteredProblems.map((problem) => {
            const isSelected = selectedProblemId === problem.id;
            return (
              <div
                key={problem.id}
                onClick={() => onSelectProblem(problem)}
                className={`p-4 border rounded-2xl flex items-center justify-between cursor-pointer transition-all duration-150 ${
                  isSelected
                    ? "border-aether-indigo/50 bg-aether-indigo/10 shadow-[0_0_15px_rgba(91,108,249,0.1)]"
                    : "border-aether bg-obsidian-depth/40 hover:border-aether-indigo/20 hover:bg-obsidian-depth/60"
                }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="p-2 rounded-xl bg-obsidian-depth border border-aether">
                    <Code className="w-4 h-4 text-[#8892B0]" />
                  </div>
                  <div className="min-w-0">
                    <h5 className="font-bold text-foreground text-sm truncate">
                      {problem.title}
                    </h5>
                    <span
                      className={`inline-block mt-1 text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full border ${getDifficultyBadge(
                        problem.difficulty
                      )}`}
                    >
                      {problem.difficulty}
                    </span>
                  </div>
                </div>

                <div className="flex-shrink-0 text-[#8892B0] pl-4">
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
