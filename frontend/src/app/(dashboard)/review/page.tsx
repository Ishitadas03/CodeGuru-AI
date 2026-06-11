"use client";

import React from "react";
import ReviewWorkspace from "@/features/review/ReviewWorkspace";

export default function ReviewPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-3xl font-black font-display tracking-tight text-foreground">
          AI CODE REVIEW
        </h1>
        <p className="text-xs sm:text-sm text-muted-foreground font-black uppercase tracking-widest">
          Obtain instant structured feedback from the Reviewer and Debugger agents.
        </p>
      </div>

      <ReviewWorkspace />
    </div>
  );
}
