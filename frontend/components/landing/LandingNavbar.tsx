"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { Badge } from "../ui/Badge";
import { Sun, Moon, ArrowRight, Activity, ShieldCheck, Cpu, Terminal } from "lucide-react";

export const LandingNavbar: React.FC = () => {
  const { theme, toggleTheme } = useFleetStore();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-white/80 dark:bg-[#0A0D14]/80 backdrop-blur-xl border-b border-slate-200/80 dark:border-slate-800/80 shadow-sm py-3"
          : "bg-transparent py-5"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 sm:px-10 flex items-center justify-between">
        {/* Brand Logo & Pill */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-cyan-500 via-emerald-500 to-emerald-400 flex items-center justify-center text-white font-extrabold text-sm shadow-md shadow-emerald-500/20 group-hover:scale-105 transition-transform">
            EV
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-base sm:text-lg tracking-tight text-slate-900 dark:text-slate-100">
                EV Battery Intelligence
              </span>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-700/60 text-emerald-700 dark:text-emerald-300">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                74 Models Live
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-mono hidden sm:block">
              Commercial Fleet AI Platform • Sub-second BMS Inference
            </p>
          </div>
        </Link>

        {/* Center Quick Navigation Links */}
        <nav className="hidden lg:flex items-center gap-8 text-xs font-semibold text-slate-600 dark:text-slate-300">
          <a href="#pipeline" className="hover:text-emerald-500 dark:hover:text-emerald-400 transition-colors">
            4-Stage Pipeline
          </a>
          <a href="#sandbox" className="hover:text-cyan-500 dark:hover:text-cyan-400 transition-colors flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            Live Model Sandbox
          </a>
          <a href="#architecture" className="hover:text-emerald-500 dark:hover:text-emerald-400 transition-colors">
            Tri-Pillar AI
          </a>
          <a href="#roi" className="hover:text-emerald-500 dark:hover:text-emerald-400 transition-colors">
            Fleet ROI
          </a>
          <a href="#comparison" className="hover:text-emerald-500 dark:hover:text-emerald-400 transition-colors">
            Vs Legacy BMS
          </a>
        </nav>

        {/* Right CTAs */}
        <div className="flex items-center gap-3">
          {/* Theme Switcher */}
          <button
            onClick={toggleTheme}
            className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all shadow-sm"
            title={`Switch to ${theme === "light" ? "Dark" : "Light"} mode`}
          >
            {theme === "light" ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
          </button>

          {/* Swagger docs link */}
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden md:inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-900/60 text-slate-600 dark:text-slate-300 text-xs font-mono font-medium hover:border-slate-300 dark:hover:border-slate-700 transition-all"
          >
            <Terminal className="w-3.5 h-3.5 text-cyan-500" />
            <span>API Docs</span>
          </a>

          {/* Primary Dashboard Launch CTA */}
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-4 sm:px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-bold text-xs shadow-md shadow-emerald-600/25 hover:shadow-lg hover:shadow-emerald-600/40 transition-all hover:scale-105 active:scale-95 cursor-pointer"
          >
            <span>Launch Dashboard</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </header>
  );
};
