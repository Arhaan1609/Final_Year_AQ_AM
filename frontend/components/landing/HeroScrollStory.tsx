"use client";

import React, { useState, useEffect, useRef } from "react";
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
  Play,
  Pause,
  RotateCcw,
  Info,
  X,
} from "lucide-react";

export const HeroScrollStory: React.FC = () => {
  const [progress, setProgress] = useState<number>(0);
  const [hudVisible, setHudVisible] = useState<boolean>(true);
  const [isAutoPlaying, setIsAutoPlaying] = useState<boolean>(false);
  const [activeHotspot, setActiveHotspot] = useState<string | null>(null);

  // Stage flags based on scroll progress (0 - 100)
  const isStage1 = progress < 25; // Assembled Heavy Truck
  const isStage2 = progress >= 25 && progress < 55; // Cab lifting (Module A)
  const isStage3 = progress >= 55 && progress < 80; // Chassis rails (Module B)
  const isStage4 = progress >= 80; // 4-Tier Exploded Pack (Module C)

  // Auto-Demo Scroll Loop
  useEffect(() => {
    let animFrame: number;
    let targetScroll = window.scrollY;

    if (isAutoPlaying) {
      const step = () => {
        const maxScroll = 4000;
        if (window.scrollY < maxScroll) {
          window.scrollBy({ top: 12, behavior: "auto" });
          animFrame = requestAnimationFrame(step);
        } else {
          setIsAutoPlaying(false);
        }
      };
      animFrame = requestAnimationFrame(step);
    }

    return () => {
      if (animFrame) cancelAnimationFrame(animFrame);
    };
  }, [isAutoPlaying]);

  const toggleAutoPlay = () => {
    if (!isAutoPlaying && window.scrollY >= 3800) {
      window.scrollTo({ top: 0, behavior: "smooth" });
      setTimeout(() => setIsAutoPlaying(true), 600);
    } else {
      setIsAutoPlaying(!isAutoPlaying);
    }
  };

  const resetToTop = () => {
    setIsAutoPlaying(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

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
        {/* ─── FLOATING PRESENTATION CONTROLLER (BOTTOM-LEFT) ─── */}
        <div className="absolute bottom-6 left-6 z-40 pointer-events-auto flex flex-wrap items-center gap-2.5">
          {/* Auto-Demo Presentation Button */}
          <button
            onClick={toggleAutoPlay}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-mono font-bold transition-all shadow-xl active:scale-95 ${
              isAutoPlaying
                ? "bg-amber-500 text-slate-950 border border-amber-400 animate-pulse"
                : "bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white border border-cyan-400/40"
            }`}
            title="Auto-scroll presentation for examiners/judges"
          >
            {isAutoPlaying ? (
              <>
                <Pause className="w-3.5 h-3.5 fill-current" />
                <span>Pause Auto-Demo</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Auto-Demo (Examiner Mode)</span>
              </>
            )}
          </button>

          {/* Reset button */}
          <button
            onClick={resetToTop}
            className="p-2 rounded-xl bg-slate-950/80 backdrop-blur-md border border-slate-700/80 text-slate-300 hover:text-white hover:border-cyan-500/60 transition-all shadow-lg active:scale-95"
            title="Reset animation to beginning"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          {/* Toggle HUD */}
          <button
            onClick={() => setHudVisible(!hudVisible)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-950/80 backdrop-blur-md border border-slate-700/80 text-slate-300 hover:text-white hover:border-cyan-500/60 text-xs font-mono transition-all shadow-lg active:scale-95"
            title="Toggle telemetry HUD visibility"
          >
            {hudVisible ? (
              <>
                <EyeOff className="w-3.5 h-3.5 text-cyan-400" />
                <span className="hidden sm:inline">Hide HUD</span>
              </>
            ) : (
              <>
                <Eye className="w-3.5 h-3.5 text-cyan-400" />
                <span className="hidden sm:inline">Show HUD</span>
              </>
            )}
          </button>

          {/* Progress Indicator */}
          <div className="px-3 py-2 rounded-xl bg-slate-950/80 backdrop-blur-md border border-slate-700/80 text-slate-400 text-xs font-mono shadow-lg">
            <span>SCRUB: </span>
            <span className="text-cyan-400 font-bold">{progress}%</span>
          </div>
        </div>

        {/* ─── INTERACTIVE 3D HOTSPOT PINS OVER THE TRUCK ─── */}
        <div className="absolute inset-0 pointer-events-none z-30">
          {/* Hotspot 1: Cab / Telematics Hub (Active on Stage 1 & 2) */}
          {(isStage1 || isStage2) && (
            <div className="absolute top-[38%] left-[36%] pointer-events-auto">
              <button
                onClick={() => setActiveHotspot(activeHotspot === "cab" ? null : "cab")}
                className="relative group flex items-center justify-center"
              >
                <span className="absolute w-7 h-7 bg-cyan-400/30 rounded-full animate-ping" />
                <span className="relative w-5 h-5 rounded-full bg-cyan-500 border-2 border-white flex items-center justify-center text-[10px] font-bold text-slate-950 shadow-[0_0_15px_rgba(6,182,212,0.8)] group-hover:scale-125 transition-transform">
                  +
                </span>
                <span className="absolute left-7 px-2.5 py-1 rounded-lg bg-slate-950/90 border border-cyan-500/40 text-[10px] font-mono text-cyan-300 font-bold whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-md">
                  CAN-Bus BMS Gateway
                </span>
              </button>
            </div>
          )}

          {/* Hotspot 2: Chassis Inverter (Active on Stage 3) */}
          {isStage3 && (
            <div className="absolute top-[52%] right-[42%] pointer-events-auto">
              <button
                onClick={() => setActiveHotspot(activeHotspot === "chassis" ? null : "chassis")}
                className="relative group flex items-center justify-center"
              >
                <span className="absolute w-7 h-7 bg-emerald-400/30 rounded-full animate-ping" />
                <span className="relative w-5 h-5 rounded-full bg-emerald-500 border-2 border-white flex items-center justify-center text-[10px] font-bold text-slate-950 shadow-[0_0_15px_rgba(16,185,129,0.8)] group-hover:scale-125 transition-transform">
                  +
                </span>
                <span className="absolute left-7 px-2.5 py-1 rounded-lg bg-slate-950/90 border border-emerald-500/40 text-[10px] font-mono text-emerald-300 font-bold whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-md">
                  Active Cooling Rail & Inverter
                </span>
              </button>
            </div>
          )}

          {/* Hotspot 3: 4-Tier Exploded Battery Array (Active on Stage 4) */}
          {isStage4 && (
            <div className="absolute top-[40%] left-[34%] pointer-events-auto">
              <button
                onClick={() => setActiveHotspot(activeHotspot === "battery" ? null : "battery")}
                className="relative group flex items-center justify-center"
              >
                <span className="absolute w-8 h-8 bg-purple-400/30 rounded-full animate-ping" />
                <span className="relative w-6 h-6 rounded-full bg-purple-500 border-2 border-white flex items-center justify-center text-xs font-bold text-white shadow-[0_0_20px_rgba(168,85,247,0.9)] group-hover:scale-125 transition-transform">
                  +
                </span>
                <span className="absolute left-8 px-2.5 py-1 rounded-lg bg-slate-950/90 border border-purple-500/40 text-[10px] font-mono text-purple-300 font-bold whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-md">
                  72V 150Ah Modular LFP Stack
                </span>
              </button>
            </div>
          )}
        </div>

        {/* ─── EXPANDABLE HOTSPOT DETAIL MODAL ─── */}
        {activeHotspot && (
          <div className="absolute top-28 right-6 md:right-12 z-40 max-w-sm p-5 rounded-2xl bg-slate-950/90 backdrop-blur-xl border border-cyan-500/50 shadow-2xl text-left pointer-events-auto animate-in fade-in zoom-in-95 duration-200">
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center gap-2 text-cyan-400 text-xs font-mono font-bold uppercase">
                <Info className="w-4 h-4" />
                <span>Component Telemetry Specs</span>
              </div>
              <button
                onClick={() => setActiveHotspot(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {activeHotspot === "cab" && (
              <div className="space-y-2 text-xs font-mono text-slate-300">
                <div className="font-bold text-sm text-white">Central Telematic Control Unit (TCU)</div>
                <p className="text-[11px] text-slate-400 font-sans">
                  Samples pack voltage, current, and module temperature over high-speed CAN 2.0B (500 kbps) for sub-second ML regression.
                </p>
                <div className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-1 text-[11px]">
                  <div className="flex justify-between"><span>Sampling Rate:</span><strong className="text-cyan-400">10 Hz</strong></div>
                  <div className="flex justify-between"><span>Inference Latency:</span><strong className="text-emerald-400">8.4 ms</strong></div>
                  <div className="flex justify-between"><span>Protocol:</span><strong className="text-purple-400">FastAPI REST / FastMCP</strong></div>
                </div>
              </div>
            )}

            {activeHotspot === "chassis" && (
              <div className="space-y-2 text-xs font-mono text-slate-300">
                <div className="font-bold text-sm text-white">Inverter & Thermal Cooling Rail</div>
                <p className="text-[11px] text-slate-400 font-sans">
                  Dual-loop liquid cooling circulation keeping MOSFET junction temperatures below 60°C under maximum 60A acceleration draw.
                </p>
                <div className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-1 text-[11px]">
                  <div className="flex justify-between"><span>Inverter Temp:</span><strong className="text-amber-400">41.5°C</strong></div>
                  <div className="flex justify-between"><span>Motor Load Temp:</span><strong className="text-purple-400">54.0°C</strong></div>
                  <div className="flex justify-between"><span>Fault Classifier:</span><strong className="text-emerald-400">RF 200T (100% Safe)</strong></div>
                </div>
              </div>
            )}

            {activeHotspot === "battery" && (
              <div className="space-y-2 text-xs font-mono text-slate-300">
                <div className="font-bold text-sm text-white">4-Tier 72V 150Ah LFP Pack</div>
                <p className="text-[11px] text-slate-400 font-sans">
                  Lithium Iron Phosphate pouch architecture with laser-welded copper busbars, active cell balancing, and deep non-linear knee prognostics.
                </p>
                <div className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-1 text-[11px]">
                  <div className="flex justify-between"><span>Nominal Voltage:</span><strong className="text-cyan-400">72.0 V (24S)</strong></div>
                  <div className="flex justify-between"><span>Internal Resistance:</span><strong className="text-emerald-400">0.035 Ω</strong></div>
                  <div className="flex justify-between"><span>Knee Margin:</span><strong className="text-purple-400">850 Cycles (XGB)</strong></div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ─── HUD OVERLAYS (PERIMETER POSITIONING) ─── */}
        {hudVisible && (
          <>
            {/* ─── STAGE 1 (0% – 25%): ASSEMBLED TRUCK (TOP-LEFT) ─── */}
            <div
              className={`absolute top-28 left-6 md:left-12 max-w-lg transition-all duration-700 pointer-events-none ${
                isStage1
                  ? "opacity-100 translate-y-0"
                  : "opacity-0 -translate-y-8"
              }`}
            >
              <div className="p-6 rounded-2xl bg-slate-950/75 backdrop-blur-xl border border-cyan-500/30 text-left shadow-2xl space-y-3 pointer-events-auto">
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
                  Cyber-physical digital twin, multi-zone thermal runaway prevention, and deep non-linear knee prognostics.
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
                  <span>Scroll or click Auto-Demo to deconstruct</span>
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
                    <div className="text-[8px] text-slate-500 font-mono">R²=0.9958</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800">
                    <div className="text-[9px] text-slate-400 uppercase">SoH (XGB)</div>
                    <div className="text-lg font-bold text-emerald-400">99.2%</div>
                    <div className="text-[8px] text-slate-500 font-mono">R²=0.9820</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800">
                    <div className="text-[9px] text-slate-400 uppercase">RUL Cycles</div>
                    <div className="text-lg font-bold text-purple-400">1,234</div>
                    <div className="text-[8px] text-slate-500 font-mono">R²=0.9997</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800">
                    <div className="text-[9px] text-slate-400 uppercase">Est. Range</div>
                    <div className="text-lg font-bold text-amber-400">119.5 km</div>
                    <div className="text-[8px] text-slate-500 font-mono">XGBoost (R)</div>
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

            {/* ─── STAGE 4 (80% – 100%): 4-TIER EXPLODED PACK (FAR-LEFT HUD) ─── */}
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
