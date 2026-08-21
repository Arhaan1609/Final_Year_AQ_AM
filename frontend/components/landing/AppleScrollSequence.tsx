"use client";

import React, { useState } from "react";
import { ScrollImageSequence } from "../ui/ScrollImageSequence";
import { ShieldCheck, Zap, Activity, Cpu, Sparkles } from "lucide-react";

export const AppleScrollSequence: React.FC = () => {
  const [scrollProgress, setScrollProgress] = useState<number>(0);

  return (
    <section className="relative w-full bg-[#0A0D14] text-white">
      {/* Sequence Section with Apple-Style Pinned Canvas */}
      <ScrollImageSequence
        frameFolder="/sequence"
        frameCount={300}
        fileNamePrefix="ezgif-frame-"
        fileNameSuffix=".jpg"
        digitPadding={3}
        scrollDistance={3600}
        scrub={0.6}
        fit="cover"
        onProgress={(p) => setScrollProgress(p)}
      >
        {/* Top Sticky Header */}
        <div className="w-full flex items-center justify-between pointer-events-auto">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 backdrop-blur-md border border-cyan-500/30 text-cyan-400 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span>4K CINEMATIC SEQUENCE • 300 FRAMES</span>
          </div>
          <div className="px-3 py-1.5 rounded-full bg-slate-900/80 backdrop-blur-md border border-slate-700 text-slate-300 text-xs font-mono">
            SCROLL SCRUB: <span className="text-cyan-400 font-bold">{scrollProgress}%</span>
          </div>
        </div>

        {/* Dynamic Telemetry Story Callout Overlays based on scroll progress */}
        <div className="w-full max-w-4xl mx-auto mb-12 grid grid-cols-1 md:grid-cols-3 gap-4 pointer-events-auto">
          <div className="p-4 rounded-2xl bg-slate-950/70 backdrop-blur-xl border border-slate-800 text-left shadow-2xl transition-all duration-300 hover:border-cyan-500/50">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center mb-2">
              <Zap className="w-4 h-4" />
            </div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono">
              High-Rate Electrochemistry
            </h4>
            <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
              Real-time scrubbing across 300 chronological pack states with zero decode stutter.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950/70 backdrop-blur-xl border border-slate-800 text-left shadow-2xl transition-all duration-300 hover:border-emerald-500/50">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-2">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono">
              Micro-Displacement Trace
            </h4>
            <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
              Visualizing thermal expansion, cell dilation, and degradation pathways during C-rate stress.
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950/70 backdrop-blur-xl border border-slate-800 text-left shadow-2xl transition-all duration-300 hover:border-purple-500/50">
            <div className="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center mb-2">
              <Cpu className="w-4 h-4" />
            </div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono">
              74 Champion Models
            </h4>
            <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
              Synchronized inference feeding dynamic CAN-bus telemetry directly into the dashboard.
            </p>
          </div>
        </div>
      </ScrollImageSequence>
    </section>
  );
};
export default AppleScrollSequence;
