"use client";

import React, { useState, useEffect, useRef } from "react";
import CodeEditor from "@/components/editor/CodeEditor";
import LanguageSelector from "@/components/editor/LanguageSelector";
import { useInterview } from "@/hooks/useInterview";
import { InterviewSession, InterviewMessage } from "@/types/interview.types";
import {
  MessageSquare,
  Send,
  Award,
  Sparkles,
  Clock,
  BookOpen,
  User,
  Bot,
  ChevronRight,
  AlertCircle,
  CheckCircle2,
  Code,
  Lightbulb,
  ArrowLeft,
  History,
  TrendingUp,
  Plus,
  Loader2,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/card";

const MotionDiv = motion.div as any;
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import dynamic from "next/dynamic";
const ScoreRing = dynamic(() => import("@/components/three/ScoreRing"), { ssr: false });
const InterviewAvatar = dynamic(() => import("@/components/three/InterviewAvatar"), { ssr: false });

export default function InterviewSimulator() {
  const [activeSession, setActiveSession] = useState<InterviewSession | null>(null);
  const [topic, setTopic] = useState<string>("System Design");
  const [difficulty, setDifficulty] = useState<string>("medium");
  const [language, setLanguage] = useState<string>("python");
  const [codeNotes, setCodeNotes] = useState<string>("# Write your solution code or design notes here during the interview...\n\n");
  const [chatInput, setChatInput] = useState<string>("");
  const chatBottomRef = useRef<HTMLDivElement>(null);

  const {
    startSession,
    isStarting,
    sendMessage,
    isSending,
    endSession,
    isEnding,
    useSessions,
  } = useInterview();

  const { data: history = [], refetch: refetchHistory, isLoading: isLoadingHistory } = useSessions(0, 50);

  // Scroll to bottom of chat when messages change
  useEffect(() => {
    if (chatBottomRef.current) {
      chatBottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [activeSession?.messages, isSending]);

  const handleStart = async () => {
    try {
      const session = await startSession({ topic, difficulty });
      setActiveSession(session);
      setCodeNotes(`# Write your solution code or design notes here during the interview...\n\n# Topic: ${topic}\n# Difficulty: ${difficulty}\n\n`);
    } catch (err) {
      console.error("Failed to start session:", err);
    }
  };

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!chatInput.trim() || isSending || !activeSession) return;

    const currentInput = chatInput;
    setChatInput("");

    // Append user message locally for optimistic update
    const userMsg: InterviewMessage = { role: "user", content: currentInput };
    setActiveSession((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        messages: [...prev.messages, userMsg],
      };
    });

    try {
      const updated = await sendMessage({
        sessionId: activeSession.id,
        message: currentInput,
      });
      setActiveSession(updated);
    } catch (err) {
      console.error("Failed to send message:", err);
    }
  };

  const handleEnd = async () => {
    if (!activeSession) return;
    if (!window.confirm("Are you sure you want to end this interview and get your grading scorecard?")) return;

    try {
      const completed = await endSession(activeSession.id);
      setActiveSession(completed);
      refetchHistory();
    } catch (err) {
      console.error("Failed to end session:", err);
    }
  };

  const handleResume = (session: InterviewSession) => {
    setActiveSession(session);
    if (!session.is_completed) {
      setCodeNotes(`# Resumed interview notes...\n# Topic: ${session.topic}\n# Difficulty: ${session.difficulty}\n\n`);
    }
  };

  const handleBackToLobby = () => {
    setActiveSession(null);
    refetchHistory();
  };

  // 1. GRADE / SCORECARD VIEW
  if (activeSession && activeSession.is_completed) {
    const feedback = activeSession.feedback;
    const score = activeSession.score ?? 0;

    return (
      <div className="flex flex-col gap-6 max-w-5xl mx-auto h-[calc(100vh-10rem)] min-h-[550px] overflow-y-auto pr-2 custom-scrollbar">
        {/* Header panel */}
        <Card className="flex flex-col sm:flex-row sm:items-center justify-between p-6 gap-4 bg-obsidian-depth/50 border border-aether shadow-md backdrop-blur-aether">
          <div className="flex items-center gap-4">
            <button
              onClick={handleBackToLobby}
              className="p-3 border border-aether bg-obsidian-depth/50 rounded-2xl hover:bg-obsidian-layer hover:border-aether-indigo/35 transition-colors shadow-sm"
            >
              <ArrowLeft className="w-5 h-5 text-aether-teal" />
            </button>
            <div>
              <div className="flex items-center gap-2">
                <Badge variant="primary">
                  {activeSession.topic}
                </Badge>
                <Badge variant="outline">
                  {activeSession.difficulty} Difficulty
                </Badge>
              </div>
              <h2 className="font-black font-display text-2xl text-foreground mt-2 tracking-tight">Interview Scorecard</h2>
            </div>
          </div>
          <Button onClick={handleBackToLobby} className="h-11 px-6">
            <Plus className="w-4 h-4 text-white" /> Start New Session
          </Button>
        </Card>

        {/* Score and Summary block */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Circular grading score card with 3D ScoreRing */}
          <Card glow className="p-8 flex flex-col items-center justify-center text-center bg-obsidian-layer/20">
            <div className="w-32 h-32 mb-3">
              <ScoreRing score={score} className="min-h-0 w-full h-full" />
            </div>
            <span className="text-[10px] font-black text-[#8892B0] uppercase tracking-widest">Overall Rating</span>
            <div className="flex items-baseline gap-1 my-3">
              <span className="text-5xl font-black text-aether-teal">{score}</span>
              <span className="text-md font-bold text-[#8892B0]">/100</span>
            </div>
            <span className="text-[9px] text-[#8892B0] uppercase tracking-wider font-black mt-3">
              {score >= 80 ? "Passed - Tier 1 Ready" : score >= 60 ? "Solid - Needs Polish" : "Needs Practice"}
            </span>
          </Card>

          {/* Qualitative Performance summary */}
          <Card className="md:col-span-2 p-6 flex flex-col justify-between bg-obsidian-layer/20">
            <div>
              <div className="flex items-center gap-2.5 text-aether-teal font-black text-xs uppercase tracking-wider mb-4">
                <TrendingUp className="w-4 h-4" /> Performance Summary
              </div>
              <p className="text-foreground text-xs sm:text-sm leading-relaxed whitespace-pre-line font-semibold">
                {feedback?.summary || "No qualitative overview recorded."}
              </p>
            </div>
            <div className="text-[9px] text-[#8892B0] font-black uppercase tracking-wider border-t border-aether pt-4 mt-6">
              Completed on {new Date(activeSession.created_at).toLocaleDateString()}
            </div>
          </Card>
        </div>

        {/* Strengths vs weaknesses */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Key strengths (Positive border: emerald) */}
          <Card className="bg-obsidian-layer/20 border border-aether-emerald/35">
            <h3 className="font-black text-foreground text-xs uppercase tracking-widest mb-5 flex items-center gap-2.5">
              <CheckCircle2 className="w-5 h-5 text-aether-emerald" />
              Key Strengths
            </h3>
            {feedback?.strengths && feedback.strengths.length > 0 ? (
              <ul className="space-y-3">
                {feedback.strengths.map((str, idx) => (
                  <li key={idx} className="flex gap-2.5 text-xs text-foreground font-semibold leading-relaxed">
                    <span className="text-aether-emerald">•</span>
                    {str}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-[#8892B0] italic font-semibold">No specific strengths listed.</p>
            )}
          </Card>

          {/* Areas for Improvement (Needs improvement border: rose) */}
          <Card className="bg-obsidian-layer/20 border border-aether-rose/35">
            <h3 className="font-black text-foreground text-xs uppercase tracking-widest mb-5 flex items-center gap-2.5">
              <AlertCircle className="w-5 h-5 text-aether-rose" />
              Areas for Improvement
            </h3>
            {feedback?.weakness_areas && feedback.weakness_areas.length > 0 ? (
              <ul className="space-y-3">
                {feedback.weakness_areas.map((wk, idx) => (
                  <li key={idx} className="flex gap-2.5 text-xs text-foreground font-semibold leading-relaxed">
                    <span className="text-aether-rose">•</span>
                    {wk}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-[#8892B0] italic font-semibold">No improvement focus areas highlighted.</p>
            )}
          </Card>
        </div>

        {/* Actionable suggestions and optimal design snippets */}
        <div className="grid grid-cols-1 gap-6">
          <Card className="bg-obsidian-layer/20">
            <h3 className="font-black text-foreground text-xs uppercase tracking-widest mb-4 flex items-center gap-2.5">
              <Lightbulb className="w-5 h-5 text-aether-teal" />
              Actionable Study Tips
            </h3>
            {feedback?.improvement_tips && feedback.improvement_tips.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {feedback.improvement_tips.map((tip, idx) => (
                  <div key={idx} className="flex gap-3 items-start bg-obsidian p-4 rounded-2xl border border-aether">
                    <div className="bg-aether-teal/10 text-aether-teal p-2 rounded-xl mt-0.5 border border-aether-teal/25">
                      <Lightbulb className="w-4 h-4" />
                    </div>
                    <span className="text-xs text-foreground font-semibold leading-relaxed">{tip}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-[#8892B0] italic font-semibold">No actionable tips suggested.</p>
            )}
          </Card>

          <Card className="bg-obsidian-layer/20 overflow-hidden">
            <h3 className="font-black text-foreground text-xs uppercase tracking-widest mb-4 flex items-center gap-2.5">
              <Code className="w-5 h-5 text-aether-teal" />
              Optimal Solution Suggestions
            </h3>
            <pre className="bg-obsidian text-foreground/80 p-5 rounded-2xl border border-aether overflow-x-auto text-xs font-mono leading-relaxed whitespace-pre-wrap custom-scrollbar">
              {feedback?.correct_code_suggestions || "// No solution details provided."}
            </pre>
          </Card>
        </div>
      </div>
    );
  }

  // 2. ACTIVE INTERVIEW CHAT WORKSPACE
  if (activeSession && !activeSession.is_completed) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-12rem)] min-h-[550px]">
        {/* Left Column: Code Workspace / Draft area */}
        <MotionDiv
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-5 flex flex-col gap-4 h-full overflow-hidden"
        >
          <Card className="flex flex-col sm:flex-row sm:items-center justify-between p-4 gap-4 bg-obsidian-depth/50 border border-aether shadow-md backdrop-blur-aether">
            <div className="flex items-center gap-2.5">
              <Badge variant="primary">
                <Code className="w-4.5 h-4.5 text-white" />
              </Badge>
              <div>
                <h3 className="font-black text-foreground text-xs uppercase tracking-widest">Coding Sandbox</h3>
                <p className="text-[9px] text-[#8892B0] font-black uppercase tracking-wider">Draft solution notes & code</p>
              </div>
            </div>
            <LanguageSelector value={language} onChange={setLanguage} />
          </Card>

          <div className="flex-1 min-h-0 rounded-2xl overflow-hidden border border-aether shadow-inner">
            <CodeEditor
              value={codeNotes}
              onChange={(val) => setCodeNotes(val || "")}
              language={language}
            />
          </div>
        </MotionDiv>

        {/* Right Column: Live Chat Messenger & AI Avatar */}
        <MotionDiv
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-7 flex flex-col border border-aether rounded-3xl bg-obsidian-depth/30 shadow-sm overflow-hidden h-full backdrop-blur-aether"
        >
          {/* Top Bar info */}
          <div className="flex items-center justify-between border-b border-aether p-4 bg-obsidian-layer/40">
            <div className="flex items-center gap-3">
              {/* Mini 3D Avatar indicator */}
              <div className="relative w-12 h-12 bg-[#060814] rounded-xl overflow-hidden border border-aether flex items-center justify-center">
                <InterviewAvatar state={isSending ? "thinking" : "speaking"} className="min-h-0 w-full h-full" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-black font-display text-xs tracking-wider uppercase text-foreground leading-none">AI Interviewer</h4>
                  <span className="text-[8px] bg-aether-emerald/10 text-aether-emerald font-black px-2 py-0.5 rounded-lg border border-aether-emerald/20 uppercase tracking-wider">
                    Online
                  </span>
                </div>
                <p className="text-[9px] text-[#8892B0] font-black uppercase tracking-wider mt-1">
                  {activeSession.topic} • {activeSession.difficulty}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleBackToLobby}
                className="py-2 px-4 bg-obsidian hover:bg-obsidian-depth text-[#8892B0] hover:text-foreground font-black rounded-xl text-[9px] uppercase tracking-wider transition-all border border-aether"
              >
                Quit
              </button>
              <Button
                onClick={handleEnd}
                disabled={isEnding}
                variant="danger"
                className="h-9 px-4 animate-pulse-soft"
              >
                {isEnding ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" /> Grading...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5 text-white animate-pulse mr-1.5" /> End & Grade
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Message History list */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
            {activeSession.messages.map((msg, idx) => {
              const isInterviewer = msg.role === "interviewer";
              return (
                <MotionDiv
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  key={idx}
                  className={`flex gap-3 max-w-[85%] ${
                    isInterviewer ? "mr-auto" : "ml-auto flex-row-reverse"
                  }`}
                >
                  <div
                    className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 border ${
                      isInterviewer
                        ? "bg-aether-teal/10 text-aether-teal border border-aether-teal/25"
                        : "bg-obsidian-depth text-muted-foreground border border-aether"
                    }`}
                  >
                    {isInterviewer ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                  </div>
                  <div
                    className={`p-4 rounded-2xl shadow-sm text-xs sm:text-sm border whitespace-pre-wrap leading-relaxed font-semibold ${
                      isInterviewer
                        ? "bg-obsidian-layer/40 border-aether text-foreground rounded-tl-none"
                        : "bg-aether-indigo/10 border border-aether-indigo/25 text-[#A4AFFF] rounded-tr-none"
                    }`}
                  >
                    {msg.content}
                  </div>
                </MotionDiv>
              );
            })}

            {isSending && (
              <div className="flex gap-3 max-w-[80%] mr-auto items-center">
                <div className="w-8 h-8 rounded-xl bg-aether-teal/10 text-aether-teal border border-aether-teal/25 flex items-center justify-center">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-obsidian-layer/40 border border-aether p-4 rounded-2xl rounded-tl-none text-xs font-semibold flex items-center gap-2 text-[#8892B0]">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-aether-teal" />
                  <span>Interviewer is analyzing your response...</span>
                </div>
              </div>
            )}

            <div ref={chatBottomRef} />
          </div>

          {/* Send Input messenger box */}
          <form
            onSubmit={handleSend}
            className="border-t border-aether p-4 bg-obsidian-layer/40 flex gap-3 items-end"
          >
            <textarea
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Type your response or paste code blocks here. Press Send or Ctrl+Enter to submit..."
              disabled={isSending}
              rows={2}
              className="flex-1 bg-obsidian border border-aether p-3 rounded-2xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-aether-indigo/25 resize-none text-foreground placeholder:text-[#3D4A6B] font-semibold custom-scrollbar"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
            <button
              type="submit"
              disabled={isSending || !chatInput.trim()}
              className="p-3.5 bg-gradient-to-br from-aether-indigo to-aether-violet hover:from-[#6B7CFF] hover:to-[#A869F7] disabled:opacity-50 text-white rounded-2xl transition-all shadow-md shadow-aether-indigo/15"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </MotionDiv>
      </div>
    );
  }

  // 3. CONFIGURATION / LOBBY VIEW
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-6xl mx-auto h-[calc(100vh-10rem)] min-h-[500px] pb-12">
      {/* Session config panel */}
      <MotionDiv
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="lg:col-span-1"
      >
        <Card className="h-full flex flex-col justify-between p-6 bg-obsidian-layer/20">
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <Badge variant="primary">
                <MessageSquare className="w-6 h-6 text-white" />
              </Badge>
              <div>
                <h3 className="font-black font-display text-base uppercase tracking-wider text-foreground">Start Interview</h3>
                <p className="text-[9px] text-[#8892B0] font-black uppercase tracking-wider">Configure mock parameters</p>
              </div>
            </div>

            <div className="space-y-5">
              {/* Topic Select */}
              <div className="space-y-2">
                <label className="text-[9px] font-black text-[#8892B0] uppercase tracking-widest block">
                  Interview Topic
                </label>
                <select
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className="w-full bg-obsidian border border-aether p-3 rounded-xl text-xs sm:text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-aether-indigo/25 font-semibold"
                >
                  <option value="System Design" className="bg-[#060814] text-foreground">System Design Architecture</option>
                  <option value="Data Structures & Algorithms" className="bg-[#060814] text-foreground">Data Structures & Algorithms</option>
                  <option value="Full Stack Development" className="bg-[#060814] text-foreground">Full Stack Development (Node/React)</option>
                  <option value="Database Tuning & SQL" className="bg-[#060814] text-foreground">Database Tuning & SQL optimization</option>
                  <option value="Machine Learning Engineering" className="bg-[#060814] text-foreground">Machine Learning Engineering</option>
                  <option value="Behavioral (STAR method)" className="bg-[#060814] text-foreground">Behavioral Leadership (STAR method)</option>
                </select>
              </div>

              {/* Difficulty select */}
              <div className="space-y-2">
                <label className="text-[9px] font-black text-[#8892B0] uppercase tracking-widest block">
                  Target Difficulty
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {["easy", "medium", "hard"].map((diff) => (
                    <button
                      key={diff}
                      type="button"
                      onClick={() => setDifficulty(diff)}
                      className={`py-2.5 rounded-xl text-[10px] font-black uppercase tracking-wider transition-all border ${
                        difficulty === diff
                          ? "bg-aether-teal/10 border-aether-teal text-aether-teal shadow-[0_0_10px_rgba(34,211,238,0.15)]"
                          : "border-aether bg-obsidian text-muted-foreground hover:bg-obsidian-depth hover:text-foreground"
                      }`}
                    >
                      {diff}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <Button
            onClick={handleStart}
            disabled={isStarting}
            className="w-full h-12 mt-8"
          >
            {isStarting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-[#060814]" /> Preparing Interview...
              </>
            ) : (
              <>
                <Sparkles className="w-4.5 h-4.5 text-white animate-pulse mr-1.5" /> Start Technical Interview
              </>
            )}
          </Button>
        </Card>
      </MotionDiv>

      {/* History panel */}
      <MotionDiv
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="lg:col-span-2"
      >
        <Card className="h-full flex flex-col overflow-hidden bg-obsidian-layer/20">
          <div className="flex items-center gap-2 mb-6 px-1">
            <History className="w-5 h-5 text-aether-teal animate-pulse" />
            <h3 className="font-black font-display text-base uppercase tracking-wider text-foreground">Your Interview Logs</h3>
          </div>

          <div className="flex-1 overflow-y-auto min-h-0 space-y-4 pr-1 custom-scrollbar">
            {isLoadingHistory ? (
              <div className="h-full flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-aether-teal animate-spin" />
              </div>
            ) : history.length > 0 ? (
              history.map((session: InterviewSession, index: number) => (
                <div
                  key={session.id}
                  onClick={() => handleResume(session)}
                  className="flex items-center justify-between p-4 bg-obsidian border border-aether hover:border-aether-indigo/35 hover:-translate-y-0.5 rounded-2xl cursor-pointer transition-all shadow-md"
                >
                  <div className="flex items-center gap-4 min-w-0">
                    <div
                      className={`w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 border ${
                        session.is_completed
                          ? "bg-aether-indigo/10 text-aether-indigo border-aether-indigo/25"
                          : "bg-aether-emerald/10 text-aether-emerald border border-aether-emerald/20 animate-pulse"
                      }`}
                    >
                      {session.is_completed ? <Award className="w-5 h-5" /> : <MessageSquare className="w-5 h-5" />}
                    </div>
                    <div className="min-w-0">
                      <h4 className="font-extrabold text-foreground text-xs sm:text-sm truncate leading-snug">{session.topic}</h4>
                      <div className="flex items-center gap-2 mt-1.5">
                        <Badge variant="outline">
                          {session.difficulty}
                        </Badge>
                        <span className="text-[10px] text-muted-foreground font-semibold flex items-center gap-1">
                          <Clock className="w-3 h-3 text-muted-foreground" /> {new Date(session.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 pl-2 flex-shrink-0">
                    {session.is_completed ? (
                      <div className="flex items-baseline gap-0.5">
                        <span className="text-xl font-black text-aether-teal">{session.score}</span>
                        <span className="text-[9px] text-muted-foreground font-black">/100</span>
                      </div>
                    ) : (
                      <Badge variant="success" className="animate-pulse">
                        Active
                      </Badge>
                    )}
                    <ChevronRight className="w-5 h-5 text-muted-foreground" />
                  </div>
                </div>
              ))
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center p-8 gap-4 border border-dashed border-aether rounded-3xl bg-obsidian-depth/20">
                <div className="bg-obsidian p-4 rounded-2xl border border-aether">
                  <BookOpen className="w-6 h-6 text-[#8892B0]" />
                </div>
                <div className="space-y-1">
                  <h4 className="font-black text-foreground uppercase tracking-widest text-xs">No interviews recorded</h4>
                  <p className="text-xs text-[#8892B0] max-w-xs mx-auto font-medium leading-relaxed">
                    Start your first mock session on the left to practice system design, algorithms, or STAR behavior.
                  </p>
                </div>
              </div>
            )}
          </div>
        </Card>
      </MotionDiv>
    </div>
  );
}
