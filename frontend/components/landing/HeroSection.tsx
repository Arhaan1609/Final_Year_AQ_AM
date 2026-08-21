"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { CyberBatteryCanvas } from "./CyberBatteryCanvas";
import {
  ArrowRight,
  Sparkles,
  Cpu,
  ShieldCheck,
  Zap,
  Activity,
  Flame,
  Gauge,
  TrendingDown,
  Terminal,
} from "lucide-react";

export const HeroSection: React.FC = () => {
  const [activeTemp, setActiveTemp] = useState(33.2);

  // Subtle cyclic oscillation to show real-time dynamic thermal reactivity in 3D canvas
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveTemp((prev) => +(31 + Math.sin(Date.now() / 3000) * 4).toFixed(1));
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative pt-32 pb-20 px-6 sm:px-10 max-w-7xl mx-auto overflow-hidden">
      {/* Background Ambient Glow Orbs */}
      <div className="absolute top-20 left-1/4 w-96 h-96 bg-emerald-500/10 dark:bg-emerald-500/15 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-40 right-1/4 w-96 h-96 bg-cyan-500/10 dark:bg-cyan-500/15 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
        {/* Left Column: Headline & Value Proposition */}
        <div className="lg:col-span-7 flex flex-col items-start text-left">
          {/* Top Tech Pill */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-700/60 text-emerald-700 dark:text-emerald-300 text-xs font-semibold mb-6 shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-emerald-500 animate-pulse" />
            <span>Tri-Pillar Cyber-Physical ML Core • 74 Production Models</span>
          </div>

          {/* Main Hero Headline */}
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-slate-50 leading-[1.12] mb-6">
            Autonomous Battery Intelligence for{" "}
            <span className="text-gradient-emerald">Commercial EV Fleets</span>.
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-slate-600 dark:text-slate-300 max-w-2xl mb-8 leading-relaxed">
            Predict State of Charge, prevent multi-zone thermal faults ($F_1 = 0.997$), and forecast non-linear degradation knee points across commercial electric vehicle fleets using 74 production-grade ML & Deep Learning models.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center gap-4 mb-10 w-full sm:w-auto">
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-bold text-sm shadow-lg shadow-emerald-600/30 hover:shadow-emerald-600/50 transition-all hover:scale-105 active:scale-95 cursor-pointer"
            >
              <span>Launch Live Fleet Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 font-semibold text-sm hover:bg-slate-50 dark:hover:bg-slate-800 shadow-sm transition-all"
            >
              <Terminal className="w-4 h-4 text-cyan-500" />
              <span>FastAPI Docs (11 Endpoints)</span>
            </a>
          </div>

          {/* Micro Telemetry Features Badge Strip */}
          <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-slate-500 dark:text-slate-400 border-t border-slate-200/80 dark:border-slate-800/80 pt-6 w-full">
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span>Zero-Leakage Scalers</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Flame className="w-4 h-4 text-amber-500" />
              <span>3-Zone Thermodynamic Safety</span>
            </div>
            <div className="flex items-center gap-1.5">
              <TrendingDown className="w-4 h-4 text-cyan-500" />
              <span>Knee-Point Accelerated Aging</span>
            </div>
          </div>
        </div>

        {/* Right Column: Interactive 3D Cybernetic Hologram */}
        <div className="lg:col-span-5 w-full">
          <CyberBatteryCanvas temperature={activeTemp} soc={94.5} />
        </div>
      </div>

      {/* Hero Real-time Stat Count-Up Strip */}
      <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
        <div className="app-card p-5 sm:p-6 bg-white/70 dark:bg-slate-900/60 backdrop-blur-xl border border-slate-200 dark:border-slate-800/80">
          <div className="text-xs font-medium text-slate-500 dark:text-slate-400">Models Evaluated</div>
          <div className="text-3xl sm:text-4xl font-extrabold text-cyan-600 dark:text-cyan-400 mt-1 font-mono">
            74
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 font-mono">
            sklearn • XGBoost • PyTorch
          </div>
        </div>

        <div className="app-card p-5 sm:p-6 bg-white/70 dark:bg-slate-900/60 backdrop-blur-xl border border-slate-200 dark:border-slate-800/80">
          <div className="text-xs font-medium text-slate-500 dark:text-slate-400">Fleet Telematics</div>
          <div className="text-3xl sm:text-4xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1 font-mono">
            930+ MB
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 font-mono">
            Euler HiLoad commercial fleet
          </div>
        </div>

        <div className="app-card p-5 sm:p-6 bg-white/70 dark:bg-slate-900/60 backdrop-blur-xl border border-slate-200 dark:border-slate-800/80">
          <div className="text-xs font-medium text-slate-500 dark:text-slate-400">Thermal Safety $F_1$</div>
          <div className="text-3xl sm:text-4xl font-extrabold text-purple-600 dark:text-purple-400 mt-1 font-mono">
            0.997
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 font-mono">
            99.71% 3-Zone Accuracy
          </div>
        </div>

        <div className="app-card p-5 sm:p-6 bg-white/70 dark:bg-slate-900/60 backdrop-blur-xl border border-slate-200 dark:border-slate-800/80">
          <div className="text-xs font-medium text-slate-500 dark:text-slate-400">REST Endpoints</div>
          <div className="text-3xl sm:text-4xl font-extrabold text-amber-600 dark:text-amber-400 mt-1 font-mono">
            11
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 font-mono">
            FastAPI Sub-second Inference
          </div>
        </div>
      </div>
    </section>
  );
};
