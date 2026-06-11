"use client";

import React, { useState } from "react";
import CodeEditor from "@/components/editor/CodeEditor";
import LanguageSelector from "@/components/editor/LanguageSelector";
import ReviewReport from "./ReviewReport";
import RefactoredCode from "./RefactoredCode";
import { useReview } from "@/hooks/useReview";
import { ReviewReport as IReviewReport } from "@/types/review.types";
import { Loader2, Sparkles, LayoutGrid, Split, Terminal } from "lucide-react";
import { motion } from "framer-motion";

const MotionDiv = motion.div as any;
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const DEFAULT_CODE_TEMPLATES: Record<string, string> = {
  python: `def bubble_sort(arr):
    n = len(arr)
    # Optimise this algorithm, it is currently slow
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                # Swap elements
                temp = arr[j]
                arr[j] = arr[j+1]
                arr[j+1] = temp
    return arr
`,
  javascript: `function calculateTotal(items) {
  var total = 0;
  // Todo: add discount handling
  for (var i = 0; i < items.length; i++) {
    total = total + items[i].price;
  }
  return total;
}
`,
  typescript: `interface User {
  name: string;
  role: string;
}

function processAdminUsers(users: any[]) {
  // Fix the 'any' type below and filter admins
  return users.filter(user => user.role === 'admin');
}
`,
  java: `public class Sort {
    public void insertionSort(int array[]) {
        int n = array.length;
        for (int j = 1; j < n; j++) {
            int key = array[j];
            int i = j-1;
            while ( (i > -1) && ( array [i] > key ) ) {
                array [i+1] = array [i];
                i--;
            }
            array [i+1] = key;
        }
    }
}
`,
  cpp: `#include <iostream>
using namespace std;

void printArray(int arr[], int size) {
    for (int i = 0; i < size; i++)
        cout << arr[i] << " ";
    cout << endl;
}
`,
};

export default function ReviewWorkspace() {
  const [language, setLanguage] = useState<string>("python");
  const [code, setCode] = useState<string>(DEFAULT_CODE_TEMPLATES.python);
  const [review, setReview] = useState<IReviewReport | null>(null);
  const [activeTab, setActiveTab] = useState<"feedback" | "diff">("feedback");

  const { submitReview, isSubmitting } = useReview();

  const handleLanguageChange = (lang: string) => {
    setLanguage(lang);
    setCode(DEFAULT_CODE_TEMPLATES[lang] || "");
  };

  const handleRunReview = async () => {
    try {
      const result = await submitReview({ code, language });
      setReview(result);
      setActiveTab("feedback");
    } catch (error) {
      // Handled by react-query mutation
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[calc(100vh-12rem)] min-h-[600px]">
      {/* Left Pane: Code Editor */}
      <MotionDiv
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col gap-4 h-full"
      >
        <Card className="flex flex-col sm:flex-row sm:items-center justify-between p-4 gap-4 bg-obsidian-depth/50 border border-aether shadow-md backdrop-blur-aether">
          <div className="flex items-center gap-3">
            <Badge variant="primary">
              <Terminal className="w-4.5 h-4.5 text-white" />
            </Badge>
            <div>
              <h3 className="font-black text-foreground text-xs uppercase tracking-widest">Input Workspace</h3>
              <p className="text-[9px] text-[#8892B0] font-black uppercase tracking-wider">Paste or type code block below</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 self-end sm:self-auto">
            <LanguageSelector
              value={language}
              onChange={handleLanguageChange}
              disabled={isSubmitting}
            />
            <Button
              onClick={handleRunReview}
              disabled={isSubmitting || !code.trim()}
              className="h-10 px-5"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-[#060814]" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-white animate-pulse" />
                  Review Code
                </>
              )}
            </Button>
          </div>
        </Card>

        <div className="flex-1 min-h-0 rounded-2xl overflow-hidden border border-aether shadow-inner">
          <CodeEditor
            value={code}
            onChange={(val) => setCode(val || "")}
            language={language}
            readOnly={isSubmitting}
          />
        </div>
      </MotionDiv>

      {/* Right Pane: Review Results */}
      <MotionDiv
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col gap-4 h-full overflow-hidden"
      >
        {isSubmitting ? (
          <Card className="flex-1 flex flex-col items-center justify-center p-8 text-center gap-6 relative overflow-hidden backdrop-blur-aether border border-aether bg-obsidian-depth/50">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-aether-indigo via-aether-violet to-aether-teal animate-pulse" />
            <div className="relative">
              <div className="w-20 h-20 border-4 border-aether-indigo/10 border-t-aether-indigo rounded-full animate-spin" />
              <Sparkles className="w-8 h-8 text-aether-indigo absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
            </div>
            <div className="space-y-2 max-w-sm">
              <h4 className="font-black text-xs uppercase tracking-widest text-foreground">Analyzing Code Quality</h4>
              <p className="text-[10px] text-[#8892B0] leading-relaxed font-bold uppercase tracking-wider">
                Executing static code analysis, auditing complexity matrices, and consulting specialized AI review agents...
              </p>
            </div>
          </Card>
        ) : review ? (
          <div className="flex-1 flex flex-col min-h-0 border border-aether rounded-2xl bg-obsidian-depth/30 shadow-sm overflow-hidden backdrop-blur-aether">
            {/* Review Navigation Tabs */}
            <div className="flex items-center justify-between border-b border-aether p-4 bg-obsidian-layer/40">
              <div className="flex gap-2">
                <button
                  onClick={() => setActiveTab("feedback")}
                  className={`flex items-center gap-2 px-4 py-2 text-[10px] font-black uppercase tracking-wider rounded-xl transition-all ${
                    activeTab === "feedback"
                      ? "bg-aether-teal/10 text-aether-teal border border-aether-teal/25"
                      : "text-muted-foreground hover:bg-obsidian-depth border border-transparent"
                  }`}
                >
                  <LayoutGrid className="w-3.5 h-3.5" />
                  Feedback Report
                </button>
                <button
                  onClick={() => setActiveTab("diff")}
                  className={`flex items-center gap-2 px-4 py-2 text-[10px] font-black uppercase tracking-wider rounded-xl transition-all ${
                    activeTab === "diff"
                      ? "bg-aether-teal/10 text-aether-teal border border-aether-teal/25"
                      : "text-muted-foreground hover:bg-obsidian-depth border border-transparent"
                  }`}
                >
                  <Split className="w-3.5 h-3.5" />
                  Refactored Code
                </button>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-[9px] font-black uppercase tracking-wider text-[#8892B0]">Score</span>
                <span className="text-sm font-black text-aether-teal bg-aether-teal/10 border border-aether-teal/25 px-3 py-1 rounded-xl">
                  {review.score}/100
                </span>
              </div>
            </div>

            {/* Tab Panels */}
            <div className="flex-1 overflow-y-auto p-6 min-h-0 custom-scrollbar">
              {activeTab === "feedback" ? (
                <ReviewReport report={review} />
              ) : (
                <RefactoredCode
                  originalCode={code}
                  refactoredCode={review.refactored_code}
                  language={language}
                />
              )}
            </div>
          </div>
        ) : (
          <Card className="flex-1 flex flex-col items-center justify-center p-8 text-center gap-5 relative overflow-hidden backdrop-blur-aether border-dashed border border-aether bg-obsidian-depth/20">
            <div className="absolute top-0 right-0 w-40 h-40 bg-aether-indigo/5 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-40 h-40 bg-aether-violet/5 rounded-full blur-3xl pointer-events-none" />
            
            <div className="bg-aether-indigo/10 text-aether-indigo p-4 rounded-2xl border border-aether shadow-lg shadow-aether-indigo/5 relative">
              <Sparkles className="w-8 h-8 animate-pulse" />
            </div>
            <div className="space-y-1.5 max-w-xs relative z-10">
              <h4 className="font-black text-xs uppercase tracking-widest text-foreground">Workspace Idle</h4>
              <p className="text-xs text-[#8892B0] font-semibold leading-relaxed">
                Submit your program code block on the left panel to trigger your AI mentors.
              </p>
            </div>
          </Card>
        )}
      </MotionDiv>
    </div>
  );
}
