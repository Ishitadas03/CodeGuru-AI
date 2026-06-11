"use client";

import React, { useState } from "react";
import { DSAExplanation } from "@/types/dsa.types";
import {
  ChevronLeft,
  ChevronRight,
  Gauge,
  Activity,
  Terminal,
  Cpu,
  BookOpen,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const MotionDiv = motion.div as any;

interface ConceptViewerProps {
  explanation: DSAExplanation;
}

export default function ConceptViewer({ explanation }: ConceptViewerProps) {
  const [currentStep, setCurrentStep] = useState<number>(0);
  const steps = explanation.dry_run;

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Explanation Box */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-[#8892B0]">
          <BookOpen className="w-4.5 h-4.5 text-aether-indigo" />
          <span>Intuition & Explanation</span>
        </div>
        <p className="text-xs sm:text-sm text-foreground leading-relaxed bg-obsidian-depth/50 p-5 border border-aether rounded-2xl font-semibold">
          {explanation.explanation}
        </p>
      </div>

      {/* Complexity Analysis Tables */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-[#8892B0]">
          <Cpu className="w-4.5 h-4.5 text-aether-teal" />
          <span>Complexity Analysis</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border border-aether p-5 rounded-2xl bg-obsidian-layer/20 space-y-3 hover:border-aether-indigo/40 hover:shadow-[0_0_20px_rgba(91,108,249,0.05)] transition-all duration-300 backdrop-blur-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 w-16 h-16 bg-aether-indigo/[0.03] rounded-full blur-lg pointer-events-none" />
            <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-wider text-[#8892B0]">
              <Gauge className="w-3.5 h-3.5 text-aether-indigo" />
              <span>TIME COMPLEXITY</span>
            </div>
            <div className="text-2xl font-black tracking-tight text-aether-indigo">
              {explanation.complexity.time_complexity}
            </div>
            <p className="text-xs text-[#8892B0] leading-relaxed font-semibold">
              {explanation.complexity.time_explanation}
            </p>
          </div>

          <div className="border border-aether p-5 rounded-2xl bg-obsidian-layer/20 space-y-3 hover:border-aether-violet/40 hover:shadow-[0_0_20px_rgba(155,89,245,0.05)] transition-all duration-300 backdrop-blur-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 w-16 h-16 bg-aether-violet/[0.03] rounded-full blur-lg pointer-events-none" />
            <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-wider text-[#8892B0]">
              <Activity className="w-3.5 h-3.5 text-aether-violet" />
              <span>SPACE COMPLEXITY</span>
            </div>
            <div className="text-2xl font-black tracking-tight text-aether-violet">
              {explanation.complexity.space_complexity}
            </div>
            <p className="text-xs text-[#8892B0] leading-relaxed font-semibold">
              {explanation.complexity.space_explanation}
            </p>
          </div>
        </div>
      </div>

      {/* Interactive Dry Run Debugger */}
      {steps.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-[#8892B0]">
              <Terminal className="w-4.5 h-4.5 text-aether-indigo" />
              <span>Trace Stepper & Dry Run</span>
            </div>

            <div className="flex items-center gap-2 bg-obsidian p-1.5 rounded-xl border border-aether">
              <MotionDiv whileTap={{ scale: 0.9 }}>
                <button
                  onClick={handlePrev}
                  disabled={currentStep === 0}
                  className="p-1 rounded-lg hover:bg-obsidian-depth disabled:opacity-30 disabled:hover:bg-transparent transition-all"
                  aria-label="Previous step"
                >
                  <ChevronLeft className="w-4 h-4 text-[#8892B0]" />
                </button>
              </MotionDiv>
              <span className="text-[10px] font-black uppercase tracking-wider text-[#8892B0] px-1">
                {currentStep + 1} / {steps.length}
              </span>
              <MotionDiv whileTap={{ scale: 0.9 }}>
                <button
                  onClick={handleNext}
                  disabled={currentStep === steps.length - 1}
                  className="p-1 rounded-lg hover:bg-obsidian-depth disabled:opacity-30 disabled:hover:bg-transparent transition-all"
                  aria-label="Next step"
                >
                  <ChevronRight className="w-4 h-4 text-[#8892B0]" />
                </button>
              </MotionDiv>
            </div>
          </div>

          <div className="border border-aether rounded-3xl overflow-hidden bg-obsidian shadow-xl shadow-obsidian/20 relative">
            {/* Header / Line reference */}
            <div className="bg-obsidian-depth p-4 border-b border-aether flex items-center justify-between text-[10px] font-black uppercase tracking-wider text-[#8892B0]">
              <span>Debug Session Console</span>
              <span className="bg-aether-indigo/10 text-aether-indigo font-black px-2.5 py-0.5 rounded-lg border border-aether-indigo/25">
                Line {steps[currentStep].line_number}
              </span>
            </div>

            {/* Stepper Content */}
            <div className="p-5 grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Left Column: Trace Description */}
              <div className="md:col-span-2 space-y-2.5">
                <span className="text-[9px] font-black text-[#8892B0]/80 uppercase tracking-widest block">
                  Action Executed
                </span>
                <AnimatePresence mode="wait">
                  <MotionDiv
                    key={currentStep}
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -5 }}
                    transition={{ duration: 0.15 }}
                    className="text-xs sm:text-sm text-[#F0F4FF] font-semibold leading-relaxed min-h-[50px]"
                  >
                    {steps[currentStep].description}
                  </MotionDiv>
                </AnimatePresence>
              </div>

              {/* Right Column: Variables Board */}
              <div className="bg-obsidian-depth/40 p-4 rounded-2xl border border-aether space-y-2">
                <span className="text-[9px] font-black text-[#8892B0]/80 uppercase tracking-widest block">
                  Variables Board
                </span>
                <AnimatePresence mode="wait">
                  <MotionDiv
                    key={currentStep}
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.98 }}
                    transition={{ duration: 0.15 }}
                    className="font-mono text-[11px] text-aether-emerald bg-obsidian/80 p-3 rounded-xl border border-aether min-h-[50px] flex items-center overflow-x-auto whitespace-pre custom-scrollbar"
                  >
                    {steps[currentStep].variables_state || "No active variables"}
                  </MotionDiv>
                </AnimatePresence>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
