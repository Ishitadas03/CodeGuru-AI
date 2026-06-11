"use client";

import React from "react";
import { LANGUAGES } from "@/lib/constants";

interface LanguageSelectorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function LanguageSelector({
  value,
  onChange,
  disabled = false,
}: LanguageSelectorProps) {
  return (
    <div className="relative inline-block">
      <select
        disabled={disabled}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="block w-44 px-3.5 py-2.5 bg-obsidian-depth border border-aether-indigo/15 text-foreground rounded-xl text-xs font-black uppercase tracking-wider focus:outline-none focus:ring-2 focus:ring-aether-indigo/25 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
      >
        {LANGUAGES.map((lang) => (
          <option key={lang.value} value={lang.value} className="bg-obsidian-layer text-foreground">
            {lang.label}
          </option>
        ))}
      </select>
    </div>
  );
}
