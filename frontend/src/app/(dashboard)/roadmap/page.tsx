"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  CheckCircle2,
  Circle,
  BookOpen,
  Sparkles,
  ChevronRight,
  ArrowRight,
  Database,
  ArrowLeft,
  Calendar,
  Layers,
  Loader2,
  Globe
} from "lucide-react";
import { aetherColors } from "@/lib/aether-theme";

const MotionDiv = motion.div as any;
const AnimatePresenceComponent = AnimatePresence as any;

interface RoadmapNode {
  id: string;
  title: string;
  duration: string;
  description: string;
  concepts: string[];
  resources: { name: string; url: string }[];
  completed: boolean;
}

interface RoadmapTrack {
  id: string;
  name: string;
  icon: React.ReactNode;
  color: string;
  nodes: RoadmapNode[];
}

const DEFAULT_TRACKS: RoadmapTrack[] = [
  {
    id: "backend",
    name: "Backend Engineer",
    icon: <Database className="w-5 h-5 text-aether-teal" />,
    color: "teal",
    nodes: [
      {
        id: "be-1",
        title: "Internet & Networking Protocols",
        duration: "Week 1",
        description: "Understand how client-server architectures interact over HTTP/HTTPS, WebSockets, TCP/IP, and DNS resolution.",
        concepts: ["DNS resolution & IP routing", "HTTP request/response lifecycle", "REST vs gRPC vs GraphQL APIs", "WebSockets and Realtime APIs"],
        resources: [
          { name: "MDN HTTP Overview", url: "https://developer.mozilla.org/en-US/docs/Web/HTTP" },
          { name: "System Design Primer - Networking", url: "https://github.com/donnemartin/system-design-primer" }
        ],
        completed: true,
      },
      {
        id: "be-2",
        title: "Relational & NoSQL Databases",
        duration: "Week 2-3",
        description: "Master database designs, query profiling, normalization, index structures, ACID transactions, and scaling trade-offs.",
        concepts: ["SQL indexes (B-Trees, Hash)", "Database normalization & schema design", "ACID transactions & isolation levels", "CAP Theorem & NoSQL stores"],
        resources: [
          { name: "PostgreSQL Official Tutorial", url: "https://www.postgresql.org/docs/" },
          { name: "Designing Data-Intensive Applications", url: "https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/" }
        ],
        completed: true,
      },
      {
        id: "be-3",
        title: "Serverless & Microservices Architecture",
        duration: "Week 4-5",
        description: "Learn how to decouple applications, build serverless handlers, design message brokers, and manage service routing.",
        concepts: ["API Gateways & reverse proxies", "Message queues (RabbitMQ, Kafka)", "Serverless compute (AWS Lambda, Cloud Run)", "Event-driven architecture patterns"],
        resources: [
          { name: "Microservice Architecture Guide", url: "https://microservices.io/" },
          { name: "FastAPI Async Routing", url: "https://fastapi.tiangolo.com/async/" }
        ],
        completed: false,
      },
      {
        id: "be-4",
        title: "Caching & Distributed Systems Scaling",
        duration: "Week 6",
        description: "Learn to design low-latency caches, read-through/write-through cache stores, and distributed locking patterns.",
        concepts: ["Redis cache store eviction policies", "Content Delivery Networks (CDN)", "Consistent hashing algorithms", "Load balancing strategies"],
        resources: [
          { name: "Redis Caching Best Practices", url: "https://redis.io/docs/manual/client-side-caching/" }
        ],
        completed: false,
      }
    ],
  },
  {
    id: "frontend",
    name: "Frontend Architect",
    icon: <Globe className="w-5 h-5 text-aether-violet" />,
    color: "violet",
    nodes: [
      {
        id: "fe-1",
        title: "Advanced DOM & Modern JavaScript",
        duration: "Week 1",
        description: "Deep dive into execution contexts, closures, event loops, microtasks, prototype chains, and performance profiling.",
        concepts: ["Event delegation & bubbling", "JS Engine memory stack vs heap", "Asynchronous Event Loop internals", "ES modules & tree-shaking"],
        resources: [
          { name: "javascript.info", url: "https://javascript.info/" }
        ],
        completed: true,
      },
      {
        id: "fe-2",
        title: "React 19 & Next.js Frameworks",
        duration: "Week 2-3",
        description: "Master React Server Components (RSC), Suspense boundaries, streaming SSR, actions, compiler optimizations, and layout routing.",
        concepts: ["React Server Components vs Client Components", "Next.js App Router & Server Actions", "Dynamic streaming and static site generation", "React 19 compiler internals"],
        resources: [
          { name: "Next.js Official Documentation", url: "https://nextjs.org/docs" },
          { name: "React 19 RC Features", url: "https://react.dev/blog/2024/04/25/react-19" }
        ],
        completed: false,
      },
      {
        id: "fe-3",
        title: "State Management & Rendering Tuning",
        duration: "Week 4",
        description: "Build scalable client state engines, optimize virtual DOM re-renders, and trace painting pipelines.",
        concepts: ["Zustand vs Redux Toolkit vs Recoil", "React.memo, useMemo, and useCallback", "CLS, LCP, and FID core web vitals", "CSS repaint and layout reflows"],
        resources: [
          { name: "Zustand Docs", url: "https://github.com/pmndrs/zustand" }
        ],
        completed: false,
      }
    ],
  },
  {
    id: "system-design",
    name: "System Design",
    icon: <Layers className="w-5 h-5 text-aether-purple" />,
    color: "purple",
    nodes: [
      {
        id: "sd-1",
        title: "Scalability Patterns & Fundamentals",
        duration: "Week 1",
        description: "Explore the core foundations of scaling services from 100 to 10M active daily users.",
        concepts: ["Vertical vs Horizontal scaling", "Rate limiters and throttles", "Reverse Proxies & DNS Geo-routing", "Single Points of Failure (SPOF)"],
        resources: [
          { name: "System Design Primer", url: "https://github.com/donnemartin/system-design-primer" }
        ],
        completed: true,
      },
      {
        id: "sd-2",
        title: "High Performance Storage Systems",
        duration: "Week 2",
        description: "Trace reading and writing pipelines across sharded databases and column-oriented indexing engines.",
        concepts: ["Database sharding & replication", "Write-Ahead Logs (WAL) and LSM trees", "NoSQL Columnar storage (Cassandra)", "Read replicas and write bottlenecks"],
        resources: [
          { name: "System Design Interview - Alex Xu", url: "https://bytebytego.com/" }
        ],
        completed: false,
      }
    ],
  }
];

const getTrackColorClasses = (color: string) => {
  const mapping: Record<string, {
    bgActive: string;
    borderActive: string;
    textActive: string;
    bgIconActive: string;
    borderIconActive: string;
    text: string;
    glowGrad: string;
  }> = {
    teal: {
      bgActive: "bg-aether-teal/5",
      borderActive: "border-aether-teal/30",
      textActive: "text-aether-teal",
      bgIconActive: "bg-aether-teal/10",
      borderIconActive: "border-aether-teal/20",
      text: "text-aether-teal",
      glowGrad: "from-aether-teal/5",
    },
    violet: {
      bgActive: "bg-aether-violet/5",
      borderActive: "border-aether-violet/30",
      textActive: "text-aether-violet",
      bgIconActive: "bg-aether-violet/10",
      borderIconActive: "border-aether-violet/20",
      text: "text-aether-violet",
      glowGrad: "from-aether-violet/5",
    },
    purple: {
      bgActive: "bg-aether-purple/5",
      borderActive: "border-aether-purple/30",
      textActive: "text-aether-purple",
      bgIconActive: "bg-aether-purple/10",
      borderIconActive: "border-aether-purple/20",
      text: "text-aether-purple",
      glowGrad: "from-aether-purple/5",
    },
    indigo: {
      bgActive: "bg-aether-indigo/5",
      borderActive: "border-aether-indigo/30",
      textActive: "text-aether-indigo",
      bgIconActive: "bg-aether-indigo/10",
      borderIconActive: "border-aether-indigo/20",
      text: "text-aether-indigo",
      glowGrad: "from-aether-indigo/5",
    },
  };

  return mapping[color] || mapping.indigo;
};

export default function RoadmapPage() {
  const [tracks, setTracks] = useState<RoadmapTrack[]>(DEFAULT_TRACKS);
  const [activeTrackId, setActiveTrackId] = useState<string>("backend");
  const [selectedNode, setSelectedNode] = useState<RoadmapNode | null>(null);
  
  // Custom AI Roadmap Generation State
  const [promptInput, setPromptInput] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  const activeTrack = tracks.find((t) => t.id === activeTrackId) || tracks[0];

  // Calculate track progress percentage
  const completedCount = activeTrack.nodes.filter((n) => n.completed).length;
  const progressPercent = Math.round((completedCount / activeTrack.nodes.length) * 100) || 0;

  const toggleNodeCompletion = (nodeId: string) => {
    setTracks(prevTracks => 
      prevTracks.map(track => {
        if (track.id !== activeTrackId) return track;
        return {
          ...track,
          nodes: track.nodes.map(node => {
            if (node.id !== nodeId) return node;
            const updated = { ...node, completed: !node.completed };
            if (selectedNode && selectedNode.id === nodeId) {
              setSelectedNode(updated);
            }
            return updated;
          })
        };
      })
    );
  };

  const handleGenerateRoadmap = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!promptInput.trim()) return;

    setIsGenerating(true);
    // Simulate rich AI roadmapping generation
    setTimeout(() => {
      const customTrack: RoadmapTrack = {
        id: "custom",
        name: promptInput.length > 20 ? `${promptInput.substring(0, 17)}...` : promptInput,
        icon: <Sparkles className="w-5 h-5 text-aether-indigo animate-pulse" />,
        color: "indigo",
        nodes: [
          {
            id: "c-1",
            title: `Foundations of ${promptInput}`,
            duration: "Week 1",
            description: `Core concepts, vocabulary, and primary setup modules for learning ${promptInput} in production environments.`,
            concepts: ["Core concepts & architecture syntax", "Developer toolchains & compiler setups", "Writing basic functional components", "Hello world program deployment"],
            resources: [{ name: "Official documentation guides", url: "#" }],
            completed: false,
          },
          {
            id: "c-2",
            title: `Intermediate Integration & Testing`,
            duration: "Week 2",
            description: `Deep dive into advanced logic structures, asynchronous routing pipelines, state engines, and automated unit testing.`,
            concepts: ["Asynchronous API invocations", "Local database sync configurations", "Unit testing frameworks", "State manipulation paradigms"],
            resources: [{ name: "Best practice reference manuals", url: "#" }],
            completed: false,
          },
          {
            id: "c-3",
            title: `Advanced Performance Tuning & Scale`,
            duration: "Week 3-4",
            description: `Tracing execution pipelines, caching strategies, containerizing the application, and launching to cluster instances.`,
            concepts: ["Caching bottlenecks & memory profiling", "Docker containerization deployment", "Metrics telemetry scrapers", "Optimizing compiler build sizes"],
            resources: [{ name: "Production deployment blueprints", url: "#" }],
            completed: false,
          }
        ]
      };

      setTracks((prev) => {
        // Remove previous custom track if exists, and append new one
        const filtered = prev.filter((t) => t.id !== "custom");
        return [...filtered, customTrack];
      });
      setActiveTrackId("custom");
      setIsGenerating(false);
      setPromptInput("");
    }, 2500);
  };

  // Find the first incomplete node to mark as "active"
  const firstIncompleteNode = activeTrack.nodes.find((n) => !n.completed);

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <h1 className="text-3xl font-extrabold tracking-tight font-display text-aether-grad">
            Learning Roadmaps
          </h1>
          <p className="text-xs sm:text-sm text-secondary font-black uppercase tracking-widest">
            Track syllabus progress, learn key engineering concepts, or generate custom tracks with AI.
          </p>
        </div>
      </div>

      {/* AI Roadmap Generator */}
      <Card glow className="relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
          <Sparkles className="w-24 h-24 text-aether-indigo animate-pulse" />
        </div>
        <CardContent className="p-6 max-w-3xl space-y-4">
          <div className="flex items-center gap-2.5">
            <span className="flex items-center justify-center bg-aether-indigo/10 text-aether-indigo p-2.5 rounded-xl border border-aether-indigo/25">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </span>
            <h3 className="font-black text-sm uppercase tracking-widest text-foreground font-display">
              AI Custom Roadmap Generator
            </h3>
          </div>
          <p className="text-xs text-secondary leading-relaxed font-semibold">
            Want to learn a specific tech stack, library, or engineering specialty? Describe your target goals and our AI agent will structure a custom syllabus timeline for you.
          </p>
          <form onSubmit={handleGenerateRoadmap} className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <Input
                type="text"
                placeholder="e.g., Learn Rust systems programming, Docker architectures, or Graph algorithms..."
                value={promptInput}
                onChange={(e) => setPromptInput(e.target.value)}
                disabled={isGenerating}
                className="w-full font-semibold border-input bg-obsidian-depth"
              />
            </div>
            <MotionDiv whileTap={{ scale: 0.98 }}>
              <Button
                type="submit"
                disabled={isGenerating || !promptInput.trim()}
                variant="primary"
                className="h-11 px-6 font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-obsidian" />
                    Generating...
                  </>
                ) : (
                  <>
                    Generate Path
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </Button>
            </MotionDiv>
          </form>
        </CardContent>
      </Card>

      {/* Main Roadmap Hub */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Track Navigation */}
        <div className="space-y-6">
          <div className="space-y-3">
            <h3 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground px-1">
              Select Syllabus Track
            </h3>
            <div className="flex flex-col gap-3">
              {tracks.map((track, idx) => {
                const isActive = activeTrackId === track.id;
                const trackCompletedCount = track.nodes.filter((n) => n.completed).length;
                const trackProgress = Math.round((trackCompletedCount / track.nodes.length) * 100);
                const theme = getTrackColorClasses(track.color);

                return (
                  <MotionDiv
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: idx * 0.05 }}
                    key={track.id}
                  >
                    <button
                      onClick={() => {
                        setActiveTrackId(track.id);
                        setSelectedNode(null);
                      }}
                      className={`w-full flex items-center justify-between p-4 rounded-xl border text-left transition-all duration-300 relative group overflow-hidden ${
                        isActive
                          ? `${theme.bgActive} ${theme.borderActive} ${theme.textActive}`
                          : "bg-obsidian-depth/40 border-border text-secondary hover:bg-obsidian-layer hover:border-aether-indigo/25 hover:text-foreground"
                      }`}
                    >
                      {/* Ambient micro-glow inside active button */}
                      {isActive && (
                        <div className={`absolute inset-0 bg-gradient-to-r ${theme.glowGrad} to-transparent pointer-events-none`} />
                      )}
                      
                      <div className="flex items-center gap-3.5 min-w-0 relative z-10">
                        <div className={`p-2.5 rounded-lg border ${
                          isActive 
                            ? `${theme.bgIconActive} ${theme.textActive} ${theme.borderIconActive}` 
                            : "bg-obsidian-depth text-secondary border-border group-hover:border-aether-indigo/20 group-hover:text-aether-indigo transition-colors"
                        }`}>
                          {track.icon}
                        </div>
                        <div className="min-w-0">
                          <h4 className="font-bold text-xs sm:text-sm text-foreground truncate leading-snug">
                            {track.name}
                          </h4>
                          <div className="flex items-center gap-1.5 mt-1 font-bold text-[9px] uppercase tracking-wider text-muted-foreground">
                            <span>{track.nodes.length} Topics</span>
                            <span>•</span>
                            <span className={theme.textActive}>{trackProgress}% Done</span>
                          </div>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-muted-foreground flex-shrink-0 group-hover:translate-x-0.5 transition-transform" />
                    </button>
                  </MotionDiv>
                );
              })}
            </div>
          </div>

          {/* Active Syllabus Progress Summary */}
          <Card className="relative overflow-hidden">
            <CardContent className="p-5 space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">
                  Syllabus Progress
                </span>
                <span className="text-xs font-black text-aether-indigo">{progressPercent}%</span>
              </div>
              
              {/* Progress Bar */}
              <div className="h-1.5 w-full bg-obsidian rounded-full overflow-hidden border border-border">
                <MotionDiv
                  className="h-full bg-gradient-to-r from-aether-indigo to-aether-teal rounded-full shadow-[0_0_8px_rgba(91,108,249,0.3)]"
                  initial={{ width: 0 }}
                  animate={{ width: `${progressPercent}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>

              <div className="flex items-start gap-3 bg-obsidian-depth/50 p-4 rounded-xl border border-border">
                <div className="bg-aether-indigo/10 text-aether-indigo p-2 rounded-lg border border-aether-indigo/10 flex-shrink-0">
                  <BookOpen className="w-4 h-4" />
                </div>
                <p className="text-[11px] text-secondary leading-relaxed font-semibold">
                  {completedCount} of {activeTrack.nodes.length} topics completed. Click any roadmap step in the timeline to view learning content, suggested readings, and log progress.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Middle & Right Column: Interactive Timeline Map */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="min-h-[500px] relative p-6 md:p-8">
            <CardHeader className="p-0 mb-8">
              <CardTitle className="font-extrabold text-sm uppercase tracking-wider text-foreground flex items-center gap-2">
                Timeline Map: <span className="text-aether-indigo font-black">{activeTrack.name}</span>
              </CardTitle>
            </CardHeader>

            {/* Timeline Graphic Area */}
            <div className="relative pl-10 md:pl-16 space-y-12">
              {/* Vertical line indicator using aether colors */}
              <div className="absolute top-2 bottom-6 left-4 md:left-7 w-[2px] bg-gradient-to-b from-aether-indigo via-aether-violet to-aether-teal opacity-50" />

              {activeTrack.nodes.map((node, index) => {
                const isSelected = selectedNode?.id === node.id;
                const isCompleted = node.completed;
                const isActiveNode = firstIncompleteNode && node.id === firstIncompleteNode.id;

                let indicatorClasses = "";
                let indicatorIcon = null;

                if (isCompleted) {
                  indicatorClasses = "border-aether-emerald text-aether-emerald shadow-[0_0_12px_rgba(52,211,153,0.4)]";
                  indicatorIcon = <CheckCircle2 className="w-4 h-4 fill-aether-emerald/10" />;
                } else if (isActiveNode) {
                  indicatorClasses = "border-aether-indigo text-aether-indigo shadow-[0_0_12px_rgba(91,108,249,0.45)] bg-obsidian-depth";
                  indicatorIcon = <Circle className="w-2.5 h-2.5 fill-aether-indigo" />;
                } else {
                  indicatorClasses = "border-muted text-muted-foreground bg-obsidian-depth";
                  indicatorIcon = <Circle className="w-2 h-2 text-muted-foreground" />;
                }

                return (
                  <MotionDiv
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.35, delay: index * 0.05 }}
                    key={node.id}
                    className="relative group cursor-pointer"
                    onClick={() => setSelectedNode(node)}
                  >

                    {/* Circle Indicator */}
                    <div className="absolute -left-10 md:-left-13 top-1.5 flex items-center justify-center z-10">
                      <MotionDiv whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleNodeCompletion(node.id);
                          }}
                          className={`w-7 h-7 rounded-full border flex items-center justify-center transition-all bg-obsidian ${indicatorClasses}`}
                        >
                          {indicatorIcon}
                        </button>
                      </MotionDiv>
                    </div>

                    {/* Step Card */}
                    <div 
                      onClick={() => setSelectedNode(node)}
                      className={`p-5 rounded-xl border transition-all duration-300 ${
                        isSelected
                          ? "bg-aether-indigo/5 border-aether-indigo/40 shadow-[0_0_20px_rgba(91,108,249,0.1)]"
                          : isCompleted
                          ? "bg-obsidian-layer/40 border-aether-emerald/10 hover:border-aether-emerald/30 hover:bg-obsidian-layer/60"
                          : isActiveNode
                          ? "bg-obsidian-layer/50 border-aether-indigo/20 hover:border-aether-indigo/40 hover:bg-obsidian-layer/70 shadow-[0_0_15px_rgba(91,108,249,0.05)]"
                          : "bg-obsidian-layer/20 border-border/5 hover:border-border/20 hover:bg-obsidian-layer/40"
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1.5">
                        <span className="text-[9px] font-black uppercase text-aether-indigo flex items-center gap-1.5 tracking-widest">
                          <Calendar className="w-3.5 h-3.5" /> {node.duration}
                        </span>
                        {isCompleted && (
                          <Badge variant="success" className="self-start sm:self-auto text-[8px] py-0 bg-aether-emerald/20 text-aether-emerald border-aether-emerald/25">
                            Completed
                          </Badge>
                        )}
                        {!isCompleted && isActiveNode && (
                          <Badge className="self-start sm:self-auto text-[8px] py-0 bg-aether-indigo/20 text-aether-indigo border-aether-indigo/25">
                            In Progress
                          </Badge>
                        )}
                      </div>
                      <h4 className="font-extrabold text-foreground leading-snug text-sm sm:text-base group-hover:text-aether-indigo transition-colors font-display">
                        {node.title}
                      </h4>
                      <p className="text-xs text-secondary mt-2 line-clamp-2 leading-relaxed font-semibold">
                        {node.description}
                      </p>
                      <div className="flex items-center gap-1.5 mt-4 text-[10px] uppercase tracking-widest text-aether-indigo font-black group-hover:translate-x-0.5 transition-transform">
                        Explore Curriculum <ArrowRight className="w-3.5 h-3.5" />
                      </div>
                    </div>
                  </MotionDiv>
                );
              })}
            </div>
          </Card>
        </div>
      </div>

      {/* Slide-over Detail Panel */}
      <AnimatePresenceComponent>
        {selectedNode && (
          <>
            {/* Backdrop */}
            <MotionDiv
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedNode(null)}
              className="fixed inset-0 bg-obsidian/80 z-40 backdrop-blur-md"
            />
            {/* Slider container */}
            <MotionDiv
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "tween", duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
              className="fixed right-0 top-0 bottom-0 w-full sm:max-w-lg bg-obsidian-depth/95 border-l border-border z-50 shadow-2xl p-6 md:p-8 flex flex-col justify-between backdrop-blur-aether"
            >
              <div className="space-y-6 overflow-y-auto pr-1 custom-scrollbar">
                {/* Header back button */}
                <button
                  onClick={() => setSelectedNode(null)}
                  className="flex items-center gap-2 text-[9px] font-black uppercase tracking-widest text-muted-foreground hover:text-aether-indigo transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" /> Back to Syllabus
                </button>

                {/* Topic Metadata */}
                <div className="space-y-2">
                  <span className="text-[9px] font-black uppercase text-aether-indigo flex items-center gap-1 mt-3 tracking-widest">
                    <Calendar className="w-3.5 h-3.5" /> {selectedNode.duration}
                  </span>
                  <h2 className="text-lg sm:text-xl font-extrabold text-foreground leading-snug font-display">
                    {selectedNode.title}
                  </h2>
                  <p className="text-xs sm:text-sm text-secondary leading-relaxed font-semibold">
                    {selectedNode.description}
                  </p>
                </div>

                <div className="h-[1px] bg-border w-full" />

                {/* Key Syllabus Concepts */}
                <div className="space-y-4">
                  <h4 className="font-black text-[9px] uppercase tracking-widest text-muted-foreground">
                    Syllabus Concepts to Master
                  </h4>
                  <ul className="grid grid-cols-1 gap-3">
                    {selectedNode.concepts.map((concept, idx) => (
                      <li key={idx} className="flex items-start gap-3.5 text-xs text-foreground leading-relaxed bg-obsidian-layer/40 p-3.5 rounded-xl border border-border font-semibold">
                        <span className="w-5 h-5 rounded-lg bg-aether-indigo/10 text-aether-indigo flex items-center justify-center flex-shrink-0 text-[10px] font-black mt-0.5 border border-aether-indigo/15">
                          {idx + 1}
                        </span>
                        <span className="min-w-0 flex-1">{concept}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="h-[1px] bg-border w-full" />

                {/* Suggested Study Resources */}
                <div className="space-y-4">
                  <h4 className="font-black text-[9px] uppercase tracking-widest text-muted-foreground">
                    Suggested Study Resources
                  </h4>
                  <div className="flex flex-col gap-3">
                    {selectedNode.resources.map((res, idx) => (
                      <a
                        key={idx}
                        href={res.url}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center justify-between p-4 bg-obsidian-layer/40 hover:bg-obsidian-layer/70 border border-border hover:border-aether-indigo/30 rounded-xl text-xs transition-all"
                      >
                        <span className="font-bold truncate text-foreground pr-2">{res.name}</span>
                        <span className="text-aether-indigo hover:underline flex items-center gap-1 font-black text-[9px] uppercase tracking-widest flex-shrink-0">
                          Link <ArrowRight className="w-3.5 h-3.5" />
                        </span>
                      </a>
                    ))}
                  </div>
                </div>
              </div>

              {/* Status Actions footer */}
              <div className="pt-6 border-t border-border bg-obsidian-depth flex flex-col gap-3.5">
                <Button
                  onClick={() => toggleNodeCompletion(selectedNode.id)}
                  variant={selectedNode.completed ? "danger" : "primary"}
                  className="w-full py-6 font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2"
                >
                  {selectedNode.completed ? (
                    <>Mark Incomplete</>
                  ) : (
                    <>
                      <CheckCircle2 className="w-4 h-4 text-obsidian" />
                      Mark Topic Completed
                    </>
                  )}
                </Button>
                <Button
                  onClick={() => setSelectedNode(null)}
                  variant="outline"
                  className="w-full py-6 font-black text-xs uppercase tracking-widest"
                >
                  Close
                </Button>
              </div>
            </MotionDiv>
          </>
        )}
      </AnimatePresenceComponent>
    </div>
  );
}

