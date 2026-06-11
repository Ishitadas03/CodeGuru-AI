"use client";

import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useTheme } from "next-themes";
import { useAuthStore } from "@/store/authStore";
import api from "@/services/api";
import { Profile } from "@/types/user.types";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Sparkles,
  Save,
  User as UserIcon,
  Tag,
  X,
  CheckCircle2,
  AlertCircle,
  Settings,
  Key,
  Laptop,
  Moon,
  Sun,
  Loader2,
  CreditCard,
  Zap,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const MotionDiv = motion.div as any;
const AnimatePresenceComponent = AnimatePresence as any;

// Form schemas for validation using Zod
const profileSchema = z.object({
  first_name: z.string().max(100, "First name must be under 100 characters").optional().nullable(),
  last_name: z.string().max(100, "Last name must be under 100 characters").optional().nullable(),
  bio: z.string().max(1000, "Bio must be under 1000 characters").optional().nullable(),
});

type ProfileFormValues = z.infer<typeof profileSchema>;

export default function SettingsPage() {
  const { user, setUser } = useAuthStore();
  const { theme, setTheme } = useTheme();

  // Tabs state
  const [activeTab, setActiveTab] = useState<"profile" | "preferences" | "api" | "billing">("profile");

  // Custom states
  const [skills, setSkills] = useState<string[]>([]);
  const [skillInput, setSkillInput] = useState("");
  const [status, setStatus] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const [isRedirecting, setIsRedirecting] = useState(false);

  // Client-side preferences state
  const [defaultLanguage, setDefaultLanguage] = useState("python");
  const [dailyReminders, setDailyReminders] = useState(true);
  const [openaiKeyOverride, setOpenaiKeyOverride] = useState("");
  const [ollamaBaseUrl, setOllamaBaseUrl] = useState("http://localhost:11434");

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      bio: "",
    },
  });

  // Load profile values and localStorage client preferences on mount
  useEffect(() => {
    if (user?.profile) {
      reset({
        first_name: user.profile.first_name || "",
        last_name: user.profile.last_name || "",
        bio: user.profile.bio || "",
      });
      setSkills(user.profile.skills || []);
    }

    // Load from local storage
    const storedLang = localStorage.getItem("codeguru_pref_lang");
    if (storedLang) setDefaultLanguage(storedLang);

    const storedReminders = localStorage.getItem("codeguru_pref_reminders");
    if (storedReminders !== null) setDailyReminders(storedReminders === "true");

    const storedApiKey = localStorage.getItem("codeguru_api_key_override");
    if (storedApiKey) setOpenaiKeyOverride(storedApiKey);

    const storedOllama = localStorage.getItem("codeguru_ollama_url");
    if (storedOllama) setOllamaBaseUrl(storedOllama);
  }, [user, reset]);

  // Handle form submission for Profile metadata
  const handleSaveProfile = async (values: ProfileFormValues) => {
    setStatus(null);
    try {
      const payload = {
        ...values,
        skills,
      };
      
      const response = await api.put<Profile>("/users/me/profile", payload);
      
      if (user) {
        setUser({
          ...user,
          profile: response.data,
        });
      }
      
      setStatus({
        type: "success",
        message: "Profile settings saved successfully!",
      });
    } catch (err: any) {
      setStatus({
        type: "error",
        message: err.response?.data?.detail || "Failed to update profile settings.",
      });
    }
  };

  // Handle client-side preferences save
  const handleSavePreferences = (e: React.FormEvent) => {
    e.preventDefault();
    setStatus(null);
    try {
      localStorage.setItem("codeguru_pref_lang", defaultLanguage);
      localStorage.setItem("codeguru_pref_reminders", String(dailyReminders));
      setStatus({
        type: "success",
        message: "Application preferences saved locally!",
      });
    } catch (err) {
      setStatus({
        type: "error",
        message: "Failed to save application preferences.",
      });
    }
  };

  // Handle API Key override save
  const handleSaveApiKeys = (e: React.FormEvent) => {
    e.preventDefault();
    setStatus(null);
    try {
      localStorage.setItem("codeguru_api_key_override", openaiKeyOverride);
      localStorage.setItem("codeguru_ollama_url", ollamaBaseUrl);
      setStatus({
        type: "success",
        message: "AI keys and endpoint configurations saved!",
      });
    } catch (err) {
      setStatus({
        type: "error",
        message: "Failed to configure LLM keys.",
      });
    }
  };

  const handleAddSkill = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanSkill = skillInput.trim().toLowerCase();
    if (cleanSkill && !skills.includes(cleanSkill)) {
      setSkills([...skills, cleanSkill]);
      setSkillInput("");
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    setSkills(skills.filter((s) => s !== skillToRemove));
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12 px-4">
      {/* Header */}
      <div className="space-y-1.5">
        <h1 className="text-3xl font-extrabold tracking-tight font-display text-aether-grad">
          Settings Console
        </h1>
        <p className="text-xs sm:text-sm text-secondary font-black uppercase tracking-widest">
          Configure credentials, visual settings, custom models, and user profile metadata.
        </p>
      </div>

      {/* Tabs Switcher */}
      <div className="flex border-b border-border gap-6">
        <button
          onClick={() => {
            setActiveTab("profile");
            setStatus(null);
          }}
          className={`pb-3 text-xs sm:text-sm font-black uppercase tracking-widest border-b-2 transition-all flex items-center gap-2 ${
            activeTab === "profile"
              ? "border-aether-indigo text-aether-indigo"
              : "border-transparent text-secondary hover:text-foreground"
          }`}
          aria-label="Profile Details Tab"
        >
          <UserIcon className="w-4 h-4" /> Profile Details
        </button>
        <button
          onClick={() => {
            setActiveTab("preferences");
            setStatus(null);
          }}
          className={`pb-3 text-xs sm:text-sm font-black uppercase tracking-widest border-b-2 transition-all flex items-center gap-2 ${
            activeTab === "preferences"
              ? "border-aether-indigo text-aether-indigo"
              : "border-transparent text-secondary hover:text-foreground"
          }`}
          aria-label="App Preferences Tab"
        >
          <Settings className="w-4 h-4" /> Preferences
        </button>
        <button
          onClick={() => {
            setActiveTab("api");
            setStatus(null);
          }}
          className={`pb-3 text-xs sm:text-sm font-black uppercase tracking-widest border-b-2 transition-all flex items-center gap-2 ${
            activeTab === "api"
              ? "border-aether-indigo text-aether-indigo"
              : "border-transparent text-secondary hover:text-foreground"
          }`}
          aria-label="AI API Keys Tab"
        >
          <Key className="w-4 h-4" /> AI Models & Keys
        </button>
        <button
          onClick={() => {
            setActiveTab("billing");
            setStatus(null);
          }}
          className={`pb-3 text-xs sm:text-sm font-black uppercase tracking-widest border-b-2 transition-all flex items-center gap-2 ${
            activeTab === "billing"
              ? "border-aether-indigo text-aether-indigo"
              : "border-transparent text-secondary hover:text-foreground"
          }`}
          aria-label="Billing & Subscriptions Tab"
        >
          <CreditCard className="w-4 h-4" /> Billing & Premium
        </button>
      </div>

      {/* Notification status bar */}
      <AnimatePresenceComponent mode="wait">
        {status && (
          <MotionDiv
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            role="status"
            className={`p-4 rounded-xl border flex items-center gap-3 backdrop-blur-sm ${
              status.type === "success"
                ? "bg-aether-emerald/10 border-aether-emerald/20 text-aether-emerald shadow-[0_0_10px_rgba(52,211,153,0.1)]"
                : "bg-aether-rose/10 border-aether-rose/25 text-aether-rose shadow-[0_0_10px_rgba(244,114,182,0.1)]"
            }`}
          >
            {status.type === "success" ? (
              <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
            )}
            <span className="text-xs font-black uppercase tracking-wider">{status.message}</span>
          </MotionDiv>
        )}
      </AnimatePresenceComponent>

      {/* Settings Panel Content */}
      <Card glow>
        <CardContent className="p-6 sm:p-8">
          
          {/* Tab 1: Profile Details */}
          {activeTab === "profile" && (
            <form onSubmit={handleSubmit(handleSaveProfile)} className="space-y-6">
              <h3 className="text-xs font-black uppercase tracking-widest text-foreground font-display flex items-center gap-2 border-b border-border pb-3">
                <UserIcon className="w-4.5 h-4.5 text-aether-indigo" /> Identity Details
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div className="flex flex-col gap-2">
                  <label htmlFor="first_name" className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">
                    First Name
                  </label>
                  <Input
                    id="first_name"
                    type="text"
                    {...register("first_name")}
                    placeholder="e.g. Jane"
                    className="font-semibold border-input bg-obsidian-depth"
                  />
                  {errors.first_name && (
                    <span className="text-xs text-aether-rose font-semibold">{errors.first_name.message}</span>
                  )}
                </div>

                <div className="flex flex-col gap-2">
                  <label htmlFor="last_name" className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">
                    Last Name
                  </label>
                  <Input
                    id="last_name"
                    type="text"
                    {...register("last_name")}
                    placeholder="e.g. Doe"
                    className="font-semibold border-input bg-obsidian-depth"
                  />
                  {errors.last_name && (
                    <span className="text-xs text-aether-rose font-semibold">{errors.last_name.message}</span>
                  )}
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <label htmlFor="bio" className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">
                  Biography / Bio
                </label>
                <textarea
                  id="bio"
                  rows={4}
                  {...register("bio")}
                  className="w-full px-4 py-3 bg-obsidian-depth border border-input focus:border-aether-indigo focus:ring-2 focus:ring-aether-indigo/15 text-foreground rounded-xl text-xs sm:text-sm transition-all outline-none resize-none font-semibold leading-relaxed"
                  placeholder="Tell us about your engineering career and study focus..."
                />
                {errors.bio && (
                  <span className="text-xs text-aether-rose font-semibold">{errors.bio.message}</span>
                )}
              </div>

              {/* Programming Skills Tagging */}
              <div className="space-y-4 pt-5 border-t border-border">
                <h4 className="text-xs font-black uppercase tracking-widest text-foreground font-display flex items-center gap-2">
                  <Tag className="w-4 h-4 text-aether-indigo" /> Skill Tags
                </h4>
                <div className="flex gap-3">
                  <div className="flex-1">
                    <Input
                      type="text"
                      value={skillInput}
                      onChange={(e) => setSkillInput(e.target.value)}
                      placeholder="Type skill tag (e.g. Python, Rust, Go) and click Add"
                      aria-label="New Skill Input"
                      className="font-semibold border-input bg-obsidian-depth"
                    />
                  </div>
                  <MotionDiv whileTap={{ scale: 0.96 }}>
                    <Button
                      type="button"
                      onClick={handleAddSkill}
                      variant="outline"
                      className="h-11 px-6 font-black text-xs uppercase tracking-widest"
                    >
                      Add
                    </Button>
                  </MotionDiv>
                </div>

                {skills.length === 0 ? (
                  <p className="text-xs text-secondary font-semibold italic">No skill tags registered yet. Add some to display on reviews.</p>
                ) : (
                  <div className="flex flex-wrap gap-2 pt-2">
                    <AnimatePresenceComponent>
                      {skills.map((skill) => (
                        <MotionDiv
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.9 }}
                          key={skill}
                        >
                          <Badge
                            variant="primary"
                            className="inline-flex items-center gap-1.5 px-3 py-1 text-xs bg-aether-indigo/20 text-aether-indigo border-aether-indigo/25"
                          >
                            {skill}
                            <button
                              type="button"
                              onClick={() => handleRemoveSkill(skill)}
                              className="text-aether-indigo hover:text-aether-indigo/80 rounded-full p-0.5"
                              aria-label={`Remove skill tag ${skill}`}
                            >
                              <X className="w-3 h-3 text-aether-indigo" />
                            </button>
                          </Badge>
                        </MotionDiv>
                      ))}
                    </AnimatePresenceComponent>
                  </div>
                )}
              </div>

              {/* Submit */}
              <div className="pt-6 border-t border-border flex justify-end">
                <MotionDiv whileTap={{ scale: 0.98 }}>
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    variant="primary"
                    className="h-11 px-6 font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2"
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin text-obsidian" />
                        Saving Details...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4 text-obsidian" /> Save Profile
                      </>
                    )}
                  </Button>
                </MotionDiv>
              </div>
            </form>
          )}

          {/* Tab 2: Preferences */}
          {activeTab === "preferences" && (
            <form onSubmit={handleSavePreferences} className="space-y-6">
              <h3 className="text-xs font-black uppercase tracking-widest text-foreground font-display flex items-center gap-2 border-b border-border pb-3">
                <Settings className="w-4.5 h-4.5 text-aether-indigo" /> Platform Preferences
              </h3>

              {/* Default Lang selection */}
              <div className="flex flex-col gap-2">
                <label htmlFor="default_lang" className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">
                  Default Coding Language
                </label>
                <select
                  id="default_lang"
                  value={defaultLanguage}
                  onChange={(e) => setDefaultLanguage(e.target.value)}
                  className="bg-obsidian-depth border border-input focus:border-aether-indigo focus:ring-2 focus:ring-aether-indigo/15 text-foreground rounded-xl px-4 py-3 text-xs sm:text-sm transition-all outline-none font-semibold"
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="java">Java</option>
                  <option value="cpp">C++</option>
                </select>
              </div>

              {/* Theme Toggle option */}
              <div className="space-y-2.5">
                <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">Visual Theme Mode</span>
                <div className="grid grid-cols-3 gap-4">
                  <button
                    type="button"
                    onClick={() => setTheme("dark")}
                    className={`flex flex-col sm:flex-row items-center justify-center gap-2 p-3.5 border rounded-xl transition-all ${
                      theme === "dark"
                        ? "border-aether-indigo bg-aether-indigo/10 text-aether-indigo"
                        : "border-border bg-obsidian-depth/50 text-secondary hover:border-aether-indigo/35 hover:text-foreground"
                    }`}
                  >
                    <Moon className="w-4 h-4" /> <span className="text-[10px] font-black uppercase tracking-widest">Dark</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setTheme("light")}
                    className={`flex flex-col sm:flex-row items-center justify-center gap-2 p-3.5 border rounded-xl transition-all ${
                      theme === "light"
                        ? "border-aether-indigo bg-aether-indigo/10 text-aether-indigo"
                        : "border-border bg-obsidian-depth/50 text-secondary hover:border-aether-indigo/35 hover:text-foreground"
                    }`}
                  >
                    <Sun className="w-4 h-4" /> <span className="text-[10px] font-black uppercase tracking-widest">Light</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setTheme("system")}
                    className={`flex flex-col sm:flex-row items-center justify-center gap-2 p-3.5 border rounded-xl transition-all ${
                      theme === "system"
                        ? "border-aether-indigo bg-aether-indigo/10 text-aether-indigo"
                        : "border-border bg-obsidian-depth/50 text-secondary hover:border-aether-indigo/35 hover:text-foreground"
                    }`}
                  >
                    <Laptop className="w-4 h-4" /> <span className="text-[10px] font-black uppercase tracking-widest">System</span>
                  </button>
                </div>
              </div>

              {/* Daily study notifications */}
              <div className="flex items-center gap-3 pt-2">
                <input
                  id="daily_reminders"
                  type="checkbox"
                  checked={dailyReminders}
                  onChange={(e) => setDailyReminders(e.target.checked)}
                  className="w-4.5 h-4.5 rounded border-input text-aether-indigo bg-obsidian focus:ring-aether-indigo/25"
                />
                <label htmlFor="daily_reminders" className="text-xs font-semibold text-secondary select-none cursor-pointer">
                  Send daily email recommendations and challenge completion reports.
                </label>
              </div>

              <div className="pt-6 border-t border-border flex justify-end">
                <MotionDiv whileTap={{ scale: 0.98 }}>
                  <Button
                    type="submit"
                    variant="primary"
                    className="h-11 px-6 font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2"
                  >
                    <Save className="w-4 h-4 text-obsidian" /> Save Preferences
                  </Button>
                </MotionDiv>
              </div>
            </form>
          )}

          {/* Tab 3: API / Model configuration */}
          {activeTab === "api" && (
            <form onSubmit={handleSaveApiKeys} className="space-y-6">
              <h3 className="text-xs font-black uppercase tracking-widest text-foreground font-display flex items-center gap-2 border-b border-border pb-3">
                <Key className="w-4.5 h-4.5 text-aether-indigo" /> AI Provider Keys
              </h3>
              <p className="text-xs text-secondary leading-relaxed font-semibold">
                By default, CodeGuru routing operates through platform provisioned proxy endpoints. If you wish to override and run locally or use proprietary keys, customize settings below.
              </p>

              {/* Custom OpenAI Key */}
              <div className="flex flex-col gap-2">
                <label htmlFor="openai_override" className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">
                  OpenAI API Key Override
                </label>
                <Input
                  id="openai_override"
                  type="password"
                  value={openaiKeyOverride}
                  onChange={(e) => setOpenaiKeyOverride(e.target.value)}
                  placeholder="sk-proj-..."
                  className="font-mono border-input bg-obsidian-depth"
                />
              </div>

              {/* Custom Ollama URL */}
              <div className="flex flex-col gap-2">
                <label htmlFor="ollama_url" className="text-[9px] font-black text-muted-foreground uppercase tracking-widest block">
                  Ollama Server Base URL
                </label>
                <Input
                  id="ollama_url"
                  type="text"
                  value={ollamaBaseUrl}
                  onChange={(e) => setOllamaBaseUrl(e.target.value)}
                  placeholder="http://localhost:11434"
                  className="font-mono border-input bg-obsidian-depth"
                />
              </div>

              <div className="pt-6 border-t border-border flex justify-end">
                <MotionDiv whileTap={{ scale: 0.98 }}>
                  <Button
                    type="submit"
                    variant="primary"
                    className="h-11 px-6 font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2"
                  >
                    <Save className="w-4 h-4 text-obsidian" /> Save Model Keys
                  </Button>
                </MotionDiv>
              </div>
            </form>
          )}

          {/* Tab 4: Stripe Billing & Subscriptions */}
          {activeTab === "billing" && (
            <div className="space-y-6">
              <h3 className="text-xs font-black uppercase tracking-widest text-foreground font-display flex items-center gap-2 border-b border-border pb-3">
                <CreditCard className="w-4.5 h-4.5 text-aether-indigo" /> Billing Control
              </h3>

              {user?.subscription_tier === "pro" ? (
                // ACTIVE PRO SUBSCRIBER CARD
                <div className="bg-obsidian-depth p-6 sm:p-8 rounded-2xl border border-aether-indigo/25 relative overflow-hidden shadow-lg">
                  <div className="absolute top-0 right-0 w-48 h-48 bg-aether-indigo/5 blur-3xl pointer-events-none rounded-full" />
                  
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 relative z-10">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2.5">
                        <Badge variant="primary" className="bg-gradient-to-r from-aether-indigo to-aether-violet px-3.5 py-1 text-[10px] font-black uppercase tracking-wider">
                          Pro Tier Active
                        </Badge>
                        <span className="text-xs text-aether-teal font-bold flex items-center gap-1">
                          <Zap className="w-3.5 h-3.5" /> Premium Features Unlocked
                        </span>
                      </div>
                      <h4 className="font-extrabold text-foreground text-sm font-display uppercase tracking-wider">Thank you for supporting CodeGuru AI!</h4>
                      <p className="text-xs text-secondary max-w-lg leading-relaxed font-semibold">
                        Your subscription plan includes unlimited automated and AI code reviews, fully enabled mock interview simulator sessions with detailed evaluation reports, and advanced document chunk limits for RAG analysis.
                      </p>
                    </div>

                    <MotionDiv whileTap={{ scale: 0.98 }} className="flex-shrink-0">
                      <Button
                        type="button"
                        onClick={async () => {
                          setIsRedirecting(true);
                          try {
                            const res = await api.post("/billing/portal", {
                              return_url: `${window.location.origin}/settings`,
                            });
                            window.location.href = res.data.portal_url;
                          } catch (err: any) {
                            setStatus({
                              type: "error",
                              message: err.response?.data?.detail || "Failed to open customer portal.",
                            });
                          } finally {
                            setIsRedirecting(false);
                          }
                        }}
                        disabled={isRedirecting}
                        className="h-11 px-6 font-black text-xs uppercase tracking-widest flex items-center gap-2"
                      >
                        {isRedirecting ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Settings className="w-4 h-4" />
                        )}
                        Manage Billing
                      </Button>
                    </MotionDiv>
                  </div>
                </div>
              ) : (
                // FREE TIER CARD & UPGRADE OPTIONS
                <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                  {/* Left list of premium details */}
                  <div className="md:col-span-3 space-y-5 flex flex-col justify-between pr-2">
                    <div className="space-y-3.5">
                      <h4 className="font-black text-foreground text-sm uppercase tracking-wider font-display">Upgrade to CodeGuru Pro</h4>
                      <p className="text-xs text-secondary leading-relaxed font-semibold">
                        Unlock the full potential of CodeGuru AI with our premium plan. Perfect for developers preparing for core engineering roles.
                      </p>
                      
                      <ul className="space-y-2.5 pt-2">
                        {[
                          "Unlimited Determinisitic & AI Code Review checks",
                          "Unlocked Advanced Technical Interview Simulator with full evaluations",
                          "Enhanced RAG document analysis chunk & upload limits",
                          "Priority access to advanced reasoning models (Gemini Pro)",
                        ].map((feat, idx) => (
                          <li key={idx} className="flex gap-2.5 items-start text-xs text-foreground font-semibold">
                            <span className="text-aether-indigo mt-0.5">•</span>
                            <span>{feat}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="text-[10px] text-secondary font-black uppercase tracking-wider pt-6 border-t border-border mt-4">
                      Current tier: <Badge variant="outline" className="ml-1 text-[9px] font-black uppercase tracking-wider">Free Plan</Badge>
                    </div>
                  </div>

                  {/* Right upgrade card with button */}
                  <div className="md:col-span-2 bg-[#060814] p-6 rounded-2xl border border-aether flex flex-col justify-between items-center text-center shadow-lg relative overflow-hidden">
                    <div className="absolute -top-12 -right-12 w-24 h-24 bg-aether-indigo/10 blur-xl pointer-events-none rounded-full" />
                    
                    <div className="space-y-2 relative z-10 w-full pt-4">
                      <span className="text-[10px] text-aether-indigo uppercase font-black tracking-widest">Premium Plan</span>
                      <div className="flex items-baseline justify-center gap-1 py-3">
                        <span className="text-4xl font-black text-foreground">$19</span>
                        <span className="text-xs text-secondary font-bold">/ month</span>
                      </div>
                      <p className="text-[10px] text-secondary font-semibold px-2">Cancel anytime. Secure subscription payments powered by Stripe.</p>
                    </div>

                    <MotionDiv whileTap={{ scale: 0.98 }} className="w-full mt-6 relative z-10">
                      <Button
                        type="button"
                        onClick={async () => {
                          setIsRedirecting(true);
                          try {
                            const res = await api.post("/billing/checkout", {
                              success_url: `${window.location.origin}/settings/billing/success`,
                              cancel_url: `${window.location.origin}/settings/billing/cancel`,
                            });
                            window.location.href = res.data.checkout_url;
                          } catch (err: any) {
                            setStatus({
                              type: "error",
                              message: err.response?.data?.detail || "Failed to initialize premium checkout.",
                            });
                          } finally {
                            setIsRedirecting(false);
                          }
                        }}
                        disabled={isRedirecting}
                        variant="primary"
                        className="w-full h-11 font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2"
                      >
                        {isRedirecting ? (
                          <Loader2 className="w-4 h-4 animate-spin text-obsidian" />
                        ) : (
                          <Sparkles className="w-4 h-4 text-obsidian animate-pulse" />
                        )}
                        Upgrade to Pro
                      </Button>
                    </MotionDiv>
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
