import React from "react";
import AnalyticsDashboard from "@/features/analytics/AnalyticsDashboard";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Analytics | CodeGuru AI",
  description: "Track your study history, coding streaks, and code review trends.",
};

export default function AnalyticsPage() {
  return <AnalyticsDashboard />;
}
