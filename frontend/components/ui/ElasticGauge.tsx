"use client";

import React, { useEffect, useRef } from "react";
import anime from "animejs";

interface ElasticGaugeProps {
  value: number;
  min?: number;
  max?: number;
  label?: string;
  unit?: string;
  color?: string;
  size?: number;
  showTicks?: boolean;
}

export const ElasticGauge: React.FC<ElasticGaugeProps> = ({
  value,
  min = 0,
  max = 100,
  label = "Gauge",
  unit = "%",
  color = "#10B981",
  size = 180,
  showTicks = true,
}) => {
  const needleRef = useRef<SVGLineElement>(null);
  const prevAngleRef = useRef<number>(-90);

  // Map value to angle (-90deg to +90deg)
  const clamped = Math.max(min, Math.min(max, value));
  const ratio = (clamped - min) / (max - min);
  const targetAngle = -90 + ratio * 180;

  useEffect(() => {
    if (!needleRef.current) return;

    const fromAngle = prevAngleRef.current;
    prevAngleRef.current = targetAngle;

    const angleObj = { angle: fromAngle };

    const anim = anime({
      targets: angleObj,
      angle: targetAngle,
      duration: 1200,
      easing: "easeOutElastic(1, 0.45)",
      update: () => {
        if (needleRef.current) {
          needleRef.current.setAttribute(
            "transform",
            `rotate(${angleObj.angle} 100 100)`
          );
        }
      },
    });

    return () => {
      anim.pause();
    };
  }, [targetAngle]);

  return (
    <div className="flex flex-col items-center justify-center relative select-none">
      <svg
        width={size}
        height={size * 0.65}
        viewBox="0 0 200 130"
        className="overflow-visible"
      >
        <defs>
          <linearGradient id={`gauge-grad-${label}`} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#06B6D4" stopOpacity="0.8" />
            <stop offset="60%" stopColor="#10B981" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#EF4444" stopOpacity="0.9" />
          </linearGradient>
          <filter id="gauge-glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Background Track */}
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="#1E293B"
          strokeWidth="12"
          strokeLinecap="round"
        />

        {/* Active Arc (Colored) */}
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke={`url(#gauge-grad-${label})`}
          strokeWidth="10"
          strokeLinecap="round"
          opacity="0.9"
        />

        {/* Scale Ticks */}
        {showTicks && (
          <>
            <line x1="20" y1="100" x2="28" y2="100" stroke="#475569" strokeWidth="2" />
            <line x1="100" y1="20" x2="100" y2="28" stroke="#475569" strokeWidth="2" />
            <line x1="180" y1="100" x2="172" y2="100" stroke="#475569" strokeWidth="2" />
          </>
        )}

        {/* Elastic Needle */}
        <line
          ref={needleRef}
          x1="100"
          y1="100"
          x2="100"
          y2="32"
          stroke={color}
          strokeWidth="3.5"
          strokeLinecap="round"
          filter="url(#gauge-glow)"
          transform="rotate(-90 100 100)"
        />

        {/* Center Hub Pivot */}
        <circle cx="100" cy="100" r="8" fill="#111622" stroke={color} strokeWidth="3" />
        <circle cx="100" cy="100" r="3" fill="#F8FAFC" />
      </svg>

      {/* Numerical readout */}
      <div className="text-center -mt-4">
        <div className="text-2xl font-bold font-mono tracking-tight text-slate-100 tabular-nums">
          {value.toFixed(1)}
          <span className="text-xs text-slate-400 font-sans ml-1">{unit}</span>
        </div>
        <div className="text-xs font-medium uppercase tracking-wider text-slate-400 mt-0.5">
          {label}
        </div>
      </div>
    </div>
  );
};
