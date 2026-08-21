"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { GlassCard } from "../ui/GlassCard";
import { Badge } from "../ui/Badge";
import { ElasticGauge } from "../ui/ElasticGauge";
import { predictSOC, predictSOH, predictRUL, predictMileage } from "../../lib/api/client";
import { ModelPredictionResponse } from "../../lib/api/types";
import { Sliders, Cpu } from "lucide-react";

export const StateEstimationTab: React.FC = () => {
  const { telemetry, updateTelemetry, selectedVehicleId } = useFleetStore();

  const [socRes, setSocRes] = useState<ModelPredictionResponse | null>(null);
  const [sohRes, setSohRes] = useState<ModelPredictionResponse | null>(null);
  const [rulRes, setRulRes] = useState<ModelPredictionResponse | null>(null);
  const [mileageRes, setMileageRes] = useState<ModelPredictionResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  // Debounced API fetch across all 4 Module A endpoints
  const fetchModuleAPredictions = useCallback(async () => {
    setLoading(true);
    try {
      const [soc, soh, rul, mileage] = await Promise.all([
        predictSOC({
          battery_voltage: telemetry.voltage,
          battery_temp: telemetry.temperature,
          battery_current: telemetry.current,
          abs_current: Math.abs(telemetry.current),
          odometer: telemetry.odometer,
        }),
        predictSOH({
          battery_voltage: telemetry.voltage,
          battery_temp: telemetry.temperature,
          battery_current: telemetry.current,
          odometer: telemetry.odometer,
          charge_cycle_count: telemetry.cycleCount,
        }),
        predictRUL({
          odometer: telemetry.odometer,
          soc_at_charge: 85,
        }),
        predictMileage({
          run_kms: 45,
          avg_speed: telemetry.avgSpeed,
          max_speed: telemetry.maxSpeed,
        }),
      ]);

      setSocRes(soc);
      setSohRes(soh);
      setRulRes(rul);
      setMileageRes(mileage);
    } catch (e) {
      console.error("Module A predictions error:", e);
    } finally {
      setLoading(false);
    }
  }, [telemetry]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchModuleAPredictions();
    }, 200);
    return () => clearTimeout(timer);
  }, [fetchModuleAPredictions]);

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="app-card p-4 flex flex-wrap items-center justify-between gap-4 border border-cyan-200 dark:border-cyan-800/60 bg-cyan-50 dark:bg-cyan-950/20">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-cyan-100 dark:bg-cyan-900/40 border border-cyan-300 text-cyan-700 dark:text-cyan-400 flex items-center justify-center">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              Module A: Macro Fleet State Estimation
              <Badge variant="cyan" size="sm">56 ML/DL Models</Badge>
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Live parameter inference using scikit-learn & XGBoost champion models on {selectedVehicleId}
            </p>
          </div>
        </div>
        {loading && (
          <span className="text-xs font-mono text-cyan-600 dark:text-cyan-400 flex items-center gap-1.5 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-cyan-500" /> Computing Inference...
          </span>
        )}
      </div>

      {/* 4 Elastic Gauges */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* SOC */}
        <GlassCard glow="cyan" className="flex flex-col items-center justify-between text-center">
          <div className="w-full flex items-center justify-between">
            <Badge variant="cyan" size="sm">SOC Estimation</Badge>
            <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400">KNN R²=0.9958</span>
          </div>
          <div className="my-2">
            <ElasticGauge
              value={socRes ? socRes.prediction : 80}
              min={0}
              max={100}
              label="State of Charge"
              unit="%"
              color="#0891B2"
            />
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-100 dark:border-slate-800 w-full pt-2">
            Model: <strong className="text-slate-800 dark:text-slate-200">K-Nearest Neighbors</strong>
          </div>
        </GlassCard>

        {/* SOH */}
        <GlassCard glow="emerald" className="flex flex-col items-center justify-between text-center">
          <div className="w-full flex items-center justify-between">
            <Badge variant="emerald" size="sm">SOH Tabular</Badge>
            <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400">XGBoost R²=0.9672</span>
          </div>
          <div className="my-2">
            <ElasticGauge
              value={sohRes ? sohRes.prediction : 94}
              min={60}
              max={100}
              label="State of Health"
              unit="%"
              color="#059669"
            />
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-100 dark:border-slate-800 w-full pt-2">
            Model: <strong className="text-slate-800 dark:text-slate-200">XGBoost Regressor</strong>
          </div>
        </GlassCard>

        {/* RUL */}
        <GlassCard glow="purple" className="flex flex-col items-center justify-between text-center">
          <div className="w-full flex items-center justify-between">
            <Badge variant="purple" size="sm">RUL Cycles</Badge>
            <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400">GB R²=0.9997</span>
          </div>
          <div className="my-2">
            <ElasticGauge
              value={rulRes ? rulRes.prediction : 1200}
              min={0}
              max={1800}
              label="Remaining Life"
              unit="cycles"
              color="#7C3AED"
            />
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-100 dark:border-slate-800 w-full pt-2">
            Model: <strong className="text-slate-800 dark:text-slate-200">Gradient Boosting</strong>
          </div>
        </GlassCard>

        {/* Mileage */}
        <GlassCard glow="amber" className="flex flex-col items-center justify-between text-center">
          <div className="w-full flex items-center justify-between">
            <Badge variant="amber" size="sm">Mileage Range</Badge>
            <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400">XGBoost R²=0.9445</span>
          </div>
          <div className="my-2">
            <ElasticGauge
              value={mileageRes ? mileageRes.prediction : 105}
              min={20}
              max={140}
              label="Range Per Charge"
              unit="km"
              color="#D97706"
            />
          </div>
          <div className="text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-100 dark:border-slate-800 w-full pt-2">
            Model: <strong className="text-slate-800 dark:text-slate-200">XGBoost Regressor</strong>
          </div>
        </GlassCard>
      </div>

      {/* Live Input Sliders Control Board */}
      <GlassCard className="space-y-5">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">Live Telemetry Control & Stress Sliders</h3>
          </div>
          <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
            Drag sliders to test models in real-time
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Voltage */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-700 dark:text-slate-300">Pack Voltage (V)</span>
              <span className="text-cyan-600 dark:text-cyan-400 font-bold">{telemetry.voltage.toFixed(1)} V</span>
            </div>
            <input
              type="range"
              min="62"
              max="84"
              step="0.2"
              value={telemetry.voltage}
              onChange={(e) => updateTelemetry({ voltage: parseFloat(e.target.value) })}
              className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-600"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>62V (Depleted)</span>
              <span>84V (Full)</span>
            </div>
          </div>

          {/* Current */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-700 dark:text-slate-300">Current (A)</span>
              <span className="text-amber-600 dark:text-amber-400 font-bold">{telemetry.current.toFixed(1)} A</span>
            </div>
            <input
              type="range"
              min="-60"
              max="30"
              step="0.5"
              value={telemetry.current}
              onChange={(e) => updateTelemetry({ current: parseFloat(e.target.value) })}
              className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-600"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>-60A (Discharge)</span>
              <span>+30A (Charging)</span>
            </div>
          </div>

          {/* Temperature */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-700 dark:text-slate-300">Pack Temp (°C)</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">{telemetry.temperature.toFixed(1)} °C</span>
            </div>
            <input
              type="range"
              min="15"
              max="58"
              step="0.5"
              value={telemetry.temperature}
              onChange={(e) => updateTelemetry({ temperature: parseFloat(e.target.value) })}
              className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-600"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>15°C (Cool)</span>
              <span>58°C (Thermal Stress)</span>
            </div>
          </div>

          {/* Odometer */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-700 dark:text-slate-300">Odometer (km)</span>
              <span className="text-purple-600 dark:text-purple-400 font-bold">{telemetry.odometer.toLocaleString()} km</span>
            </div>
            <input
              type="range"
              min="500"
              max="45000"
              step="500"
              value={telemetry.odometer}
              onChange={(e) => updateTelemetry({ odometer: parseInt(e.target.value) })}
              className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-600"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>0 km</span>
              <span>45,000 km</span>
            </div>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};
