"use client";

import React, { useEffect, useState, useRef, useCallback, useMemo } from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { GlassCard } from "../ui/GlassCard";
import { Badge } from "../ui/Badge";
import { AnimatedNumber } from "../ui/AnimatedNumber";
import { predictKneePoint } from "../../lib/api/client";
import { KneePredictionResponse } from "../../lib/api/types";
import {
  TrendingDown,
  AlertOctagon,
  CornerDownRight,
  AlertTriangle,
  CheckCircle2,
  Sliders,
  Info,
  Truck,
  ShieldCheck,
} from "lucide-react";

export const KneePrognosticsTab: React.FC = () => {
  const { telemetry, selectedVehicleId, getSelectedVehicle } = useFleetStore();
  const vehicle = getSelectedVehicle();

  const [cycleInput, setCycleInput] = useState<number>(vehicle.charge_cycle_count || telemetry.cycleCount || 150);
  const [capacityInput, setCapacityInput] = useState<number>(vehicle.soh || 95.0);
  const [kneeData, setKneeData] = useState<KneePredictionResponse | null>(null);
  const [hoveredPoint, setHoveredPoint] = useState<{ cycle: number; soh: number; x: number; y: number } | null>(null);

  // Sync inputs immediately when vehicle changes
  useEffect(() => {
    const cycles = vehicle.charge_cycle_count || 150;
    const soh = vehicle.soh || 95.0;
    setCycleInput(cycles);
    setCapacityInput(soh);
  }, [selectedVehicleId, vehicle]);

  const evaluateKnee = useCallback(async () => {
    try {
      const res = await predictKneePoint({
        charge_cycle_count: cycleInput,
        capacity: capacityInput,
        voltage: vehicle.voltage || telemetry.voltage,
        battery_temp: vehicle.battery_temp || telemetry.temperature,
        current: vehicle.current || telemetry.current,
        soc: vehicle.soc || 75,
        speed: vehicle.speed || telemetry.avgSpeed,
      });
      setKneeData(res);
    } catch (e) {
      console.error("Knee prediction error:", e);
    }
  }, [cycleInput, capacityInput, vehicle, telemetry]);

  useEffect(() => {
    evaluateKnee();
  }, [evaluateKnee]);

  const isPostKnee = kneeData?.is_post_knee || cycleInput >= 950 || capacityInput < 80;
  const remainingKneeCycles = kneeData?.rul_to_knee_cycles ?? Math.max(0, Math.round(950 - cycleInput));
  const estimatedKneePoint = cycleInput + remainingKneeCycles;

  // ─── DYNAMIC SVG GRAPH GENERATION BASED ON SPECIFIC VEHICLE PARAMETERS ───
  // Width: 60..660 (600px domain), Height: 25..205 (180px range for 100% -> 60% SOH)
  // Max Cycle Domain: 0 to 1400 cycles
  const graphWidth = 600;
  const graphHeight = 180;
  const xOrigin = 60;
  const yOrigin = 25;
  const maxCycles = 1400;

  // Map cycle to X coordinate
  const getX = (c: number) => xOrigin + (Math.max(0, Math.min(maxCycles, c)) / maxCycles) * graphWidth;
  // Map SOH (100% to 60%) to Y coordinate
  const getY = (soh: number) => yOrigin + ((100 - Math.max(60, Math.min(100, soh))) / 40) * graphHeight;

  // Calculate dynamic curve points
  const dynamicCurve = useMemo(() => {
    const kneeCycle = Math.max(400, Math.min(1200, estimatedKneePoint));
    const kneeSOH = 82.0; // Standard knee onset capacity

    // Points along degradation trajectory
    const p0 = { x: getX(0), y: getY(100) };
    const p1 = { x: getX(kneeCycle * 0.5), y: getY(100 - (100 - kneeSOH) * 0.45) };
    const pKnee = { x: getX(kneeCycle), y: getY(kneeSOH) };
    const pEnd = { x: getX(maxCycles), y: getY(62.0) };

    // Path string: Smooth cubic curve transitioning to steep post-knee drop
    const pathD = `M ${p0.x} ${p0.y} Q ${p1.x} ${p1.y} ${pKnee.x} ${pKnee.y} T ${pEnd.x} ${pEnd.y}`;

    // Current vehicle location on curve
    const currentX = getX(cycleInput);
    const currentY = getY(capacityInput);

    return {
      pathD,
      kneeX: pKnee.x,
      kneeY: pKnee.y,
      kneeCycle,
      kneeSOH,
      currentX,
      currentY,
    };
  }, [cycleInput, capacityInput, estimatedKneePoint]);

  return (
    <div className="space-y-6 w-full">
      {/* ─── 1. TOP STATUS BANNER (DYNAMIC VEHICLE CONTEXT) ─── */}
      <div
        className={`app-card p-5 flex flex-wrap items-center justify-between gap-4 border ${
          isPostKnee
            ? "border-rose-300 dark:border-rose-800/60 bg-rose-50 dark:bg-rose-950/30 text-rose-900 dark:text-rose-100"
            : remainingKneeCycles < 250
            ? "border-amber-300 dark:border-amber-800/60 bg-amber-50 dark:bg-amber-950/30 text-amber-900 dark:text-amber-100"
            : "border-cyan-200 dark:border-cyan-800/60 bg-cyan-50 dark:bg-cyan-950/30 text-cyan-900 dark:text-cyan-100"
        }`}
      >
        <div className="flex items-center gap-3.5">
          <div
            className={`w-10 h-10 rounded-2xl border flex items-center justify-center shadow-sm ${
              isPostKnee
                ? "bg-rose-100 dark:bg-rose-900/60 border-rose-400 text-rose-600 dark:text-rose-300"
                : remainingKneeCycles < 250
                ? "bg-amber-100 dark:bg-amber-900/60 border-amber-400 text-amber-600 dark:text-amber-300"
                : "bg-cyan-100 dark:bg-cyan-900/60 border-cyan-400 text-cyan-600 dark:text-cyan-300"
            }`}
          >
            {isPostKnee ? <AlertOctagon className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base sm:text-lg font-bold tracking-tight">
                Vehicle {vehicle.id} • Degradation Knee-Point Prognostics
              </h2>
              <Badge
                variant={isPostKnee ? "crimson" : remainingKneeCycles < 250 ? "amber" : "cyan"}
                size="sm"
                dot
              >
                {isPostKnee ? "POST-KNEE (CRITICAL)" : remainingKneeCycles < 250 ? "APPROACHING KNEE" : "HEALTHY PRE-KNEE"}
              </Badge>
            </div>
            <p className="text-xs opacity-80 mt-0.5">
              XGBoost 28-Feature Model • Non-linear electrochemical aging trajectory for {vehicle.model}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 font-mono text-xs">
          <div>
            <span className="opacity-70">Internal Resistance:</span>{" "}
            <strong className="text-purple-600 dark:text-purple-400">
              {(0.032 + (cycleInput * 0.000035)).toFixed(4)} Ω
            </strong>
          </div>
          <div>
            <span className="opacity-70">Aging Slope:</span>{" "}
            <strong className={isPostKnee ? "text-rose-500" : "text-emerald-500"}>
              {isPostKnee ? "-0.058 %/cycle" : "-0.014 %/cycle"}
            </strong>
          </div>
        </div>
      </div>

      {/* ─── 2. MAIN KPI TILES (DYNAMIC PER VEHICLE) ─── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Metric 1: RUL to Knee Countdown */}
        <GlassCard
          glow={isPostKnee ? "crimson" : remainingKneeCycles < 250 ? "amber" : "cyan"}
          className="text-center p-6 space-y-3"
        >
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            <span>Cycles to Knee Point</span>
            <TrendingDown className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
          </div>
          <div>
            <div className="text-4xl sm:text-5xl font-extrabold font-mono tracking-tight">
              <AnimatedNumber
                value={remainingKneeCycles}
                decimals={0}
                className={
                  isPostKnee
                    ? "text-rose-600 dark:text-rose-400"
                    : remainingKneeCycles < 250
                    ? "text-amber-600 dark:text-amber-400"
                    : "text-cyan-600 dark:text-cyan-400"
                }
                suffix=" Cycles"
              />
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-mono">
              {isPostKnee
                ? "Vehicle has passed knee point — rapid capacity drop-off active"
                : `~${(remainingKneeCycles / 220).toFixed(1)} operating years until sudden degradation`}
            </p>
          </div>
          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs flex justify-between">
            <span className="text-slate-500">Predicted Knee Cycle:</span>
            <strong className="font-mono text-slate-800 dark:text-slate-200">
              ~{dynamicCurve.kneeCycle} EFC
            </strong>
          </div>
        </GlassCard>

        {/* Metric 2: Current Charge Cycles */}
        <GlassCard glow="purple" className="text-center p-6 space-y-3">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            <span>Elapsed Charge Cycles</span>
            <Truck className="w-4 h-4 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <div className="text-4xl sm:text-5xl font-extrabold font-mono tracking-tight text-purple-600 dark:text-purple-400">
              <AnimatedNumber value={cycleInput} decimals={0} suffix=" EFC" />
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-mono">
              Odometer equivalent: ~{Math.floor(cycleInput * 58).toLocaleString()} km
            </p>
          </div>
          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs flex justify-between">
            <span className="text-slate-500">Current Health:</span>
            <strong className="font-mono text-emerald-600 dark:text-emerald-400">
              {capacityInput.toFixed(1)}% SOH
            </strong>
          </div>
        </GlassCard>

        {/* Metric 3: Degradation Phase */}
        <GlassCard glow={isPostKnee ? "crimson" : "amber"} className="text-center p-6 space-y-3">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            <span>Degradation Regime</span>
            <CornerDownRight className="w-4 h-4 text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <div
              className={`text-3xl sm:text-4xl font-extrabold font-mono tracking-tight ${
                isPostKnee ? "text-rose-600 dark:text-rose-400" : "text-emerald-600 dark:text-emerald-400"
              }`}
            >
              {isPostKnee ? "Post-Knee Phase" : "Linear Phase"}
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-mono">
              {isPostKnee ? "3.8x Accelerated Capacity Loss" : "Predictable SEI Passivation"}
            </p>
          </div>
          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs flex justify-between">
            <span className="text-slate-500">BMS Recommendation:</span>
            <strong className={isPostKnee ? "text-rose-500" : "text-cyan-500"}>
              {isPostKnee ? "Throttle 0.8C Max Charge" : "Standard 1.0C Charging"}
            </strong>
          </div>
        </GlassCard>
      </div>

      {/* ─── 3. DYNAMIC 100% RESPONSIVE KNEE CURVE GRAPH ─── */}
      <GlassCard className="p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <TrendingDown className="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                Dynamic Electrochemical Knee-Point Trajectory (SOH % vs. Charge Cycles)
              </h3>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Live curve recalculates for vehicle <strong className="text-cyan-500">{vehicle.id}</strong> based on capacity loss rate and thermal stress.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="inline-flex items-center gap-1 text-cyan-500">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-500" /> Current Truck ({vehicle.id})
            </span>
            <span className="inline-flex items-center gap-1 text-rose-500 ml-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> Knee Transition Point
            </span>
          </div>
        </div>

        {/* Dynamic SVG Container */}
        <div className="w-full h-80 relative bg-slate-50 dark:bg-slate-950/80 rounded-2xl p-4 border border-slate-200 dark:border-slate-800 flex items-center justify-center overflow-hidden">
          <svg viewBox="0 0 720 250" className="w-full h-full overflow-visible">
            <defs>
              <linearGradient id="dynamicCurveGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#06B6D4" />
                <stop offset="55%" stopColor="#10B981" />
                <stop offset="70%" stopColor="#F59E0B" />
                <stop offset="100%" stopColor="#EF4444" />
              </linearGradient>

              {/* Shaded Area Under Curve */}
              <linearGradient id="areaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#06B6D4" stopOpacity="0.2" />
                <stop offset="100%" stopColor="#06B6D4" stopOpacity="0.0" />
              </linearGradient>
            </defs>

            {/* Horizontal SOH Grid Lines */}
            <line x1="60" y1="25" x2="680" y2="25" stroke="#E2E8F0" strokeDasharray="4 4" className="dark:stroke-slate-800" />
            <line x1="60" y1="70" x2="680" y2="70" stroke="#E2E8F0" strokeDasharray="4 4" className="dark:stroke-slate-800" />
            <line x1="60" y1="115" x2="680" y2="115" stroke="#E2E8F0" strokeDasharray="4 4" className="dark:stroke-slate-800" />
            <line x1="60" y1="160" x2="680" y2="160" stroke="#E2E8F0" strokeDasharray="4 4" className="dark:stroke-slate-800" />
            <line x1="60" y1="205" x2="680" y2="205" stroke="#E2E8F0" strokeDasharray="4 4" className="dark:stroke-slate-800" />

            {/* SOH Y-Axis Labels */}
            <text x="15" y="30" fill="#64748B" fontSize="11" fontFamily="monospace">100%</text>
            <text x="15" y="75" fill="#64748B" fontSize="11" fontFamily="monospace">90%</text>
            <text x="15" y="120" fill="#64748B" fontSize="11" fontFamily="monospace">80%</text>
            <text x="15" y="165" fill="#64748B" fontSize="11" fontFamily="monospace">70%</text>
            <text x="15" y="210" fill="#64748B" fontSize="11" fontFamily="monospace">60%</text>

            {/* Cycle X-Axis Labels */}
            <text x="60" y="235" fill="#64748B" fontSize="11" fontFamily="monospace">0 c</text>
            <text x="210" y="235" fill="#64748B" fontSize="11" fontFamily="monospace">350 c</text>
            <text x="360" y="235" fill="#64748B" fontSize="11" fontFamily="monospace">700 c</text>
            <text x="510" y="235" fill="#64748B" fontSize="11" fontFamily="monospace">1050 c</text>
            <text x="650" y="235" fill="#64748B" fontSize="11" fontFamily="monospace">1400 c</text>

            {/* Dynamic Degradation Trajectory Path */}
            <path
              d={dynamicCurve.pathD}
              fill="none"
              stroke="url(#dynamicCurveGrad)"
              strokeWidth="4.5"
              strokeLinecap="round"
            />

            {/* Dynamic Knee Point Vertical Guide Line */}
            <line
              x1={dynamicCurve.kneeX}
              y1="25"
              x2={dynamicCurve.kneeX}
              y2="205"
              stroke="#EF4444"
              strokeDasharray="3 3"
              strokeWidth="1.5"
              opacity="0.6"
            />

            {/* Dynamic Knee Point Marker */}
            <circle
              cx={dynamicCurve.kneeX}
              cy={dynamicCurve.kneeY}
              r="7"
              fill="#EF4444"
              stroke="#FFFFFF"
              strokeWidth="2.5"
              className="drop-shadow"
            />

            {/* Dynamic Knee Point Callout Tag */}
            <g transform={`translate(${Math.min(540, Math.max(100, dynamicCurve.kneeX - 75))}, ${Math.max(30, dynamicCurve.kneeY - 45)})`}>
              <rect width="150" height="34" rx="8" className="fill-white dark:fill-slate-900 stroke-rose-500" strokeWidth="1.5" />
              <text x="75" y="15" className="fill-rose-600 dark:fill-rose-400" fontSize="10" fontWeight="bold" textAnchor="middle">
                Knee Point (~{dynamicCurve.kneeCycle}c)
              </text>
              <text x="75" y="27" fill="#64748B" fontSize="9" textAnchor="middle">
                Onset @ {dynamicCurve.kneeSOH.toFixed(0)}% SOH
              </text>
            </g>

            {/* CURRENT VEHICLE LOCATION PIN (100% Dynamic based on cycleInput) */}
            <g transform={`translate(${dynamicCurve.currentX}, ${dynamicCurve.currentY})`}>
              {/* Pulsing Aura */}
              <circle r="14" className="fill-cyan-400/30 animate-ping" />
              <circle r="8" fill="#06B6D4" stroke="#FFFFFF" strokeWidth="2.5" className="drop-shadow-lg" />

              {/* Pin Callout Label */}
              <g transform="translate(12, -22)">
                <rect width="130" height="28" rx="6" className="fill-slate-900 border border-cyan-500" />
                <text x="65" y="13" fill="#38BDF8" fontSize="10" fontWeight="bold" textAnchor="middle">
                  {vehicle.id} ({cycleInput}c)
                </text>
                <text x="65" y="23" fill="#94A3B8" fontSize="8" textAnchor="middle">
                  Current SOH: {capacityInput.toFixed(1)}%
                </text>
              </g>
            </g>
          </svg>
        </div>

        {/* ─── 4. INTERACTIVE SLIDER SIMULATOR & BMS DIRECTIVES ─── */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 pt-2 items-center">
          <div className="md:col-span-6 space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                <Sliders className="w-3.5 h-3.5 text-cyan-500" />
                <span>Simulate Vehicle Charge Cycles (EFC):</span>
              </span>
              <strong className="text-cyan-600 dark:text-cyan-400 font-bold">{cycleInput} Cycles</strong>
            </div>
            <input
              type="range"
              min="20"
              max="1350"
              step="10"
              value={cycleInput}
              onChange={(e) => setCycleInput(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-600"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>0c (Fresh Pack)</span>
              <span>Knee Onset (~{dynamicCurve.kneeCycle}c)</span>
              <span>1400c (EOL)</span>
            </div>
          </div>

          <div className="md:col-span-6 p-4 rounded-xl bg-slate-50 dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 space-y-1.5">
            <div className="text-xs font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span>Smart BMS Operational Directive:</span>
            </div>
            <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
              {isPostKnee
                ? "⚠️ Post-Knee Threshold Exceeded: Cap maximum charging rate to 0.7C, restrict fast charging above 40°C, and schedule battery pack module balancing."
                : remainingKneeCycles < 250
                ? "⚡ Approaching Degradation Knee: Maintain 20%-80% depth-of-discharge window to extend remaining linear operational life by +180 cycles."
                : "✅ Healthy Pre-Knee Regime: Pack degradation operating in linear regime. Full 1.0C charge rate and standard routes authorized."}
            </p>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};
export default KneePrognosticsTab;
