"use client";

import React, { useEffect, useState, useRef, useCallback } from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { GlassCard } from "../ui/GlassCard";
import { Badge } from "../ui/Badge";
import { AnimatedNumber } from "../ui/AnimatedNumber";
import { predictKneePoint } from "../../lib/api/client";
import { KneePredictionResponse } from "../../lib/api/types";
import { animate, createDrawable } from "animejs";
import { TrendingDown, AlertOctagon, CornerDownRight } from "lucide-react";

export const KneePrognosticsTab: React.FC = () => {
  const { telemetry, getSelectedVehicle } = useFleetStore();
  const vehicle = getSelectedVehicle();

  const [cycleInput, setCycleInput] = useState<number>(telemetry.cycleCount);
  const [capacityInput, setCapacityInput] = useState<number>(vehicle.soh);
  const [kneeData, setKneeData] = useState<KneePredictionResponse | null>(null);

  const curvePathRef = useRef<SVGPathElement>(null);
  const kneePointRef = useRef<SVGCircleElement>(null);

  const evaluateKnee = useCallback(async () => {
    try {
      const res = await predictKneePoint({
        charge_cycle_count: cycleInput,
        capacity: capacityInput,
        voltage: telemetry.voltage,
        battery_temp: telemetry.temperature,
        current: telemetry.current,
        soc: 75,
        speed: telemetry.avgSpeed,
      });
      setKneeData(res);
    } catch (e) {
      console.error("Knee prediction error:", e);
    }
  }, [cycleInput, capacityInput, telemetry]);

  useEffect(() => {
    evaluateKnee();
  }, [evaluateKnee]);

  // Signature Animation Moment #2: Knee curve draw-on with anime.js v4 createDrawable
  useEffect(() => {
    if (!curvePathRef.current) return;

    try {
      const drawable = createDrawable(curvePathRef.current);
      animate(drawable, {
        draw: ["0 0", "0 1"],
        duration: 1400,
        ease: "inOut(3)",
      });

      if (kneePointRef.current) {
        animate(kneePointRef.current, {
          scale: [0, 1.4, 1],
          opacity: [0, 1],
          duration: 600,
          delay: 1000,
          ease: "outElastic(1, .5)",
        });
      }
    } catch (e) {
      console.warn("Curve draw animation fallback:", e);
    }
  }, []);

  const isPostKnee = kneeData?.is_post_knee || false;
  const remainingKneeCycles = kneeData?.rul_to_knee_cycles || 720;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className={`app-card p-4 flex flex-wrap items-center justify-between gap-4 border ${
        isPostKnee
          ? "border-rose-300 dark:border-rose-800/60 bg-rose-50 dark:bg-rose-950/20"
          : remainingKneeCycles < 200
          ? "border-amber-300 dark:border-amber-800/60 bg-amber-50 dark:bg-amber-950/20"
          : "border-cyan-200 dark:border-cyan-800/60 bg-cyan-50 dark:bg-cyan-950/20"
      }`}>
        <div className="flex items-center gap-3">
          <div className={`w-9 h-9 rounded-xl border flex items-center justify-center ${
            isPostKnee
              ? "bg-rose-100 dark:bg-rose-900/40 border-rose-300 text-rose-600 dark:text-rose-400"
              : remainingKneeCycles < 200
              ? "bg-amber-100 dark:bg-amber-900/40 border-amber-300 text-amber-600 dark:text-amber-400"
              : "bg-cyan-100 dark:bg-cyan-900/40 border-cyan-300 text-cyan-600 dark:text-cyan-400"
          }`}>
            {isPostKnee ? <AlertOctagon className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
                Module C: Degradation Knee-Point Prognostics
              </h2>
              <Badge variant={isPostKnee ? "crimson" : remainingKneeCycles < 200 ? "amber" : "cyan"} size="sm" dot>
                {kneeData?.knee_risk_state || "EVALUATING"}
              </Badge>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              28-Feature XGBoost Booster & Piecewise Linear Joint MSE Optimizer
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="text-slate-500 dark:text-slate-400">Aging Slope:</span>
          <span className="text-slate-900 dark:text-slate-200 font-bold">{kneeData?.aging_rate_slope} %/cycle</span>
        </div>
      </div>

      {/* Main KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* RUL to Knee Countdown */}
        <GlassCard glow={isPostKnee ? "crimson" : remainingKneeCycles < 200 ? "amber" : "cyan"} className="text-center">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            <span>RUL to Degradation Knee</span>
            <TrendingDown className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
          </div>
          <div className="my-4">
            <div className="text-5xl font-extrabold font-mono tracking-tight">
              <AnimatedNumber
                value={remainingKneeCycles}
                decimals={0}
                className={isPostKnee ? "text-rose-600 dark:text-rose-400" : remainingKneeCycles < 200 ? "text-amber-600 dark:text-amber-400" : "text-cyan-600 dark:text-cyan-400"}
                suffix=" c"
              />
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-mono">Cycles remaining until rapid aging onset</div>
          </div>
          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-300">
            Status: <strong className={isPostKnee ? "text-rose-600 dark:text-rose-400" : "text-emerald-600 dark:text-emerald-400"}>{kneeData?.knee_risk_state}</strong>
          </div>
        </GlassCard>

        {/* Current Cycle Offset */}
        <GlassCard glow="purple" className="text-center">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            <span>Current Charge Cycle</span>
            <TrendingDown className="w-4 h-4 text-purple-600 dark:text-purple-400" />
          </div>
          <div className="my-4">
            <div className="text-5xl font-extrabold font-mono tracking-tight text-purple-600 dark:text-purple-400">
              <AnimatedNumber value={cycleInput} decimals={0} suffix=" EFC" />
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-mono">Estimated Knee Point at ~950 Cycles</div>
          </div>
          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-300">
            Capacity: <strong className="text-slate-900 dark:text-slate-100">{capacityInput.toFixed(1)}% SOH</strong>
          </div>
        </GlassCard>

        {/* Aging Rate Acceleration */}
        <GlassCard glow="amber" className="text-center">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            <span>Degradation Trajectory</span>
            <CornerDownRight className="w-4 h-4 text-amber-600 dark:text-amber-400" />
          </div>
          <div className="my-4">
            <div className="text-4xl font-extrabold font-mono tracking-tight text-amber-600 dark:text-amber-400">
              {isPostKnee ? "3.6x Accelerated" : "Linear Baseline"}
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-mono">
              {isPostKnee ? "SEI layer breakdown & Li plating" : "Predictable capacity fade"}
            </div>
          </div>
          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-300">
            Phase: <strong className="text-cyan-600 dark:text-cyan-400">{isPostKnee ? "Post-Knee Zone" : "Pre-Knee Safe Regime"}</strong>
          </div>
        </GlassCard>
      </div>

      {/* Signature Animated Knee Curve SVG Graph */}
      <GlassCard className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <TrendingDown className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
              Degradation Curve & Knee-Point Localization (SOH vs. Cycles)
            </h3>
          </div>
          <Badge variant="cyan" size="sm">anime.js v4 createDrawable</Badge>
        </div>

        {/* SVG Curve Container */}
        <div className="w-full h-72 relative bg-slate-50 dark:bg-slate-950/80 rounded-xl p-4 border border-slate-200 dark:border-slate-800 flex items-center justify-center">
          <svg viewBox="0 0 700 240" className="w-full h-full overflow-visible">
            <defs>
              <linearGradient id="curveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#0891B2" />
                <stop offset="65%" stopColor="#059669" />
                <stop offset="78%" stopColor="#D97706" />
                <stop offset="100%" stopColor="#DC2626" />
              </linearGradient>
            </defs>

            {/* Grid Lines */}
            <line x1="60" y1="20" x2="680" y2="20" stroke="#CBD5E1" strokeDasharray="4 4" className="dark:stroke-slate-800" />
            <line x1="60" y1="75" x2="680" y2="75" stroke="#CBD5E1" strokeDasharray="4 4" className="dark:stroke-slate-800" />
            <line x1="60" y1="130" x2="680" y2="130" stroke="#CBD5E1" strokeDasharray="4 4" className="dark:stroke-slate-800" />
            <line x1="60" y1="185" x2="680" y2="185" stroke="#CBD5E1" strokeDasharray="4 4" className="dark:stroke-slate-800" />

            {/* Axis Labels */}
            <text x="15" y="25" fill="#64748B" fontSize="11" fontFamily="monospace">100%</text>
            <text x="15" y="80" fill="#64748B" fontSize="11" fontFamily="monospace">90%</text>
            <text x="15" y="135" fill="#64748B" fontSize="11" fontFamily="monospace">80%</text>
            <text x="15" y="190" fill="#64748B" fontSize="11" fontFamily="monospace">70%</text>

            <text x="60" y="215" fill="#64748B" fontSize="11" fontFamily="monospace">0 c</text>
            <text x="240" y="215" fill="#64748B" fontSize="11" fontFamily="monospace">400 c</text>
            <text x="420" y="215" fill="#64748B" fontSize="11" fontFamily="monospace">800 c</text>
            <text x="520" y="215" fill="#059669" fontSize="11" fontFamily="monospace" fontWeight="bold">Knee (~950c)</text>
            <text x="640" y="215" fill="#64748B" fontSize="11" fontFamily="monospace">1400 c</text>

            {/* Degradation Curve (Draw-On with anime.js v4) */}
            <path
              id="knee-curve-path"
              ref={curvePathRef}
              d="M 60 25 Q 300 50 480 85 T 530 115 Q 580 160 670 200"
              fill="none"
              stroke="url(#curveGrad)"
              strokeWidth="4"
              strokeLinecap="round"
            />

            {/* Knee Point Marker */}
            <circle
              ref={kneePointRef}
              cx="530"
              cy="115"
              r="7"
              fill="#DC2626"
              stroke="#FFF"
              strokeWidth="2.5"
            />

            {/* Knee Point Callout Box */}
            <g transform="translate(450, 45)">
              <rect width="160" height="38" rx="8" className="fill-white dark:fill-slate-900 stroke-rose-500" strokeWidth="1.5" />
              <text x="80" y="17" className="fill-rose-600 dark:fill-rose-400" fontSize="11" fontWeight="bold" textAnchor="middle">
                Degradation Knee Point
              </text>
              <text x="80" y="30" fill="#64748B" fontSize="10" textAnchor="middle">
                Slope: -0.016 → -0.058
              </text>
            </g>
          </svg>
        </div>

        {/* Live Simulation Controls & Directive */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-700 dark:text-slate-300">Simulate Elapsed Cycles:</span>
              <span className="text-cyan-600 dark:text-cyan-400 font-bold">{cycleInput} EFC</span>
            </div>
            <input
              type="range"
              min="50"
              max="1350"
              step="25"
              value={cycleInput}
              onChange={(e) => setCycleInput(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-600"
            />
          </div>

          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300">
            <strong className="text-cyan-700 dark:text-cyan-400">BMS Directive:</strong> {kneeData?.bms_directive}
          </div>
        </div>
      </GlassCard>
    </div>
  );
};
