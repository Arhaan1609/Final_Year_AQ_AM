"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  Activity,
  Cpu,
  Flame,
  ShieldCheck,
  Zap,
  TrendingDown,
  Gauge,
  CheckCircle2,
  Database,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";

export const ScrollIntelligenceStory: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const totalScroll = containerRef.current.offsetHeight - window.innerHeight;
      if (totalScroll <= 0) return;

      const progress = Math.max(0, Math.min(1, -rect.top / totalScroll));
      setScrollProgress(progress);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Determine current active stage
  const activeStage =
    scrollProgress < 0.25 ? 0 : scrollProgress < 0.5 ? 1 : scrollProgress < 0.75 ? 2 : 3;

  const stages = [
    {
      step: "01",
      title: "High-Frequency CAN Telematics Ingestion",
      tagline: "Sub-second packets across 778 commercial EV chassis",
      icon: Activity,
      color: "cyan",
      badge: "CAN 2.0B / 500 kbps",
      description:
        "Continuously streams synchronized cell voltage sag, high-rate discharge current (-150A to +80A regen), pack temperatures, inverter thermals, and motor telemetry with real-time outlier rejection.",
      metrics: [
        { label: "Sampling Rate", val: "100 ms" },
        { label: "Active Channels", val: "28 Telemetry Signals" },
        { label: "Data Scale", val: "930+ MB Logged" },
      ],
    },
    {
      step: "02",
      title: "Tri-Pillar Machine Learning Core",
      tagline: "74 Specialized ML & Deep Learning models in parallel",
      icon: Cpu,
      color: "emerald",
      badge: "sklearn • XGBoost • PyTorch",
      description:
        "Dispatches streaming features across specialized pipelines: KNN & XGBoost for SOC/SOH, 200-Tree Random Forest for multi-zone safety, and 28-feature XGBoost for non-linear knee-point prognostics.",
      metrics: [
        { label: "SOC Champion", val: "KNN (95.8% Acc)" },
        { label: "SOH Tabular", val: "XGBoost (R² 0.982)" },
        { label: "Knee Prognostics", val: "XGBoost 28-Feature" },
      ],
    },
    {
      step: "03",
      title: "Cyber-Physical 3-Zone Thermodynamic Twin",
      tagline: "Synchronized Battery, Controller & Motor thermal monitoring",
      icon: Flame,
      color: "amber",
      badge: "99.71% F1 Accuracy",
      description:
        "Fuses multi-zone sensor streams into a real-time thermodynamic thermal model. Evaluates localized hot-spots, thermal gradients, and triggers proactive BMS throttling before thermal runaway risks emerge.",
      metrics: [
        { label: "Battery Zone (VBT)", val: "Pack Core Temp" },
        { label: "Inverter Zone (VCT)", val: "MOSFET Thermals" },
        { label: "Motor Zone (VMT)", val: "Stator Heat Flux" },
      ],
    },
    {
      step: "04",
      title: "Fleet Longevity & Longevity Optimization",
      tagline: "Proactive warranty protection and lifetime extension",
      icon: ShieldCheck,
      color: "purple",
      badge: "+3.2 Years Lifespan",
      description:
        "Translates mathematical insights into actionable fleet decisions. Normalizes driver aggressiveness ($AI$), mitigates battery stress ($BSI$), and predicts capacity knee points to save thousands per vehicle annually.",
      metrics: [
        { label: "Annual Cost Savings", val: "₹1,45,000 / EV" },
        { label: "Knee Warning Buffer", val: "450+ Cycles" },
        { label: "Thermal Incident Rate", val: "0.0% Zero Runaway" },
      ],
    },
  ];

  const curr = stages[activeStage];
  const Icon = curr.icon;

  return (
    <div id="pipeline" ref={containerRef} className="relative w-full" style={{ height: "320vh" }}>
      {/* Sticky 100vh Viewport Stage */}
      <div className="sticky top-0 h-screen w-full overflow-hidden flex flex-col items-center justify-center bg-slate-950 text-slate-100 px-6 sm:px-12 py-10 cyber-grid border-y border-slate-800">
        {/* Background Ambient Glow */}
        <div
          className={`absolute w-[600px] h-[600px] rounded-full blur-[140px] pointer-events-none transition-all duration-700 -z-10 ${
            activeStage === 0
              ? "bg-cyan-500/15 top-1/4 left-1/4"
              : activeStage === 1
              ? "bg-emerald-500/15 top-1/3 right-1/4"
              : activeStage === 2
              ? "bg-amber-500/15 bottom-1/4 left-1/3"
              : "bg-purple-500/15 top-1/4 right-1/3"
          }`}
        />

        {/* Top Header & Scrub Progress */}
        <div className="w-full max-w-6xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-mono font-bold tracking-wider uppercase text-emerald-400">
                DeepTech Architecture Narrative
              </span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
              How Autonomous Fleet Intelligence Works
            </h2>
          </div>

          {/* Scrub Indicator */}
          <div className="flex items-center gap-3 bg-slate-900/90 border border-slate-800 px-4 py-2 rounded-full backdrop-blur-xl">
            <span className="text-xs font-mono text-slate-400">
              Stage <strong className="text-white">{activeStage + 1}</strong> of 4
            </span>
            <div className="w-28 h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 transition-all duration-150"
                style={{ width: `${Math.round(scrollProgress * 100)}%` }}
              />
            </div>
            <span className="text-xs font-mono font-bold text-emerald-400">
              {Math.round(scrollProgress * 100)}%
            </span>
          </div>
        </div>

        {/* 4 Interactive Stage Tabs */}
        <div className="w-full max-w-6xl grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
          {stages.map((s, idx) => {
            const isCurr = idx === activeStage;
            const isDone = idx < activeStage;
            return (
              <div
                key={s.step}
                className={`p-3.5 rounded-2xl border transition-all duration-300 flex items-center gap-3 ${
                  isCurr
                    ? "bg-slate-900 border-emerald-500/80 shadow-lg shadow-emerald-500/10"
                    : isDone
                    ? "bg-slate-950/60 border-slate-800/80 opacity-80"
                    : "bg-slate-950/40 border-slate-900 opacity-40"
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-xl flex items-center justify-center font-mono font-extrabold text-xs shrink-0 ${
                    isCurr
                      ? "bg-emerald-500 text-slate-950"
                      : isDone
                      ? "bg-slate-800 text-emerald-400"
                      : "bg-slate-900 text-slate-500"
                  }`}
                >
                  {isDone ? <CheckCircle2 className="w-4 h-4" /> : s.step}
                </div>
                <div className="truncate text-left">
                  <div className="text-[11px] font-mono text-slate-400">{s.tagline.split(" ")[0]}</div>
                  <div className={`text-xs font-bold truncate ${isCurr ? "text-white" : "text-slate-400"}`}>
                    {s.title}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Main Stage Display Card */}
        <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-12 gap-8 items-center bg-slate-900/80 backdrop-blur-2xl border border-slate-800/90 rounded-3xl p-6 sm:p-10 shadow-2xl relative overflow-hidden">
          {/* Glowing Top Border Accent */}
          <div
            className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r transition-all duration-500 ${
              activeStage === 0
                ? "from-cyan-500 via-cyan-400 to-transparent"
                : activeStage === 1
                ? "from-emerald-500 via-emerald-400 to-transparent"
                : activeStage === 2
                ? "from-amber-500 via-amber-400 to-transparent"
                : "from-purple-500 via-purple-400 to-transparent"
            }`}
          />

          {/* Left: Stage Details */}
          <div className="lg:col-span-7 flex flex-col items-start text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-semibold bg-slate-800/80 border border-slate-700 text-slate-300 mb-4">
              <Icon className="w-3.5 h-3.5 text-emerald-400" />
              <span>{curr.badge}</span>
            </div>

            <h3 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mb-3">
              {curr.title}
            </h3>

            <p className="text-sm sm:text-base text-slate-300 leading-relaxed mb-8 font-normal">
              {curr.description}
            </p>

            {/* Metrics Chips */}
            <div className="grid grid-cols-3 gap-3 w-full border-t border-slate-800 pt-6">
              {curr.metrics.map((m, idx) => (
                <div key={idx} className="bg-slate-950/70 border border-slate-800/80 p-3 rounded-xl">
                  <div className="text-[10px] font-mono text-slate-400">{m.label}</div>
                  <div className="text-xs sm:text-sm font-extrabold text-white font-mono mt-1 truncate">
                    {m.val}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Futuristic Visual Representation */}
          <div className="lg:col-span-5 w-full flex flex-col items-center justify-center min-h-[220px] bg-slate-950/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
            {activeStage === 0 && (
              <div className="w-full space-y-3 font-mono text-xs">
                <div className="flex justify-between text-slate-400 border-b border-slate-800 pb-2">
                  <span>CAN Stream [0x18FEF100]</span>
                  <span className="text-cyan-400">SYNC OK</span>
                </div>
                <div className="space-y-1.5 text-[11px]">
                  <div className="flex justify-between text-slate-300">
                    <span>Pack Voltage (V):</span>
                    <span className="text-emerald-400 font-bold">75.8 V (Nominal)</span>
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span>Current Draw (A):</span>
                    <span className="text-amber-400 font-bold">-24.2 A (Discharge)</span>
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span>Battery Temp (VBT):</span>
                    <span className="text-cyan-400 font-bold">33.2°C (Healthy)</span>
                  </div>
                  <div className="flex justify-between text-slate-300">
                    <span>CAN Jitter:</span>
                    <span className="text-purple-400 font-bold">&lt; 1.4 ms</span>
                  </div>
                </div>
              </div>
            )}

            {activeStage === 1 && (
              <div className="w-full space-y-3 font-mono text-xs">
                <div className="flex justify-between text-slate-400 border-b border-slate-800 pb-2">
                  <span>Inference Engines</span>
                  <span className="text-emerald-400">74 ACTIVE</span>
                </div>
                <div className="space-y-2 text-[11px]">
                  <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 flex justify-between">
                    <span>Mod A: SOC / SOH</span>
                    <strong className="text-cyan-400">KNN &amp; XGBoost</strong>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 flex justify-between">
                    <span>Mod B: Thermal Safety</span>
                    <strong className="text-emerald-400">Random Forest 200T</strong>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 flex justify-between">
                    <span>Mod C: Knee Prognostics</span>
                    <strong className="text-purple-400">XGBoost Booster</strong>
                  </div>
                </div>
              </div>
            )}

            {activeStage === 2 && (
              <div className="w-full space-y-3 font-mono text-xs">
                <div className="flex justify-between text-slate-400 border-b border-slate-800 pb-2">
                  <span>3-Zone Thermodynamic State</span>
                  <span className="text-emerald-400">SAFE (Benign)</span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span>Battery Zone: 33.2°C</span>
                    <span className="text-emerald-400 font-bold">Optimal</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div className="bg-emerald-500 h-full w-2/5" />
                  </div>
                  <div className="flex justify-between text-xs">
                    <span>Controller Zone: 38.5°C</span>
                    <span className="text-cyan-400 font-bold">Normal</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div className="bg-cyan-500 h-full w-1/2" />
                  </div>
                  <div className="flex justify-between text-xs">
                    <span>Motor Powertrain: 42.1°C</span>
                    <span className="text-amber-400 font-bold">Nominal</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div className="bg-amber-500 h-full w-3/5" />
                  </div>
                </div>
              </div>
            )}

            {activeStage === 3 && (
              <div className="w-full space-y-4 text-center">
                <div className="w-12 h-12 rounded-2xl bg-emerald-950/80 border border-emerald-500/60 text-emerald-400 flex items-center justify-center mx-auto">
                  <ShieldCheck className="w-6 h-6" />
                </div>
                <div>
                  <div className="text-xl font-extrabold text-white font-mono">
                    ₹1,45,000 / Year
                  </div>
                  <div className="text-xs text-slate-400 font-mono mt-0.5">
                    Estimated Savings Per Commercial Chassis
                  </div>
                </div>
                <Link
                  href="/dashboard"
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-400 hover:text-emerald-300 font-mono"
                >
                  <span>Explore in Live Dashboard</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Bottom Scroll Prompt */}
        <div className="mt-8 flex items-center gap-2 text-xs font-mono text-slate-500">
          <span>{scrollProgress < 0.95 ? "Scroll to progress through the deeptech pipeline" : "Pipeline complete • Scroll to explore live model sandbox"}</span>
          <span className="text-emerald-400 animate-bounce">↓</span>
        </div>
      </div>
    </div>
  );
};
