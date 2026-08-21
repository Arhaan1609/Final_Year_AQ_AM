"use client";

import React from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { Badge } from "../ui/Badge";
import { Sparkles, Shield, Cpu, ToggleLeft, ToggleRight, Radio } from "lucide-react";

export const Header: React.FC = () => {
  const {
    vehicles,
    selectedVehicleId,
    setSelectedVehicle,
    isMock,
    setIsMock,
    copilotOpen,
    setCopilotOpen,
  } = useFleetStore();

  return (
    <header className="h-16 border-b border-slate-800/80 bg-[#0A0D14]/80 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Brand Title */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-600 to-emerald-500 flex items-center justify-center text-slate-950 font-extrabold text-sm shadow-glow-cyan">
          EV
        </div>
        <div>
          <h1 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            EV Battery Intelligence Platform
            <Badge variant="emerald" size="sm" dot>Production v1.0</Badge>
          </h1>
          <p className="text-[10px] text-slate-400 font-mono">
            74 ML & DL Models • Tri-Pillar Architecture
          </p>
        </div>
      </div>

      {/* Center Vehicle Switcher */}
      <div className="hidden md:flex items-center gap-2 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-xl">
        <span className="text-[11px] font-mono text-slate-400">Chassis:</span>
        <select
          value={selectedVehicleId}
          onChange={(e) => setSelectedVehicle(e.target.value)}
          className="bg-transparent text-xs font-mono font-bold text-cyan-400 focus:outline-none cursor-pointer"
        >
          {vehicles.map((v) => (
            <option key={v.id} value={v.id} className="bg-slate-900 text-slate-200">
              {v.id} — {v.model.split(" ")[0]} ({v.status.toUpperCase()})
            </option>
          ))}
        </select>
      </div>

      {/* Right Controls: Live/Mock toggle & Copilot */}
      <div className="flex items-center gap-3">
        {/* Mock/Live Mode Toggle */}
        <button
          onClick={() => setIsMock(!isMock)}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-mono font-medium transition-all ${
            isMock
              ? "bg-slate-900/80 border-slate-700 text-slate-300 hover:border-slate-600"
              : "bg-emerald-950/40 border-emerald-500/40 text-emerald-300 shadow-glow-emerald"
          }`}
        >
          <Radio className={`w-3.5 h-3.5 ${isMock ? "text-slate-400" : "text-emerald-400 animate-pulse"}`} />
          <span>{isMock ? "Mock Mode" : "Live API (8000)"}</span>
        </button>

        {/* Copilot Button */}
        <button
          onClick={() => setCopilotOpen(!copilotOpen)}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white font-semibold text-xs transition-all hover:scale-105 shadow-glow-cyan"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Fleet Copilot</span>
        </button>
      </div>
    </header>
  );
};
