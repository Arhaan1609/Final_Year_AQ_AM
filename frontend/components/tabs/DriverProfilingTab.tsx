"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { GlassCard } from "../ui/GlassCard";
import { Badge } from "../ui/Badge";
import { AnimatedNumber } from "../ui/AnimatedNumber";
import { predictDriverBehavior } from "../../lib/api/client";
import { DriverBehaviorResponse } from "../../lib/api/types";
import { Gauge, Zap, TrendingDown, UserCheck } from "lucide-react";

export const DriverProfilingTab: React.FC = () => {
  const { telemetry, selectedVehicleId, getSelectedVehicle } = useFleetStore();
  const vehicle = getSelectedVehicle();

  const [harshAccel, setHarshAccel] = useState<number>(telemetry.harshAccel || 2);
  const [harshBrake, setHarshBrake] = useState<number>(telemetry.harshBrake || 1);
  const [harshCorner, setHarshCorner] = useState<number>(telemetry.harshCorner || 1);
  const [speedVariance, setSpeedVariance] = useState<number>(7.8);
  const [maxDischarge, setMaxDischarge] = useState<number>(36.0);

  // Sync driver inputs immediately when vehicle changes
  useEffect(() => {
    const isWarn = vehicle.status === "warning";
    const isCrit = vehicle.status === "critical";
    setHarshAccel(isCrit ? 8 : isWarn ? 5 : 1);
    setHarshBrake(isCrit ? 6 : isWarn ? 3 : 1);
    setHarshCorner(isCrit ? 3 : isWarn ? 2 : 1);
    setSpeedVariance(isCrit ? 22.5 : isWarn ? 14.0 : 6.5);
    setMaxDischarge(isCrit ? 65.0 : isWarn ? 45.0 : 25.0);
  }, [selectedVehicleId, vehicle]);

  const [behaviorData, setBehaviorData] = useState<DriverBehaviorResponse | any | null>(null);

  const evaluateBehavior = useCallback(async () => {
    try {
      const res = await predictDriverBehavior({
        harsh_accel_count: harshAccel,
        harsh_brake_count: harshBrake,
        harsh_corner_count: harshCorner,
        speed_variance: speedVariance,
        avg_speed: telemetry.avgSpeed || 34,
        max_speed: telemetry.maxSpeed || 58,
        battery_temp_max: (telemetry.temperature || 32) + 4,
        max_discharge_current: maxDischarge,
      });
      setBehaviorData(res);
    } catch (e) {
      console.error("Driver behavior error:", e);
    }
  }, [harshAccel, harshBrake, harshCorner, speedVariance, telemetry, maxDischarge]);

  useEffect(() => {
    const timer = setTimeout(() => {
      evaluateBehavior();
    }, 150);
    return () => clearTimeout(timer);
  }, [evaluateBehavior]);

  const ai = behaviorData?.aggressiveness_index ?? 0.25;
  const bsi = behaviorData?.battery_stress_index ?? 0.32;
  const isAggressive = ai > 0.65;
  const isModerate = ai > 0.35 && ai <= 0.65;

  const annualPenalty =
    behaviorData?.estimated_annual_soh_penalty_pct ??
    behaviorData?.annual_soh_penalty_percent ??
    1.2;

  // Extract recommendations safely from array or backend string fields
  const recommendationList: string[] = Array.isArray(behaviorData?.recommendations)
    ? behaviorData.recommendations
    : [
        behaviorData?.bms_recommended_directive,
        behaviorData?.behavioral_impact_description,
      ].filter(Boolean) as string[];

  const finalRecommendations =
    recommendationList.length > 0
      ? recommendationList
      : [
          "Smooth throttle tip-in maintains nominal C-rate bounds (+4.7% SOH retention).",
          "Regenerative braking efficiency operating within target recovery envelope.",
          "Thermal strain within baseline passive cooling dissipation limits.",
        ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="app-card p-4 flex flex-wrap items-center justify-between gap-4 border border-purple-200 dark:border-purple-800/60 bg-purple-50 dark:bg-purple-950/20">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-purple-100 dark:bg-purple-900/40 border border-purple-300 text-purple-700 dark:text-purple-400 flex items-center justify-center">
            <Gauge className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
                Module C: Behavior-Aware BMS (BA-BMS) Profiling
              </h2>
              <Badge variant={isAggressive ? "crimson" : isModerate ? "amber" : "emerald"} size="sm" dot>
                {behaviorData?.driver_classification || "PROFILING"}
              </Badge>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Quantifying electrochemical degradation impact from driver throttle dynamics on {selectedVehicleId}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="text-slate-500 dark:text-slate-400">Assigned Driver:</span>
          <span className="text-slate-900 dark:text-slate-100 font-bold">{vehicle.driver}</span>
        </div>
      </div>

      {/* Primary Indices Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Aggressiveness Index Card */}
        <GlassCard glow={isAggressive ? "crimson" : isModerate ? "amber" : "cyan"} className="text-center">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            <span>Driver Aggressiveness Index (AI)</span>
            <Gauge className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
          </div>
          <div className="my-4">
            <div className="text-5xl font-extrabold font-mono tracking-tight">
              <AnimatedNumber
                value={ai}
                decimals={3}
                className={isAggressive ? "text-rose-600 dark:text-rose-400" : isModerate ? "text-amber-600 dark:text-amber-400" : "text-cyan-600 dark:text-cyan-400"}
              />
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-mono">Scale: 0.0 (Calm) → 1.0 (Extreme)</div>
          </div>
          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-300">
            Cohort: <strong className={isAggressive ? "text-rose-600 dark:text-rose-400" : isModerate ? "text-amber-600 dark:text-amber-400" : "text-emerald-600 dark:text-emerald-400"}>
              {behaviorData?.driver_classification || "Smooth & Energy-Conscious"}
            </strong>
          </div>
        </GlassCard>

        {/* Battery Stress Index Card */}
        <GlassCard glow={bsi > 0.6 ? "crimson" : bsi > 0.4 ? "amber" : "purple"} className="text-center">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            <span>Battery Stress Index (BSI)</span>
            <Zap className="w-4 h-4 text-purple-600 dark:text-purple-400" />
          </div>
          <div className="my-4">
            <div className="text-5xl font-extrabold font-mono tracking-tight">
              <AnimatedNumber
                value={bsi}
                decimals={3}
                className={bsi > 0.6 ? "text-rose-600 dark:text-rose-400" : bsi > 0.4 ? "text-amber-600 dark:text-amber-400" : "text-purple-600 dark:text-purple-400"}
              />
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-mono">Electrochemical Strain (C-rate + Temp)</div>
          </div>
          <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-300">
            Peak Current Draw: <strong className="text-amber-600 dark:text-amber-400">{maxDischarge} A</strong>
          </div>
        </GlassCard>

        {/* Projected Annual SOH Penalty */}
        <GlassCard glow="amber" className="text-center flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            <span>Annual SOH Penalty</span>
            <TrendingDown className="w-4 h-4 text-amber-600 dark:text-amber-400" />
          </div>
          <div className="my-3">
            <div className="text-4xl font-extrabold font-mono tracking-tight text-amber-600 dark:text-amber-400">
              -<AnimatedNumber value={annualPenalty} decimals={1} suffix="%" />
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-mono">Excess degradation per 25,000 km</div>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-100 dark:border-slate-800 pt-2">
            Aggressive tip-in elevates calendar fade rate
          </p>
        </GlassCard>
      </div>

      {/* Behavioral Controls & Policy Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sliders */}
        <GlassCard className="space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 border-b border-slate-100 dark:border-slate-800 pb-2">
            Simulate Driving Pattern Telemetry
          </h3>

          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-slate-500 dark:text-slate-400">Harsh Acceleration Events / Trip</span>
                <span className="text-cyan-600 dark:text-cyan-400 font-bold">{harshAccel}</span>
              </div>
              <input
                type="range"
                min="0"
                max="12"
                value={harshAccel}
                onChange={(e) => setHarshAccel(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-600"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-slate-500 dark:text-slate-400">Harsh Braking Events / Trip</span>
                <span className="text-amber-600 dark:text-amber-400 font-bold">{harshBrake}</span>
              </div>
              <input
                type="range"
                min="0"
                max="12"
                value={harshBrake}
                onChange={(e) => setHarshBrake(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-600"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-slate-500 dark:text-slate-400">Harsh Cornering Events / Trip</span>
                <span className="text-purple-600 dark:text-purple-400 font-bold">{harshCorner}</span>
              </div>
              <input
                type="range"
                min="0"
                max="12"
                value={harshCorner}
                onChange={(e) => setHarshCorner(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-600"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-slate-500 dark:text-slate-400">Speed Variance (σ)</span>
                <span className="text-purple-600 dark:text-purple-400 font-bold">{speedVariance.toFixed(1)} km/h</span>
              </div>
              <input
                type="range"
                min="2"
                max="20"
                step="0.5"
                value={speedVariance}
                onChange={(e) => setSpeedVariance(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-600"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1">
                <span className="text-slate-500 dark:text-slate-400">Peak Discharge Current (A)</span>
                <span className="text-rose-600 dark:text-rose-400 font-bold">{maxDischarge.toFixed(0)} A</span>
              </div>
              <input
                type="range"
                min="15"
                max="65"
                step="1"
                value={maxDischarge}
                onChange={(e) => setMaxDischarge(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-rose-600"
              />
            </div>
          </div>
        </GlassCard>

        {/* AI Recommendations */}
        <GlassCard className="space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 border-b border-slate-100 dark:border-slate-800 pb-2 flex items-center gap-2">
              <UserCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              BMS Driver Guidance Directives
            </h3>
            <div className="mt-3 space-y-2.5">
              {finalRecommendations.map((rec, i) => (
                <div key={i} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300 flex items-start gap-2">
                  <span className="text-emerald-600 dark:text-emerald-400 font-bold">•</span>
                  <span>{rec}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 pt-3 border-t border-slate-100 dark:border-slate-800">
            Formulation: <code className="text-xs text-slate-800 dark:text-slate-200 font-mono">AI = 0.25·Accel + 0.20·Brake + 0.15·σ + 0.15·v²</code>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
