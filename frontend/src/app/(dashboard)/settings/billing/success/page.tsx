"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle2, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import api from "@/services/api";
import { useAuthStore } from "@/store/authStore";
import { User } from "@/types/user.types";

export default function BillingSuccessPage() {
  const router = useRouter();
  const { setUser } = useAuthStore();

  useEffect(() => {
    // Silent background reload of the user details to fetch updated subscription_tier
    const reloadUser = async () => {
      try {
        const response = await api.get<User>("/users/me");
        setUser(response.data);
      } catch (err) {
        console.error("Failed to reload user after billing success:", err);
      }
    };
    reloadUser();
  }, [setUser]);

  const handleReturn = () => {
    router.push("/settings");
  };

  return (
    <div className="min-h-[60vh] flex items-center justify-center p-4">
      <Card glow className="max-w-md w-full bg-obsidian-layer/20 border border-aether-emerald/35">
        <CardContent className="p-8 text-center flex flex-col items-center gap-6">
          <div className="w-16 h-16 bg-aether-emerald/10 text-aether-emerald border border-aether-emerald/25 rounded-2xl flex items-center justify-center animate-bounce-slow shadow-[0_0_15px_rgba(52,211,153,0.15)]">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          
          <div className="space-y-2">
            <span className="text-[10px] text-aether-emerald font-black uppercase tracking-widest">Upgrade Successful</span>
            <h1 className="text-2xl font-black font-display text-foreground tracking-tight uppercase">Welcome to Pro Tier!</h1>
            <p className="text-xs sm:text-sm text-secondary font-medium leading-relaxed max-w-xs mx-auto">
              Your payment has been processed successfully. Premium access to all CodeGuru modules has been unlocked on your account.
            </p>
          </div>

          <Button
            onClick={handleReturn}
            variant="primary"
            className="w-full h-12 font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2 mt-4"
          >
            Go to Settings Console <ArrowRight className="w-4 h-4 text-obsidian" />
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
