"use client";

import React from "react";
import { ReviewReport as IReviewReport, ReviewIssue } from "@/types/review.types";
import {
  AlertTriangle,
  CheckCircle,
  ShieldAlert,
  Zap,
  BookOpen,
  Eye,
} from "lucide-react";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";

const MotionDiv = motion.div as any;
import { Badge } from "@/components/ui/badge";
import dynamic from "next/dynamic";
const ScoreRing = dynamic(() => import("@/components/three/ScoreRing"), { ssr: false });

interface ReviewReportProps {
  report: IReviewReport;
}

export default function ReviewReport({ report }: ReviewReportProps) {
  const getCategoryIcon = (category: ReviewIssue["category"]) => {
    switch (category) {
      case "security":
        return <ShieldAlert className="w-4 h-4 text-aether-rose" />;
      case "performance":
        return <Zap className="w-4 h-4 text-aether-violet" />;
      case "readability":
        return <Eye className="w-4 h-4 text-aether-indigo" />;
      case "style":
        return <BookOpen className="w-4 h-4 text-aether-teal" />;
    }
  };

  const getCategoryVariant = (category: ReviewIssue["category"]) => {
    switch (category) {
      case "security":
        return "danger"; // rose badge
      case "performance":
        return "secondary"; // violet badge
      case "readability":
        return "primary"; // indigo badge
      case "style":
      default:
        return "teal"; // teal badge
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* 3D Torus Score Banner */}
      <Card glow className="p-6 flex flex-col md:flex-row items-center justify-around gap-6 bg-obsidian-layer/20">
        <div className="w-40 h-40">
          <ScoreRing score={report.score} />
        </div>
        <div className="text-center md:text-left space-y-2">
          <Badge variant={report.score >= 70 ? "success" : report.score >= 45 ? "primary" : "danger"}>
            Quality Metric
          </Badge>
          <h3 className="text-2xl font-black font-display text-foreground tracking-wide">
            CODE QUALITY SCORE: {report.score}/100
          </h3>
          <p className="text-xs text-muted-foreground max-w-sm font-semibold">
            {report.score >= 70 
              ? "Your code follows solid engineering standards and contains minimal smells." 
              : report.score >= 45 
              ? "Your code is functional but contains performance, style, or security bottlenecks."
              : "Critical fault paths detected. Review suggestions and refactoring diffs below."}
          </p>
        </div>
      </Card>

      {/* Code Review Summary */}
      <div className="space-y-3">
        <h4 className="text-xs font-black uppercase tracking-widest text-[#8892B0]">Review Summary</h4>
        <p className="text-xs sm:text-sm text-foreground leading-relaxed bg-obsidian-depth/50 p-5 border border-aether rounded-2xl shadow-inner font-semibold">
          {report.summary}
        </p>
      </div>

      {/* Bugs Panel */}
      {report.has_bugs && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-aether-rose font-black text-xs uppercase tracking-widest">
            <AlertTriangle className="w-4.5 h-4.5 animate-bounce" />
            <span>Critical Faults / Logical Bugs Detected</span>
          </div>

          <div className="space-y-4">
            {report.bugs.map((bug, index) => (
              <MotionDiv
                whileHover={{ y: -2 }}
                key={index}
                className="border border-aether-rose/25 bg-obsidian-layer/40 rounded-2xl p-5 space-y-3.5 shadow-sm hover:shadow-aether-rose/5 transition-all duration-300"
              >
                <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-wider">
                  <span className="text-aether-rose">Line {bug.line}</span>
                  <Badge variant="danger">
                    {bug.severity}
                  </Badge>
                </div>
                <p className="text-xs sm:text-sm text-foreground leading-relaxed font-semibold">
                  {bug.description}
                </p>
                <div className="bg-obsidian p-4 rounded-xl border border-aether-rose/20 shadow-inner relative overflow-hidden">
                  <span className="text-[9px] uppercase font-black tracking-widest text-[#8892B0] block mb-2">
                    Suggested Fix
                  </span>
                  <code className="text-[11px] sm:text-xs text-aether-emerald font-mono block overflow-x-auto whitespace-pre custom-scrollbar">
                    {bug.fix}
                  </code>
                </div>
              </MotionDiv>
            ))}
          </div>
        </div>
      )}

      {/* Code Smell Issues */}
      <div className="space-y-4">
        <h4 className="text-xs font-black uppercase tracking-widest text-[#8892B0]">Code Improvements</h4>
        {report.issues.length === 0 ? (
          <div className="flex items-center gap-3 p-5 border border-aether-emerald/20 bg-aether-emerald/5 text-aether-emerald rounded-2xl">
            <CheckCircle className="w-5 h-5 flex-shrink-0" />
            <span className="text-xs sm:text-sm font-black uppercase tracking-wider">Excellent code quality! No improvements suggested.</span>
          </div>
        ) : (
          <div className="space-y-4">
            {report.issues.map((issue, index) => (
              <MotionDiv
                whileHover={{ y: -2 }}
                key={index}
                className="flex gap-4 p-5 border border-aether rounded-2xl bg-obsidian-layer/30 hover:shadow-aether-indigo/5 transition-all duration-300"
              >
                <div className="flex-shrink-0 mt-0.5">
                  <div className="p-2.5 rounded-xl border border-aether">
                    {getCategoryIcon(issue.category)}
                  </div>
                </div>

                <div className="space-y-2 flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-black uppercase tracking-wider text-[#8892B0]">
                      Line {issue.line}
                    </span>
                    <Badge variant={getCategoryVariant(issue.category)}>
                      {issue.category}
                    </Badge>
                  </div>
                  <h5 className="font-extrabold text-foreground text-sm sm:text-base leading-snug">
                    {issue.description}
                  </h5>
                  <p className="text-xs text-[#8892B0] leading-relaxed font-semibold">
                    <span className="font-black uppercase tracking-wider text-foreground">Suggestion:</span>{" "}
                    {issue.suggestion}
                  </p>
                </div>
              </MotionDiv>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
