"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { LogOut, User as UserIcon, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useUIStore } from "@/store/uiStore";

const MotionDiv = motion.div as any;

export default function Navbar() {
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const setCursorType = useUIStore((state) => state.setCursorType);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-aether bg-obsidian-depth/65 backdrop-blur-aether transition-all duration-300">
      <div className="flex h-16 items-center justify-between px-6">
        
        {/* Logo container */}
        <Link 
          href="/" 
          className="flex items-center gap-3 select-none"
          onMouseEnter={() => setCursorType("hover")}
          onMouseLeave={() => setCursorType("default")}
        >
          <MotionDiv 
            whileHover={{ scale: 1.05, rotate: 5 }}
            whileTap={{ scale: 0.95 }}
            className="bg-gradient-to-tr from-aether-indigo to-aether-violet p-2 rounded-xl text-white shadow-lg shadow-aether-indigo/20"
          >
            <Sparkles className="w-4.5 h-4.5" />
          </MotionDiv>
          <span className="text-lg font-black tracking-widest font-display text-foreground">
            CODEGURU <span className="bg-gradient-to-r from-aether-indigo via-aether-violet to-aether-teal bg-clip-text text-transparent">AI</span>
          </span>
        </Link>

        {/* Action controls */}
        <div className="flex items-center gap-4">
          
          {/* User actions / menu dropdown */}
          {user && (
            <div className="relative">
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                onMouseEnter={() => setCursorType("hover")}
                onMouseLeave={() => setCursorType("default")}
                className="flex items-center gap-2.5 p-1 rounded-full md:pr-4 md:pl-1 border border-aether bg-obsidian-depth/50 hover:bg-obsidian-layer hover:border-aether-indigo/45 transition-all focus:outline-none"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-aether-indigo to-aether-violet border border-white/10 flex items-center justify-center text-white font-black uppercase text-xs shadow-md">
                  {user.email.substring(0, 2)}
                </div>
                <span className="text-xs font-black tracking-wider uppercase text-slate-300 hidden md:block max-w-[150px] truncate">
                  {user.profile?.first_name || user.email.split("@")[0]}
                </span>
              </button>

              <AnimatePresence>
                {dropdownOpen && (
                  <>
                    {/* Overlay to close on tap */}
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setDropdownOpen(false)}
                    />
                    <MotionDiv
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 10, scale: 0.95 }}
                      transition={{ duration: 0.15 }}
                      className="absolute right-0 mt-2 w-56 rounded-2xl border border-aether bg-obsidian-layer p-2 shadow-2xl z-20 backdrop-blur-aether"
                    >
                      <div className="px-3 py-2.5 border-b border-aether text-[10px] text-muted-foreground font-black tracking-wider uppercase truncate">
                        {user.email}
                      </div>
                      <div className="pt-1.5 space-y-0.5">
                        <Link
                          href="/settings"
                          onClick={() => setDropdownOpen(false)}
                          onMouseEnter={() => setCursorType("hover")}
                          onMouseLeave={() => setCursorType("default")}
                          className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-black uppercase tracking-wider text-foreground hover:bg-obsidian-depth hover:text-aether-teal transition-colors text-left"
                        >
                          <UserIcon className="w-4 h-4 text-aether-teal" />
                          Settings
                        </Link>
                        <button
                          onClick={() => {
                            setDropdownOpen(false);
                            logout();
                          }}
                          onMouseEnter={() => setCursorType("hover")}
                          onMouseLeave={() => setCursorType("default")}
                          className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-black uppercase tracking-wider text-aether-rose hover:bg-aether-rose/10 transition-colors text-left"
                        >
                          <LogOut className="w-4 h-4" />
                          Sign Out
                        </button>
                      </div>
                    </MotionDiv>
                  </>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
