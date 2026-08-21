"use client";

import React, { useEffect, useRef } from "react";
import Link from "next/link";
import { animate, createDrawable, onScroll } from "animejs";
import { useFleetStore } from "../lib/store/useFleetStore";
import BatteryHero from "../components/hero/BatteryHero";
import { Badge } from "../components/ui/Badge";
import {
  ArrowRight,
  ShieldCheck,
  Zap,
  Flame,
  Activity,
  Cpu,
  TrendingDown,
  Gauge,
  Sun,
  Moon,
  Sparkles,
  Layers,
  Database,
  Award,
  CheckCircle2,
} from "lucide-react";

export default function LandingPage() {
  const { theme, toggleTheme } = useFleetStore();
  const svgDiagramRef = useRef<SVGPathElement>(null);

  useEffect(() => {
    // Animated SVG Circuit Path using anime.js v4 createDrawable
    if (svgDiagramRef.current) {
      try {
        const drawable = createDrawable(svgDiagramRef.current);
        animate(drawable, {
          draw: ["0 0", "0 1"],
          duration: 2000,
          ease: "inOutSine",
          autoplay: onScroll({
            target: svgDiagramRef.current,
            sync: true,
            enter: "bottom top",
            leave: "top top",
          }),
        });
      } catch (e) {
        console.warn("SVG diagram draw-on animation fallback:", e);
      }
    }
  }, []);

  return (
    <div className="min-h-screen bg-[var(--bg-page)] text-[var(--text-primary)] transition-colors">
      {/* Top Marketing Navigation */}
      <header className="h-20 border-b border-[var(--border-subtle)] bg-[var(--bg-card)]/80 backdrop-blur-xl sticky top-0 z-40 px-6 sm:px-12 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-cyan-600 via-emerald-600 to-emerald-500 flex items-center justify-center text-white font-extrabold text-sm shadow-md">
            EV
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-base sm:text-lg tracking-tight text-slate-900 dark:text-slate-100">
                EV Battery Intelligence
              </span>
              <Badge variant="emerald" size="sm" dot>v1.0 Ready</Badge>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">
              74 Trained ML/DL Models • 11 FastAPI Endpoints
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Theme Switcher */}
          <button
            onClick={toggleTheme}
            className="p-2.5 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all shadow-sm"
            title={`Switch to ${theme === "light" ? "Dark" : "Light"} mode`}
          >
            {theme === "light" ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
          </button>

          {/* Primary CTA */}
          <Link
            href="/dashboard"
            className="hidden sm:inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-sm hover:shadow-md transition-all hover:scale-105"
          >
            <span>Launch Dashboard</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </header>

      {/* 1. HERO SECTION WITH SIGNATURE SCROLL-SCRUBBED BATTERY CELLS */}
      <BatteryHero />

      {/* 2. TRI-PILLAR ARCHITECTURE SECTION */}
      <section className="py-24 px-6 max-w-7xl mx-auto border-t border-[var(--border-subtle)]">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <Badge variant="cyan" size="sm" className="mb-3">
            Tri-Pillar ML Architecture
          </Badge>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">
            Engineered Across 3 Specialized Intelligence Modules
          </h2>
          <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 mt-3 leading-relaxed">
            From granular cell thermodynamics to fleet-wide predictive degradation, each pillar is powered by dedicated champion models.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Pillar A */}
          <div className="app-card p-8 flex flex-col justify-between hover:border-cyan-500/50 transition-all group">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-cyan-100 dark:bg-cyan-950/60 border border-cyan-300 dark:border-cyan-800 text-cyan-700 dark:text-cyan-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Cpu className="w-6 h-6" />
              </div>
              <Badge variant="cyan" size="sm" className="mb-2">Module A</Badge>
              <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100 mt-1">Fleet State Estimation</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-2.5 leading-relaxed">
                Precision estimation of SOC, SOH, Remaining Useful Life (RUL), and Range per charge using KNN, Random Forest, and Gradient Boosting champions.
              </p>

              <div className="mt-6 space-y-2 border-t border-[var(--border-subtle)] pt-4 text-xs font-mono text-slate-600 dark:text-slate-300">
                <div className="flex justify-between"><span>SOC Champion:</span><strong className="text-cyan-600 dark:text-cyan-400">KNN (95.8% Acc)</strong></div>
                <div className="flex justify-between"><span>SOH Champion:</span><strong className="text-emerald-600 dark:text-emerald-400">XGBoost (R²=0.982)</strong></div>
                <div className="flex justify-between"><span>RUL Champion:</span><strong className="text-purple-600 dark:text-purple-400">GradientBoosting</strong></div>
              </div>
            </div>
            <Link href="/dashboard" className="mt-6 text-xs font-semibold text-cyan-600 dark:text-cyan-400 flex items-center gap-1 group-hover:underline">
              Explore State Estimation Hub →
            </Link>
          </div>

          {/* Pillar B */}
          <div className="app-card p-8 flex flex-col justify-between hover:border-emerald-500/50 transition-all group">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-emerald-100 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-800 text-emerald-700 dark:text-emerald-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Flame className="w-6 h-6" />
              </div>
              <Badge variant="emerald" size="sm" className="mb-2">Module B</Badge>
              <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100 mt-1">BatteryIQ Thermal Safety</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-2.5 leading-relaxed">
                Cyber-physical 3-zone thermal hazard detection across battery pack, motor, and controller with deep sequential 1D-CNN + LSTM time-series analysis.
              </p>

              <div className="mt-6 space-y-2 border-t border-[var(--border-subtle)] pt-4 text-xs font-mono text-slate-600 dark:text-slate-300">
                <div className="flex justify-between"><span>Thermal Safety:</span><strong className="text-emerald-600 dark:text-emerald-400">200-Tree RF (F1=0.997)</strong></div>
                <div className="flex justify-between"><span>Deep Sequence SOH:</span><strong className="text-cyan-600 dark:text-cyan-400">PyTorch CNN-LSTM</strong></div>
                <div className="flex justify-between"><span>Accuracy:</span><strong className="text-emerald-600 dark:text-emerald-400">99.71% Verified</strong></div>
              </div>
            </div>
            <Link href="/dashboard" className="mt-6 text-xs font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1 group-hover:underline">
              Explore Thermal Safety Heat Map →
            </Link>
          </div>

          {/* Pillar C */}
          <div className="app-card p-8 flex flex-col justify-between hover:border-purple-500/50 transition-all group">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-purple-100 dark:bg-purple-950/60 border border-purple-300 dark:border-purple-800 text-purple-700 dark:text-purple-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Gauge className="w-6 h-6" />
              </div>
              <Badge variant="purple" size="sm" className="mb-2">Module C</Badge>
              <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100 mt-1">BA-BMS & Knee Prognostics</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-2.5 leading-relaxed">
                Driver Aggressiveness Index (AI), Battery Stress Index (BSI), and Degradation Knee-Point localization before rapid non-linear capacity drop.
              </p>

              <div className="mt-6 space-y-2 border-t border-[var(--border-subtle)] pt-4 text-xs font-mono text-slate-600 dark:text-slate-300">
                <div className="flex justify-between"><span>Knee Predictor:</span><strong className="text-purple-600 dark:text-purple-400">XGBoost Booster</strong></div>
                <div className="flex justify-between"><span>BMS Policy:</span><strong className="text-amber-600 dark:text-amber-400">Active Directives</strong></div>
                <div className="flex justify-between"><span>Meta-Ensemble:</span><strong className="text-emerald-600 dark:text-emerald-400">Asset Certifications</strong></div>
              </div>
            </div>
            <Link href="/dashboard" className="mt-6 text-xs font-semibold text-purple-600 dark:text-purple-400 flex items-center gap-1 group-hover:underline">
              Explore Knee Prognostics →
            </Link>
          </div>
        </div>
      </section>

      {/* 3. ANIMATED SVG CIRCUIT DIAGRAM SECTION */}
      <section className="py-20 px-6 max-w-7xl mx-auto border-t border-[var(--border-subtle)]">
        <div className="app-card p-8 sm:p-12 relative overflow-hidden bg-slate-900 text-white">
          <div className="max-w-xl relative z-10">
            <Badge variant="emerald" size="sm" className="mb-3">Live Telemetry Pipeline</Badge>
            <h3 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white mb-3">
              Cyber-Physical Current Flow & Model Pipeline
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed mb-6">
              Continuous 10-Hz CAN-bus telemetry streams from vehicle sensors through the feature engineering pipeline directly into the 74-model inference engine.
            </p>
            <div className="flex flex-wrap gap-4 text-xs font-mono text-slate-300">
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> 370k+ Telemetry Samples</span>
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-cyan-400" /> Multi-Zone Thermal Coupling</span>
            </div>
          </div>

          {/* Circuit SVG line diagram with anime.js createDrawable */}
          <div className="absolute right-0 top-0 bottom-0 w-1/2 opacity-60 hidden md:flex items-center justify-center">
            <svg viewBox="0 0 500 300" className="w-full h-full">
              <path
                ref={svgDiagramRef}
                d="M 50 150 L 150 150 L 200 80 L 300 80 L 350 220 L 420 220 L 480 150"
                fill="none"
                stroke="#10B981"
                strokeWidth="4"
                strokeLinecap="round"
              />
              <circle cx="150" cy="150" r="6" fill="#06B6D4" />
              <circle cx="200" cy="80" r="6" fill="#10B981" />
              <circle cx="300" cy="80" r="6" fill="#F59E0B" />
              <circle cx="350" cy="220" r="6" fill="#8B5CF6" />
              <circle cx="480" cy="150" r="8" fill="#10B981" />
            </svg>
          </div>
        </div>
      </section>

      {/* 4. FOOTER CTA SECTION */}
      <footer className="py-20 px-6 max-w-7xl mx-auto border-t border-[var(--border-subtle)] text-center">
        <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight mb-4">
          Ready to Explore the Commercial Fleet?
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-400 max-w-xl mx-auto mb-8">
          Browse 778 real commercial chassis, test live telemetry sliders, and evaluate multi-zone safety across 74 trained models.
        </p>
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm shadow-md hover:shadow-lg transition-all hover:scale-105 active:scale-95"
        >
          <span>Launch Fleet Dashboard</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
        <div className="mt-12 text-xs text-slate-400 dark:text-slate-500 font-mono">
          EV Battery Intelligence Platform • Final Year Engineering Project
        </div>
      </footer>
    </div>
  );
}
