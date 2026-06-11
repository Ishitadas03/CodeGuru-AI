"use client";

import React, { useMemo } from "react";
import { useAnalytics } from "@/hooks/useAnalytics";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Flame,
  Award,
  Terminal,
  Activity,
  AlertTriangle,
  BookOpen,
  ArrowRight,
  TrendingUp,
  Loader2,
} from "lucide-react";
import {
  ResponsiveContainer as RechartsResponsiveContainer,
  LineChart as RechartsLineChart,
  Line as RechartsLine,
  XAxis as RechartsXAxis,
  YAxis as RechartsYAxis,
  Tooltip as RechartsTooltip,
  BarChart as RechartsBarChart,
  Bar as RechartsBar,
  Cell as RechartsCell,
  PieChart as RechartsPieChart,
  Pie as RechartsPie,
  CartesianGrid as RechartsCartesianGrid,
} from "recharts";
import { motion } from "framer-motion";
import { aetherColors, aetherChartColors } from "@/lib/aether-theme";

const ResponsiveContainer = RechartsResponsiveContainer as any;
const LineChart = RechartsLineChart as any;
const Line = RechartsLine as any;
const XAxis = RechartsXAxis as any;
const YAxis = RechartsYAxis as any;
const Tooltip = RechartsTooltip as any;
const BarChart = RechartsBarChart as any;
const Bar = RechartsBar as any;
const Cell = RechartsCell as any;
const PieChart = RechartsPieChart as any;
const Pie = RechartsPie as any;
const CartesianGrid = RechartsCartesianGrid as any;
const MotionDiv = motion.div as any;

// Helper to format date strings for readability (e.g., Jun 7)
const formatDateLabel = (dateStr: string) => {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  } catch {
    return dateStr;
  }
};

export default function AnalyticsDashboard() {
  const { useOverview } = useAnalytics();
  const { data: overview, isLoading, error } = useOverview();

  // 1. Process Heatmap data into columns (weeks of 7 days)
  const heatmapGrid = useMemo(() => {
    if (!overview?.heatmap || overview.heatmap.length === 0) return [];
    
    // Sort chronologically
    const sorted = [...overview.heatmap].sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
    );

    const columns: typeof sorted[] = [];
    let tempCol: typeof sorted = [];
    
    sorted.forEach((day, index) => {
      tempCol.push(day);
      if (tempCol.length === 7 || index === sorted.length - 1) {
        columns.push(tempCol);
        tempCol = [];
      }
    });

    return columns;
  }, [overview?.heatmap]);

  // 2. Format Line Chart score history
  const chartData = useMemo(() => {
    if (!overview?.review_stats?.score_history) return [];
    return overview.review_stats.score_history.map((h: any, index: number) => ({
      name: `Review ${index + 1}`,
      date: formatDateLabel(h.date),
      score: h.score,
    }));
  }, [overview?.review_stats?.score_history]);

  // 3. Format Topic Mastery data
  const topicData = useMemo(() => {
    if (!overview?.dsa_stats?.solved_by_topic) return [];
    return Object.entries(overview.dsa_stats.solved_by_topic).map(([topic, count]) => ({
      name: topic.replace("-", " ").toUpperCase(),
      solved: count,
    }));
  }, [overview?.dsa_stats?.solved_by_topic]);

  // 4. Format Common Issues Pie chart data
  const pieData = useMemo(() => {
    if (!overview?.review_stats?.common_issues) return [];
    return overview.review_stats.common_issues.map((issue: any) => ({
      name: issue.category.toUpperCase(),
      value: issue.count,
    }));
  }, [overview?.review_stats?.common_issues]);

  const COLORS = [
    aetherChartColors.primary,
    aetherChartColors.secondary,
    aetherChartColors.teal,
    aetherChartColors.purple,
    aetherChartColors.emerald,
    aetherChartColors.rose,
    aetherChartColors.amber
  ];

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4 relative">
        {/* Glow ambient */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-aether-indigo/5 rounded-full blur-[100px]" />
        <Loader2 className="w-10 h-10 animate-spin text-aether-indigo relative z-10" />
        <p className="text-xs text-muted-foreground font-black uppercase tracking-widest animate-pulse relative z-10">
          Compiling stats and trajectories...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-aether-rose/10 border border-aether-rose/25 text-aether-rose p-6 rounded-2xl flex flex-col items-center gap-4 text-center max-w-md mx-auto my-12 relative overflow-hidden">
        {/* Glow ambient */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-aether-rose/5 rounded-full blur-xl pointer-events-none" />
        <AlertTriangle className="w-10 h-10 text-aether-rose relative z-10" />
        <h3 className="font-black text-sm uppercase tracking-widest text-foreground relative z-10">Failed to Load Analytics</h3>
        <p className="text-xs text-secondary leading-relaxed font-semibold relative z-10">
          An error occurred while compiling your study stats. Please try again or submit a code review to generate metrics.
        </p>
      </div>
    );
  }

  const dsa = overview?.dsa_stats || { total_solved: 0, total_attempted: 0, solved_by_difficulty: { easy: 0, medium: 0, hard: 0 } };
  const reviews = overview?.review_stats || { total_reviews: 0, average_score: 0, common_issues: [] };
  const streak = overview?.streak || { current_streak: 0, longest_streak: 0 };

  return (
    <div className="space-y-8 pb-12">
      {/* Page Header */}
      <div className="space-y-1.5">
        <h1 className="text-3xl font-extrabold tracking-tight font-display text-aether-grad">
          Learning Analytics
        </h1>
        <p className="text-xs sm:text-sm text-secondary font-black uppercase tracking-widest">
          Track your skill progress, coding consistency streaks, and automated AI code review trends.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Streak card */}
        <Card hoverable className="group">
          {/* Accent glow on hover */}
          <div className="absolute top-0 right-0 w-24 h-24 bg-aether-rose/5 rounded-full blur-2xl group-hover:bg-aether-rose/15 transition-all duration-350" />
          <CardContent className="p-0 flex flex-col justify-between h-full">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <p className="text-muted-foreground text-[9px] font-black uppercase tracking-widest">
                  Coding Streak
                </p>
                <h3 className="text-3xl font-extrabold text-foreground flex items-baseline gap-1 font-display">
                  {streak.current_streak} <span className="text-xs font-semibold text-muted-foreground uppercase">days</span>
                </h3>
              </div>
              <div className="bg-aether-rose/10 text-aether-rose p-3 rounded-lg border border-aether-rose/15 shadow-[0_0_10px_rgba(244,114,182,0.15)]">
                <Flame className="w-5 h-5 fill-aether-rose/10 animate-pulse" />
              </div>
            </div>
            <p className="text-[9px] text-aether-rose font-black uppercase tracking-widest mt-5">
              <span>All-time record: </span>
              <span>{streak.longest_streak} days</span>
            </p>
          </CardContent>
        </Card>

        {/* Avg Code Score card */}
        <Card hoverable className="group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-aether-teal/5 rounded-full blur-2xl group-hover:bg-aether-teal/15 transition-all duration-350" />
          <CardContent className="p-0 flex flex-col justify-between h-full">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <p className="text-muted-foreground text-[9px] font-black uppercase tracking-widest">
                  Average Code Score
                </p>
                <h3 className="text-3xl font-extrabold text-foreground font-display">
                  {reviews.average_score}<span className="text-xs font-semibold text-muted-foreground">/100</span>
                </h3>
              </div>
              <div className="bg-aether-teal/10 text-aether-teal p-3 rounded-lg border border-aether-teal/15 shadow-[0_0_10px_rgba(34,211,238,0.15)]">
                <Award className="w-5 h-5" />
              </div>
            </div>
            <p className="text-[9px] text-aether-teal font-black uppercase tracking-widest mt-5 flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>AI Quality Benchmark</span>
            </p>
          </CardContent>
        </Card>

        {/* DSA Solved card */}
        <Card hoverable className="group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-aether-emerald/5 rounded-full blur-2xl group-hover:bg-aether-emerald/15 transition-all duration-350" />
          <CardContent className="p-0 flex flex-col justify-between h-full">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <p className="text-muted-foreground text-[9px] font-black uppercase tracking-widest">
                  DSA Solved
                </p>
                <h3 className="text-3xl font-extrabold text-foreground font-display">
                  {dsa.total_solved} <span className="text-[9px] font-semibold text-muted-foreground uppercase">completed</span>
                </h3>
              </div>
              <div className="bg-aether-emerald/10 text-aether-emerald p-3 rounded-lg border border-aether-emerald/15 shadow-[0_0_10px_rgba(52,211,153,0.15)]">
                <Terminal className="w-5 h-5" />
              </div>
            </div>
            <p className="text-[9px] text-aether-emerald font-black uppercase tracking-widest mt-5">
              <span>Attempting: </span>
              <span>{dsa.total_attempted} problems</span>
            </p>
          </CardContent>
        </Card>

        {/* Total Reviews card */}
        <Card hoverable className="group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-aether-indigo/5 rounded-full blur-2xl group-hover:bg-aether-indigo/15 transition-all duration-350" />
          <CardContent className="p-0 flex flex-col justify-between h-full">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <p className="text-muted-foreground text-[9px] font-black uppercase tracking-widest">
                  Total Reviews
                </p>
                <h3 className="text-3xl font-extrabold text-foreground font-display">
                  {reviews.total_reviews} <span className="text-[9px] font-semibold text-muted-foreground uppercase">analyses</span>
                </h3>
              </div>
              <div className="bg-aether-indigo/10 text-aether-indigo p-3 rounded-lg border border-aether-indigo/15 shadow-[0_0_10px_rgba(91,108,249,0.15)]">
                <Activity className="w-5 h-5" />
              </div>
            </div>
            <p className="text-[9px] text-aether-indigo font-black uppercase tracking-widest mt-5">
              <span>Feedback reports saved</span>
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Contribution Heatmap */}
      <Card glow>
        <CardContent className="p-6">
          <h3 className="text-xs font-black uppercase tracking-widest text-foreground font-display mb-1">Coding Activity Heatmap</h3>
          <p className="text-xs text-secondary mb-6 font-semibold">Visualizes your aggregate daily interactions (submissions & reviews) over the past 365 days.</p>
          
          <div className="overflow-x-auto pb-4 custom-scrollbar">
            <div className="flex gap-1 min-w-[760px] select-none justify-start items-center">
              {heatmapGrid.map((week, wIdx) => (
                <div key={wIdx} className="flex flex-col gap-1">
                  {week.map((day) => {
                    let colorClass = "bg-obsidian-layer border border-border";
                    if (day.count === 1) colorClass = "bg-aether-indigo/10 border border-aether-indigo/20";
                    else if (day.count === 2) colorClass = "bg-aether-indigo/25 border border-aether-indigo/35 shadow-[0_0_5px_rgba(91,108,249,0.1)]";
                    else if (day.count === 3) colorClass = "bg-aether-indigo/50 border border-aether-indigo/60 shadow-[0_0_8px_rgba(91,108,249,0.2)]";
                    else if (day.count >= 4) colorClass = "bg-aether-indigo shadow-[0_0_12px_rgba(91,108,249,0.4)]";

                    return (
                      <div
                        key={day.date}
                        className={`w-3.5 h-3.5 rounded-sm transition-all duration-150 relative group cursor-pointer ${colorClass}`}
                        title={`${day.count} activities on ${formatDateLabel(day.date)}`}
                      >
                        {/* Floating mini-tooltip */}
                        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-obsidian-depth border border-border text-foreground text-[9px] font-black py-1 px-2 rounded-lg opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity duration-150 shadow-xl whitespace-nowrap z-50 uppercase tracking-widest">
                          {day.count} activities • {formatDateLabel(day.date)}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
          
          {/* Heatmap Legend */}
          <div className="flex justify-end gap-2 text-[8px] text-muted-foreground font-black uppercase tracking-widest mt-2 mr-2">
            <span>Less</span>
            <div className="w-3 h-3 bg-obsidian-layer rounded-sm border border-border" />
            <div className="w-3 h-3 bg-aether-indigo/10 rounded-sm" />
            <div className="w-3 h-3 bg-aether-indigo/25 rounded-sm" />
            <div className="w-3 h-3 bg-aether-indigo/50 rounded-sm" />
            <div className="w-3 h-3 bg-aether-indigo rounded-sm" />
            <span>More</span>
          </div>
        </CardContent>
      </Card>

      {/* Graphs Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Code Review score trend line chart */}
        <Card glow>
          <CardContent className="p-6">
            <h3 className="text-xs font-black uppercase tracking-widest text-foreground font-display mb-6">Code Review Score Progress</h3>
            {chartData.length === 0 ? (
              <div className="flex flex-col items-center justify-center min-h-[220px] text-muted-foreground text-xs font-bold uppercase tracking-wider">
                <Activity className="w-8 h-8 text-aether-indigo mb-2 animate-pulse" />
                <p>No code reviews requested yet.</p>
              </div>
            ) : (
              <div className="w-full h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ left: -15, right: 10, top: 10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={aetherChartColors.grid} vertical={false} />
                    <XAxis dataKey="date" stroke={aetherChartColors.text} fontSize={10} tickLine={false} />
                    <YAxis domain={[0, 100]} stroke={aetherChartColors.text} fontSize={10} tickLine={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: aetherChartColors.tooltip.bg,
                        borderColor: aetherChartColors.tooltip.border,
                        borderRadius: "12px",
                        color: "#F0F4FF",
                        fontSize: "10px",
                        fontFamily: "var(--font-jetbrains)"
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="score"
                      stroke={aetherChartColors.primary}
                      strokeWidth={3}
                      dot={{ fill: aetherColors.obsidian, stroke: aetherChartColors.primary, strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, fill: aetherChartColors.primary, stroke: aetherColors.obsidian, strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Topic Mastery Bar chart */}
        <Card glow>
          <CardContent className="p-6">
            <h3 className="text-xs font-black uppercase tracking-widest text-foreground font-display mb-6">DSA Topic Mastery</h3>
            {topicData.length === 0 ? (
              <div className="flex flex-col items-center justify-center min-h-[220px] text-muted-foreground text-xs font-bold uppercase tracking-wider">
                <BookOpen className="w-8 h-8 text-aether-violet mb-2 animate-pulse" />
                <p>Solve some DSA problems to show topic breakdown.</p>
              </div>
            ) : (
              <div className="w-full h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={topicData} margin={{ left: -15, right: 10, top: 10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={aetherChartColors.grid} vertical={false} />
                    <XAxis dataKey="name" stroke={aetherChartColors.text} fontSize={10} tickLine={false} />
                    <YAxis stroke={aetherChartColors.text} fontSize={10} tickLine={false} allowDecimals={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: aetherChartColors.tooltip.bg,
                        borderColor: aetherChartColors.tooltip.border,
                        borderRadius: "12px",
                        color: "#F0F4FF",
                        fontSize: "10px",
                        fontFamily: "var(--font-jetbrains)"
                      }}
                    />
                    <Bar dataKey="solved" fill={aetherChartColors.primary} radius={[4, 4, 0, 0]}>
                      {topicData.map((entry: any, index: number) => (
                         <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Issues Breakdown & Detailed stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Pie chart representing common issue categories */}
        <Card glow className="lg:col-span-2 flex flex-col justify-between">
          <CardContent className="p-6 flex flex-col justify-between h-full">
            <div>
              <h3 className="text-xs font-black uppercase tracking-widest text-foreground font-display mb-1">Code Quality Issue Breakdown</h3>
              <p className="text-xs text-secondary mb-6 font-semibold">Aggregated category frequencies of design issues identified by the AI reviewers.</p>
            </div>
            {pieData.length === 0 ? (
              <div className="flex flex-col items-center justify-center min-h-[200px] text-muted-foreground text-xs font-bold uppercase tracking-wider w-full">
                <AlertTriangle className="w-8 h-8 text-aether-rose mb-2 animate-pulse" />
                <p>No review issues flagged yet.</p>
              </div>
            ) : (
              <div className="flex flex-col md:flex-row items-center gap-8 py-2 w-full">
                <div className="w-44 h-44 relative flex-shrink-0 mx-auto md:mx-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={45}
                        outerRadius={65}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {pieData.map((entry: any, index: number) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: aetherChartColors.tooltip.bg,
                          borderColor: aetherChartColors.tooltip.border,
                          borderRadius: "12px",
                          color: "#F0F4FF",
                          fontSize: "10px",
                          fontFamily: "var(--font-jetbrains)"
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Legends list with counts */}
                <div className="flex-1 space-y-3.5 w-full">
                  {pieData.map((entry: any, index: number) => (
                    <div key={entry.name} className="flex items-center justify-between text-xs font-bold uppercase tracking-wider">
                      <div className="flex items-center gap-2.5">
                        <div
                          className="w-2.5 h-2.5 rounded-full"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        />
                        <span className="text-secondary font-black tracking-wide">
                          {entry.name}
                        </span>
                      </div>
                      <span className="text-muted-foreground">{entry.value} flags</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* DSA difficulty breakdown card */}
        <Card glow className="flex flex-col justify-between">
          <CardContent className="p-6 flex flex-col justify-between h-full">
            <div>
              <h3 className="text-xs font-black uppercase tracking-widest text-foreground font-display mb-1">Challenge Solved Ratios</h3>
              <p className="text-xs text-secondary mb-6 font-semibold">DSA exercises completed grouped by difficulty.</p>
            </div>

            <div className="space-y-5">
              {/* Easy ratio */}
              <div>
                <div className="flex justify-between text-[9px] font-black mb-1.5 text-muted-foreground uppercase tracking-widest">
                  <span className="text-aether-emerald">Easy</span>
                  <span className="text-secondary">{dsa.solved_by_difficulty.easy} solved</span>
                </div>
                <div className="h-1.5 w-full bg-obsidian rounded-full overflow-hidden border border-border">
                  <div
                    className="h-full bg-aether-emerald transition-all duration-500 shadow-[0_0_8px_rgba(52,211,153,0.3)]"
                    style={{
                      width: `${
                        dsa.total_solved > 0
                          ? (dsa.solved_by_difficulty.easy / dsa.total_solved) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
              </div>

              {/* Medium ratio */}
              <div>
                <div className="flex justify-between text-[9px] font-black mb-1.5 text-muted-foreground uppercase tracking-widest">
                  <span className="text-aether-teal">Medium</span>
                  <span className="text-secondary">{dsa.solved_by_difficulty.medium} solved</span>
                </div>
                <div className="h-1.5 w-full bg-obsidian rounded-full overflow-hidden border border-border">
                  <div
                    className="h-full bg-aether-teal transition-all duration-500 shadow-[0_0_8px_rgba(34,211,238,0.3)]"
                    style={{
                      width: `${
                        dsa.total_solved > 0
                          ? (dsa.solved_by_difficulty.medium / dsa.total_solved) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
              </div>

              {/* Hard ratio */}
              <div>
                <div className="flex justify-between text-[9px] font-black mb-1.5 text-muted-foreground uppercase tracking-widest">
                  <span className="text-aether-rose">Hard</span>
                  <span className="text-secondary">{dsa.solved_by_difficulty.hard} solved</span>
                </div>
                <div className="h-1.5 w-full bg-obsidian rounded-full overflow-hidden border border-border">
                  <div
                    className="h-full bg-aether-rose transition-all duration-500 shadow-[0_0_8px_rgba(244,114,182,0.3)]"
                    style={{
                      width: `${
                        dsa.total_solved > 0
                          ? (dsa.solved_by_difficulty.hard / dsa.total_solved) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
              </div>
            </div>

            <div className="mt-8 pt-4 border-t border-border flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-aether-indigo hover:text-aether-indigo/85 cursor-pointer">
              <span className="flex items-center gap-1">
                Go solve more coding puzzles <ArrowRight className="w-3.5 h-3.5" />
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
