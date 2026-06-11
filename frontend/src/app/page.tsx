"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import dynamic from "next/dynamic";
const NeuralNetwork = dynamic(() => import("@/components/three/NeuralNetwork"), { ssr: false });
import {
  ArrowRight,
  Code2,
  BookOpen,
  MessageSquare,
  Zap,
  Sparkles,
  ChevronDown,
  Menu,
  X,
  Terminal,
  Cpu,
  Trophy,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const MotionDiv = motion.div as any;
const MotionSection = motion.section as any;
const AnimatePresenceComponent = AnimatePresence as any;

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"review" | "dsa" | "interview">("review");
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const stats = [
    { label: "AI Code Reviews Run", value: "250K+", icon: Code2, color: "text-aether-indigo" },
    { label: "Active Student Engineers", value: "15,000+", icon: Cpu, color: "text-aether-teal" },
    { label: "Interview Pass Success", value: "94.2%", icon: Trophy, color: "text-aether-violet" },
    { label: "Average Skill Improvement", value: "3.5x", icon: Zap, color: "text-aether-rose" }
  ];

  const features = [
    {
      id: "review",
      title: "AI Code Reviews",
      icon: Code2,
      color: "text-aether-indigo border-aether-indigo/20 bg-aether-indigo/5",
      description: "Submit your script and receive multi-agent reviews covering bugs, complexity, style, and security within seconds."
    },
    {
      id: "dsa",
      title: "Interactive DSA Mentor",
      icon: BookOpen,
      color: "text-aether-teal border-aether-teal/20 bg-aether-teal/5",
      description: "Trace algorithmic executions line-by-line. Visualize state progression, variables change, and space complexities."
    },
    {
      id: "interview",
      title: "Technical Mock Interviews",
      icon: MessageSquare,
      color: "text-aether-violet border-aether-violet/20 bg-aether-violet/5",
      description: "Practice technical mock rounds with behavioral or coding scenarios, and analyze an institutional-grade scorecard."
    }
  ];

  const faqs = [
    {
      q: "How does the AI review my code concurrently?",
      a: "CodeGuru AI utilizes parallel worker agents (Reviewer and Debugger) that execute alongside your submission to separately audit functional logic bugs and overall design style simultaneously, minimizing review latency."
    },
    {
      q: "Can I use CodeGuru offline or with local models?",
      a: "Yes. Our architecture supports Ollama providers out-of-the-box. When no OpenAI token is configured, system routines automatically fall back to local models like codellama."
    },
    {
      q: "How does the DSA variable stepper work?",
      a: "The DSA Mentor steps through algorithms utilizing custom compiler tracing, recording values of indices, vectors, and hash tables at each instruction block, displaying them step-by-step."
    },
    {
      q: "Is there a subscription fee or trial limit?",
      a: "All new developers receive a free trial quota to test code reviews, DSA mentors, and mock interviews. Premium plans unlock unlimited multi-agent evaluations and dashboard streak calendars."
    }
  ];

  const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
  };

  const staggerContainer = {
    hidden: { opacity: 1 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  return (
    <div className="min-h-screen bg-transparent text-foreground flex flex-col font-sans relative selection:bg-aether-indigo/30 selection:text-aether-teal overflow-x-hidden">
      
      {/* Decorative Glow Elements */}
      <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-aether-indigo/5 rounded-full blur-[140px] pointer-events-none animate-pulse z-0" />
      <div className="absolute top-[30%] right-10 w-[700px] h-[700px] bg-aether-violet/5 rounded-full blur-[160px] pointer-events-none z-0" />
      <div className="absolute bottom-[10%] left-[10%] w-[500px] h-[500px] bg-aether-teal/5 rounded-full blur-[120px] pointer-events-none z-0" />

      {/* Background Dot Grid */}
      <div className="absolute inset-0 dot-grid opacity-20 pointer-events-none z-0" />

      {/* Header / Navigation */}
      <header className="sticky top-0 z-50 border-b border-aether bg-obsidian-depth/75 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <MotionDiv
              whileHover={{ rotate: 10, scale: 1.05 }}
              className="bg-gradient-to-tr from-aether-indigo to-aether-violet text-white p-2.5 rounded-xl shadow-[0_0_15px_rgba(91,108,249,0.3)]"
            >
              <Sparkles className="w-5 h-5 text-white" />
            </MotionDiv>
            <span className="font-extrabold text-lg sm:text-xl tracking-wider font-display text-gradient text-aether-grad">
              CodeGuru AI
            </span>
          </div>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-8 text-xs font-black uppercase tracking-widest text-[#8892B0]">
            <a href="#features" className="hover:text-aether-teal transition-colors">Features</a>
            <a href="#demo" className="hover:text-aether-teal transition-colors">Workspace Demo</a>
            <a href="#faqs" className="hover:text-aether-teal transition-colors">FAQs</a>
            <Link href="/login" className="hover:text-aether-teal transition-colors">Sign In</Link>
            <Link href="/register">
              <Button variant="primary" size="default" className="text-[10px] tracking-widest">
                Get Started
              </Button>
            </Link>
          </nav>

          {/* Mobile Menu Btn */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-xl text-[#8892B0] hover:text-aether-teal bg-obsidian-depth border border-aether"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile Menu Panel */}
        {mobileMenuOpen && (
          <div className="md:hidden absolute top-20 left-0 w-full bg-obsidian-depth border-b border-aether px-6 py-6 flex flex-col gap-4 animate-in fade-in slide-in-from-top-4 duration-200 backdrop-blur-xl">
            <a
              href="#features"
              onClick={() => setMobileMenuOpen(false)}
              className="text-xs font-black uppercase tracking-widest text-[#8892B0] hover:text-aether-teal"
            >
              Features
            </a>
            <a
              href="#demo"
              onClick={() => setMobileMenuOpen(false)}
              className="text-xs font-black uppercase tracking-widest text-[#8892B0] hover:text-aether-teal"
            >
              Workspace Demo
            </a>
            <a
              href="#faqs"
              onClick={() => setMobileMenuOpen(false)}
              className="text-xs font-black uppercase tracking-widest text-[#8892B0] hover:text-aether-teal"
            >
              FAQs
            </a>
            <hr className="border-aether" />
            <Link
              href="/login"
              onClick={() => setMobileMenuOpen(false)}
              className="text-xs font-black uppercase tracking-widest text-[#8892B0] hover:text-aether-teal py-1"
            >
              Sign In
            </Link>
            <Link href="/register" onClick={() => setMobileMenuOpen(false)}>
              <Button variant="primary" className="w-full text-xs py-3">
                Get Started
              </Button>
            </Link>
          </div>
        )}
      </header>

      {/* Hero Section */}
      <section 
        className="relative z-10 flex flex-col items-center justify-center text-center px-6 pt-24 pb-16 max-w-7xl mx-auto w-full min-h-[80vh]"
      >
        {/* Render interactive 3D particle network in hero background */}
        <NeuralNetwork />

        <MotionDiv 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="relative z-10"
        >
          <Badge variant="primary" className="mb-8 font-black tracking-widest py-1.5 px-4 rounded-full bg-aether-indigo/10 border-aether-indigo/25 text-[#A4AFFF]">
            <Zap className="w-3.5 h-3.5 fill-aether-indigo/10 text-aether-indigo animate-pulse mr-2" />
            Production-Grade AI Coding Mentor
          </Badge>
        </MotionDiv>

        <MotionDiv 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight leading-[1.1] mb-6 max-w-5xl relative z-10 font-display text-foreground"
        >
          Accelerate Your Software Engineering Mastery with{" "}
          <span className="text-aether-grad">
            AI Mentorship
          </span>
        </MotionDiv>

        <MotionDiv 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="text-sm sm:text-base md:text-lg text-[#8892B0] max-w-3xl mb-12 leading-relaxed font-semibold relative z-10"
        >
          CodeGuru AI is a premium SaaS workspace offering concurrent multi-agent reviews, interactive DSA step-debugger run logs, live mock interview grading, and comprehensive study streak dashboards.
        </MotionDiv>

        <MotionDiv 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="flex flex-col sm:flex-row gap-4 mb-24 relative z-10"
        >
          <Link href="/register">
            <Button variant="primary" size="lg" className="w-full sm:w-auto flex items-center justify-center gap-2">
              Start Free Trial <ArrowRight className="w-4 h-4 text-white" />
            </Button>
          </Link>
          <Link href="/login">
            <Button variant="outline" size="lg" className="w-full sm:w-auto">
              Access Dashboard
            </Button>
          </Link>
        </MotionDiv>

        {/* Stats Row */}
        <MotionDiv 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-8 w-full border-y border-aether py-12 relative z-10 bg-obsidian/50 backdrop-blur-sm rounded-2xl px-6"
        >
          {stats.map((stat, i) => {
            const StatIcon = stat.icon;
            return (
              <div key={i} className="text-center space-y-2 relative group">
                <div className="relative flex flex-col items-center">
                  <div className="text-3xl sm:text-4xl font-extrabold text-foreground font-display">
                    {stat.value}
                  </div>
                  <div className="text-[9px] text-[#8892B0] font-black mt-2.5 uppercase tracking-widest flex items-center gap-1.5">
                    <StatIcon className={`w-3.5 h-3.5 ${stat.color}`} />
                    {stat.label}
                  </div>
                </div>
              </div>
            );
          })}
        </MotionDiv>
      </section>

      {/* Feature Catalog Grid */}
      <section id="features" className="relative z-10 max-w-7xl mx-auto px-6 py-24 w-full">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight font-display text-aether-grad">
            Curated Ecosystem Built For Real Growth
          </h2>
          <p className="text-[#8892B0] text-sm sm:text-base leading-relaxed font-semibold">
            Personalized coding reviews, detailed complexity stepper traces, and conversational interview preparation — engineered with strict architectures and concurrent executions.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feat) => {
            const Icon = feat.icon;
            return (
              <MotionDiv
                whileHover={{ y: -6 }}
                key={feat.id}
                className="group"
              >
                <Card className="h-full p-8 flex flex-col justify-between hoverable">
                  <div>
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-6 border border-aether shadow-[0_0_15px_rgba(91,108,249,0.1)] ${feat.color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <h3 className="text-lg font-bold mb-3 text-foreground font-display group-hover:text-aether-teal transition-colors">
                      {feat.title}
                    </h3>
                    <p className="text-xs sm:text-sm text-[#8892B0] leading-relaxed font-semibold">
                      {feat.description}
                    </p>
                  </div>
                </Card>
              </MotionDiv>
            );
          })}
        </div>
      </section>

      {/* Product Live Demo Panel */}
      <section id="demo" className="relative z-10 max-w-7xl mx-auto px-6 py-16 w-full">
        <Card className="relative overflow-hidden p-6 sm:p-10">
          <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-aether-indigo/5 rounded-full blur-[100px] pointer-events-none" />
          
          <div className="flex flex-col lg:flex-row gap-10 items-center justify-between mb-8 border-b border-aether pb-8">
            <div className="space-y-1.5">
              <h2 className="text-2xl sm:text-3xl font-extrabold text-foreground font-display">
                Inside the Mentorship Workspace
              </h2>
              <p className="text-xs sm:text-sm text-[#8892B0] font-semibold">
                Click the workspace modules below to preview our interactive AI mentor agents.
              </p>
            </div>
            
            {/* Tab switch buttons */}
            <div className="flex bg-obsidian p-1 rounded-xl border border-aether self-start lg:self-center relative">
              {(["review", "dsa", "interview"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`relative text-xs font-black uppercase tracking-widest px-4 py-2.5 rounded-lg transition-all z-10 ${
                    activeTab === tab ? "text-foreground" : "text-[#8892B0] hover:text-foreground"
                  }`}
                >
                  {activeTab === tab && (
                    <MotionDiv
                      layoutId="landing-demo-tab"
                      className="absolute inset-0 bg-gradient-to-r from-aether-indigo to-aether-violet rounded-lg z-[-1] shadow-[0_0_15px_rgba(91,108,249,0.4)]"
                      transition={{ type: "spring", stiffness: 380, damping: 30 }}
                    />
                  )}
                  {tab === "review" ? "Code Reviewer" : tab === "dsa" ? "DSA Stepper" : "Mock Interviewer"}
                </button>
              ))}
            </div>
          </div>

          {/* Interactive Workspace Monitor */}
          <Card className="border-aether overflow-hidden p-0 shadow-2xl bg-obsidian">
            {/* Header window control buttons */}
            <div className="bg-obsidian-depth px-4 py-3 border-b border-aether flex items-center justify-between text-xs font-mono text-[#3D4A6B]">
              <div className="flex gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-aether-rose/60" />
                <span className="w-2.5 h-2.5 rounded-full bg-aether-violet/60" />
                <span className="w-2.5 h-2.5 rounded-full bg-aether-indigo/60" />
              </div>
              <div className="flex items-center gap-1.5 font-black uppercase tracking-widest text-[9px]">
                <Terminal className="w-3.5 h-3.5 text-aether-teal" />
                <span>codeguru-ai-workspace -- {activeTab}</span>
              </div>
              <span>UTF-8</span>
            </div>

            {/* Content body based on active tab */}
            <div className="p-6 font-mono text-xs sm:text-sm overflow-x-auto min-h-[300px] bg-[#060814]">
              <AnimatePresenceComponent mode="wait">
                {activeTab === "review" && (
                  <MotionDiv
                    key="review"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className="space-y-4"
                  >
                    <div className="text-[#3D4A6B]">// Submitted Python Function</div>
                    <div className="text-aether-indigo">
                      <span className="text-aether-rose">def</span> <span className="text-aether-violet">calculate_fibonacci</span>(n):<br />
                      &nbsp;&nbsp;&nbsp;&nbsp;<span className="text-aether-rose">if</span> n &lt; <span className="text-aether-teal">2</span>: <span className="text-aether-rose">return</span> n<br />
                      &nbsp;&nbsp;&nbsp;&nbsp;<span className="text-aether-rose">return</span> calculate_fibonacci(n - <span className="text-aether-teal">1</span>) + calculate_fibonacci(n - <span className="text-aether-teal">2</span>)
                    </div>
                    <hr className="border-aether" />
                    <div className="bg-obsidian-depth p-4 rounded-xl border border-aether space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-aether-indigo font-black uppercase tracking-widest text-xs flex items-center gap-1.5">
                          <Sparkles className="w-3.5 h-3.5"/> AI review feedback
                        </span>
                        <Badge variant="success" className="text-[8px]">
                          Quality Score: 92/100
                        </Badge>
                      </div>
                      <div className="text-foreground font-sans text-xs font-semibold leading-relaxed">
                        <span className="font-extrabold text-aether-rose">[Performance Issue]</span>: Exponential time complexity O(2^N). Use memoization or dynamic programming to achieve linear O(N) complexity.
                      </div>
                      <div className="text-[#8892B0] font-sans text-[11px] font-semibold">
                        👉 Suggestion: Swap recursion for iteration or decorate with `@lru_cache`.
                      </div>
                    </div>
                  </MotionDiv>
                )}

                {activeTab === "dsa" && (
                  <MotionDiv
                    key="dsa"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className="space-y-4"
                  >
                    <div className="text-[#3D4A6B]">// Trace stepper execution: Two Sum (target = 9)</div>
                    <div className="space-y-2 font-mono text-xs">
                      <div className="flex items-center gap-4 text-aether-emerald">
                        <Badge variant="success" className="text-[8px] py-0">Step 1</Badge>
                        <span>Line 3: nums = [2, 7, 11, 15], map = &#123;&#125;</span>
                      </div>
                      <div className="text-[#8892B0] pl-14 text-xs font-sans font-semibold">Action: Inspect value 2. Complement = 7 (9 - 2). Map lookup: False. Insert (2, 0) into map.</div>
                      <div className="flex items-center gap-4 text-aether-emerald pt-2">
                        <Badge variant="success" className="text-[8px] py-0">Step 2</Badge>
                        <span>Line 3: nums = [2, 7, 11, 15], map = &#123;2: 0&#125;</span>
                      </div>
                      <div className="text-aether-teal pl-14 font-extrabold text-xs font-sans">Action: Inspect value 7. Complement = 2 (9 - 7). Map lookup: True (found index 0). Return indices [0, 1].</div>
                    </div>
                  </MotionDiv>
                )}

                {activeTab === "interview" && (
                  <MotionDiv
                    key="interview"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className="space-y-4 font-sans text-xs"
                  >
                    <div className="flex items-start gap-3">
                      <Badge variant="secondary" className="text-[8px] py-0 flex-shrink-0 mt-0.5">AI</Badge>
                      <div className="bg-obsidian-depth p-3.5 rounded-xl text-xs text-[#8892B0] max-w-[80%] border border-aether/40 font-semibold">
                        Welcome to your system design interview. Today we are designing a scalable, real-time message notification queue that processes millions of requests. How would you handle rate-limiting and duplicate notifications?
                      </div>
                    </div>
                    <div className="flex items-start gap-3 justify-end">
                      <Badge variant="primary" className="text-[8px] py-0 flex-shrink-0 mt-0.5 order-2">Candidate</Badge>
                      <div className="bg-aether-indigo text-white p-3.5 rounded-xl text-xs max-w-[80%] order-1 shadow-[0_0_15px_rgba(91,108,249,0.15)] font-extrabold">
                        I would introduce a Token Bucket rate-limiter at the API Gateway level. To prevent duplicate messages, I'd cache client-provided idempotent keys in Redis for 24 hours.
                      </div>
                    </div>
                  </MotionDiv>
                )}
              </AnimatePresenceComponent>
            </div>
          </Card>
        </Card>
      </section>

      {/* Frequently Asked Questions */}
      <section id="faqs" className="relative z-10 max-w-4xl mx-auto px-6 py-24 w-full">
        <h2 className="text-3xl font-extrabold text-center mb-12 font-display text-aether-grad">Frequently Asked Questions</h2>
        <div className="space-y-4">
          {faqs.map((faq, idx) => (
            <div
              key={idx}
              className="border border-aether bg-obsidian-depth/50 rounded-xl overflow-hidden transition-all duration-350 hover:border-aether-indigo/30"
            >
              <button
                onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                className="w-full flex items-center justify-between px-6 py-5 text-left font-bold text-foreground hover:text-aether-teal transition-colors"
              >
                <span className="text-sm md:text-base font-display">{faq.q}</span>
                <ChevronDown className={`w-4.5 h-4.5 text-[#8892B0] transition-transform duration-200 ${openFaq === idx ? "rotate-180 text-aether-teal" : ""}`} />
              </button>
              
              <AnimatePresenceComponent>
                {openFaq === idx && (
                  <MotionDiv
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="px-6 pb-6 text-xs sm:text-sm text-[#8892B0] leading-relaxed font-semibold">
                      {faq.a}
                    </div>
                  </MotionDiv>
                )}
              </AnimatePresenceComponent>
            </div>
          ))}
        </div>
      </section>

      {/* Call To Action */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-16 w-full text-center">
        <Card className="relative overflow-hidden p-12 sm:p-20">
          <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-aether-indigo/5 rounded-full blur-[100px] pointer-events-none" />
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight mb-6 font-display text-aether-grad">
            Ready to Accelerate Your Mastery?
          </h2>
          <p className="text-[#8892B0] max-w-2xl mx-auto mb-10 text-xs sm:text-sm leading-relaxed font-semibold">
            Create your account today and gain access to the CodeGuru AI multi-agent workspace. Leverage professional concurrent evaluations and complete your learning goals.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register">
              <Button variant="primary" size="lg" className="w-full sm:w-auto uppercase tracking-widest text-[11px] font-black h-14">
                Get Started for Free
              </Button>
            </Link>
            <Link href="/login">
              <Button variant="outline" size="lg" className="w-full sm:w-auto uppercase tracking-widest text-[11px] font-black h-14">
                Access Platform
              </Button>
            </Link>
          </div>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t border-aether bg-obsidian-depth py-12 relative z-10 mt-auto">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between text-[10px] text-[#3D4A6B] font-black uppercase tracking-widest gap-4">
          <p>© {new Date().getFullYear()} CodeGuru AI Platform. All rights reserved.</p>
          <div className="flex gap-6">
            <a href="#" className="hover:text-aether-teal transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-aether-teal transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-aether-teal transition-colors">Documentation</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
