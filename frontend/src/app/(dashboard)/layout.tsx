"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";
import { Loader2 } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    // Check if store has already hydrated
    if (useAuthStore.persist.hasHydrated()) {
      setHydrated(true);
    } else {
      const unsub = useAuthStore.persist.onFinishHydration(() => {
        setHydrated(true);
      });
      return () => unsub();
    }
  }, []);

  useEffect(() => {
    if (!hydrated) return;

    if (!isAuthenticated) {
      router.replace("/login");
    } else {
      setLoading(false);
    }
  }, [hydrated, isAuthenticated, router]);

  if (loading || !isAuthenticated) {
    return (
      <div className="min-h-screen bg-obsidian flex flex-col items-center justify-center gap-4 text-white">
        {/* Glow ambient */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-aether-indigo/5 rounded-full blur-[100px]" />
        
        <Loader2 className="w-10 h-10 animate-spin text-aether-indigo relative z-10" />
        <p className="text-xs text-muted-foreground font-black uppercase tracking-widest animate-pulse relative z-10">
          Securing your session...
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-obsidian text-foreground transition-colors duration-200">
      {/* Grid Overlay */}
      <div className="absolute inset-0 dot-grid opacity-20 pointer-events-none z-0" />

      <Navbar />
      <div className="flex-1 flex overflow-hidden relative z-10">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-8 relative custom-scrollbar">
          <div className="max-w-6xl mx-auto space-y-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
