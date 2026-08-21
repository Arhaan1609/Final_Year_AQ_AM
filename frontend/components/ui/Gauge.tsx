'use client';
import React, { useEffect, useRef } from 'react';
import { animate } from 'animejs';

export function Gauge({ value, max = 100, label }: { value: number; max?: number; label: string }) {
  const needleRef = useRef<SVGLineElement>(null);
  const angle = -90 + (Math.max(0, Math.min(value, max)) / max) * 180;

  useEffect(() => {
    if (!needleRef.current) return;
    try {
      animate(needleRef.current, {
        rotate: angle,
        ease: 'outElastic(1, .6)',
        duration: 800,
      });
    } catch (e) {
      if (needleRef.current) {
        needleRef.current.style.transform = `rotate(${angle}deg)`;
      }
    }
  }, [angle]);

  return (
    <svg viewBox="0 0 200 120" className="gauge w-full max-w-[200px] h-auto overflow-visible" role="img" aria-label={`${label}: ${value}`}>
      <path d="M20 100 A80 80 0 0 1 180 100" fill="none" stroke="var(--border-subtle, #E4E7EC)" strokeWidth="12" strokeLinecap="round" />
      <line
        ref={needleRef}
        x1="100" y1="100" x2="100" y2="30"
        stroke="var(--accent-telemetry, #0891B2)" strokeWidth="4"
        strokeLinecap="round"
        style={{ transformOrigin: '100px 100px', transform: `rotate(${angle}deg)` }}
      />
      <circle cx="100" cy="100" r="6" fill="var(--accent-telemetry, #0891B2)" />
      <text x="100" y="118" textAnchor="middle" fontSize="12" fill="var(--text-secondary, #475569)" className="font-semibold">{label}</text>
    </svg>
  );
}

export default Gauge;
