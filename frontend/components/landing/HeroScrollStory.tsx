"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ScrollImageSequence } from "../ui/ScrollImageSequence";
import {
  Activity,
  ChevronRight,
  ArrowDown,
  Sparkles,
  Play,
  Pause,
  RotateCcw,
} from "lucide-react";

export const HeroScrollStory: React.FC = () => {
  const [progress, setProgress] = useState<number>(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState<boolean>(false);

  // Stage flag for hero intro
  const isStage1 = progress < 25; // Assembled Heavy Truck
  const isStage4 = progress >= 80; // Exploded Battery Pack

  // Auto-Demo Scroll Loop
  useEffect(() => {
    let animFrame: number;

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
                <span>Auto-Demo Mode</span>
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

          {/* Progress Indicator */}
          <div className="px-3 py-2 rounded-xl bg-slate-950/80 backdrop-blur-md border border-slate-700/80 text-slate-400 text-xs font-mono shadow-lg">
            <span>SCRUB: </span>
            <span className="text-cyan-400 font-bold">{progress}%</span>
          </div>
        </div>

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

        {/* ─── BOTTOM-RIGHT DIRECT LAUNCH CTA ON 100% DECONSTRUCTION ─── */}
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
      </ScrollImageSequence>
    </section>
  );
};
export default HeroScrollStory;
