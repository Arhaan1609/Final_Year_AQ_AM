"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Terminal, Sparkles, ShieldCheck, Cpu, Database } from "lucide-react";

export const FinalCallToAction: React.FC = () => {
  return (
    <section className="py-24 px-6 sm:px-10 max-w-7xl mx-auto">
      {/* Outer Card with Gradient Border */}
      <div className="relative rounded-3xl overflow-hidden bg-gradient-to-b from-slate-900 via-slate-950 to-slate-950 text-white border border-slate-800 p-8 sm:p-16 text-center shadow-2xl">
        {/* Glowing Orbs */}
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-emerald-500/20 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-cyan-500/20 rounded-full blur-[120px] pointer-events-none" />

        <div className="relative z-10 max-w-3xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 text-xs font-mono font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Ready for Production Fleet Deployment</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
            Deploy Autonomous Battery Intelligence in Minutes.
          </h2>

          <p className="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Gain immediate visibility into 778 commercial chassis, test custom telemetry, and harness 74 pre-trained machine learning and deep learning models.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2.5 px-8 py-4 rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-400 hover:from-emerald-400 hover:to-emerald-300 text-slate-950 font-extrabold text-sm shadow-lg shadow-emerald-500/30 hover:shadow-emerald-500/50 transition-all hover:scale-105 active:scale-95 cursor-pointer"
            >
              <span>Launch Live Fleet Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-7 py-4 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 font-semibold text-sm hover:bg-slate-800 transition-all font-mono"
            >
              <Terminal className="w-4 h-4 text-cyan-400" />
              <span>Swagger API Docs</span>
            </a>
          </div>
        </div>
      </div>

      {/* Modern Startup Footer */}
      <footer className="mt-20 pt-8 border-t border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-slate-500 dark:text-slate-400">
        <div>
          EV Battery Intelligence Platform • Tri-Pillar Cyber-Physical BMS System
        </div>
        <div className="flex items-center gap-6">
          <a href="#pipeline" className="hover:text-emerald-500 transition-colors">Architecture</a>
          <a href="#sandbox" className="hover:text-cyan-500 transition-colors">Live Sandbox</a>
          <a href="#roi" className="hover:text-emerald-500 transition-colors">ROI Calculator</a>
          <a href="http://localhost:8000/health" target="_blank" rel="noopener noreferrer" className="hover:text-emerald-500 transition-colors">Health Probe</a>
        </div>
      </footer>
    </section>
  );
};
