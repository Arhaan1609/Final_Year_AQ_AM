'use client';
import React, { useEffect, useRef } from 'react';
import { animate, createDrawable } from 'animejs';

export function KneeCurve({ pathD, kneeX, kneeY }: { pathD: string; kneeX: number; kneeY: number }) {
  const pathRef = useRef<SVGPathElement>(null);
  const markerRef = useRef<SVGCircleElement>(null);

  useEffect(() => {
    if (!pathRef.current) return;
    try {
      const drawable = createDrawable(pathRef.current);
      animate(drawable, {
        draw: ['0 0', '0 1'],
        duration: 1400,
        ease: 'inOut(3)',
        onComplete: () => {
          if (markerRef.current) {
            animate(markerRef.current, { scale: [0, 1.3, 1], duration: 500, ease: 'outElastic(1, .5)' });
          }
        },
      });
    } catch (e) {
      console.warn("Knee curve animation fallback:", e);
    }
  }, [pathD]);

  return (
    <svg viewBox="0 0 400 200" className="w-full h-auto overflow-visible" role="img" aria-label="Degradation curve with knee point">
      <path ref={pathRef} d={pathD} fill="none" stroke="var(--accent-telemetry, #0891B2)" strokeWidth="3" strokeLinecap="round" />
      <circle ref={markerRef} cx={kneeX} cy={kneeY} r="7" fill="var(--accent-warning, #D97706)" stroke="#FFF" strokeWidth="2" style={{ transform: 'scale(0)', transformOrigin: `${kneeX}px ${kneeY}px` }} />
    </svg>
  );
}

export default KneeCurve;
