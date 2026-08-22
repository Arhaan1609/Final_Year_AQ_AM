"use client";

import React from "react";
import { useFleetStore, DashboardTab } from "../../lib/store/useFleetStore";
import {
  LayoutDashboard,
  Cpu,
  Flame,
  Gauge,
  TrendingDown,
  FileText,
  Briefcase,
} from "lucide-react";

export const Sidebar: React.FC = () => {
  const { activeTab, setActiveTab, viewMode, setViewMode } = useFleetStore();

  const navItems: {
    id: DashboardTab;
    label: string;
    sub: string;
    icon: React.ComponentType<{ className?: string }>;
  }[] = [
    {
      id: "fleet",
      label: "Fleet Health Overview",
      sub: "3D Twin & KPIs",
      icon: LayoutDashboard,
    },
    {
      id: "state-est",
      label: "State Estimation Hub",
      sub: "Module A • 56 Models",
      icon: Cpu,
    },
    {
      id: "thermal",
      label: "Thermal Safety",
      sub: "Module B • Multi-Zone",
      icon: Flame,
    },
    {
      id: "behavior",
      label: "Driver Profiling",
      sub: "Module C • AI & BSI",
      icon: Gauge,
    },
    {
      id: "knee",
      label: "Knee Prognostics",
      sub: "Module C • Aging Curve",
      icon: TrendingDown,
    },
    {
      id: "meta-ensemble",
      label: "Meta-Ensemble Report",
      sub: "74-Model Audit",
      icon: FileText,
    },
  ];

  return (
    <aside className="w-60 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0A0D14] p-3.5 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-3.5rem)] transition-colors select-none shrink-0">
      <div className="space-y-1">
        {/* Operations Command Quick Switch */}
        <button
          onClick={() => setViewMode("operations")}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all mb-2 ${
            viewMode === "operations"
              ? "bg-gradient-to-r from-cyan-600 to-emerald-600 text-white font-bold shadow-md shadow-emerald-500/20"
              : "bg-slate-100 dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-800"
          }`}
        >
          <Briefcase className="w-4 h-4 text-cyan-200" />
          <div>
            <div className="text-xs font-bold">Operations Hub</div>
            <div className="text-[10px] opacity-80">Non-EV Dispatch Triage</div>
          </div>
        </button>

        <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 px-3 py-2">
          Diagnostic Modules (ML)
        </div>

        {navItems.map((item) => {
          const isActive = viewMode === "engineering" && activeTab === item.id;
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => {
                setViewMode("engineering");
                setActiveTab(item.id);
              }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all ${
                isActive
                  ? "bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-semibold border-l-2 border-emerald-500 shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-900/60"
              }`}
            >
              <Icon
                className={`w-4 h-4 shrink-0 ${
                  isActive ? "text-emerald-600 dark:text-emerald-400" : "text-slate-400"
                }`}
              />
              <div className="overflow-hidden">
                <div className="text-xs leading-tight truncate">{item.label}</div>
                <div className="text-[10px] text-slate-400 dark:text-slate-500 truncate mt-0.5">
                  {item.sub}
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Footer System Status */}
      <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 text-[11px] font-mono text-slate-500 dark:text-slate-400 space-y-1">
        <div className="flex items-center justify-between text-[10px]">
          <span className="text-slate-400 uppercase font-semibold">Inference Engine</span>
          <span className="text-emerald-600 dark:text-emerald-400 font-bold">● Active</span>
        </div>
        <div className="text-[10px] text-slate-400">Euler HiLoad 12.4 kWh LFP</div>
      </div>
    </aside>
  );
};
