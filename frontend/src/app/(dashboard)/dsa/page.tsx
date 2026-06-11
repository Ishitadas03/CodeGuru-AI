"use client";

import React, { useState } from "react";
import { useDSA } from "@/hooks/useDSA";
import { DSATopic, DSAProblem, DSAExplanation } from "@/types/dsa.types";
import TopicCard from "@/features/dsa/TopicCard";
import ProblemList from "@/features/dsa/ProblemList";
import ConceptViewer from "@/features/dsa/ConceptViewer";
import CodeEditor from "@/components/editor/CodeEditor";
import LanguageSelector from "@/components/editor/LanguageSelector";
import {
  Sparkles,
  BookOpen,
  ArrowLeft,
  Loader2,
  Terminal,
  Award,
} from "lucide-react";
import { motion } from "framer-motion";
const MotionDiv = motion.div as any;
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import dynamic from "next/dynamic";
const AlgoVisualizer = dynamic(() => import("@/components/three/AlgoVisualizer"), { ssr: false });

export default function DSAMentorPage() {
  const { useTopics, useProblems, explainSolution, isExplaining } = useDSA();

  const { data: topics = [], isLoading: loadingTopics } = useTopics();
  const [selectedTopicSlug, setSelectedTopicSlug] = useState<string>("arrays");
  
  const { data: problems = [], isLoading: loadingProblems } = useProblems(selectedTopicSlug);
  const [activeProblem, setActiveProblem] = useState<DSAProblem | null>(null);

  const [code, setCode] = useState<string>("");
  const [language, setLanguage] = useState<string>("python");
  const [explanation, setExplanation] = useState<DSAExplanation | null>(null);

  const handleSelectProblem = (problem: DSAProblem) => {
    setActiveProblem(problem);
    setExplanation(null);
    
    // Load starter code for language or default to python
    const defaultLang = problem.starter_code[language] ? language : Object.keys(problem.starter_code)[0];
    setLanguage(defaultLang);
    setCode(problem.starter_code[defaultLang] || "");
  };

  const handleLanguageChange = (lang: string) => {
    setLanguage(lang);
    if (activeProblem) {
      setCode(activeProblem.starter_code[lang] || "");
    }
  };

  const handleExplain = async () => {
    if (!activeProblem) return;
    try {
      const result = await explainSolution({
        problemId: activeProblem.id,
        code,
        language,
      });
      setExplanation(result);
    } catch (e) {
      // Handled by react-query
    }
  };

  // Determine the 3D visualization mode based on topic slug
  const visualizerMode = React.useMemo(() => {
    if (!selectedTopicSlug) return "sorting";
    if (selectedTopicSlug.toLowerCase().includes("tree")) return "tree";
    if (selectedTopicSlug.toLowerCase().includes("graph")) return "graph";
    return "sorting";
  }, [selectedTopicSlug]);

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      {!activeProblem && (
        <div className="space-y-1">
          <h1 className="text-3xl font-black font-display tracking-tight text-foreground">
            DSA MENTOR
          </h1>
          <p className="text-xs sm:text-sm text-[#8892B0] font-black uppercase tracking-widest">
            Learn data structures and algorithms with interactive trace step debuggers.
          </p>
        </div>
      )}

      {activeProblem ? (
        // Problem Workspace view (when a problem is actively selected)
        <div className="space-y-6">
          {/* Back button and title */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => setActiveProblem(null)}
              className="p-3 border border-aether bg-obsidian-depth/50 rounded-2xl hover:bg-obsidian-layer hover:border-aether-indigo/35 transition-colors shadow-sm backdrop-blur-aether"
            >
              <ArrowLeft className="w-5 h-5 text-aether-indigo" />
            </button>
            <div>
              <h2 className="text-2xl font-black font-display tracking-tight text-foreground">
                {activeProblem.title}
              </h2>
              <p className="text-[10px] text-aether-indigo font-black uppercase tracking-widest">
                TOPIC: {selectedTopicSlug.replace("-", " ")}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 min-h-[500px]">
            {/* Left Column: Code description and Editor */}
            <div className="space-y-6 flex flex-col h-full">
              {/* Problem Description card */}
              <Card glow className="p-6 space-y-3 bg-obsidian-layer/20">
                <h4 className="text-xs font-black uppercase tracking-widest text-aether-indigo">Challenge Description</h4>
                <p className="text-xs sm:text-sm text-foreground leading-relaxed font-semibold">
                  {activeProblem.description}
                </p>
              </Card>

              {/* Editor panel header */}
              <div className="flex flex-col gap-4 flex-1 min-h-0">
                <Card className="flex flex-col sm:flex-row sm:items-center justify-between p-4 gap-4 bg-obsidian-depth/50 border border-aether shadow-md backdrop-blur-aether">
                  <div className="flex items-center gap-2.5">
                    <Badge variant="primary">
                      <Terminal className="w-4 h-4 text-white" />
                    </Badge>
                    <div>
                      <h4 className="text-xs font-black uppercase tracking-widest text-foreground">Solution Draft</h4>
                      <p className="text-[9px] text-[#8892B0] font-black uppercase tracking-wider">Write solution algorithm</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 self-end sm:self-auto">
                    <LanguageSelector
                      value={language}
                      onChange={handleLanguageChange}
                      disabled={isExplaining}
                    />
                    <Button
                      onClick={handleExplain}
                      disabled={isExplaining || !code.trim()}
                      className="h-10 px-5"
                    >
                      {isExplaining ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin text-[#060814]" />
                          Explaining...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4 text-white animate-pulse" />
                          Explain Solution
                        </>
                      )}
                    </Button>
                  </div>
                </Card>

                <div className="flex-1 min-h-[400px] rounded-2xl overflow-hidden border border-aether shadow-inner">
                  <CodeEditor
                    value={code}
                    onChange={(val) => setCode(val || "")}
                    language={language}
                    readOnly={isExplaining}
                  />
                </div>
              </div>
            </div>

            {/* Right Column: AI Mentoring traces & 3D visualization */}
            <div className="h-full flex flex-col gap-6">
              {/* 3D Visualizer Scene */}
              <div className="w-full h-80">
                <AlgoVisualizer mode={visualizerMode} />
              </div>

              {isExplaining ? (
                <Card className="flex-1 flex flex-col items-center justify-center p-8 text-center gap-6 min-h-[200px] relative overflow-hidden backdrop-blur-aether border border-aether bg-obsidian-depth/50">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-aether-indigo via-aether-violet to-aether-teal animate-pulse" />
                  <div className="relative">
                    <div className="w-20 h-20 border-4 border-aether-indigo/10 border-t-aether-indigo rounded-full animate-spin" />
                    <BookOpen className="w-8 h-8 text-aether-indigo absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
                  </div>
                  <div className="space-y-2 max-w-sm">
                    <h4 className="font-black text-xs uppercase tracking-widest text-foreground">Formulating Explanations</h4>
                    <p className="text-[10px] text-[#8892B0] leading-relaxed font-bold uppercase tracking-wider">
                      Our DSA Mentor is mapping execution flows and running a compiler trace simulator. Hang tight...
                    </p>
                  </div>
                </Card>
              ) : explanation ? (
                <div className="flex-1 border border-aether rounded-3xl bg-obsidian-depth/20 p-6 shadow-sm overflow-y-auto custom-scrollbar backdrop-blur-aether">
                  <ConceptViewer explanation={explanation} />
                </div>
              ) : (
                <Card className="flex-1 flex flex-col items-center justify-center p-8 text-center gap-5 min-h-[200px] relative overflow-hidden backdrop-blur-aether border border-dashed border-aether bg-obsidian-depth/20">
                  <div className="absolute top-0 right-0 w-40 h-40 bg-aether-indigo/5 rounded-full blur-3xl pointer-events-none" />
                  
                  <div className="bg-aether-indigo/10 text-aether-indigo p-4 rounded-2xl border border-aether shadow-lg shadow-aether-indigo/5 relative">
                    <BookOpen className="w-8 h-8 animate-pulse" />
                  </div>
                  <div className="space-y-1.5 max-w-xs relative z-10">
                    <h4 className="font-black text-xs uppercase tracking-widest text-foreground">Explanation Feed Empty</h4>
                    <p className="text-xs text-[#8892B0] font-semibold leading-relaxed">
                      Click the "Explain Solution" button to trigger step-by-step compiler trace debugger analysis.
                    </p>
                  </div>
                </Card>
              )}
            </div>
          </div>
        </div>
      ) : (
        // Catalog Overview view (when no problem is selected yet)
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left panel: Topics grid + Problems checklist */}
          <div className="lg:col-span-2 space-y-6">
            <h3 className="text-xs font-black uppercase tracking-widest text-[#8892B0] px-1">Topics Catalog</h3>
            {loadingTopics ? (
              <div className="flex justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-aether-teal" />
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {topics.map((topic: DSATopic, index: number) => (
                  <MotionDiv
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    key={topic.slug}
                  >
                    <TopicCard
                      topic={topic}
                      isSelected={selectedTopicSlug === topic.slug}
                      onClick={() => setSelectedTopicSlug(topic.slug)}
                    />
                  </MotionDiv>
                ))}
              </div>
            )}

            {/* Problems list */}
            {selectedTopicSlug && (
              <div className="pt-4">
                {loadingProblems ? (
                  <div className="flex justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-aether-teal" />
                  </div>
                ) : (
                  <ProblemList
                    problems={problems}
                    selectedProblemId={null}
                    onSelectProblem={handleSelectProblem}
                  />
                )}
              </div>
            )}
          </div>

          {/* Right panel: Learning stats reminder / workspace details */}
          <div className="space-y-6">
            <h3 className="text-xs font-black uppercase tracking-widest text-[#8892B0] px-1">Study Statistics</h3>
            <Card glow className="space-y-4 bg-obsidian-layer/20">
              <div className="flex items-center gap-3">
                <Badge variant="primary">
                  <Sparkles className="w-4.5 h-4.5 text-white" />
                </Badge>
                <h4 className="font-extrabold text-foreground text-xs uppercase tracking-widest">
                  Daily Recommendation
                </h4>
              </div>
              <p className="text-xs text-[#8892B0] leading-relaxed font-semibold">
                Choose **Arrays & Hashing &gt; Two Sum** challenge. It is an industry-standard interview warm up for testing hash table lookups.
              </p>
            </Card>

            <Card glow className="space-y-4 bg-obsidian-layer/20">
              <div className="flex items-center gap-3">
                <Badge variant="success">
                  <Award className="w-4.5 h-4.5 text-white" />
                </Badge>
                <h4 className="font-extrabold text-foreground text-xs uppercase tracking-widest">
                  Mastery Levels
                </h4>
              </div>
              <div className="space-y-3 pt-1">
                <div>
                  <div className="flex justify-between text-[9px] font-black uppercase text-[#8892B0] mb-1 tracking-wider">
                    <span>Arrays & Hashing</span>
                    <span className="text-aether-teal">100%</span>
                  </div>
                  <div className="w-full bg-obsidian-depth h-1.5 rounded-full overflow-hidden border border-aether">
                    <div className="bg-gradient-to-r from-aether-indigo to-aether-teal h-1.5 rounded-full shadow-[0_0_8px_rgba(91,108,249,0.3)] w-[100%]" />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-[9px] font-black uppercase text-[#8892B0] mb-1 tracking-wider">
                    <span>Linked Lists</span>
                    <span className="text-aether-violet">100%</span>
                  </div>
                  <div className="w-full bg-obsidian-depth h-1.5 rounded-full overflow-hidden border border-aether">
                    <div className="bg-gradient-to-r from-aether-violet to-aether-purple h-1.5 rounded-full shadow-[0_0_8px_rgba(155,89,245,0.3)] w-[100%]" />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-[9px] font-black uppercase text-[#8892B0] mb-1 tracking-wider">
                    <span>Trees & Graphs</span>
                    <span className="text-muted">0%</span>
                  </div>
                  <div className="w-full bg-obsidian-depth h-1.5 rounded-full overflow-hidden border border-aether">
                    <div className="bg-obsidian-layer h-1.5 rounded-full w-[0%]" />
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
