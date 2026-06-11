"use client";

import React from "react";
import dynamic from "next/dynamic";
const NeuralNetwork = dynamic(() => import("@/components/three/NeuralNetwork"), { ssr: false });
import { Sparkles } from "lucide-react";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex bg-obsidian relative overflow-hidden font-sans">
      
      {/* Left panel: 3D scene (Hidden on mobile) */}
      <div className="hidden lg:flex lg:w-[58%] relative h-screen flex-col justify-between p-12 border-r border-aether bg-[#060814]">
        {/* Glow ambient */}
        <div className="absolute top-1/3 left-1/3 w-96 h-96 bg-aether-indigo/5 rounded-full blur-[140px]" />
        
        {/* Logo tag */}
        <div className="flex items-center gap-3 relative z-10 select-none">
          <div className="bg-gradient-to-tr from-aether-indigo to-aether-violet p-2.5 rounded-xl text-white shadow-lg shadow-aether-indigo/25">
            <Sparkles className="w-5 h-5" />
          </div>
          <span className="text-lg font-black tracking-widest font-display text-foreground">
            CODEGURU <span className="bg-gradient-to-r from-aether-indigo via-aether-violet to-aether-teal bg-clip-text text-transparent">AI</span>
          </span>
        </div>

        {/* Floating background neural canvas */}
        <NeuralNetwork />

        {/* Footnote text */}
        <div className="relative z-10">
          <h2 className="text-3xl font-black font-display text-foreground tracking-tight max-w-md leading-tight">
            ACCELERATE YOUR SOFTWARE ENGINEERING LEARNING.
          </h2>
          <p className="text-xs text-muted-foreground font-black uppercase tracking-widest mt-4">
            Powered by GPT-4o, LangChain, & Async Executions.
          </p>
        </div>
      </div>

      {/* Right panel: Form host */}
      <div className="w-full lg:w-[42%] flex flex-col justify-center items-center p-6 sm:p-12 bg-obsidian-depth relative h-screen overflow-y-auto">
        {/* Grid Overlay */}
        <div className="absolute inset-0 dot-grid opacity-25 pointer-events-none" />
        
        {/* Ambient glow */}
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-aether-violet/5 rounded-full blur-[120px] pointer-events-none" />

        <div className="w-full max-w-md relative z-10">
          {children}
        </div>
      </div>
    </div>
  );
}
