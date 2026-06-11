"use client";

import React from "react";
import InterviewSimulator from "@/features/interview/InterviewSimulator";

export default function InterviewPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-3xl font-black font-display tracking-tight text-foreground">
          TECHNICAL INTERVIEW SIMULATOR
        </h1>
        <p className="text-xs sm:text-sm text-muted-foreground font-black uppercase tracking-widest">
          Simulate professional coding, system design, or behavioral interviews with customized AI mentors and get instant grading feedback.
        </p>
      </div>
      <InterviewSimulator />
    </div>
  );
}
