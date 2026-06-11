"use client";

import React from "react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";

export default function OAuthButtons() {
  const { googleLogin, isLoggingInWithGoogle } = useAuth();

  const handleGoogleMockLogin = async () => {
    try {
      const mockEmail = `oauth_${Math.floor(Math.random() * 10000)}`;
      await googleLogin(`mock_google_token_${mockEmail}`);
    } catch (e) {
      // Handled by react-query error state
    }
  };

  return (
    <div className="w-full">
      {/* Futuristic Coding GIF Core */}
      <div className="w-full flex justify-center mb-6">
        <div className="w-full h-28 rounded-2xl border border-aether-indigo/15 bg-obsidian-layer/40 overflow-hidden relative group shadow-[0_0_15px_rgba(91,108,249,0.03)] hover:border-aether-indigo/30 hover:shadow-[0_0_20px_rgba(91,108,249,0.06)] transition-all duration-300">
          <img 
            src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExaDhkbDNyaTU2OTh3andkeDl4c25nZWt4bHQ4bjFidXJhNjFhbWp5YSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26tn33aiTi1jkl6H6/giphy.gif" 
            alt="Neural Coding Core" 
            className="w-full h-full object-cover opacity-35 group-hover:opacity-50 transition-opacity duration-300 filter hue-rotate-[200deg] saturate-150 scale-105 group-hover:scale-100 transition-transform duration-700"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-obsidian-depth via-transparent to-transparent pointer-events-none" />
          <div className="absolute bottom-2.5 left-4 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-aether-indigo animate-pulse shadow-[0_0_8px_#5B6CF9]" />
            <span className="text-[8px] font-black uppercase tracking-widest text-aether-indigo/70">Neural Compilation Stream Active</span>
          </div>
        </div>
      </div>

      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-aether-indigo/10" />
        </div>
        <div className="relative flex justify-center text-[9px] uppercase font-black tracking-widest">
          <span className="px-3 bg-obsidian-depth text-muted-foreground">
            Or Connect With
          </span>
        </div>
      </div>

      <Button
        variant="outline"
        type="button"
        onClick={handleGoogleMockLogin}
        disabled={isLoggingInWithGoogle}
        className="w-full h-12 flex items-center justify-center gap-2.5 rounded-xl text-[10px] font-black uppercase tracking-wider transition-all"
      >
        <svg className="w-4.5 h-4.5" viewBox="0 0 24 24">
          <path
            fill="currentColor"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          />
          <path
            fill="currentColor"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          />
          <path
            fill="currentColor"
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
          />
          <path
            fill="currentColor"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
          />
        </svg>
        Google Identity Portal
      </Button>
    </div>
  );
}
