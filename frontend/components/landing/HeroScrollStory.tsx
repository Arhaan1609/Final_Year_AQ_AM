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
  ArrowDown,
  Sparkles,
  Eye,
  EyeOff,
} from "lucide-react";

export const HeroScrollStory: React.FC = () => {
  const [progress, setProgress] = useState<number>(0);
  const [hudVisible, setHudVisible] = useState<boolean>(true);

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
        {/* ─── HUD VISIBILITY CONTROLS (BOTTOM-LEFT) ─── */}
        <div className="absolute bottom-6 left-6 z-30 pointer-events-auto flex items-center gap-3">
          <button
            onClick={() => setHudVisible(!hudVisible)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-950/80 backdrop-blur-md border border-slate-700/60 text-slate-300 hover:text-white hover:border-cyan-500/60 text-xs font-mono transition-all shadow-lg active:scale-95"
            title="Toggle telemetry HUD visibility"
          >
            {hudVisible ? (
              <>
                <EyeOff className="w-3.5 h-3.5 text-cyan-400" />
                <span>Hide HUD</span>
              </>
            ) : (
              <>
                <Eye className="w-3.5 h-3.5 text-cyan-400" />
                <span>Show HUD</span>
              </>
            )}
          </button>

          <div className="px-3 py-1.5 rounded-xl bg-slate-950/80 backdrop-blur-md border border-slate-700/60 text-slate-400 text-xs font-mono shadow-lg">
            <span>DECONSTRUCT: </span>
            <span className="text-cyan-400 font-bold">{progress}%</span>
          </div>
        </div>

        {/* ─── HUD OVERLAYS (NON-BLOCKING PERIMETER POSITIONING) ─── */}
        {hudVisible && (
          <>
            {/* ─── STAGE 1 (0% – 25%): ASSEMBLED TRUCK INTRO (TOP-LEFT POSITIONED) ─── */}
            <div
              className={`absolute top-28 left-6 md:left-12 max-w-lg transition-all duration-700 pointer-events-none ${
                isStage1
                  ? "opacity-100 translate-y-0"
                  : "opacity-0 -translate-y-8"
              }`}
            >
              <div className="p-6 rounded-2xl bg-slate-950/70 backdrop-blur-xl border border-cyan-500/30 text-left shadow-2xl space-y-3 pointer-events-auto">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-[11px] font-mono font-bold tracking-wider uppercase">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>EV Fleet Battery Intelligence</span>
                </div>

                <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white leading-tight">
                  74 ML Models. <br />
                  <span className="bg-gradient-to-r from-cyan-400 via-emerald-400 to-teal-200 bg-clip-text text-transparent">
                    One Fleet. Zero Surprises.
                  </span>
                </h1>

                <p className="text-xs text-slate-300 font-light leading-relaxed">
                  Real-time cyber-physical digital twin, multi-zone thermal safety, and non-linear knee prognostics.
                </p>

                <div className="pt-2 flex items-center gap-3">
                  <Link
                    href="/dashboard"
                    className="px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs shadow-md transition-all active:scale-95 flex items-center gap-1.5"
                  >
                    <Activity className="w-3.5 h-3.5" />
                    <span>Open Command Center</span>
                  </Link>
                </div>

                <div className="pt-2 flex items-center gap-2 text-cyan-400 font-mono text-[11px] animate-pulse">
                  <ArrowDown className="w-3.5 h-3.5" />
                  <span>Scroll down to deconstruct truck architecture</span>
                </div>
              </div>
            </div>

            {/* ─── STAGE 2 (25% – 55%): CAB EXPANSION (FAR-LEFT HUD) ─── */}
            <div
              className={`absolute top-28 left-6 md:left-12 max-w-sm transition-all duration-700 pointer-events-none ${
                isStage2
                  ? "opacity-100 translate-x-0"
                  : "opacity-0 -translate-x-12"
              }`}
            >
              <div className="p-5 rounded-2xl bg-slate-950/80 backdrop-blur-xl border border-cyan-500/40 text-left shadow-2xl space-y-3 pointer-events-auto">
                <div className="flex items-center gap-2 text-cyan-400 text-xs font-mono font-bold uppercase">
                  <Zap className="w-4 h-4 text-cyan-400" />
                  <span>Module A • State Estimation</span>
                </div>

                <h2 className="text-lg font-bold text-white tracking-tight">
                  Cab Lift & High-Voltage Telemetry
                </h2>

                <div className="grid grid-cols-2 gap-2 pt-1 font-mono">
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800">
                    <div className="text-[9px] text-slate-400 uppercase">SoC (KNN)</div>
                    <div className="text-lg font-bold text-cyan-400">95.8%</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800">
                    <div className="text-[9px] text-slate-400 uppercase">SoH (XGB)</div>
                    <div className="text-lg font-bold text-emerald-400">99.2%</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800">
                    <div className="text-[9px] text-slate-400 uppercase">RUL Cycles</div>
                    <div className="text-lg font-bold text-purple-400">1,234</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800">
                    <div className="text-[9px] text-slate-400 uppercase">Est. Range</div>
                    <div className="text-lg font-bold text-amber-400">119.5 km</div>
                  </div>
                </div>
              </div>
            </div>

            {/* ─── STAGE 3 (55% – 80%): CHASSIS EXPOSURE (FAR-RIGHT HUD) ─── */}
            <div
              className={`absolute top-28 right-6 md:right-12 max-w-sm transition-all duration-700 pointer-events-none ${
                isStage3
                  ? "opacity-100 translate-x-0"
                  : "opacity-0 translate-x-12"
              }`}
            >
              <div className="p-5 rounded-2xl bg-slate-950/80 backdrop-blur-xl border border-emerald-500/40 text-left shadow-2xl space-y-3 pointer-events-auto">
                <div className="flex items-center gap-2 text-emerald-400 text-xs font-mono font-bold uppercase">
                  <Flame className="w-4 h-4 text-emerald-400" />
                  <span>Module B • Thermal Safety</span>
                </div>

                <h2 className="text-lg font-bold text-white tracking-tight">
                  Chassis Rails & Cooling Matrix
                </h2>

                <div className="space-y-2 font-mono text-xs">
                  <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 flex justify-between items-center">
                    <span className="text-slate-300">Zone 1 (Battery Array)</span>
                    <span className="font-bold text-emerald-400">33.2°C (Safe)</span>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 flex justify-between items-center">
                    <span className="text-slate-300">Zone 2 (Power Controller)</span>
                    <span className="font-bold text-amber-400">41.5°C (Warm)</span>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 flex justify-between items-center">
                    <span className="text-slate-300">Zone 3 (Motor Assembly)</span>
                    <span className="font-bold text-purple-400">54.0°C</span>
                  </div>
                </div>

                <div className="p-2.5 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-[11px] font-mono flex items-center gap-2">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                  <span>Runaway Risk: 0.00% (RF 200T)</span>
                </div>
              </div>
            </div>

            {/* ─── STAGE 4 (80% – 100%): 4-TIER EXPLODED PACK (SIDEBAR + COMPACT BOTTOM-RIGHT CTA) ─── */}
            <div
              className={`absolute top-28 left-6 md:left-12 max-w-sm transition-all duration-700 pointer-events-none ${
                isStage4
                  ? "opacity-100 translate-x-0"
                  : "opacity-0 -translate-x-12"
              }`}
            >
              <div className="p-5 rounded-2xl bg-slate-950/85 backdrop-blur-xl border border-purple-500/50 shadow-2xl space-y-3 pointer-events-auto">
                <div className="flex items-center gap-2 text-purple-400 text-xs font-mono font-bold uppercase">
                  <Cpu className="w-4 h-4 text-purple-400" />
                  <span>Module C • Exploded Pack & Knee</span>
                </div>

                <h2 className="text-lg font-bold text-white tracking-tight">
                  72V 150Ah Modular Cell Stacks
                </h2>

                <div className="space-y-2 font-mono text-xs">
                  <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Knee Margin:</span>
                    <strong className="text-purple-400">850 Cycles (XGB)</strong>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Driver AI Score:</span>
                    <strong className="text-cyan-400">0.32 (Eco-Pro)</strong>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Degradation:</span>
                    <strong className="text-emerald-400">-0.4% / year</strong>
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom-Right Direct Launch CTA on Stage 4 */}
            <div
              className={`absolute bottom-6 right-6 z-30 transition-all duration-700 pointer-events-none ${
                isStage4
                  ? "opacity-100 translate-y-0"
                  : "opacity-0 translate-y-8"
              }`}
            >
              <Link
                href="/dashboard"
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 via-cyan-600 to-emerald-600 hover:opacity-90 text-white font-bold text-xs shadow-xl transition-all pointer-events-auto flex items-center gap-2 active:scale-95"
              >
                <span>Launch Diagnostics Dashboard</span>
                <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          </>
        )}
      </ScrollImageSequence>
    </section>
  );
};
export default HeroScrollStory;
