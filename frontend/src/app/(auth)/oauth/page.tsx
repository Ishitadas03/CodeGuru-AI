"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useAuth } from "@/hooks/useAuth";
import { Loader2, AlertCircle, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

function OAuthCallbackHandler() {
  const { googleLogin } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check query parameters and hash fragment
    const searchParams = new URLSearchParams(window.location.search);
    const hashParams = new URLSearchParams(window.location.hash.substring(1));

    const token =
      searchParams.get("access_token") ||
      searchParams.get("token") ||
      searchParams.get("code") ||
      hashParams.get("access_token") ||
      hashParams.get("token") ||
      hashParams.get("code");

    const urlError = searchParams.get("error") || hashParams.get("error");

    if (urlError) {
      setError(`OAuth Authorization Error: ${urlError}`);
      return;
    }

    if (!token) {
      setError("No authorization token was found in the redirect URI.");
      return;
    }

    // Perform login with retrieved token
    const performLogin = async () => {
      try {
        await googleLogin(token);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Authentication with Google failed.");
      }
    };

    performLogin();
  }, [googleLogin]);

  if (error) {
    return (
      <div className="space-y-6 text-center">
        <div className="flex flex-col items-center justify-center space-y-3 p-6 border border-aether-rose/30 bg-aether-rose/5 rounded-2xl">
          <AlertCircle className="w-10 h-10 text-aether-rose animate-bounce" />
          <h2 className="text-sm font-black uppercase tracking-widest text-foreground">Authentication Failed</h2>
          <p className="text-xs text-muted-foreground font-semibold leading-relaxed max-w-sm">
            {error}
          </p>
        </div>
        <Link href="/login" passHref>
          <Button variant="outline" className="w-full h-12 flex items-center justify-center gap-2 rounded-xl text-[10px] font-black uppercase tracking-widest">
            <ArrowLeft className="w-4 h-4" /> Return to Login
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-center py-8">
      <div className="flex flex-col items-center justify-center space-y-4">
        <div className="relative flex items-center justify-center">
          <Loader2 className="w-12 h-12 text-aether-indigo animate-spin" />
          <div className="absolute w-6 h-6 rounded-full bg-aether-indigo/15 animate-ping" />
        </div>
        <div className="space-y-2">
          <h2 className="text-sm font-black uppercase tracking-widest text-foreground">Connecting Identity</h2>
          <p className="text-xs text-muted-foreground font-semibold">
            Please wait while we verify your Google credentials with the secure gateway...
          </p>
        </div>
      </div>
    </div>
  );
}

export default function OAuthCallbackPage() {
  return (
    <Suspense fallback={
      <div className="space-y-6 text-center py-8">
        <div className="flex flex-col items-center justify-center space-y-4">
          <Loader2 className="w-12 h-12 text-aether-indigo animate-spin" />
          <h2 className="text-sm font-black uppercase tracking-widest text-foreground">Loading Security Context...</h2>
        </div>
      </div>
    }>
      <OAuthCallbackHandler />
    </Suspense>
  );
}
