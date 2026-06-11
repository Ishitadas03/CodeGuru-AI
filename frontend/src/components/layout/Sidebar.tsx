"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ROUTES } from "@/lib/constants";
import {
  LayoutDashboard,
  Code2,
  BookOpen,
  MessageSquare,
  Map,
  BarChart2,
  FileText,
  Settings,
} from "lucide-react";
import { motion } from "framer-motion";
import { useUIStore } from "@/store/uiStore";

const MotionDiv = motion.div as any;

export default function Sidebar() {
  const pathname = usePathname();
  const setCursorType = useUIStore((state) => state.setCursorType);

  const navigation = [
    { name: "Dashboard", href: ROUTES.DASHBOARD, icon: LayoutDashboard },
    { name: "Code Review", href: ROUTES.REVIEW, icon: Code2 },
    { name: "DSA Mentor", href: ROUTES.DSA, icon: BookOpen },
    { name: "Interviews", href: ROUTES.INTERVIEW, icon: MessageSquare },
    { name: "Roadmap", href: ROUTES.ROADMAP, icon: Map },
    { name: "Analytics", href: ROUTES.ANALYTICS, icon: BarChart2 },
    { name: "Documents", href: ROUTES.DOCUMENTS, icon: FileText },
    { name: "Settings", href: ROUTES.SETTINGS, icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-aether bg-obsidian-depth/30 backdrop-blur-aether hidden md:flex flex-col h-[calc(100vh-4rem)] sticky top-16">
      <div className="flex-1 py-6 px-4 space-y-1.5 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              onMouseEnter={() => setCursorType("hover")}
              onMouseLeave={() => setCursorType("default")}
              className={`group flex items-center gap-3 px-4.5 py-3 text-xs font-black uppercase tracking-wider rounded-xl transition-all relative overflow-hidden ${
                isActive
                  ? "text-aether-teal font-black"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {/* Animated capsule background */}
              {isActive && (
                <MotionDiv
                  layoutId="active-sidebar-nav"
                  className="absolute inset-0 bg-aether-indigo/5 border-l-2 border-aether-indigo z-0"
                  initial={false}
                  transition={{ type: "spring", stiffness: 380, damping: 30 }}
                />
              )}

              {/* Icon and label */}
              <div className="flex items-center gap-3 z-10 relative">
                <Icon 
                  className={`w-4.5 h-4.5 group-hover:scale-105 transition-transform ${
                    isActive 
                      ? "text-aether-teal" 
                      : "text-muted-foreground/60 group-hover:text-aether-teal/70"
                  }`} 
                />
                <span className="tracking-widest">{item.name}</span>
              </div>
            </Link>
          );
        })}
      </div>
    </aside>
  );
}
