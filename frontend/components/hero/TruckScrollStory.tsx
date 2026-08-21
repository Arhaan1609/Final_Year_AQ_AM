'use client';
import React, { useEffect, useRef, useState } from 'react';
import { createTimeline, stagger, onScroll } from 'animejs';
import { Zap, ShieldCheck, BatteryCharging, Gauge, CheckCircle2 } from 'lucide-react';

export default function TruckScrollStory() {
  const trackRef = useRef<HTMLDivElement>(null);
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    if (!trackRef.current) return;

    // Direct Window Scroll Listener (guarantees real-time 60fps scrub across all browsers)
    const handleScroll = () => {
      if (!trackRef.current) return;
      const rect = trackRef.current.getBoundingClientRect();
      const totalScroll = trackRef.current.offsetHeight - window.innerHeight;
      if (totalScroll <= 0) return;

      const progress = Math.max(0, Math.min(1, -rect.top / totalScroll));
      setScrollProgress(progress);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Initial check

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  // Compute live visual states for seamless fallback & fluid rendering
  const stage1P = Math.min(1, Math.max(0, scrollProgress / 0.35)); // 0 -> 1 during stage 1
  const stage2P = Math.min(1, Math.max(0, (scrollProgress - 0.35) / 0.25)); // 0 -> 1 during stage 2
  const stage3P = Math.min(1, Math.max(0, (scrollProgress - 0.60) / 0.25)); // 0 -> 1 during stage 3
  const stage4P = Math.min(1, Math.max(0, (scrollProgress - 0.85) / 0.15)); // 0 -> 1 during stage 4

  const truckX = -800 * (1 - stage1P);
  const wheelDeg = stage1P * 720;
  const doorScale = Math.max(0.05, 1 - stage2P);
  const packOpacity = stage3P;
  const sceneScale = 1 - stage4P * 0.1;
  const sceneOpacity = Math.max(0.1, 1 - stage4P * 0.9);

  return (
    <div ref={trackRef} className="relative w-full" style={{ height: '400vh' }}>
      {/* Pinned 100vh Viewport Stage */}
      <div className="sticky top-0 h-screen w-full overflow-hidden flex flex-col items-center justify-center bg-[var(--bg-page)] border-b border-[var(--border-subtle)]">
        
        {/* Top Floating Badge & Progress Bar */}
        <div className="absolute top-6 left-1/2 -translate-x-1/2 z-20 flex flex-col items-center gap-2">
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/95 dark:bg-slate-900/95 border border-slate-200 dark:border-slate-800 shadow-md backdrop-blur-md">
            <Zap className="w-4 h-4 text-emerald-600 dark:text-emerald-400 animate-pulse" />
            <span className="text-xs font-mono font-bold text-slate-800 dark:text-slate-200">
              Interactive EV Fleet Story • {Math.round(scrollProgress * 100)}% Scrubbed
            </span>
          </div>

          {/* Stage Breadcrumb */}
          <div className="flex items-center gap-3 text-[11px] font-mono font-medium text-slate-500 dark:text-slate-400 bg-white/80 dark:bg-slate-900/80 px-3 py-1 rounded-full border border-slate-200/60 dark:border-slate-800/60">
            <span className={stage1P < 1 ? "text-cyan-600 dark:text-cyan-400 font-bold" : "text-emerald-600 dark:text-emerald-400"}>1. Arrival</span>
            <span>→</span>
            <span className={stage1P === 1 && stage2P < 1 ? "text-cyan-600 dark:text-cyan-400 font-bold" : stage2P === 1 ? "text-emerald-600 dark:text-emerald-400" : ""}>2. Door Reveal</span>
            <span>→</span>
            <span className={stage2P === 1 && stage3P < 1 ? "text-cyan-600 dark:text-cyan-400 font-bold" : stage3P === 1 ? "text-emerald-600 dark:text-emerald-400" : ""}>3. Pack Online</span>
            <span>→</span>
            <span className={stage4P > 0 ? "text-cyan-600 dark:text-cyan-400 font-bold" : ""}>4. Fleet Telematics</span>
          </div>
        </div>

        {/* The Animated SVG Scene */}
        <svg
          viewBox="0 0 1000 500"
          className="truck-scene w-full h-full max-h-[85vh] select-none"
          style={{
            transform: `scale(${sceneScale})`,
            opacity: sceneOpacity,
            transition: 'transform 0.05s linear, opacity 0.05s linear',
          }}
        >
          <defs>
            <linearGradient id="truckBodyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0F172A" />
              <stop offset="100%" stopColor="#1E293B" />
            </linearGradient>
            <linearGradient id="cabWindowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.85" />
              <stop offset="100%" stopColor="#0284C7" stopOpacity="0.4" />
            </linearGradient>
            <linearGradient id="packEnclosure" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#0A0D14" />
              <stop offset="50%" stopColor="#111622" />
              <stop offset="100%" stopColor="#0A0D14" />
            </linearGradient>
            <filter id="glowG" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="8" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Road Surface & Horizon Lines */}
          <line x1="0" y1="390" x2="1000" y2="390" stroke="var(--border-subtle, #E4E7EC)" strokeWidth="3" />
          <line
            x1="0"
            y1="394"
            x2="1000"
            y2="394"
            stroke="#059669"
            strokeWidth="2"
            strokeDasharray="24 16"
            strokeDashoffset={-wheelDeg * 1.5}
            opacity="0.8"
          />

          {/* Main Commercial Delivery Truck Group */}
          <g
            className="truck-group"
            transform={`translate(${200 + truckX}, 160)`}
          >
            {/* Cargo Box Chassis */}
            <rect x="0" y="30" width="460" height="190" rx="12" fill="url(#truckBodyGrad)" stroke="#334155" strokeWidth="2.5" />
            
            {/* Cab Section (Right / Front of Truck) */}
            <path d="M 460 70 L 530 70 Q 570 70 580 120 L 590 190 Q 590 220 560 220 L 460 220 Z" fill="#0F172A" stroke="#334155" strokeWidth="2.5" />
            
            {/* Windshield */}
            <path d="M 470 80 L 525 80 Q 550 80 558 120 L 470 120 Z" fill="url(#cabWindowGrad)" />

            {/* Front Headlight & Beam */}
            <polygon points="585,180 780,130 780,230 585,200" fill="#38BDF8" opacity="0.2" />
            <circle cx="585" cy="190" r="7" fill="#38BDF8" />

            {/* Interior Battery Pack (Revealed when doors open) */}
            <g
              className="battery-pack"
              transform="translate(40, 50)"
              style={{
                opacity: packOpacity,
                transform: `translate(40px, ${50 + (1 - stage3P) * 20}px)`,
                transition: 'opacity 0.1s linear, transform 0.1s linear',
              }}
            >
              {/* Pack Frame */}
              <rect x="0" y="0" width="380" height="150" rx="10" fill="url(#packEnclosure)" stroke="#059669" strokeWidth="2" />
              
              {/* BMS Active Header */}
              <rect x="15" y="12" width="350" height="24" rx="5" fill="#0F172A" stroke="#059669" strokeWidth="1" />
              <circle cx="30" cy="24" r="5" fill={stage3P > 0.3 ? "#10B981" : "#64748B"} />
              <text x="45" y="28" fill="#10B981" fontSize="11" fontFamily="monospace" fontWeight="bold">
                BMS MASTER UNIT • 72V 150Ah LFP • 99.4% SOH
              </text>
              <text x="335" y="28" fill="#38BDF8" fontSize="10" fontFamily="monospace" fontWeight="bold">
                CAN-BUS
              </text>

              {/* 8 Lithium Battery Cells */}
              {Array.from({ length: 8 }).map((_, i) => {
                const cellActive = stage3P > (i * 0.1);
                return (
                  <g key={i} transform={`translate(${20 + i * 43}, 46)`}>
                    <rect
                      className="battery-cell"
                      x="0"
                      y="0"
                      width="35"
                      height="85"
                      rx="6"
                      fill={cellActive ? "#059669" : "#334155"}
                      stroke={cellActive ? "#34D399" : "#475569"}
                      strokeWidth="1.5"
                    />
                    <circle cx="17.5" cy="14" r="4" fill={cellActive ? "#A7F3D0" : "#64748B"} />
                    <text
                      x="17.5"
                      y="52"
                      fill="#FFFFFF"
                      fontSize="10"
                      fontFamily="monospace"
                      textAnchor="middle"
                      fontWeight="bold"
                    >
                      C{i + 1}
                    </text>
                    <text
                      x="17.5"
                      y="68"
                      fill={cellActive ? "#A7F3D0" : "#94A3B8"}
                      fontSize="8"
                      fontFamily="monospace"
                      textAnchor="middle"
                    >
                      {cellActive ? "3.32V" : "0.0V"}
                    </text>
                  </g>
                );
              })}
            </g>

            {/* Left Cargo Door (Hinged at left x=0) */}
            <g
              className="door-left"
              style={{
                transformOrigin: '0px 125px',
                transform: `scaleX(${doorScale})`,
                transition: 'transform 0.05s linear',
              }}
            >
              <rect x="0" y="30" width="230" height="190" rx="6" fill="#1E293B" stroke="#475569" strokeWidth="2" />
              <line x1="25" y1="50" x2="25" y2="200" stroke="#334155" strokeWidth="1.5" />
              <circle cx="210" cy="125" r="6" fill="#94A3B8" />
            </g>

            {/* Right Cargo Door (Hinged at right x=460) */}
            <g
              className="door-right"
              style={{
                transformOrigin: '460px 125px',
                transform: `scaleX(${doorScale})`,
                transition: 'transform 0.05s linear',
              }}
            >
              <rect x="230" y="30" width="230" height="190" rx="6" fill="#1E293B" stroke="#475569" strokeWidth="2" />
              <line x1="435" y1="50" x2="435" y2="200" stroke="#334155" strokeWidth="1.5" />
              <circle cx="250" cy="125" r="6" fill="#94A3B8" />
            </g>

            {/* Rear Wheel */}
            <g transform="translate(80, 220)">
              <circle cx="0" cy="0" r="32" fill="#0F172A" stroke="#334155" strokeWidth="4" />
              <g className="wheel-spin" style={{ transformOrigin: '0px 0px', transform: `rotate(${wheelDeg}deg)` }}>
                <circle cx="0" cy="0" r="18" fill="#475569" />
                <line x1="-18" y1="0" x2="18" y2="0" stroke="#94A3B8" strokeWidth="3.5" />
                <line x1="0" y1="-18" x2="0" y2="18" stroke="#94A3B8" strokeWidth="3.5" />
              </g>
            </g>

            {/* Middle Wheel */}
            <g transform="translate(380, 220)">
              <circle cx="0" cy="0" r="32" fill="#0F172A" stroke="#334155" strokeWidth="4" />
              <g className="wheel-spin" style={{ transformOrigin: '0px 0px', transform: `rotate(${wheelDeg}deg)` }}>
                <circle cx="0" cy="0" r="18" fill="#475569" />
                <line x1="-18" y1="0" x2="18" y2="0" stroke="#94A3B8" strokeWidth="3.5" />
                <line x1="0" y1="-18" x2="0" y2="18" stroke="#94A3B8" strokeWidth="3.5" />
              </g>
            </g>

            {/* Front Wheel */}
            <g transform="translate(520, 220)">
              <circle cx="0" cy="0" r="32" fill="#0F172A" stroke="#334155" strokeWidth="4" />
              <g className="wheel-spin" style={{ transformOrigin: '0px 0px', transform: `rotate(${wheelDeg}deg)` }}>
                <circle cx="0" cy="0" r="18" fill="#475569" />
                <line x1="-18" y1="0" x2="18" y2="0" stroke="#94A3B8" strokeWidth="3.5" />
                <line x1="0" y1="-18" x2="0" y2="18" stroke="#94A3B8" strokeWidth="3.5" />
              </g>
            </g>
          </g>
        </svg>

        {/* Bottom Callout Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 text-xs font-mono text-slate-500 dark:text-slate-400">
          <span>{scrollProgress < 0.95 ? "Scroll down to drive the truck & energize cells" : "Release to Explore Platform Stats"}</span>
          <span className="text-emerald-600 dark:text-emerald-400 animate-bounce text-base font-bold">
            {scrollProgress < 0.95 ? "↓" : "✓"}
          </span>
        </div>

      </div>
    </div>
  );
}
