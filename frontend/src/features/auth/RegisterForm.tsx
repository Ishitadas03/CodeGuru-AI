"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useAuth } from "@/hooks/useAuth";
import { registerSchema, RegisterRequest } from "@/schemas/auth";
import { ROUTES } from "@/lib/constants";
import { Loader2, ArrowRight, Eye, EyeOff, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

const MotionDiv = motion.div as any;

export default function RegisterForm() {
  const { register: signup, isRegistering, registerError } = useAuth();
  const [success, setSuccess] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register: formRegister,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterRequest>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterRequest) => {
    try {
      await signup(data);
      setSuccess(true);
    } catch (e) {
      // Error handled by hook
    }
  };

  if (success) {
    return (
      <MotionDiv
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center py-6 space-y-5"
      >
        <div className="inline-flex bg-aether-emerald/10 border border-aether-emerald/20 text-aether-emerald p-4 rounded-full animate-bounce shadow-lg shadow-aether-emerald/10">
          <CheckCircle2 className="w-10 h-10" />
        </div>
        <h3 className="text-xl font-black font-display tracking-wide text-foreground">REGISTRATION SUCCESSFUL!</h3>
        <p className="text-xs text-muted-foreground font-semibold leading-relaxed">
          Your CodeGuru AI account has been created. You are ready to log in and start learning.
        </p>
        <div className="pt-4">
          <Link href={ROUTES.LOGIN} className="block w-full">
            <Button className="w-full">
              Go to Sign In <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </MotionDiv>
    );
  }

  return (
    <MotionDiv
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div className="space-y-2 text-center lg:text-left">
        <h2 className="text-3xl font-black font-display tracking-tight text-foreground">
          CREATE ACCOUNT
        </h2>
        <p className="text-[10px] text-muted-foreground font-black uppercase tracking-widest">
          Or{" "}
          <Link href={ROUTES.LOGIN} className="text-aether-indigo hover:underline underline-offset-4">
            sign in to your existing account
          </Link>
        </p>
      </div>

      <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
        {registerError && (
          <div className="bg-aether-rose/10 border border-aether-rose/30 text-aether-rose p-3.5 rounded-xl text-xs font-semibold text-center shadow-[0_0_15px_rgba(244,114,182,0.1)]">
            {(registerError as any)?.response?.data?.detail || "Email already registered."}
          </div>
        )}

        <div className="space-y-1.5">
          <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground block">
            Email Address
          </label>
          <input
            type="email"
            disabled={isRegistering}
            {...formRegister("email")}
            placeholder="you@example.com"
            className={`flex h-11 w-full rounded-xl border ${
              errors.email ? "border-aether-rose/50 focus:ring-aether-rose/15" : "border-input focus:border-aether-indigo focus:ring-aether-indigo/15"
            } bg-obsidian-depth px-4 py-3 text-sm font-semibold text-foreground placeholder:text-muted-foreground/60 focus-visible:outline-none focus-visible:ring-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-300`}
          />
          {errors.email && (
            <p className="text-[10px] text-aether-rose font-black uppercase tracking-wider">{errors.email.message}</p>
          )}
        </div>

        <div className="space-y-1.5">
          <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground block">
            Password
          </label>
          <div className="relative">
            <input
              type={showPassword ? "text" : "password"}
              disabled={isRegistering}
              {...formRegister("password")}
              placeholder="••••••••"
              className={`flex h-11 w-full rounded-xl border ${
                errors.password ? "border-aether-rose/50 focus:ring-aether-rose/15" : "border-input focus:border-aether-indigo focus:ring-aether-indigo/15"
              } bg-obsidian-depth px-4 py-3 pr-10 text-sm font-semibold text-foreground placeholder:text-muted-foreground/60 focus-visible:outline-none focus-visible:ring-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-300`}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-aether-indigo transition-colors"
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {errors.password && (
            <p className="text-[10px] text-aether-rose font-black uppercase tracking-wider">{errors.password.message}</p>
          )}
        </div>

        <div className="pt-3">
          <Button
            type="submit"
            disabled={isRegistering}
            className="w-full flex justify-center items-center gap-2"
          >
            {isRegistering ? (
              <Loader2 className="w-4.5 h-4.5 animate-spin" />
            ) : (
              <>
                Create Account <ArrowRight className="w-4 h-4" />
              </>
            )}
          </Button>
        </div>
      </form>
    </MotionDiv>
  );
}
