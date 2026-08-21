"use client";

import React, { useState } from "react";
import Link from "next/link";
import { ScrollImageSequence } from "../ui/ScrollImageSequence";
import {
  Zap,
  ShieldCheck,
  Cpu,
  Flame,
  Activity,
  ChevronRight,
  TrendingDown,
  ArrowDown,
  Sparkles,
} from "lucide-react";

export const HeroScrollStory: React.FC = () => {
  const [progress, setProgress] = useState<number>(0);

  // Stage flags based on scroll progress (0 - 100)
  const isStage1 = progress < 25; // Hero intro (Assembled Truck)
  const isStage2 = progress >= 25 && progress < 55; // Cab lifting (Module A State Estimation)
  const isStage3 = progress >= 55 && progress < 80; // Cargo removal (Module B Thermal Safety)
  const isStage4 = progress >= 80; // Exploded Battery Pack (Module C Knee Prognostics)

  return (
    <section className="relative w-full bg-[#0A0D14] text-white">
      {/* 300-Frame Apple-Style Pinned Canvas Sequence */}
      <ScrollImageSequence
        frameFolder="/sequence"
        frameCount={300}
        fileNamePrefix="ezgif-frame-"
        fileNameSuffix=".jpg"
        digitPadding={3}
        scrollDistance={4000}
        fit="cover"
        scrub={0.5}
        onProgress={(p) => setProgress(p)}
      >
        {/* ─── FLOATING TOP STATUS BAR ─── */}
        <div className="w-full flex items-center justify-between pointer-events-auto transition-opacity duration-300">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-950/80 backdrop-blur-md border border-cyan-500/30 text-cyan-400 text-xs font-mono shadow-lg">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span className="font-bold">CYBER-PHYSICAL DIGITAL TWIN</span>
            <span className="text-slate-500">|</span>
            <span className="text-slate-300">300 4K FRAMES</span>
          </div>

          <div className="flex items-center gap-3">
            <div className="px-3 py-1.5 rounded-full bg-slate-950/80 backdrop-blur-md border border-slate-800 text-slate-300 text-xs font-mono shadow-lg hidden sm:flex items-center gap-2">
              <span>DECONSTRUCTION:</span>
              <span className="text-cyan-400 font-bold">{progress}%</span>
            </div>
            <Link
              href="/dashboard"
              className="px-4 py-1.5 rounded-full bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-md transition-all flex items-center gap-1 active:scale-95"
            >
              <span>Live Platform</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* ─── STAGE 1 OVERLAY (0% – 25%): ASSEMBLED TRUCK HERO ─── */}
        <div
          className={`absolute inset-0 flex flex-col justify-center items-center text-center p-6 transition-all duration-700 pointer-events-none ${
            isStage1
              ? "opacity-100 translate-y-0"
              : "opacity-0 -translate-y-8"
          }`}
        >
          <div className="max-w-4xl mx-auto space-y-4">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-bold tracking-wider uppercase mb-2 shadow-[0_0_15px_rgba(6,182,212,0.2)]">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Next-Generation EV Fleet Intelligence</span>
            </div>

            <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-white leading-tight drop-shadow-2xl">
              74 ML Models. <br />
              <span className="bg-gradient-to-r from-cyan-400 via-emerald-400 to-teal-200 bg-clip-text text-transparent">
                One Fleet. Zero Surprises.
              </span>
            </h1>

            <p className="text-sm sm:text-base md:text-lg text-slate-300 max-w-2xl mx-auto font-light leading-relaxed drop-shadow">
              Enterprise cyber-physical battery diagnostics, real-time thermal runaway prevention, and non-linear knee-point prognostics for commercial EV fleets.
            </p>

            <div className="pt-6 flex flex-col sm:flex-row items-center justify-center gap-4 pointer-events-auto">
              <Link
                href="/dashboard"
                className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white font-bold text-sm shadow-[0_0_25px_rgba(6,182,212,0.4)] transition-all active:scale-95 flex items-center gap-2"
              >
                <Activity className="w-4 h-4" />
                <span>Open Fleet Command Center</span>
              </Link>
            </div>

            {/* Scroll Indicator Prompt */}
            <div className="pt-12 flex flex-col items-center gap-2 text-cyan-400 font-mono text-xs animate-bounce">
              <span>Scroll to deconstruct truck architecture</span>
              <ArrowDown className="w-4 h-4" />
            </div>
          </div>
        </div>

        {/* ─── STAGE 2 OVERLAY (25% – 55%): CAB EXPANSION & MODULE A STATE ESTIMATION ─── */}
        <div
          className={`absolute inset-0 flex items-center justify-start p-6 md:p-16 transition-all duration-700 pointer-events-none ${
            isStage2
              ? "opacity-100 translate-x-0"
              : "opacity-0 -translate-x-12"
          }`}
        >
          <div className="w-full max-w-md p-6 rounded-2xl bg-slate-950/80 backdrop-blur-xl border border-cyan-500/40 text-left shadow-2xl space-y-4 pointer-events-auto">
            <div className="flex items-center gap-2 text-cyan-400 text-xs font-mono font-bold tracking-widest uppercase">
              <Zap className="w-4 h-4 text-cyan-400" />
              <span>Module A • Macro State Estimation</span>
            </div>

            <h2 className="text-2xl font-extrabold text-white tracking-tight">
              Cab Aerodynamics & High-Voltage Telemetry
            </h2>
            <p className="text-xs text-slate-300 leading-relaxed font-light">
              As the aerodynamic cab expands, live multi-model regressors estimate core electrochemical parameters with sub-1% RMSE.
            </p>

            <div className="grid grid-cols-2 gap-3 pt-2 font-mono">
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <div className="text-[10px] text-slate-400 uppercase">State of Charge</div>
                <div className="text-xl font-bold text-cyan-400">95.8%</div>
                <div className="text-[9px] text-slate-500">KNN (R²=0.9958)</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <div className="text-[10px] text-slate-400 uppercase">State of Health</div>
                <div className="text-xl font-bold text-emerald-400">99.2%</div>
                <div className="text-[9px] text-slate-500">XGBoost (R²=0.982)</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <div className="text-[10px] text-slate-400 uppercase">RUL Cycles</div>
                <div className="text-xl font-bold text-purple-400">1,234</div>
                <div className="text-[9px] text-slate-500">GBoost (R²=0.9997)</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <div className="text-[10px] text-slate-400 uppercase">Range Per Charge</div>
                <div className="text-xl font-bold text-amber-400">119.5 km</div>
                <div className="text-[9px] text-slate-500">XGBoost Regressor</div>
              </div>
            </div>
          </div>
        </div>

        {/* ─── STAGE 3 OVERLAY (55% – 80%): CHASSIS EXPOSURE & MODULE B THERMAL SAFETY ─── */}
        <div
          className={`absolute inset-0 flex items-center justify-end p-6 md:p-16 transition-all duration-700 pointer-events-none ${
            isStage3
              ? "opacity-100 translate-x-0"
              : "opacity-0 translate-x-12"
          }`}
        >
          <div className="w-full max-w-md p-6 rounded-2xl bg-slate-950/80 backdrop-blur-xl border border-emerald-500/40 text-left shadow-2xl space-y-4 pointer-events-auto">
            <div className="flex items-center gap-2 text-emerald-400 text-xs font-mono font-bold tracking-widest uppercase">
              <Flame className="w-4 h-4 text-emerald-400" />
              <span>Module B • Multi-Zone Thermal Safety</span>
            </div>

            <h2 className="text-2xl font-extrabold text-white tracking-tight">
              Structural Chassis & Active Cooling Rails
            </h2>
            <p className="text-xs text-slate-300 leading-relaxed font-light">
              Container hull deconstructs to inspect structural rails, power electronics inverter, and multi-zone thermal gradients.
            </p>

            <div className="space-y-2.5 pt-2 font-mono text-xs">
              <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 flex justify-between items-center">
                <span className="text-slate-300 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  Zone 1 (Battery Array)
                </span>
                <span className="font-bold text-emerald-400">33.2°C (Safe)</span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 flex justify-between items-center">
                <span className="text-slate-300 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-amber-400" />
                  Zone 2 (Power Controller)
                </span>
                <span className="font-bold text-amber-400">41.5°C (Warm)</span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 flex justify-between items-center">
                <span className="text-slate-300 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-purple-400" />
                  Zone 3 (Motor Assembly)
                </span>
                <span className="font-bold text-purple-400">54.0°C (High Load)</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs font-mono flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span>Random Forest (200 Trees): 0.00% Runaway Probability</span>
            </div>
          </div>
        </div>

        {/* ─── STAGE 4 OVERLAY (80% – 100%): 4-TIER EXPLODED BATTERY PACK & MODULE C PROGNOSTICS ─── */}
        <div
          className={`absolute inset-0 flex flex-col justify-end items-center p-6 md:p-12 text-center transition-all duration-700 pointer-events-none ${
            isStage4
              ? "opacity-100 translate-y-0"
              : "opacity-0 translate-y-8"
          }`}
        >
          <div className="w-full max-w-3xl p-6 rounded-2xl bg-slate-950/85 backdrop-blur-xl border border-purple-500/50 shadow-2xl space-y-4 pointer-events-auto">
            <div className="flex items-center justify-center gap-2 text-purple-400 text-xs font-mono font-bold tracking-widest uppercase">
              <Cpu className="w-4 h-4 text-purple-400" />
              <span>Module C • 4-Tier Exploded Pack & Knee Prognostics</span>
            </div>

            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              LFP Pouch Cell Array & Knee Degradation Frontier
            </h2>

            <p className="text-xs sm:text-sm text-slate-300 max-w-xl mx-auto font-light leading-relaxed">
              Exploded 72V 150Ah modular architecture showing direct cell stack coupling, high-voltage orange busbars, and deep non-linear knee aging curves.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 font-mono text-xs">
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-left">
                <div className="text-[10px] text-slate-400 uppercase">Knee-Point Margin</div>
                <div className="text-lg font-bold text-purple-400">850 Cycles</div>
                <div className="text-[9px] text-slate-500">XGBoost Booster</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-left">
                <div className="text-[10px] text-slate-400 uppercase">Driver AI (Aggressiveness)</div>
                <div className="text-lg font-bold text-cyan-400">0.32 (Eco-Pro)</div>
                <div className="text-[9px] text-slate-500">BA-BMS Engine</div>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-left">
                <div className="text-[10px] text-slate-400 uppercase">Annual SOH Penalty</div>
                <div className="text-lg font-bold text-emerald-400">-0.4% / yr</div>
                <div className="text-[9px] text-slate-500">Controlled Stress Index</div>
              </div>
            </div>

            <div className="pt-3 flex justify-center gap-4">
              <Link
                href="/dashboard"
                className="px-8 py-3 rounded-xl bg-gradient-to-r from-purple-600 via-cyan-600 to-emerald-600 hover:opacity-90 text-white font-bold text-sm shadow-[0_0_25px_rgba(147,51,234,0.4)] transition-all active:scale-95 flex items-center gap-2"
              >
                <span>Launch Diagnostics Dashboard</span>
                <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </ScrollImageSequence>
    </section>
  );
};
export default HeroScrollStory;
