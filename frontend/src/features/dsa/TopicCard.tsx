"use client";

import React from "react";
import { DSATopic } from "@/types/dsa.types";
import { Braces, Network, ListCollapse, FolderCheck } from "lucide-react";

interface TopicCardProps {
  topic: DSATopic;
  isSelected: boolean;
  onClick: () => void;
}

export default function TopicCard({ topic, isSelected, onClick }: TopicCardProps) {
  const getTopicIcon = (slug: string) => {
    switch (slug) {
      case "arrays":
        return <Braces className="w-5 h-5 text-aether-indigo" />;
      case "linked-lists":
        return <ListCollapse className="w-5 h-5 text-aether-teal" />;
      case "trees":
        return <Network className="w-5 h-5 text-aether-violet" />;
      default:
        return <FolderCheck className="w-5 h-5 text-aether-aurora" />;
    }
  };

  const getActiveBorder = () => {
    if (isSelected) {
      return "border-aether-indigo/50 bg-aether-indigo/10 shadow-[0_0_20px_rgba(91,108,249,0.15)]";
    }
    return "border-aether bg-obsidian-depth/40 hover:border-aether-indigo/30 hover:scale-[1.01]";
  };

  return (
    <div
      onClick={onClick}
      className={`p-5 rounded-2xl border cursor-pointer transition-all duration-200 shadow-sm flex flex-col justify-between ${getActiveBorder()}`}
    >
      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-obsidian-layer border border-aether shadow-inner">
            {getTopicIcon(topic.slug)}
          </div>
          <h4 className="font-bold text-foreground text-base">
            {topic.name}
          </h4>
        </div>
        
        <p className="text-xs md:text-sm text-[#8892B0] leading-relaxed">
          {topic.description}
        </p>
      </div>

      <div className="mt-5 pt-4 border-t border-aether flex items-center justify-between text-xs text-[#8892B0]">
        <span>Completion</span>
        <span className="font-semibold text-foreground">
          {topic.slug === "arrays" ? "2/2" : topic.slug === "linked-lists" ? "1/1" : "0/0"} problems
        </span>
      </div>
    </div>
  );
}
