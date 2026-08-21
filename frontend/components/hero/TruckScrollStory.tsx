'use client';
import React, { useEffect, useRef } from 'react';
import { createTimeline, stagger, onScroll } from 'animejs';
import { Zap, ShieldCheck, Cpu } from 'lucide-react';

export default function TruckScrollStory() {
  const trackRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!trackRef.current) return;

    try {
      const tl = createTimeline({
        autoplay: onScroll({
          target: trackRef.current,
          sync: true, // scrubbed exactly to scroll position, forward AND backward
          enter: 'top top',
          leave: 'bottom bottom',
        }),
      });

      tl
        // Stage 1: Commercial EV Truck drives in from off-screen left
        .add('.truck-group', { translateX: ['-70vw', '0vw'], duration: 1200, ease: 'linear' })
        // Stage 1b: Wheels rotate during motion
        .add('.wheel-spin', { rotate: [0, 720], duration: 1200, ease: 'linear' }, '<')
        // Stage 2: Hold briefly, then cargo doors rotate open on their hinges
        .add('.door-left', { rotateY: [0, -110], duration: 800, ease: 'inOutQuad' }, '+=200')
        .add('.door-right', { rotateY: [0, 110], duration: 800, ease: 'inOutQuad' }, '<')
        // Stage 3: Battery pack slides up into view and cells energize one by one
        .add('.battery-pack', { translateY: [40, 0], opacity: [0, 1], duration: 700 }, '-=300')
        .add('.battery-cell', { fill: ['#CBD5E1', '#059669'], delay: stagger(80) }, '-=200')
        .add('.pack-glow', { opacity: [0, 0.8], duration: 600, ease: 'outQuad' }, '<')
        // Stage 4: Whole scene scales down and fades, handing off to the stats section below
        .add('.truck-scene', { scale: [1, 0.92], opacity: [1, 0], duration: 700 }, '+=300');
    } catch (e) {
      console.warn("TruckScrollStory timeline animation error:", e);
    }
  }, []);

  return (
    <div ref={trackRef} className="relative" style={{ height: '400vh' }}>
      <div className="sticky top-0 h-screen w-full overflow-hidden flex flex-col items-center justify-center bg-[var(--bg-page)] border-b border-[var(--border-subtle)]">
        
        {/* Pinned Stage Header Notice */}
        <div className="absolute top-8 left-1/2 -translate-x-1/2 z-20 flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/90 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm backdrop-blur-md">
          <Zap className="w-4 h-4 text-emerald-600 dark:text-emerald-400 animate-pulse" />
          <span className="text-xs font-mono font-semibold text-slate-700 dark:text-slate-200">
            Interactive Fleet Digital Twin • Scroll to Inspect Cyber-Physical Pack
          </span>
        </div>

        {/* Pinned SVG Stage */}
        <svg viewBox="0 0 1000 500" className="truck-scene w-full h-full max-h-[85vh] select-none">
          <defs>
            <linearGradient id="truckBodyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0F172A" />
              <stop offset="100%" stopColor="#1E293B" />
            </linearGradient>
            <linearGradient id="cabWindowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#0284C7" stopOpacity="0.4" />
            </linearGradient>
            <linearGradient id="packEnclosure" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#0F172A" />
              <stop offset="50%" stopColor="#1E293B" />
              <stop offset="100%" stopColor="#0F172A" />
            </linearGradient>
            <filter id="glowEffect" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="8" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Road and Grid Horizon */}
          <line x1="0" y1="390" x2="1000" y2="390" stroke="var(--border-subtle, #E4E7EC)" strokeWidth="3" />
          <line x1="0" y1="394" x2="1000" y2="394" stroke="#059669" strokeWidth="1.5" strokeDasharray="24 16" opacity="0.6" />

          {/* Main Truck Group (Moves in from left) */}
          <g className="truck-group" transform="translate(180, 160)">
            
            {/* Cargo Container Body */}
            <rect x="0" y="30" width="460" height="190" rx="12" fill="url(#truckBodyGrad)" stroke="#334155" strokeWidth="2" />
            <line x1="230" y1="30" x2="230" y2="220" stroke="#334155" strokeWidth="2" />

            {/* Cab Section (Right side - Front of Truck) */}
            <path d="M 460 70 L 530 70 Q 570 70 580 120 L 590 190 Q 590 220 560 220 L 460 220 Z" fill="#0F172A" stroke="#334155" strokeWidth="2" />
            
            {/* Cab Windshield */}
            <path d="M 470 80 L 525 80 Q 550 80 558 120 L 470 120 Z" fill="url(#cabWindowGrad)" />

            {/* Headlight Beam */}
            <polygon points="585,180 750,140 750,220 585,200" fill="#38BDF8" opacity="0.15" />
            <circle cx="585" cy="190" r="6" fill="#38BDF8" />

            {/* Cargo Doors (Rotate open in Stage 2) */}
            <g className="door-left" style={{ transformOrigin: '0px 125px' }}>
              <rect x="0" y="30" width="230" height="190" rx="6" fill="#1E293B" stroke="#475569" strokeWidth="1.5" />
              <line x1="20" y1="50" x2="20" y2="200" stroke="#334155" strokeWidth="1" />
              <circle cx="210" cy="125" r="5" fill="#94A3B8" />
            </g>

            <g className="door-right" style={{ transformOrigin: '460px 125px' }}>
              <rect x="230" y="30" width="230" height="190" rx="6" fill="#1E293B" stroke="#475569" strokeWidth="1.5" />
              <line x1="440" y1="50" x2="440" y2="200" stroke="#334155" strokeWidth="1" />
              <circle cx="250" cy="125" r="5" fill="#94A3B8" />
            </g>

            {/* Interior Battery Pack System (Revealed in Stage 3) */}
            <g className="battery-pack" style={{ opacity: 0 }} transform="translate(60, 60)">
              {/* Pack Shell */}
              <rect x="0" y="0" width="340" height="130" rx="10" fill="url(#packEnclosure)" stroke="#059669" strokeWidth="2" />
              
              {/* BMS Control Header */}
              <rect x="15" y="12" width="310" height="20" rx="4" fill="#0A0D14" />
              <text x="25" y="26" fill="#10B981" fontSize="10" fontFamily="monospace" fontWeight="bold">BMS ACTIVE • 72V 150Ah LFP</text>
              <circle cx="310" cy="22" r="4" fill="#10B981" />

              {/* Pack Glow Backdrop */}
              <rect className="pack-glow" x="20" y="40" width="300" height="75" rx="6" fill="#059669" opacity="0" filter="url(#glowEffect)" />

              {/* 8 Prismatic Lithium Battery Cells (Energize in Stage 3) */}
              {Array.from({ length: 8 }).map((_, i) => (
                <g key={i} transform={`translate(${25 + i * 36}, 45)`}>
                  <rect className="battery-cell" x="0" y="0" width="28" height="65" rx="4" fill="#CBD5E1" stroke="#334155" strokeWidth="1" />
                  <circle cx="14" cy="12" r="3" fill="#64748B" />
                  <text x="14" y="45" fill="#FFFFFF" fontSize="8" fontFamily="monospace" textAnchor="middle" opacity="0.8">
                    C{i + 1}
                  </text>
                </g>
              ))}
            </g>

            {/* Wheels & Tires with Rotation Origin */}
            <g transform="translate(80, 220)">
              <circle cx="0" cy="0" r="30" fill="#0F172A" stroke="#334155" strokeWidth="4" />
              <g className="wheel-spin" style={{ transformOrigin: '0px 0px' }}>
                <circle cx="0" cy="0" r="16" fill="#475569" />
                <line x1="-16" y1="0" x2="16" y2="0" stroke="#94A3B8" strokeWidth="3" />
                <line x1="0" y1="-16" x2="0" y2="16" stroke="#94A3B8" strokeWidth="3" />
              </g>
            </g>

            <g transform="translate(380, 220)">
              <circle cx="0" cy="0" r="30" fill="#0F172A" stroke="#334155" strokeWidth="4" />
              <g className="wheel-spin" style={{ transformOrigin: '0px 0px' }}>
                <circle cx="0" cy="0" r="16" fill="#475569" />
                <line x1="-16" y1="0" x2="16" y2="0" stroke="#94A3B8" strokeWidth="3" />
                <line x1="0" y1="-16" x2="0" y2="16" stroke="#94A3B8" strokeWidth="3" />
              </g>
            </g>

            <g transform="translate(520, 220)">
              <circle cx="0" cy="0" r="30" fill="#0F172A" stroke="#334155" strokeWidth="4" />
              <g className="wheel-spin" style={{ transformOrigin: '0px 0px' }}>
                <circle cx="0" cy="0" r="16" fill="#475569" />
                <line x1="-16" y1="0" x2="16" y2="0" stroke="#94A3B8" strokeWidth="3" />
                <line x1="0" y1="-16" x2="0" y2="16" stroke="#94A3B8" strokeWidth="3" />
              </g>
            </g>

          </g>
        </svg>

        {/* Scroll Instruction Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 text-xs font-mono text-slate-500 dark:text-slate-400">
          <span>Scroll to drive truck & energize battery pack</span>
          <span className="text-emerald-600 dark:text-emerald-400 animate-bounce text-base font-bold">↓</span>
        </div>

      </div>
    </div>
  );
}
