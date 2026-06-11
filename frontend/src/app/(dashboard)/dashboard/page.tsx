"use client";

import React from "react";
import { useAuth } from "@/hooks/useAuth";
import {
  Code,
  Flame,
  Clock,
  Sparkles,
  BookOpen,
  ArrowUpRight,
  TrendingUp,
} from "lucide-react";
import Link from "next/link";
import { ROUTES } from "@/lib/constants";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import dynamic from "next/dynamic";
const SkillOrb = dynamic(() => import("@/components/three/SkillOrb"), { ssr: false });

export default function DashboardPage() {
  const { user } = useAuth();

  const stats = [
    {
      name: "Code Reviews",
      value: "12",
      change: "+3 this week",
      icon: Code,
      variant: "primary" as const, // Indigo
    },
    {
      name: "DSA Solved",
      value: "34",
      change: "+5 this week",
      icon: BookOpen,
      variant: "teal" as const, // Teal
    },
    {
      name: "Daily Streak",
      value: "5 days",
      change: "Active today",
      icon: Flame,
      variant: "secondary" as const, // Violet
    },
    {
      name: "Interviews Done",
      value: "4 sessions",
      change: "Avg score: 85%",
      icon: Sparkles,
      variant: "danger" as const, // Rose
    },
  ];

  const recentReviews = [
    {
      id: "1",
      title: "Binary Search Implementation",
      language: "Python",
      status: "Completed",
      score: 92,
      date: "2 hours ago",
    },
    {
      id: "2",
      title: "Express JWT Middleware Auth",
      language: "JavaScript",
      status: "Completed",
      score: 84,
      date: "Yesterday",
    },
    {
      id: "3",
      title: "Heap Min-Priority Queue",
      language: "C++",
      status: "Under Review",
      score: null,
      date: "2 days ago",
    },
  ];

  return (
    <div className="space-y-8">
      
      {/* Welcome Header */}
      <div className="space-y-1">
        <h1 className="text-3xl font-black font-display tracking-tight text-foreground sm:text-4xl">
          WELCOME BACK,{" "}
          <span className="text-aether-grad">
            {user?.profile?.first_name || user?.email.split("@")[0] || "DEVELOPER"}
          </span>{" "}
          👋
        </h1>
        <p className="text-xs sm:text-sm text-[#8892B0] font-black uppercase tracking-widest">
          Ready to level up your engineering skills today? Here is your learning overview.
        </p>
      </div>

      {/* Grid Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.name} hoverable glow>
              <div className="flex items-center justify-between">
                <span className="text-[9px] font-black uppercase tracking-widest text-[#8892B0]">
                  {item.name}
                </span>
                <Badge variant={item.variant}>
                  <Icon className="w-3.5 h-3.5" />
                </Badge>
              </div>
              <div className="mt-4">
                <span className="text-2xl font-black tracking-tight text-foreground">
                  {item.value}
                </span>
                <p className="mt-1.5 text-[9px] text-[#8892B0] flex items-center gap-1 font-black uppercase tracking-wider">
                  <TrendingUp className="w-3 h-3 text-aether-teal" />
                  {item.change}
                </p>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Main Workspace content */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        
        {/* Recent Code Reviews */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between px-1">
            <h3 className="text-xs font-black uppercase tracking-widest text-[#8892B0]">
              Recent Code Reviews
            </h3>
            <Link
              href={ROUTES.REVIEW}
              className="text-xs font-black uppercase tracking-widest text-aether-teal hover:text-aether-teal/80 flex items-center gap-1 group transition-colors"
            >
              New Review
              <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </Link>
          </div>

          <Card className="p-0 overflow-hidden">
            <ul role="list" className="divide-y divide-aether">
              {recentReviews.map((review) => (
                <li
                  key={review.id}
                  className="flex items-center justify-between gap-x-6 px-6 py-5 hover:bg-obsidian-depth/30 transition-colors"
                >
                  <div className="min-w-0">
                    <div className="flex items-center gap-x-3">
                      <p className="text-sm font-extrabold leading-6 text-foreground">
                        {review.title}
                      </p>
                      <Badge variant="primary">
                        {review.language}
                      </Badge>
                    </div>
                    <div className="mt-1 flex items-center gap-x-2 text-[9px] font-black uppercase tracking-wider text-[#8892B0]">
                      <Clock className="w-3.5 h-3.5" />
                      <p>{review.date}</p>
                    </div>
                  </div>
                  <div className="flex flex-none items-center gap-x-4">
                    {review.score !== null ? (
                      <div className="text-right">
                        <span className="text-[10px] font-black uppercase tracking-widest text-foreground">
                          Score: {review.score}/100
                        </span>
                        <div className="w-24 bg-obsidian-depth h-1.5 rounded-full mt-1.5 overflow-hidden border border-aether">
                          <div
                            className="bg-gradient-to-r from-aether-indigo to-aether-teal h-1.5 rounded-full shadow-[0_0_10px_rgba(91,108,249,0.3)]"
                            style={{ width: `${review.score}%` }}
                          />
                        </div>
                      </div>
                    ) : (
                      <Badge variant="secondary" className="animate-pulse">
                        Analyzing
                      </Badge>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </Card>
        </div>

        {/* 3D skill orb & Insights */}
        <div className="space-y-6">
          <h3 className="text-xs font-black uppercase tracking-widest text-[#8892B0] px-1">
            Topic Mastery
          </h3>
          <Card className="flex flex-col items-center justify-center p-4 relative overflow-hidden">
            <div className="absolute top-3 left-4 text-[9px] font-black text-[#8892B0] uppercase tracking-widest z-10">
              3D Neural Skill Sphere
            </div>
            {/* 3D Skill Orb Canvas */}
            <SkillOrb mastery={76} />
            <div className="text-center mt-2 z-10">
              <span className="text-xl font-black text-foreground">76% Aggregate Mastery</span>
              <p className="text-[9px] text-[#8892B0] font-black uppercase tracking-widest mt-1">Sway matches cursor parallax</p>
            </div>
          </Card>

          <Card className="space-y-4">
            <div className="flex items-center gap-3">
              <Badge variant="secondary">
                <Sparkles className="w-4 h-4" />
              </Badge>
              <h4 className="font-extrabold text-foreground text-sm uppercase tracking-wider">
                Daily Insights
              </h4>
            </div>
            <p className="text-xs text-[#8892B0] leading-relaxed font-semibold">
              Based on your study profile, we recommend spending 15 minutes today solving the "Group Anagrams" DSA question. This will reinforce hash mapping concepts.
            </p>
            <div className="pt-2">
              <Link href={ROUTES.DSA} className="block w-full">
                <Button variant="outline" className="w-full">
                  Go to DSA Mentor
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
