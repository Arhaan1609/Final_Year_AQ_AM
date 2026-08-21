"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { Badge } from "../ui/Badge";
import { Sparkles, Sun, Moon, Radio, Search } from "lucide-react";

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

  const [headerSearch, setHeaderSearch] = useState("");

  const matchingVehicles = headerSearch
    ? vehicles.filter(
        (v) =>
          v.id.toLowerCase().includes(headerSearch.toLowerCase()) ||
          v.driver.toLowerCase().includes(headerSearch.toLowerCase()) ||
          v.fleet.toLowerCase().includes(headerSearch.toLowerCase())
      )
    : vehicles;

  return (
    <header className="h-16 border-b border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-[#0A0D14]/80 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-30 transition-colors">
      {/* Brand Title with link back to landing page */}
      <div className="flex items-center gap-3">
        <Link
          href="/"
          className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-600 to-emerald-600 flex items-center justify-center text-white font-extrabold text-xs shadow-sm hover:scale-105 transition-transform"
          title="Back to Landing Page"
        >
          EV
        </Link>
        <div>
          <div className="flex items-center gap-2">
            <Link href="/" className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors">
              EV Battery Intelligence
            </Link>
            <Badge variant="emerald" size="sm" dot>v1.0</Badge>
          </div>
          <p className="text-[10px] text-slate-500 dark:text-slate-400 font-mono hidden sm:block">
            {vehicles.length} Fleet Vehicles • 74 Models
          </p>
        </div>
      </div>

      {/* Center Vehicle Switcher & Fast Search */}
      <div className="hidden md:flex items-center gap-2 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-3 py-1.5 rounded-xl">
        <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400">Chassis:</span>
        <select
          value={selectedVehicleId}
          onChange={(e) => setSelectedVehicle(e.target.value)}
          className="bg-transparent text-xs font-mono font-bold text-cyan-600 dark:text-cyan-400 focus:outline-none cursor-pointer max-w-[260px]"
        >
          {vehicles.map((v) => (
            <option key={v.id} value={v.id} className="bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-200">
              {v.id} — {v.model.split(" ")[0]} ({v.status.toUpperCase()}) • {v.driver.split(" ")[0]}
            </option>
          ))}
        </select>
      </div>

      {/* Right Controls: Theme toggle, Live/Mock toggle & Copilot */}
      <div className="flex items-center gap-2.5">
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-700 transition-all"
          title={`Switch to ${theme === "light" ? "Dark" : "Light"} mode`}
        >
          {theme === "light" ? <Moon className="w-3.5 h-3.5" /> : <Sun className="w-3.5 h-3.5" />}
        </button>

        {/* Mock/Live Mode Toggle */}
        <button
          onClick={() => setIsMock(!isMock)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-mono font-medium transition-all ${
            isMock
              ? "bg-slate-100 dark:bg-slate-900 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300"
              : "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-500/40 text-emerald-700 dark:text-emerald-300"
          }`}
          title="Toggle between Live FastAPI backend (8000) and realistic Mock Mode"
        >
          <Radio className={`w-3 h-3 ${isMock ? "text-slate-400" : "text-emerald-600 dark:text-emerald-400 animate-pulse"}`} />
          <span className="hidden sm:inline">{isMock ? "Mock Mode" : "Live API"}</span>
        </button>

        {/* Copilot Button */}
        <button
          onClick={() => setCopilotOpen(!copilotOpen)}
          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white font-semibold text-xs transition-all hover:scale-105 shadow-sm"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Fleet Copilot</span>
        </button>
      </div>
    </header>
  );
};
