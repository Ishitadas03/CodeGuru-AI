"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, ArrowLeft } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function BillingCancelPage() {
  const router = useRouter();

  const handleReturn = () => {
    router.push("/settings");
  };

  return (
    <div className="min-h-[60vh] flex items-center justify-center p-4">
      <Card className="max-w-md w-full bg-obsidian-layer/20 border border-aether">
        <CardContent className="p-8 text-center flex flex-col items-center gap-6">
          <div className="w-16 h-16 bg-obsidian-depth text-[#8892B0] border border-aether rounded-2xl flex items-center justify-center">
            <AlertCircle className="w-8 h-8" />
          </div>
          
          <div className="space-y-2">
            <span className="text-[10px] text-muted-foreground font-black uppercase tracking-widest">Upgrade Cancelled</span>
            <h1 className="text-2xl font-black font-display text-foreground tracking-tight uppercase">Checkout Cancelled</h1>
            <p className="text-xs sm:text-sm text-secondary font-medium leading-relaxed max-w-xs mx-auto">
              Your transaction was cancelled. No charges were made, and your account remains on the Free plan.
            </p>
          </div>

          <Button
            onClick={handleReturn}
            className="w-full h-12 font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2 mt-4"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Settings
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
