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
  ShieldAlert,
} from "lucide-react";

export const Sidebar: React.FC = () => {
  const { activeTab, setActiveTab } = useFleetStore();

  const navItems: { id: DashboardTab; label: string; sub: string; icon: React.ComponentType<{ className?: string }> }[] = [
    {
      id: "fleet",
      label: "Fleet Health Overview",
      sub: "3D Twin & Fleet KPIs",
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
      sub: "Module B • Multi-Zone RF",
      icon: Flame,
    },
    {
      id: "behavior",
      label: "Driver Profiling",
      sub: "Module C • AI & BSI Dials",
      icon: Gauge,
    },
    {
      id: "knee",
      label: "Knee Prognostics",
      sub: "Module C • Degradation Curve",
      icon: TrendingDown,
    },
    {
      id: "meta-ensemble",
      label: "Meta-Ensemble Report",
      sub: "A+B+C Asset Summary",
      icon: FileText,
    },
  ];

  return (
    <aside className="w-64 border-r border-slate-800/80 bg-[#0A0D14]/60 backdrop-blur-xl p-4 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-4rem)]">
      <div className="space-y-1.5">
        <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400 px-3 py-2">
          Diagnostic Navigation
        </div>

        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3.5 py-3 rounded-xl text-left transition-all select-none ${
                isActive
                  ? "bg-slate-800/90 text-cyan-300 border border-cyan-500/40 shadow-glow-cyan font-semibold"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent"
              }`}
            >
              <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? "text-cyan-400" : "text-slate-400"}`} />
              <div className="overflow-hidden">
                <div className="text-xs leading-tight truncate">{item.label}</div>
                <div className="text-[10px] font-mono text-slate-400 truncate mt-0.5">{item.sub}</div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Footer Info */}
      <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800/80 text-[11px] text-slate-400 font-mono">
        <div className="flex items-center gap-2 text-emerald-400 font-semibold mb-1">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          Backend Ready
        </div>
        <div>FastAPI Port: 8000</div>
        <div>MCP Port: 8001</div>
      </div>
    </aside>
  );
};
