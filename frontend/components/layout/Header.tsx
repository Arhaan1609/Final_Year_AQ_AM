"use client";

import React from "react";
import Link from "next/link";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { Sparkles, Sun, Moon, ArrowLeft, Activity } from "lucide-react";
import { getVehicleTriage, triageLabel } from "../../lib/triage";

export const Header: React.FC = () => {
  const {
    theme,
    toggleTheme,
    vehicles,
    selectedVehicleId,
    setSelectedVehicle,
    isMock,
    setIsMock,
    copilotOpen,
    setCopilotOpen,
  } = useFleetStore();

  const selectedVehicle = vehicles.find((v) => v.id === selectedVehicleId) || vehicles[0];

  return (
    <header className="h-14 border-b border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-[#0A0D14]/95 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30 transition-colors">
      {/* Left: Brand Identity & Landing Link */}
      <div className="flex items-center gap-4">
        <Link
          href="/"
          className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Landing</span>
        </Link>

        <div className="h-4 w-px bg-slate-200 dark:bg-slate-800" />

        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-lg bg-emerald-600 flex items-center justify-center text-white font-extrabold text-[11px] shadow-sm">
            EV
          </div>
          <span className="text-sm font-bold text-slate-900 dark:text-slate-100 tracking-tight whitespace-nowrap">
            EV Battery Intelligence
          </span>
          <span className="hidden lg:inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-mono font-medium bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            74 Models Live
          </span>
        </div>
      </div>

      {/* Center: Clean Minimalist VIN Selector */}
      <div className="hidden md:flex items-center gap-2 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-3 py-1 rounded-lg">
        <span className="text-[10px] font-mono uppercase font-semibold text-slate-400">VIN:</span>
        <select
          value={selectedVehicleId}
          onChange={(e) => setSelectedVehicle(e.target.value)}
          className="bg-transparent text-xs font-mono font-bold text-slate-800 dark:text-slate-200 focus:outline-none cursor-pointer pr-1"
        >
          {vehicles.map((v) => {
            const triage = getVehicleTriage(v);
            return (
              <option key={v.id} value={v.id} className="bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-200">
                {v.id} — {v.model.split(" ")[0]} ({triageLabel(triage)}) • {v.fleet.split(" ")[0]}
              </option>
            );
          })}
        </select>
      </div>

      {/* Right: Controls & Copilot Button */}
      <div className="flex items-center gap-2.5">
        {/* Latency badge */}
        <div className="hidden xl:flex items-center gap-1.5 text-[11px] font-mono text-slate-500 dark:text-slate-400">
          <Activity className="w-3.5 h-3.5 text-emerald-500" />
          <span>12ms</span>
        </div>

        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
          title={`Switch to ${theme === "light" ? "Dark" : "Light"} mode`}
        >
          {theme === "light" ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4 text-amber-400" />}
        </button>

        {/* Copilot button */}
        <button
          onClick={() => setCopilotOpen(!copilotOpen)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 text-xs font-semibold hover:opacity-90 transition-all shadow-sm"
        >
          <Sparkles className="w-3.5 h-3.5 text-emerald-400 dark:text-emerald-600" />
          <span>Copilot</span>
        </button>
      </div>
    </header>
  );
};
