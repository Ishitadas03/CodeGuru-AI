"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  FileText,
  Search,
  BookOpen,
  Calendar,
  Clock,
  Bookmark,
  Sparkles,
  Tag,
  PenTool,
  Save,
  CheckCircle2,
  ArrowLeft,
  Plus,
} from "lucide-react";

const MotionDiv = motion.div as any;
const AnimatePresenceComponent = AnimatePresence as any;

interface DocumentItem {
  id: string;
  title: string;
  category: "cheat-sheet" | "interview-guide" | "best-practices" | "notes";
  summary: string;
  content: string;
  readTime: string;
  lastUpdated: string;
  tags: string[];
  isBookmarked: boolean;
}

const INITIAL_DOCUMENTS: DocumentItem[] = [
  {
    id: "doc-1",
    title: "System Design Latency & Scale Cheat Sheet",
    category: "cheat-sheet",
    summary: "The ultimate resource containing absolute latency numbers every engineer should know, storage sizing calculations, and caching decisions.",
    readTime: "5 min read",
    lastUpdated: "June 2026",
    tags: ["system-design", "scalability", "architecture"],
    isBookmarked: true,
    content: `### Latency Numbers Every Programmer Should Know
* **L1 cache reference**: 0.5 ns
* **Branch misprediction**: 5 ns
* **L2 cache reference**: 7 ns
* **Mutex lock/unlock**: 25 ns
* **Main memory reference (RAM)**: 100 ns
* **Compress 1K bytes with Zippy**: 3,000 ns (3 µs)
* **Send 1K bytes over 1 Gbps network**: 10,050 ns (10 µs)
* **Read 4K randomly from SSD**: 150,000 ns (150 µs)
* **Read 1 MB sequentially from memory**: 250,000 ns (250 µs)
* **Round trip within same datacenter**: 500,000 ns (500 µs)
* **SSD sequential read**: 1,000,000 ns (1 ms)
* **Disk seek (HDD)**: 10,000,000 ns (10 ms)
* **Read 1 MB sequentially from disk**: 20,000,000 ns (20 ms)
* **Send packet California to Netherlands**: 150,000,000 ns (150 ms)

---

### Database Availability vs Consistency (CAP Theorem)
* **Consistency (C)**: Every read receives the most recent write or an error.
* **Availability (A)**: Every non-failing node returns a non-error response for any request (without guarantee that it contains the most recent write).
* **Partition Tolerance (P)**: The system continues to operate despite an arbitrary number of messages being dropped or delayed by the network between nodes.

> **Trade-off Rule**: In a distributed system, network partitions (P) are inevitable. Therefore, you must choose between Consistency (CP) or Availability (AP).`
  },
  {
    id: "doc-2",
    title: "Next.js 15 & React 19 Quick Reference",
    category: "cheat-sheet",
    summary: "A practical developer reference guide explaining React Server Components (RSC), server actions, client state hooks, and Next.js compiler caching.",
    readTime: "7 min read",
    lastUpdated: "May 2026",
    tags: ["react-19", "nextjs-15", "frontend"],
    isBookmarked: false,
    content: `### React Server Components (RSC) vs Client Components
* **Server Components (Default)**: Fetch data directly inside async components. Smaller bundle size since dependencies stay on the server.
* **Client Components (\`"use client"\`)**: Handle user interactions (useState, useEffect, event listeners).

---

### Server Actions
Execute database modifications directly in form handlers without building separate REST API endpoints.
\`\`\`typescript
// src/app/actions.ts
"use server";

export async function submitComment(formData: FormData) {
  const comment = formData.get("comment");
  // Save directly to database
  await db.saveComment(comment);
}
\`\`\`

---

### React 19 Hooks Cheat Sheet
* **useActionState**: Tracks loading, action callbacks, and state data return.
* **useFormStatus**: Accesses parent form state (pending, method, action).
* **use**: Resolves Promises or Context dynamically inside loops or conditions.`
  },
  {
    id: "doc-3",
    title: "FastAPI Production-Grade Bootstrap Checklist",
    category: "best-practices",
    summary: "Complete blueprint for building secure, scalable FastAPI apps, covering async connection pools, correlations, rate limiting, and structured logging.",
    readTime: "10 min read",
    lastUpdated: "June 2026",
    tags: ["fastapi", "python", "backend"],
    isBookmarked: true,
    content: `### 1. Database Connection Management
Always configure the connection pool and pre-ping parameters when using an async engine to handle connection lifecycles:
\`\`\`python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connection is alive before routing queries
    pool_size=20,            # Standard connection pool size
    max_overflow=10,         # Allow burst connections under high load
)
\`\`\`

---

### 2. Structured JSON Logging Middleware
Standardize request tracing by generating correlation IDs and logging them in JSON formatting:
\`\`\`python
import time
import uuid
from fastapi import Request
from python_json_logger import jsonlogger

# In middleware:
correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
# Log as JSON to stdout for log aggregators (Elasticsearch, Loki)
\`\`\`

---

### 3. Rate Limiting Guidelines
Apply slowapi or Redis token buckets to prevent server resource starvation on CPU-intensive routes (like AI generation or authentication).`
  },
  {
    id: "doc-4",
    title: "Cracking the Coding Interview: DSA Topic Blueprint",
    category: "interview-guide",
    summary: "Syllabus outlines and optimal approaches for Arrays, Two Pointers, Sliding Windows, LinkedLists, Binary Trees, and Backtracking.",
    readTime: "12 min read",
    lastUpdated: "April 2026",
    tags: ["dsa", "algorithms", "interviews"],
    isBookmarked: false,
    content: `### 1. Two Pointers Pattern
* **Core Idea**: Initialize two markers at opposite boundaries or at the same start point, moving them toward each other based on comparison rules.
* **Ideal for**: Sorted arrays, reversing strings, finding target triplets.
* **Complexity**: Reduces O(N^2) searches to O(N) linear time.

---

### 2. Sliding Window Pattern
* **Core Idea**: Maintain a sub-segment (window) of data, expanding or shrinking its boundaries based on state constraints.
* **Ideal for**: Longest substring without repeating characters, subarray sums.
* **Complexity**: O(N) linear scan instead of redundant sub-scans.

---

### 3. Binary Tree Traversals
* **In-Order**: Left -> Root -> Right (Produces sorted order in Binary Search Trees)
* **Pre-Order**: Root -> Left -> Right (Ideal for copying tree structures)
* **Post-Order**: Left -> Right -> Root (Ideal for deleting nodes or bottom-up evaluations)`
  }
];

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>(INITIAL_DOCUMENTS);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);

  // Note Creator State
  const [isCreatingNote, setIsCreatingNote] = useState(false);
  const [newNoteTitle, setNewNoteTitle] = useState("");
  const [newNoteContent, setNewNoteContent] = useState("");
  const [newNoteTags, setNewNoteTags] = useState("");
  const [saveSuccess, setSaveSuccess] = useState(false);

  const toggleBookmark = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDocuments((prev) =>
      prev.map((doc) => (doc.id === id ? { ...doc, isBookmarked: !doc.isBookmarked } : doc))
    );
  };

  const handleCreateNoteSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNoteTitle.trim() || !newNoteContent.trim()) return;

    const newDoc: DocumentItem = {
      id: `custom-note-${Date.now()}`,
      title: newNoteTitle,
      category: "notes",
      summary: newNoteContent.substring(0, 100) + (newNoteContent.length > 100 ? "..." : ""),
      content: newNoteContent,
      readTime: `${Math.max(1, Math.round(newNoteContent.split(" ").length / 200))} min read`,
      lastUpdated: "Just Now",
      tags: newNoteTags
        .split(",")
        .map((tag) => tag.trim())
        .filter((tag) => tag.length > 0),
      isBookmarked: false,
    };

    setDocuments((prev) => [newDoc, ...prev]);
    setSaveSuccess(true);
    setTimeout(() => {
      setSaveSuccess(false);
      setIsCreatingNote(false);
      setNewNoteTitle("");
      setNewNoteContent("");
      setNewNoteTags("");
    }, 1500);
  };

  // Filter documents based on search and category
  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch =
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesCategory =
      activeCategory === "all" ||
      (activeCategory === "bookmarked" && doc.isBookmarked) ||
      doc.category === activeCategory;

    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div className="space-y-1.5">
          <h1 className="text-3xl font-extrabold tracking-tight font-display text-aether-grad">
            Notes & Resources
          </h1>
          <p className="text-xs sm:text-sm text-[#8892B0] font-black uppercase tracking-widest">
            Browse language references, system design formulas, algorithm cheat sheets, or draft study notes.
          </p>
        </div>
        {!isCreatingNote && (
          <MotionDiv whileHover={{ y: -2 }} whileTap={{ scale: 0.98 }}>
            <Button
              onClick={() => setIsCreatingNote(true)}
              variant="primary"
              className="w-full sm:w-auto h-11 px-5 font-black text-xs uppercase tracking-widest flex items-center gap-2 shadow-[0_0_15px_rgba(91,108,249,0.2)]"
            >
              <Plus className="w-4 h-4 text-white" />
              Create Study Note
            </Button>
          </MotionDiv>
        )}
      </div>

      <AnimatePresenceComponent mode="wait">
        {isCreatingNote ? (
          // Markdown Note Creator Form
          <MotionDiv
            key="creator"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="w-full"
          >
            <Card glow>
              <CardContent className="p-6 md:p-8 space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="bg-aether-indigo/10 text-aether-indigo p-2.5 rounded-lg border border-aether">
                      <PenTool className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-black text-sm uppercase tracking-widest text-foreground font-display">
                        New Developer Note
                      </h3>
                      <p className="text-[8px] text-[#8892B0]/80 font-black uppercase tracking-widest">
                        Draft personalized revision files
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setIsCreatingNote(false)}
                    className="text-[9px] font-black uppercase tracking-widest text-[#8892B0] hover:text-aether-teal transition-colors"
                  >
                    Cancel
                  </button>
                </div>

                <form onSubmit={handleCreateNoteSubmit} className="space-y-5">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div className="space-y-2">
                      <label className="text-[9px] font-black text-[#8892B0] uppercase tracking-widest block">
                        Note Title
                      </label>
                      <Input
                        type="text"
                        placeholder="e.g., GraphQL API Design Best Practices"
                        value={newNoteTitle}
                        onChange={(e) => setNewNoteTitle(e.target.value)}
                        required
                        className="w-full font-semibold border-aether bg-obsidian-depth"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[9px] font-black text-[#8892B0] uppercase tracking-widest block">
                        Tags (Comma Separated)
                      </label>
                      <Input
                        type="text"
                        placeholder="e.g., graphql, api-design, web-scaling"
                        value={newNoteTags}
                        onChange={(e) => setNewNoteTags(e.target.value)}
                        className="w-full font-semibold border-aether bg-obsidian-depth"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between items-center text-[9px] font-black text-[#8892B0] uppercase tracking-widest">
                      <span>Note Body Content (Markdown Supported)</span>
                      <span className="text-[8px] text-[#8892B0] font-semibold normal-case">Use headers (#), lists (*), or code (\`...\`)</span>
                    </div>
                    <textarea
                      placeholder="### My Study Notes..."
                      rows={12}
                      value={newNoteContent}
                      onChange={(e) => setNewNoteContent(e.target.value)}
                      required
                      className="w-full px-4 py-3 bg-obsidian-depth border border-aether rounded-xl text-sm outline-none focus:border-aether-indigo focus:ring-2 focus:ring-aether-indigo/15 text-foreground transition-all duration-300 font-mono leading-relaxed custom-scrollbar"
                    />
                  </div>

                  <div className="flex items-center gap-3 pt-2">
                    <MotionDiv whileTap={{ scale: 0.98 }}>
                      <Button
                        type="submit"
                        disabled={saveSuccess}
                        variant={saveSuccess ? "secondary" : "primary"}
                        className="h-11 px-6 font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2"
                      >
                        {saveSuccess ? (
                          <>
                            <CheckCircle2 className="w-4 h-4 animate-bounce text-foreground" /> Note Saved!
                          </>
                        ) : (
                          <>
                            <Save className="w-4 h-4 text-white" /> Save Note
                          </>
                        )}
                      </Button>
                    </MotionDiv>
                    <Button
                      type="button"
                      onClick={() => setIsCreatingNote(false)}
                      variant="outline"
                      className="h-11 px-6 font-black text-xs uppercase tracking-widest"
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </MotionDiv>
        ) : (
          // Main Documentation Hub
          <MotionDiv
            key="hub"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-6"
          >
            {/* Search & Category Filter */}
            <div className="flex flex-col lg:flex-row gap-4 items-center justify-between">
              {/* Category buttons */}
              <div className="flex items-center gap-2 overflow-x-auto w-full lg:w-auto pb-1.5 lg:pb-0 scrollbar-none custom-scrollbar">
                {[
                  { id: "all", name: "All Documents" },
                  { id: "cheat-sheet", name: "Cheat Sheets" },
                  { id: "interview-guide", name: "Guides" },
                  { id: "best-practices", name: "Best Practices" },
                  { id: "notes", name: "My Notes" },
                  { id: "bookmarked", name: "Bookmarked" },
                ].map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => setActiveCategory(cat.id)}
                    className={`px-4 py-2 rounded-full text-[9px] font-black uppercase tracking-widest transition-all border whitespace-nowrap ${
                      activeCategory === cat.id
                        ? "bg-aether-teal/10 border-aether-teal text-aether-teal shadow-[0_0_10px_rgba(34,211,238,0.15)]"
                        : "bg-obsidian-depth border border-aether text-[#8892B0] hover:bg-obsidian-depth hover:text-foreground hover:border-aether-indigo/25"
                    }`}
                  >
                    {cat.id === "bookmarked" && "⭐ "}{cat.name}
                  </button>
                ))}
              </div>

              {/* Search Box */}
              <div className="w-full lg:w-80">
                <Input
                  icon={<Search className="w-4 h-4 text-[#8892B0]" />}
                  type="text"
                  placeholder="Search materials or tags..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="font-semibold border-aether bg-obsidian-depth"
                />
              </div>
            </div>

            {/* Document grid listing */}
            {filteredDocuments.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {filteredDocuments.map((doc, idx) => (
                  <MotionDiv
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: idx * 0.04 }}
                    key={doc.id}
                    onClick={() => setSelectedDoc(doc)}
                    className="group"
                  >
                    <Card hoverable className="cursor-pointer h-full flex flex-col justify-between p-6">
                      <div className="space-y-4">
                        {/* Top bar info */}
                        <div className="flex justify-between items-start gap-4">
                          <Badge
                            variant={
                              doc.category === "cheat-sheet"
                                ? "danger" // rose
                                : doc.category === "interview-guide"
                                ? "secondary" // violet
                                : doc.category === "best-practices"
                                ? "success" // emerald
                                : "primary" // indigo
                            }
                            className="text-[8px]"
                          >
                            {doc.category.replace("-", " ")}
                          </Badge>
                          
                          {/* Bookmark Button */}
                          <button
                            onClick={(e) => toggleBookmark(doc.id, e)}
                            className={`p-1.5 rounded-lg transition-colors border ${
                              doc.isBookmarked
                                ? "bg-aether-teal/10 border-aether-teal/20 text-aether-teal"
                                : "border-transparent text-muted-foreground hover:text-aether-teal hover:bg-obsidian-depth"
                            }`}
                          >
                            <Bookmark className={`w-3.5 h-3.5 ${doc.isBookmarked ? "fill-aether-teal text-aether-teal" : ""}`} />
                          </button>
                        </div>

                        {/* Title & description */}
                        <div className="space-y-2">
                          <h4 className="font-extrabold text-foreground group-hover:text-aether-teal transition-colors leading-snug text-sm sm:text-base font-display">
                            {doc.title}
                          </h4>
                          <p className="text-xs text-secondary leading-relaxed line-clamp-2 font-semibold">
                            {doc.summary}
                          </p>
                        </div>
                      </div>

                      <div className="mt-5 pt-4 border-t border-aether flex flex-wrap items-center justify-between gap-3">
                        {/* Read metrics */}
                        <div className="flex items-center gap-3 text-[9px] text-muted-foreground font-black uppercase tracking-widest">
                          <span className="flex items-center gap-1.5">
                            <Clock className="w-3.5 h-3.5 text-aether-teal" /> {doc.readTime}
                          </span>
                          <span>•</span>
                          <span className="flex items-center gap-1.5">
                            <Calendar className="w-3.5 h-3.5 text-aether-teal" /> {doc.lastUpdated}
                          </span>
                        </div>

                        {/* Tags list */}
                        <div className="flex items-center gap-1.5 flex-wrap">
                          {doc.tags.slice(0, 2).map((tag, idx) => (
                            <Badge key={idx} variant="outline" className="text-[8px] flex items-center gap-1 border-aether">
                              <Tag className="w-2.5 h-2.5 text-aether-teal" />
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </Card>
                  </MotionDiv>
                ))}
              </div>
            ) : (
              <div className="h-96 flex flex-col items-center justify-center border border-dashed border-aether rounded-2xl bg-obsidian-depth/20 p-8 text-center gap-4">
                <div className="bg-aether-indigo/10 text-aether-indigo p-4 rounded-xl border border-aether shadow-[0_0_15px_rgba(91,108,249,0.15)]">
                  <FileText className="w-8 h-8 animate-pulse" />
                </div>
                <div className="space-y-1">
                  <h4 className="font-extrabold text-foreground uppercase tracking-widest text-xs font-display">No documentation found</h4>
                  <p className="text-xs text-[#8892B0] max-w-xs mx-auto font-semibold">
                    Try modifying your search query or select a different category filter above.
                  </p>
                </div>
              </div>
            )}
          </MotionDiv>
        )}
      </AnimatePresenceComponent>

      {/* Full-screen Reader Overlay Modal */}
      <AnimatePresenceComponent>
        {selectedDoc && (
          <>
            {/* Backdrop */}
            <MotionDiv
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.7 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedDoc(null)}
              className="fixed inset-0 bg-obsidian/85 z-40 backdrop-blur-md"
            />
            {/* Reader Card Modal */}
            <MotionDiv
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="fixed inset-x-4 md:inset-x-12 top-6 bottom-6 md:top-12 md:bottom-12 m-auto max-w-3xl bg-obsidian-depth border border-aether rounded-2xl z-50 shadow-2xl flex flex-col overflow-hidden backdrop-blur-aether"
            >
              {/* Header */}
              <div className="p-6 md:px-8 border-b border-aether flex items-center justify-between bg-obsidian-depth">
                <div className="flex items-center gap-3">
                  <MotionDiv whileTap={{ scale: 0.9 }}>
                    <Button
                      onClick={() => setSelectedDoc(null)}
                      variant="outline"
                      size="icon"
                      className="rounded-lg h-9 w-9"
                    >
                      <ArrowLeft className="w-4 h-4 text-aether-teal" />
                    </Button>
                  </MotionDiv>
                  <div>
                    <Badge variant="primary" className="text-[8px] py-0">
                      {selectedDoc.category.replace("-", " ")}
                    </Badge>
                    <h3 className="font-extrabold text-foreground truncate max-w-xs sm:max-w-md mt-1.5 text-sm sm:text-base tracking-tight font-display">
                      {selectedDoc.title}
                    </h3>
                  </div>
                </div>
                {/* Metrics */}
                <div className="flex items-center gap-3 text-[9px] text-[#8892B0] font-black uppercase tracking-widest flex-shrink-0">
                  <span className="hidden sm:flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-aether-teal" /> {selectedDoc.readTime}
                  </span>
                </div>
              </div>

              {/* Body Content */}
              <div className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 text-[#F0F4FF] font-semibold custom-scrollbar">
                <div className="text-xs sm:text-sm leading-relaxed whitespace-pre-line font-medium text-[#8892B0] prose prose-invert max-w-none">
                  {selectedDoc.content}
                </div>
              </div>

              {/* Footer */}
              <div className="p-6 md:px-8 border-t border-aether bg-obsidian-depth flex justify-between items-center gap-4">
                <div className="flex items-center gap-2 flex-wrap font-bold">
                  {selectedDoc.tags.map((tag, idx) => (
                    <Badge key={idx} variant="outline" className="text-[8px] border-aether">
                      <Tag className="w-2.5 h-2.5 text-aether-teal mr-1" />
                      {tag}
                    </Badge>
                  ))}
                </div>
                <Button
                  onClick={() => setSelectedDoc(null)}
                  variant="outline"
                  className="px-5 py-2.5 font-black text-xs uppercase tracking-widest rounded-xl"
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
