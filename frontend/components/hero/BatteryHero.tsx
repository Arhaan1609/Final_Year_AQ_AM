'use client';
import React, { useEffect, useRef } from 'react';
import { animate, stagger, onScroll, utils } from 'animejs';
import Link from 'next/link';
import { ArrowRight, Sparkles, Shield, Cpu, Activity, Zap } from 'lucide-react';

export default function BatteryHero() {
  const heroRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!heroRef.current) return;

    try {
      // Headline: word-by-word stagger reveal on mount
      animate('.hero-word', {
        opacity: [0, 1],
        translateY: [24, 0],
        delay: stagger(80),
        duration: 700,
        ease: 'outExpo',
      });

      // SIGNATURE ELEMENT: battery cells fill, scroll-scrubbed (not one-shot).
      // As the user scrolls through the hero, cells fill bottom-to-top in sync
      // with scroll position, and un-fill if they scroll back up.
      animate('.battery-cell', {
        scaleY: [0, 1],
        backgroundColor: ['#E4E7EC', '#059669'],
        delay: stagger(40, { from: 'first' }),
        autoplay: onScroll({
          target: heroRef.current,
          sync: true,
          enter: 'bottom top',
          leave: 'top top',
        }),
      });

      // Stat strip count-ups, each triggered independently as it scrolls into view
      document.querySelectorAll<HTMLElement>('.stat-value').forEach((el) => {
        const to = Number(el.dataset.value);
        animate(el, {
          innerHTML: [0, to],
          modifier: utils.round(1),
          duration: 1200,
          ease: 'outExpo',
          autoplay: onScroll({ target: el, sync: false }),
        });
      });
    } catch (e) {
      console.warn("Hero animation initialization:", e);
    }
  }, []);

  return (
    <section ref={heroRef} className="relative py-20 px-6 max-w-7xl mx-auto flex flex-col items-center text-center">
      {/* Top Badge */}
      <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800/80 text-emerald-700 dark:text-emerald-300 text-xs font-semibold mb-8 shadow-sm">
        <Sparkles className="w-3.5 h-3.5" />
        <span>Tri-Pillar EV Telematics Engine • 74 Production Models</span>
      </div>

      {/* Main Headline */}
      <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100 max-w-5xl leading-[1.1] mb-6">
        {'74 models. One fleet. Zero surprises.'.split(' ').map((word, i) => (
          <span className="hero-word inline-block mr-3" key={i}>
            {word}
          </span>
        ))}
      </h1>

      {/* Subheadline */}
      <p className="text-base sm:text-xl text-slate-600 dark:text-slate-300 max-w-3xl mb-10 leading-relaxed font-normal">
        Real-time multi-OEM State Estimation, Cyber-Physical Thermal Safety, and Behavior-Aware Knee Prognostics engineered for commercial EV fleets across India.
      </p>

      {/* CTA Buttons */}
      <div className="flex flex-wrap items-center justify-center gap-4 mb-16">
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2.5 px-7 py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm shadow-md hover:shadow-lg transition-all hover:scale-105 active:scale-95"
        >
          <span>Launch Dashboard</span>
          <ArrowRight className="w-4 h-4" />
        </Link>

        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 font-semibold text-sm hover:bg-slate-50 dark:hover:bg-slate-800 shadow-sm transition-all"
        >
          <Cpu className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
          <span>FastAPI Docs (11 Endpoints)</span>
        </a>
      </div>

      {/* SIGNATURE ELEMENT: Battery Pack Cells filling with scroll */}
      <div className="w-full max-w-xl p-6 rounded-2xl bg-white dark:bg-[#111622] border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col items-center">
        <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-4 flex items-center gap-2">
          <Zap className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          <span>Scroll-Scrubbed Battery Cell Energization</span>
        </div>

        <div
          className="battery-pack"
          aria-hidden="true"
          style={{ display: 'flex', gap: 10, alignItems: 'flex-end', height: 160 }}
        >
          {Array.from({ length: 12 }).map((_, i) => (
            <div
              className="battery-cell"
              key={i}
              style={{
                width: 28,
                height: 140,
                transform: 'scaleY(0)',
                transformOrigin: '50% 100%',
                background: 'var(--border-subtle)',
                borderRadius: 6,
              }}
            />
          ))}
        </div>
        <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-3 font-mono">
          Scroll down to scrub cell charge level ↑↓
        </p>
      </div>

      {/* Stat Strip Count-Ups */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 w-full max-w-5xl mt-16 text-left">
        <div className="app-card p-5">
          <div className="text-xs font-medium text-slate-500 dark:text-slate-400">Models Trained</div>
          <div className="text-3xl sm:text-4xl font-extrabold text-cyan-700 dark:text-cyan-400 mt-1 font-mono">
            <span className="stat-value" data-value="74">0</span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Across 8 task subfolders</p>
        </div>

        <div className="app-card p-5">
          <div className="text-xs font-medium text-slate-500 dark:text-slate-400">Live Endpoints</div>
          <div className="text-3xl sm:text-4xl font-extrabold text-emerald-700 dark:text-emerald-400 mt-1 font-mono">
            <span className="stat-value" data-value="11">0</span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">FastAPI REST microservice</p>
        </div>

        <div className="app-card p-5">
          <div className="text-xs font-medium text-slate-500 dark:text-slate-400">Telemetry Processed</div>
          <div className="text-3xl sm:text-4xl font-extrabold text-purple-700 dark:text-purple-400 mt-1 font-mono">
            <span className="stat-value" data-value="930">0</span>
            <span className="text-xl">MB+</span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">370,666 raw driving cycles</p>
        </div>

        <div className="app-card p-5">
          <div className="text-xs font-medium text-slate-500 dark:text-slate-400">Champion Accuracy</div>
          <div className="text-3xl sm:text-4xl font-extrabold text-amber-700 dark:text-amber-400 mt-1 font-mono">
            <span className="stat-value" data-value="99.97">0</span>
            <span className="text-xl">%</span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">R² score on RUL prognostics</p>
        </div>
      </div>
    </section>
  );
}
