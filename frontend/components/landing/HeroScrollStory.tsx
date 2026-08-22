"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ScrollImageSequence } from "../ui/ScrollImageSequence";
import { MaskedHeading } from "../ui/MaskedHeading";
import {
  Activity,
  ChevronRight,
  ArrowDown,
  Sparkles,
  Play,
  Pause,
  RotateCcw,
  Cpu,
  Flame,
  Gauge,
  ShieldCheck,
  Zap,
  Radio,
  Sliders,
} from "lucide-react";

export const HeroScrollStory: React.FC = () => {
  const [progress, setProgress] = useState<number>(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState<boolean>(false);
  const [activeChapter, setActiveChapter] = useState<number>(1);

  // Stage boundaries (0-100)
  const isStage1 = progress < 22; // 0% - 22%: Assembled Commercial Vehicle
  const isStage2 = progress >= 22 && progress < 50; // 22% - 50%: Powertrain & CAN Ingestion
  const isStage3 = progress >= 50 && progress < 76; // 50% - 76%: 12.4 kWh LFP Thermal Twin
  const isStage4 = progress >= 76; // 76% - 100%: Exploded Cell Matrix & Knee Prognostics

  // Update active chapter based on scrub progress
  useEffect(() => {
    if (progress < 22) setActiveChapter(1);
    else if (progress < 50) setActiveChapter(2);
    else if (progress < 76) setActiveChapter(3);
    else setActiveChapter(4);
  }, [progress]);

  // Auto-Demo Scroll Loop
  useEffect(() => {
    let animFrame: number;

    if (isAutoPlaying) {
      const step = () => {
        const maxScroll = 3800;
        if (window.scrollY < maxScroll) {
          window.scrollBy({ top: 7, behavior: "auto" });
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
    if (!isAutoPlaying && window.scrollY >= 3600) {
      window.scrollTo({ top: 0, behavior: "instant" });
      setTimeout(() => setIsAutoPlaying(true), 300);
    } else {
      setIsAutoPlaying(!isAutoPlaying);
    }
  };

  const jumpToChapter = (chapter: number) => {
    setIsAutoPlaying(false);
    const scrollMap: Record<number, number> = {
      1: 0,
      2: 1050,
      3: 2200,
      4: 3350,
    };
    window.scrollTo({ top: scrollMap[chapter] ?? 0, behavior: "smooth" });
  };

  const resetToTop = () => {
    setIsAutoPlaying(false);
    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
  };

  return (
    <section id="story" className="relative w-full bg-[#06080E] text-white select-none overflow-hidden">
      {/* Ambient Stage-Responsive Radial Glows */}
      <div
        className={`fixed top-1/4 left-1/3 w-[650px] h-[650px] rounded-full blur-[160px] pointer-events-none transition-all duration-1000 z-0 ${
          isStage1
            ? "bg-cyan-500/15"
            : isStage2
            ? "bg-emerald-500/15"
            : isStage3
            ? "bg-amber-500/15"
            : "bg-purple-600/15"
        }`}
      />
      <div
        className={`fixed bottom-1/4 right-1/4 w-[500px] h-[500px] rounded-full blur-[160px] pointer-events-none transition-all duration-1000 z-0 ${
          isStage1
            ? "bg-emerald-500/10"
            : isStage2
            ? "bg-cyan-500/15"
            : isStage3
            ? "bg-rose-500/15"
            : "bg-blue-600/15"
        }`}
      />

      {/* 300-Frame Apple-Style Pinned Canvas Sequence */}
      <ScrollImageSequence
        frameFolder="/sequence"
        frameCount={300}
        fileNamePrefix="ezgif-frame-"
        fileNameSuffix=".jpg"
        digitPadding={3}
        scrollDistance={4000}
        fit="cover"
        scrub={0.3}
        onProgress={(p) => setProgress(p)}
      >
        {/* ─── TOP MINIMALIST CHAPTER STATUS PILL ─── */}
        <div className="absolute top-7 left-1/2 -translate-x-1/2 z-30 pointer-events-none transition-all duration-500">
          <div className="flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-slate-950/80 backdrop-blur-xl border border-white/10 shadow-2xl text-[11px] font-mono tracking-wider">
            <span className="flex h-2 w-2 relative">
              <span
                className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                  isStage1
                    ? "bg-cyan-400"
                    : isStage2
                    ? "bg-emerald-400"
                    : isStage3
                    ? "bg-amber-400"
                    : "bg-purple-400"
                }`}
              />
              <span
                className={`relative inline-flex rounded-full h-2 w-2 ${
                  isStage1
                    ? "bg-cyan-500"
                    : isStage2
                    ? "bg-emerald-500"
                    : isStage3
                    ? "bg-amber-500"
                    : "bg-purple-500"
                }`}
              />
            </span>
            <span className="text-slate-400 hidden sm:inline">3D DIGITAL TWIN:</span>
            <span className="font-bold text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-100 to-slate-300">
              {isStage1 && "ACT 01 • ASSEMBLED COMMERCIAL CHASSIS"}
              {isStage2 && "ACT 02 • HIGH-FREQUENCY CAN INGESTION"}
              {isStage3 && "ACT 03 • 12.4 kWh THERMAL DIGITAL TWIN"}
              {isStage4 && "ACT 04 • CELL MATRIX & KNEE INFLECTION"}
            </span>
          </div>
        </div>

        {/* ═══════════════════════════════════════════════════════════════
            ACT 1 (0% – 22%): HERO HEADLINE & HIGH-IMPACT LAUNCHPAD
           ═══════════════════════════════════════════════════════════════ */}
        <div
          className={`absolute inset-0 flex flex-col justify-between p-6 sm:p-12 md:p-16 transition-all duration-700 pointer-events-none z-20 ${
            isStage1
              ? "opacity-100 translate-y-0"
              : "opacity-0 -translate-y-8 pointer-events-none"
          }`}
        >
          {/* Main Hero Header */}
          <div className="max-w-3xl pt-8 sm:pt-6 pointer-events-auto space-y-4">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-semibold tracking-wide">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Tri-Pillar Fleet AI Platform • 74 Models</span>
            </div>

            <div className="w-full py-1">
              <MaskedHeading
                text="EV Battery Intelligence"
                tag="h1"
                src="/assets/battery_mesh_mask.jpg"
                fillScale={1.35}
                parallax={30}
                drift={14}
                brightness={1.45}
                saturation={1.6}
                reveal="rise"
                duration={1.2}
                align="left"
                weight={900}
                tracking={-0.02}
                lineHeight={1.05}
                textScale={0.088}
                className="drop-shadow-[0_0_40px_rgba(6,182,212,0.4)] text-left"
              />
            </div>

            <p className="text-xs sm:text-base text-slate-300 font-light leading-relaxed max-w-xl">
              Physics-informed digital twins, 3-zone thermodynamic runaway prevention ($F_1 = 0.997$), and non-linear degradation knee prognostics trained on 930+ MB Indian commercial fleet telematics.
            </p>

            {/* Quick Action CTAs */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <Link
                href="/dashboard"
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 via-emerald-500 to-emerald-400 hover:from-cyan-400 hover:to-emerald-300 text-slate-950 font-extrabold text-xs shadow-lg shadow-emerald-500/25 transition-all hover:scale-105 active:scale-95 flex items-center gap-2"
              >
                <Activity className="w-4 h-4" />
                <span>Launch Fleet Command Center</span>
              </Link>

              <a
                href="#sandbox"
                className="px-5 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-850 text-slate-200 border border-slate-700/80 text-xs font-semibold backdrop-blur-md transition-all hover:border-cyan-500/50 flex items-center gap-2"
              >
                <Sliders className="w-3.5 h-3.5 text-cyan-400" />
                <span>Test Live Model Sandbox</span>
              </a>
            </div>
          </div>

          {/* Bottom Floating Proof Metrics Bar */}
          <div className="pointer-events-auto flex flex-col sm:flex-row items-start sm:items-end justify-between gap-4 pb-16 sm:pb-12">
            <div className="flex items-center gap-2 sm:gap-4 p-2 sm:p-2.5 rounded-2xl bg-slate-950/70 backdrop-blur-xl border border-white/10 shadow-2xl">
              <div className="px-3 py-1.5 border-r border-white/10">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Fleet Size</div>
                <div className="text-sm sm:text-base font-extrabold font-mono text-cyan-400">778 Commercial EVs</div>
              </div>
              <div className="px-3 py-1.5 border-r border-white/10">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Trained Models</div>
                <div className="text-sm sm:text-base font-extrabold font-mono text-emerald-400">74 Pipelines</div>
              </div>
              <div className="px-3 py-1.5 border-r border-white/10">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Thermal F1</div>
                <div className="text-sm sm:text-base font-extrabold font-mono text-purple-400">99.71%</div>
              </div>
              <div className="px-3 py-1.5">
                <div className="text-[10px] font-mono text-slate-400 uppercase">REST API</div>
                <div className="text-sm sm:text-base font-extrabold font-mono text-amber-400">11 Endpoints</div>
              </div>
            </div>

            {/* Animated Scroll Prompt */}
            <div className="flex items-center gap-2 text-cyan-400 font-mono text-xs animate-pulse bg-slate-950/60 backdrop-blur-md px-3.5 py-2 rounded-full border border-cyan-500/20">
              <ArrowDown className="w-3.5 h-3.5" />
              <span>Scroll down to deconstruct chassis in 3D</span>
            </div>
          </div>
        </div>

        {/* ═══════════════════════════════════════════════════════════════
            ACT 2 (22% – 50%): POWERTRAIN & SUB-SECOND CAN INGESTION HUD
           ═══════════════════════════════════════════════════════════════ */}
        <div
          className={`absolute inset-0 p-6 sm:p-12 transition-all duration-700 pointer-events-none z-20 flex flex-col justify-between ${
            isStage2
              ? "opacity-100 translate-y-0"
              : "opacity-0 -translate-y-8 pointer-events-none"
          }`}
        >
          {/* Top-Left Sleek HUD Beacon */}
          <div className="max-w-md pt-16 pointer-events-auto">
            <div className="p-4 sm:p-5 rounded-2xl bg-slate-950/75 backdrop-blur-xl border border-emerald-500/40 shadow-2xl space-y-2">
              <div className="flex items-center justify-between">
                <span className="inline-flex items-center gap-1.5 text-[10px] font-mono font-bold text-emerald-400 uppercase px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30">
                  <Cpu className="w-3 h-3" />
                  PILLAR A • TELEMETRICS
                </span>
                <span className="text-[10px] font-mono text-slate-400">100 ms Sync (500 kbps)</span>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-white leading-snug">
                Sub-Second CAN Telematics Ingestion
              </h3>
              <p className="text-xs text-slate-300 font-light leading-relaxed">
                Streams 28 high-frequency telemetry channels including dynamic discharge current (-150A to +80A regen) and localized voltage sag.
              </p>
            </div>
          </div>

          {/* Top-Right Live CAN Stream Beacon */}
          <div className="self-end max-w-xs pointer-events-auto hidden md:block">
            <div className="p-4 rounded-2xl bg-slate-950/75 backdrop-blur-xl border border-cyan-500/30 shadow-2xl space-y-2 text-xs font-mono">
              <div className="flex items-center justify-between text-cyan-400 font-bold border-b border-white/10 pb-2">
                <span className="flex items-center gap-1.5">
                  <Radio className="w-3.5 h-3.5 animate-pulse" />
                  CAN BUS [0x18FEF100]
                </span>
                <span className="text-[10px] text-emerald-400">SYNC OK</span>
              </div>
              <div className="space-y-1 text-slate-300 text-[11px]">
                <div className="flex justify-between">
                  <span className="text-slate-500">Bus Voltage:</span>
                  <span className="font-bold text-slate-100">75.8 V (Nominal)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Discharge Flow:</span>
                  <span className="font-bold text-amber-400">-24.2 A</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Champion SOC Regressor:</span>
                  <span className="font-bold text-emerald-400">KNN (99.58% R²)</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ═══════════════════════════════════════════════════════════════
            ACT 3 (50% – 76%): 12.4 kWh LFP 3-ZONE THERMAL DIGITAL TWIN HUD
           ═══════════════════════════════════════════════════════════════ */}
        <div
          className={`absolute inset-0 p-6 sm:p-12 transition-all duration-700 pointer-events-none z-20 flex flex-col justify-between ${
            isStage3
              ? "opacity-100 translate-y-0"
              : "opacity-0 -translate-y-8 pointer-events-none"
          }`}
        >
          {/* Top-Left Thermal Specification Beacon */}
          <div className="max-w-md pt-16 pointer-events-auto">
            <div className="p-4 sm:p-5 rounded-2xl bg-slate-950/75 backdrop-blur-xl border border-amber-500/40 shadow-2xl space-y-2">
              <div className="flex items-center justify-between">
                <span className="inline-flex items-center gap-1.5 text-[10px] font-mono font-bold text-amber-400 uppercase px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30">
                  <Flame className="w-3 h-3" />
                  PILLAR B • THERMODYNAMICS
                </span>
                <span className="text-[10px] font-mono text-emerald-400 font-bold">F1 = 0.9971</span>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-white leading-snug">
                3-Zone Cyber-Physical Thermal Safety Twin
              </h3>
              <p className="text-xs text-slate-300 font-light leading-relaxed">
                Synchronously tracks heat flux between the 12.4 kWh battery pack, inverter MOSFETs, and motor stator to eliminate thermal runaway.
              </p>
            </div>
          </div>

          {/* Top-Right 3-Zone Live Gauge Strip */}
          <div className="self-end max-w-sm pointer-events-auto">
            <div className="p-4 rounded-2xl bg-slate-950/75 backdrop-blur-xl border border-emerald-500/40 shadow-2xl space-y-3 font-mono text-xs">
              <div className="flex items-center justify-between text-emerald-400 font-bold border-b border-white/10 pb-1.5">
                <span className="flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  3-ZONE THERMAL STATUS
                </span>
                <span className="text-[10px] text-emerald-300">SAFE (0.000 Risk)</span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-center text-[10px]">
                <div className="p-2 rounded-xl bg-slate-900/80 border border-emerald-500/30">
                  <div className="text-slate-400">Pack Core</div>
                  <div className="text-sm font-bold text-emerald-400 mt-0.5">33.2°C</div>
                </div>
                <div className="p-2 rounded-xl bg-slate-900/80 border border-cyan-500/30">
                  <div className="text-slate-400">Inverter</div>
                  <div className="text-sm font-bold text-cyan-400 mt-0.5">38.5°C</div>
                </div>
                <div className="p-2 rounded-xl bg-slate-900/80 border border-amber-500/30">
                  <div className="text-slate-400">Motor</div>
                  <div className="text-sm font-bold text-amber-400 mt-0.5">42.1°C</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ═══════════════════════════════════════════════════════════════
            ACT 4 (76% – 100%): EXPLODED CELL MATRIX & KNEE PROGNOSTICS HUD
           ═══════════════════════════════════════════════════════════════ */}
        <div
          className={`absolute inset-0 p-6 sm:p-12 transition-all duration-700 pointer-events-none z-20 flex flex-col justify-between ${
            isStage4
              ? "opacity-100 translate-y-0"
              : "opacity-0 -translate-y-8 pointer-events-none"
          }`}
        >
          {/* Top-Left Knee Degradation Beacon */}
          <div className="max-w-md pt-16 pointer-events-auto">
            <div className="p-4 sm:p-5 rounded-2xl bg-slate-950/75 backdrop-blur-xl border border-purple-500/40 shadow-2xl space-y-2">
              <div className="flex items-center justify-between">
                <span className="inline-flex items-center gap-1.5 text-[10px] font-mono font-bold text-purple-400 uppercase px-2 py-0.5 rounded-full bg-purple-500/10 border border-purple-500/30">
                  <Gauge className="w-3 h-3" />
                  PILLAR C • KNEE PROGNOSTICS
                </span>
                <span className="text-[10px] font-mono text-purple-300">28-Feature XGBoost</span>
              </div>
              <h3 className="text-base sm:text-lg font-bold text-white leading-snug">
                Forecasting Non-Linear Aging Knee Inflection
              </h3>
              <p className="text-xs text-slate-300 font-light leading-relaxed">
                Piecewise linear joint MSE optimization isolates the tipping point where linear aging transitions to accelerated capacity drop.
              </p>
            </div>
          </div>

          {/* Top-Right Degradation Metrics */}
          <div className="self-end max-w-xs pointer-events-auto hidden md:block">
            <div className="p-4 rounded-2xl bg-slate-950/75 backdrop-blur-xl border border-purple-500/30 shadow-2xl space-y-2 text-xs font-mono">
              <div className="text-slate-400 text-[10px] uppercase">Estimated Knee Inflection Point</div>
              <div className="text-2xl font-extrabold text-cyan-400 font-mono">~931.0 EFC</div>
              <div className="text-[11px] text-emerald-400">846 Cycles Pre-Knee Buffer Margin</div>
              <div className="pt-2 border-t border-white/10 flex justify-between text-[11px] text-slate-300">
                <span>Driver Strain (AI / BSI):</span>
                <span className="font-bold text-purple-400">0.16 / 0.22</span>
              </div>
            </div>
          </div>
        </div>

        {/* ─── UNIFIED FLOATING CONTROLLER DOCK (BOTTOM CENTER) ─── */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-40 pointer-events-auto flex items-center gap-2 p-1.5 rounded-2xl bg-slate-950/85 backdrop-blur-2xl border border-white/10 shadow-2xl max-w-[95vw] overflow-x-auto">
          {/* Chapter Quick Jump Pills */}
          {[
            { id: 1, label: "01 Chassis", icon: Zap },
            { id: 2, label: "02 Telematics", icon: Cpu },
            { id: 3, label: "03 Thermal Twin", icon: Flame },
            { id: 4, label: "04 Cell Matrix", icon: Gauge },
          ].map((ch) => {
            const Icon = ch.icon;
            const isActive = activeChapter === ch.id;
            return (
              <button
                key={ch.id}
                onClick={() => jumpToChapter(ch.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-mono font-semibold transition-all duration-300 shrink-0 ${
                  isActive
                    ? "bg-gradient-to-r from-cyan-600 to-emerald-600 text-white shadow-md shadow-cyan-500/20 scale-105"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">{ch.label}</span>
                <span className="sm:hidden">{ch.id}</span>
              </button>
            );
          })}

          <div className="w-px h-5 bg-white/10 shrink-0 mx-0.5" />

          {/* Auto-Demo Playback Button */}
          <button
            onClick={toggleAutoPlay}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition-all shadow-md active:scale-95 shrink-0 ${
              isAutoPlaying
                ? "bg-amber-500 text-slate-950 border border-amber-400 animate-pulse"
                : "bg-slate-900 hover:bg-slate-800 text-white border border-slate-700/80"
            }`}
            title="Auto-scroll demo"
          >
            {isAutoPlaying ? (
              <>
                <Pause className="w-3 h-3 fill-current" />
                <span className="hidden md:inline">Pause</span>
              </>
            ) : (
              <>
                <Play className="w-3 h-3 fill-current" />
                <span className="hidden md:inline">Auto-Demo</span>
              </>
            )}
          </button>

          {/* Reset Button (Instant 0% Reset) */}
          <button
            onClick={resetToTop}
            className="p-1.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/80 transition-all shrink-0 active:scale-95"
            title="Reset to 0% (Beginning)"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          {/* Scrub Percentage Indicator */}
          <div className="px-2.5 py-1 rounded-xl bg-slate-900/80 text-cyan-400 text-xs font-mono font-bold shrink-0">
            {progress}%
          </div>
        </div>
      </ScrollImageSequence>
    </section>
  );
};

export default HeroScrollStory;
