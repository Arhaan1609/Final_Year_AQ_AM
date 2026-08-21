"use client";

import React, { useEffect, useRef } from "react";
import Link from "next/link";
import { animate, stagger, createDrawable, onScroll } from "animejs";
import { useFleetStore } from "../lib/store/useFleetStore";
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
} from "lucide-react";

export default function LandingPage() {
  const { theme, toggleTheme } = useFleetStore();

  const heroHeadlineRef = useRef<HTMLHeadingElement>(null);
  const heroSubRef = useRef<HTMLParagraphElement>(null);
  const heroCtaRef = useRef<HTMLDivElement>(null);
  const svgDiagramRef = useRef<SVGPathElement>(null);

  const stat1Ref = useRef<HTMLSpanElement>(null);
  const stat2Ref = useRef<HTMLSpanElement>(null);
  const stat3Ref = useRef<HTMLSpanElement>(null);
  const stat4Ref = useRef<HTMLSpanElement>(null);

  // 1. Page Load: Staggered Hero Reveal using animejs v4
  useEffect(() => {
    // Reveal hero text elements with smooth stagger
    if (heroHeadlineRef.current) {
      animate(heroHeadlineRef.current, {
        opacity: [0, 1],
        translateY: [24, 0],
        duration: 900,
        ease: "outExpo",
      });
    }

    if (heroSubRef.current) {
      animate(heroSubRef.current, {
        opacity: [0, 1],
        translateY: [20, 0],
        duration: 900,
        delay: 150,
        ease: "outExpo",
      });
    }

    if (heroCtaRef.current) {
      animate(heroCtaRef.current, {
        opacity: [0, 1],
        translateY: [16, 0],
        duration: 900,
        delay: 300,
        ease: "outExpo",
      });
    }

    // 2. Stat counters count-up on scroll / view
    const triggerCounters = () => {
      const stats = [
        { ref: stat1Ref, to: 74, suffix: "" },
        { ref: stat2Ref, to: 11, suffix: " APIs" },
        { ref: stat3Ref, to: 930, suffix: " MB+" },
        { ref: stat4Ref, to: 99.97, suffix: "%" },
      ];

      stats.forEach((s) => {
        if (s.ref.current) {
          const obj = { val: 0 };
          animate(obj, {
            val: s.to,
            duration: 1200,
            ease: "outExpo",
            onUpdate: () => {
              if (s.ref.current) {
                s.ref.current.innerHTML =
                  s.to === 99.97
                    ? `${obj.val.toFixed(2)}${s.suffix}`
                    : `${Math.floor(obj.val)}${s.suffix}`;
              }
            },
          });
        }
      });
    };

    // Trigger stat counters
    const timer = setTimeout(triggerCounters, 400);

    // 3. Staggered reveal of Pillar cards
    const cards = document.querySelectorAll(".pillar-card");
    if (cards.length > 0) {
      animate(cards, {
        opacity: [0, 1],
        translateY: [30, 0],
        delay: stagger(120),
        duration: 1000,
        ease: "outExpo",
      });
    }

    // 4. Animated SVG Circuit Diagram draw-on
    if (svgDiagramRef.current) {
      try {
        const drawable = createDrawable(svgDiagramRef.current);
        animate(drawable, {
          draw: ["0 0", "0 1"],
          duration: 1600,
          ease: "inOut(3)",
        });
      } catch (e) {
        // fallback
      }
    }

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={`min-h-screen ${theme === "dark" ? "hero-radial-dark text-slate-100" : "hero-radial-light text-slate-900"}`}>
      {/* Top Navbar */}
      <header className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-emerald-600 flex items-center justify-center text-white font-extrabold text-base shadow-sm">
            EV
          </div>
          <div>
            <span className="font-bold text-base tracking-tight font-sans text-slate-900 dark:text-white">
              EV Battery Intelligence
            </span>
            <span className="hidden sm:inline-block ml-2 text-xs font-mono text-slate-600 dark:text-slate-400">
              • Final Year Platform
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Theme Switcher */}
          <button
            onClick={toggleTheme}
            className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-700 transition-all shadow-sm"
            title={`Switch to ${theme === "light" ? "Dark" : "Light"} mode`}
          >
            {theme === "light" ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
          </button>

          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 dark:bg-emerald-500 dark:hover:bg-emerald-600 text-white dark:text-slate-950 font-semibold text-sm transition-all hover:scale-[1.02] shadow-sm"
          >
            <span>Launch Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </header>

      {/* 1. HERO SECTION */}
      <section className="max-w-5xl mx-auto px-6 pt-16 pb-14 text-center">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-cyan-200 dark:border-cyan-800/60 bg-cyan-50 dark:bg-cyan-950/40 text-cyan-800 dark:text-cyan-300 text-xs font-semibold mb-6">
          <Sparkles className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400" />
          Tri-Pillar Machine Learning & Deep Learning Suite
        </div>

        <h1
          ref={heroHeadlineRef}
          className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.1]"
        >
          74 models. One fleet. <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-cyan-600 via-emerald-600 to-amber-600 bg-clip-text text-transparent">
            Zero surprises.
          </span>
        </h1>

        <p
          ref={heroSubRef}
          className="max-w-2xl mx-auto text-base sm:text-lg text-slate-600 dark:text-slate-400 mt-6 leading-relaxed"
        >
          A production-grade intelligence platform delivering real-time state estimation,
          200-Tree multi-zone thermal hazard detection, and non-linear degradation knee-point prognostics.
        </p>

        <div
          ref={heroCtaRef}
          className="mt-8 flex flex-wrap items-center justify-center gap-4"
        >
          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-7 py-3.5 rounded-xl bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white font-bold text-base transition-all hover:scale-105 shadow-md"
          >
            <span>Launch Live Dashboard</span>
            <ArrowRight className="w-5 h-5" />
          </Link>

          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-6 py-3.5 rounded-xl border border-slate-300 dark:border-slate-800 bg-white/80 dark:bg-slate-900 text-slate-700 dark:text-slate-200 font-semibold text-base hover:bg-slate-50 dark:hover:bg-slate-800 transition-all"
          >
            <Database className="w-4 h-4 text-slate-500" />
            <span>Interactive API Docs</span>
          </a>
        </div>
      </section>

      {/* 2. LIVE-FEELING STAT STRIP */}
      <section className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="app-card p-6 text-center">
            <div className="text-3xl sm:text-4xl font-extrabold font-mono text-cyan-600 dark:text-cyan-400">
              <span ref={stat1Ref}>74</span>
            </div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mt-1">
              Models Trained
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5">scikit-learn, XGBoost, PyTorch</div>
          </div>

          <div className="app-card p-6 text-center">
            <div className="text-3xl sm:text-4xl font-extrabold font-mono text-emerald-600 dark:text-emerald-400">
              <span ref={stat2Ref}>11 APIs</span>
            </div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mt-1">
              REST Endpoints
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5">FastAPI & FastMCP tools</div>
          </div>

          <div className="app-card p-6 text-center">
            <div className="text-3xl sm:text-4xl font-extrabold font-mono text-amber-600 dark:text-amber-400">
              <span ref={stat3Ref}>930 MB+</span>
            </div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mt-1">
              Telemetry Processed
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5">Euler HiLoad fleet dataset</div>
          </div>

          <div className="app-card p-6 text-center">
            <div className="text-3xl sm:text-4xl font-extrabold font-mono text-purple-600 dark:text-purple-400">
              <span ref={stat4Ref}>99.97%</span>
            </div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mt-1">
              Champion Model R²
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5">Gradient Boosting RUL Champion</div>
          </div>
        </div>
      </section>

      {/* 3. TRI-PILLAR ARCHITECTURE SECTION */}
      <section className="max-w-6xl mx-auto px-6 py-14">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <Badge variant="emerald" size="sm">System Architecture</Badge>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mt-2">
            Engineered Across Three Synchronous Pillars
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
            Every layer addresses a distinct critical challenge in electric mobility operations.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Module A */}
          <div className="pillar-card app-card p-6 flex flex-col justify-between hover:shadow-md transition-all">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-cyan-50 dark:bg-cyan-950/60 border border-cyan-200 dark:border-cyan-800 flex items-center justify-center text-cyan-600 dark:text-cyan-400 mb-4">
                <Cpu className="w-6 h-6" />
              </div>
              <Badge variant="cyan" size="sm">Module A</Badge>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mt-2">
                Macro Fleet State Estimation
              </h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
                56 ML/DL models predicting State of Charge (SOC), State of Health (SOH), Remaining Useful Life (RUL), and Dynamic Range per charge.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-slate-100 dark:border-slate-800/80 text-[11px] font-mono text-cyan-700 dark:text-cyan-300">
              KNN (R²=0.9958) • XGBoost (R²=0.9672)
            </div>
          </div>

          {/* Module B */}
          <div className="pillar-card app-card p-6 flex flex-col justify-between hover:shadow-md transition-all">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 flex items-center justify-center text-emerald-600 dark:text-emerald-400 mb-4">
                <Flame className="w-6 h-6" />
              </div>
              <Badge variant="emerald" size="sm">Module B</Badge>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mt-2">
                BatteryIQ Cyber-Physical Safety
              </h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
                Multi-zone thermal hazard classification across battery, inverter, and motor. Sequential spatial-temporal SOH using PyTorch 1D-CNN+LSTM.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-slate-100 dark:border-slate-800/80 text-[11px] font-mono text-emerald-700 dark:text-emerald-300">
              200-Tree RF (99.71% Acc) • PyTorch CNN-LSTM
            </div>
          </div>

          {/* Module C */}
          <div className="pillar-card app-card p-6 flex flex-col justify-between hover:shadow-md transition-all">
            <div>
              <div className="w-12 h-12 rounded-2xl bg-purple-50 dark:bg-purple-950/60 border border-purple-200 dark:border-purple-800 flex items-center justify-center text-purple-600 dark:text-purple-400 mb-4">
                <TrendingDown className="w-6 h-6" />
              </div>
              <Badge variant="purple" size="sm">Module C</Badge>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mt-2">
                BA-BMS & Knee Prognostics
              </h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
                Driver Aggressiveness Index (AI) and Battery Stress Index (BSI) stress models, paired with 28-feature XGBoost non-linear knee point forecasting.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-slate-100 dark:border-slate-800/80 text-[11px] font-mono text-purple-700 dark:text-purple-300">
              RUL to Knee Cycles • Piecewise MSE Optimizer
            </div>
          </div>
        </div>
      </section>

      {/* 4. ANIMATED SVG CIRCUIT / BATTERY DIAGRAM */}
      <section className="max-w-4xl mx-auto px-6 py-10 text-center">
        <div className="app-card p-6 sm:p-8">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500">
              Digital Twin Telemetry Circuit Loop
            </span>
            <Badge variant="cyan" size="sm">anime.js v4 Animated Path</Badge>
          </div>

          <svg
            viewBox="0 0 600 160"
            className="w-full h-32 sm:h-40 overflow-visible text-cyan-600 dark:text-cyan-400"
          >
            <defs>
              <linearGradient id="circuitGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#0891B2" />
                <stop offset="50%" stopColor="#059669" />
                <stop offset="100%" stopColor="#7C3AED" />
              </linearGradient>
            </defs>

            {/* Circuit Outline */}
            <path
              ref={svgDiagramRef}
              d="M 30 80 L 140 80 L 170 30 L 220 130 L 270 30 L 320 130 L 350 80 L 460 80 L 490 50 L 520 110 L 570 80"
              fill="none"
              stroke="url(#circuitGrad)"
              strokeWidth="3.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Node markers */}
            <circle cx="30" cy="80" r="5" className="fill-cyan-600" />
            <circle cx="140" cy="80" r="4" className="fill-emerald-600" />
            <circle cx="350" cy="80" r="4" className="fill-purple-600" />
            <circle cx="570" cy="80" r="5" className="fill-rose-600" />

            {/* Labels */}
            <text x="30" y="115" fontSize="10" fontFamily="monospace" textAnchor="middle" fill="#64748B">
              BMS Sensor Input
            </text>
            <text x="245" y="150" fontSize="10" fontFamily="monospace" textAnchor="middle" fill="#64748B">
              74 Model Feature Pipeline
            </text>
            <text x="570" y="115" fontSize="10" fontFamily="monospace" textAnchor="middle" fill="#64748B">
              Prognostic Output
            </text>
          </svg>
        </div>
      </section>

      {/* 5. FOOTER CTA */}
      <footer className="max-w-6xl mx-auto px-6 pt-8 pb-16 border-t border-slate-200 dark:border-slate-800/80 text-center">
        <h3 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
          Ready to inspect live vehicle telemetry?
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5">
          Launch the full dashboard with interactive 3D digital twin, anime.js gauges, and AI Copilot.
        </p>

        <div className="mt-6 flex justify-center">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-8 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 dark:bg-emerald-500 dark:hover:bg-emerald-600 text-white dark:text-slate-950 font-bold text-sm transition-all hover:scale-105 shadow-md"
          >
            <span>Launch Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="mt-10 text-xs text-slate-600 dark:text-slate-400 font-mono">
          Final Year Project • EV Battery Intelligence Platform • 2026
        </div>
      </footer>
    </div>
  );
}
