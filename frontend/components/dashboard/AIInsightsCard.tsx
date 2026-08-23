"use client";

import React, { useEffect, useState } from "react";
import { Sparkles, RefreshCw, AlertOctagon, AlertTriangle, CheckCircle2, Cpu, Wrench, Flame, HelpCircle } from "lucide-react";
import { VehicleInsightResponse } from "../../lib/api/types";
import { explainVehicle } from "../../lib/api/copilot";

interface AIInsightsCardProps {
  vehicle: any;
  livePredictions: {
    soc?: number;
    soh?: number;
    rul?: number;
    mileage?: number;
  };
}

export const AIInsightsCard: React.FC<AIInsightsCardProps> = ({ vehicle, livePredictions }) => {
  const [insight, setInsight] = useState<VehicleInsightResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const fetchInsight = async (force: boolean = false) => {
    if (!vehicle?.id) return;
    if (force) setIsRefreshing(true);
    else setLoading(true);

    try {
      const data = await explainVehicle(vehicle.id, vehicle, livePredictions, force);
      setInsight(data);
    } catch (e) {
      console.error("[AIInsightsCard] Failed to fetch diagnostic:", e);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchInsight(false);
  }, [vehicle?.id, livePredictions?.soh, livePredictions?.soc]);

  if (loading && !insight) {
    return (
      <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-50 to-indigo-50/20 dark:from-[#0D111A] dark:to-[#131B2E] border border-slate-200 dark:border-slate-800 shadow-sm animate-pulse space-y-3">
        <div className="flex items-center justify-between">
          <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-1/3" />
          <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-24" />
        </div>
        <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-full" />
        <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-4/5" />
      </div>
    );
  }

  if (!insight) return null;

  const isCritical = insight.urgency === "CRITICAL";
  const isWarning = insight.urgency === "WARNING";

  return (
    <div className={`p-5 rounded-2xl border shadow-sm transition-all duration-300 ${
      isCritical
        ? "bg-gradient-to-br from-rose-50/70 via-white to-orange-50/40 dark:from-[#1A0B10] dark:via-[#0D111A] dark:to-[#181116] border-rose-200/90 dark:border-rose-900/60"
        : isWarning
        ? "bg-gradient-to-br from-amber-50/70 via-white to-yellow-50/40 dark:from-[#1A140B] dark:via-[#0D111A] dark:to-[#181611] border-amber-200/90 dark:border-amber-900/60"
        : "bg-gradient-to-br from-emerald-50/60 via-white to-cyan-50/40 dark:from-[#0B1A14] dark:via-[#0D111A] dark:to-[#11181B] border-emerald-200/80 dark:border-emerald-900/60"
    }`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100 dark:border-slate-800/80">
        <div className="flex items-center gap-2">
          <div className={`p-1.5 rounded-lg ${
            isCritical
              ? "bg-rose-100 dark:bg-rose-950 text-rose-600 dark:text-rose-400"
              : isWarning
              ? "bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400"
              : "bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400"
          }`}>
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <span>AI Powertrain Diagnostic & Root Cause</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${
                isCritical
                  ? "bg-rose-100 dark:bg-rose-900/60 text-rose-700 dark:text-rose-300 border border-rose-300 dark:border-rose-800"
                  : isWarning
                  ? "bg-amber-100 dark:bg-amber-900/60 text-amber-700 dark:text-amber-300 border border-amber-300 dark:border-amber-800"
                  : "bg-emerald-100 dark:bg-emerald-900/60 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800"
              }`}>
                {insight.urgency}
              </span>
            </h3>
          </div>
        </div>

        {/* Model Badge & Refresh */}
        <div className="flex items-center gap-2">
          <span className="px-2 py-1 rounded-md bg-slate-100 dark:bg-slate-800/90 text-[10px] font-mono text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 flex items-center gap-1.5">
            <Cpu className="w-3 h-3 text-indigo-500" />
            <span>{insight.model_used}</span>
          </span>

          <button
            onClick={() => fetchInsight(true)}
            disabled={isRefreshing}
            className="p-1 rounded-md hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-all disabled:opacity-50"
            title="Re-run AI Diagnostic Analysis"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin text-indigo-500" : ""}`} />
          </button>
        </div>
      </div>

      {/* Main Analysis Sections */}
      <div className="mt-3.5 space-y-3.5 text-xs">
        {/* 1. Executive Summary */}
        <div className="p-3 rounded-xl bg-white/80 dark:bg-slate-900/80 border border-slate-200/80 dark:border-slate-800/80 leading-relaxed text-slate-800 dark:text-slate-200">
          <p className="font-semibold text-slate-900 dark:text-slate-100 mb-1 flex items-center gap-1.5 text-xs sm:text-[13px]">
            {isCritical ? (
              <AlertOctagon className="w-4 h-4 text-rose-500 shrink-0" />
            ) : isWarning ? (
              <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />
            ) : (
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
            )}
            <span>Executive Health Summary</span>
          </p>
          <p className="text-slate-700 dark:text-slate-300">{insight.summary}</p>
        </div>

        {/* 2. Why is it performing in this manner? */}
        <div className="space-y-1.5">
          <h4 className="text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5 text-indigo-500" />
            <span>Why Is This Battery Performing This Way?</span>
          </h4>
          <p className="text-slate-700 dark:text-slate-300 leading-relaxed pl-1 bg-white/40 dark:bg-slate-900/40 p-2.5 rounded-lg border border-slate-100 dark:border-slate-800/50">
            {insight.why_performing_this_way}
          </p>
        </div>

        {/* 3. Dual Columns: Root Causes & Prescriptive Directives */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
          {/* Root Causes */}
          <div className="p-3 rounded-xl bg-slate-50/90 dark:bg-slate-900/60 border border-slate-200/70 dark:border-slate-800/70 space-y-2">
            <h5 className="font-bold text-[11px] text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Flame className="w-3.5 h-3.5 text-amber-500" />
              <span>Contributing Telemetry Factors</span>
            </h5>
            <ul className="space-y-1.5 text-[11px] text-slate-600 dark:text-slate-300">
              {insight.root_causes.map((rc, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <span className="text-amber-500 font-bold mt-0.5">•</span>
                  <span>{rc}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Prescriptive Actions */}
          <div className="p-3 rounded-xl bg-slate-50/90 dark:bg-slate-900/60 border border-slate-200/70 dark:border-slate-800/70 space-y-2">
            <h5 className="font-bold text-[11px] text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Wrench className="w-3.5 h-3.5 text-emerald-500" />
              <span>Prescriptive Action Directives</span>
            </h5>
            <ul className="space-y-1.5 text-[11px] text-slate-600 dark:text-slate-300">
              {insight.prescriptive_actions.map((act, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <span className="text-emerald-500 font-bold mt-0.5">✓</span>
                  <span>{act}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
export default AIInsightsCard;
