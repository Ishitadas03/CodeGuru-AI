"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useAuth } from "@/hooks/useAuth";
import { loginSchema, LoginRequest } from "@/schemas/auth";
import { ROUTES } from "@/lib/constants";
import { Loader2, ArrowRight, Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

const MotionDiv = motion.div as any;

export default function LoginForm() {
  const { login, isLoggingIn, loginError } = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginRequest>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginRequest) => {
    try {
      await login(data);
    } catch (e) {
      // Handled by react-query error state
    }
  };

  return (
    <MotionDiv
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div className="space-y-2 text-center lg:text-left">
        <h2 className="text-3xl font-black font-display tracking-tight text-foreground">
          WELCOME BACK
        </h2>
        <p className="text-[10px] text-muted-foreground font-black uppercase tracking-widest">
          Or{" "}
          <Link href={ROUTES.REGISTER} className="text-aether-indigo hover:underline underline-offset-4">
            create a new account
          </Link>
        </p>
      </div>

      <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
        {loginError && (
          <div className="bg-aether-rose/10 border border-aether-rose/30 text-aether-rose p-3.5 rounded-xl text-xs font-semibold text-center shadow-[0_0_15px_rgba(244,114,182,0.1)]">
            {(loginError as any)?.response?.data?.detail || "Invalid email or password."}
          </div>
        )}

        <div className="space-y-1.5">
          <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground block">
            Email Address
          </label>
          <input
            type="email"
            disabled={isLoggingIn}
            {...register("email")}
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
              disabled={isLoggingIn}
              {...register("password")}
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
            disabled={isLoggingIn}
            className="w-full flex justify-center items-center gap-2"
          >
            {isLoggingIn ? (
              <Loader2 className="w-4.5 h-4.5 animate-spin" />
            ) : (
              <>
                Sign In <ArrowRight className="w-4 h-4" />
              </>
            )}
          </Button>
        </div>
      </form>
    </MotionDiv>
  );
}
