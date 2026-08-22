"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { predictSOC, predictSOH, predictRUL, predictMileage } from "../../lib/api/client";
import { ModelPredictionResponse } from "../../lib/api/types";
import { RefreshCw, Zap, Cpu, Activity, ShieldCheck, Flame, Gauge } from "lucide-react";

export const StateEstimationTab: React.FC = () => {
  const { telemetry, updateTelemetry, selectedVehicleId, getSelectedVehicle } = useFleetStore();
  const vehicle = getSelectedVehicle();

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
          soc_at_charge: vehicle.soc || 85,
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
  }, [telemetry, vehicle.soc]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchModuleAPredictions();
    }, 200);
    return () => clearTimeout(timer);
  }, [fetchModuleAPredictions]);

  const resetTelemetry = () => {
    updateTelemetry({
      voltage: vehicle.voltage || 75.8,
      current: vehicle.current || -18.4,
      temperature: vehicle.battery_temp || 33.2,
      odometer: vehicle.charge_cycle_count * 58 || 12500,
      cycleCount: vehicle.charge_cycle_count || 150,
      avgSpeed: vehicle.speed || 30.0,
      maxSpeed: (vehicle.speed || 30.0) + 25,
    });
  };

  // Synchronize telemetry sliders immediately when vehicle selection changes
  useEffect(() => {
    resetTelemetry();
  }, [selectedVehicleId]);

  const socVal = socRes?.prediction ?? vehicle.soc ?? 64.8;
  const sohVal = sohRes?.prediction ?? vehicle.soh ?? 91.2;
  const rulVal = rulRes?.prediction ? Math.round(rulRes.prediction) : vehicle.rul ?? 1240;
  const mileageVal = mileageRes?.prediction ? Math.round(mileageRes.prediction * 10) / 10 : vehicle.mileage ?? 119.5;

  // Arc calculation for SOC circular meter
  const circumference = 2 * Math.PI * 40; // 251.3
  const strokeDash = (Math.max(0, Math.min(100, socVal)) / 100) * 188.5;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full relative">
      
      {/* ─── LEFT COLUMN: SIMULATE CONTEXT & ACTIVE ENSEMBLE (Stitch Aside) ─── */}
      <aside className="col-span-1 lg:col-span-4 xl:col-span-3 flex flex-col gap-6">
        
        {/* Simulate Context Card */}
        <div className="app-card p-6 shadow-md relative overflow-hidden group">
          <div className="flex justify-between items-end mb-6 relative z-10">
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-2">
                <Zap className="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
                Simulate Context
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Adjust live vehicle state inputs</p>
            </div>
            <button
              onClick={resetTelemetry}
              title="Reset to vehicle live telemetry"
              className="p-2 rounded-xl bg-cyan-50 dark:bg-cyan-950/60 border border-cyan-200 dark:border-cyan-800 text-cyan-700 dark:text-cyan-400 hover:bg-cyan-100 dark:hover:bg-cyan-900/60 transition-all shadow-sm active:scale-95"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          {/* Sliders Stack */}
          <div className="space-y-6 relative z-10">
            {/* Voltage */}
            <div className="space-y-2">
              <div className="flex justify-between items-baseline text-xs font-semibold">
                <label className="text-slate-600 dark:text-slate-400 uppercase tracking-wider font-mono">Pack Voltage (V)</label>
                <span className="text-sm font-bold text-cyan-600 dark:text-cyan-400 font-mono">{telemetry.voltage.toFixed(1)} V</span>
              </div>
              <input
                type="range"
                min="60"
                max="84"
                step="0.1"
                value={telemetry.voltage}
                onChange={(e) => updateTelemetry({ voltage: parseFloat(e.target.value) })}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full appearance-none outline-none accent-cyan-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 dark:text-slate-400 font-mono">
                <span>60V (Depleted)</span>
                <span>84V (Full)</span>
              </div>
            </div>

            {/* Current */}
            <div className="space-y-2">
              <div className="flex justify-between items-baseline text-xs font-semibold">
                <label className="text-slate-600 dark:text-slate-400 uppercase tracking-wider font-mono">Pack Current (A)</label>
                <span className="text-sm font-bold text-amber-600 dark:text-amber-400 font-mono">{telemetry.current.toFixed(1)} A</span>
              </div>
              <input
                type="range"
                min="-60"
                max="60"
                step="1"
                value={telemetry.current}
                onChange={(e) => updateTelemetry({ current: parseFloat(e.target.value) })}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full appearance-none outline-none accent-amber-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 dark:text-slate-400 font-mono">
                <span>-60A (Discharge)</span>
                <span>+60A (Charging)</span>
              </div>
            </div>

            {/* Avg Temp */}
            <div className="space-y-2">
              <div className="flex justify-between items-baseline text-xs font-semibold">
                <label className="text-slate-600 dark:text-slate-400 uppercase tracking-wider font-mono">Avg Temp (°C)</label>
                <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400 font-mono">{telemetry.temperature.toFixed(1)} °C</span>
              </div>
              <input
                type="range"
                min="10"
                max="65"
                step="0.5"
                value={telemetry.temperature}
                onChange={(e) => updateTelemetry({ temperature: parseFloat(e.target.value) })}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full appearance-none outline-none accent-emerald-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 dark:text-slate-400 font-mono">
                <span>10°C (Cold)</span>
                <span>65°C (Thermal Stress)</span>
              </div>
            </div>

            {/* Odometer */}
            <div className="space-y-2">
              <div className="flex justify-between items-baseline text-xs font-semibold">
                <label className="text-slate-600 dark:text-slate-400 uppercase tracking-wider font-mono">Odometer (km)</label>
                <span className="text-sm font-bold text-purple-600 dark:text-purple-400 font-mono">{Math.round(telemetry.odometer).toLocaleString()} km</span>
              </div>
              <input
                type="range"
                min="0"
                max="60000"
                step="100"
                value={telemetry.odometer}
                onChange={(e) => updateTelemetry({ odometer: parseFloat(e.target.value) })}
                className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full appearance-none outline-none accent-purple-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 dark:text-slate-400 font-mono">
                <span>0 km</span>
                <span>60,000 km</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-5 border-t border-slate-200 dark:border-slate-800">
            <button
              onClick={fetchModuleAPredictions}
              disabled={loading}
              className="w-full py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs shadow-md transition-all active:scale-95 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Computing Live Inference...</span>
                </>
              ) : (
                <>
                  <Cpu className="w-4 h-4" />
                  <span>Run Inference Engine</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Active Ensemble Card with Watermark */}
        <div className="app-card p-5 relative overflow-hidden bg-slate-50 dark:bg-[#111622]">
          <div className="absolute right-2 bottom-0 text-[100px] font-extrabold text-slate-200 dark:text-slate-800/40 leading-none pointer-events-none select-none font-mono">
            ML
          </div>
          <h3 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4 relative z-10">
            Active Ensemble
          </h3>
          <div className="space-y-3 relative z-10 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-700 dark:text-slate-300 flex items-center gap-2 font-medium">
                <span className="w-2 h-2 rounded-full bg-cyan-500" />
                SoC Est. (KNN)
              </span>
              <span className="bg-cyan-100 dark:bg-cyan-950/60 border border-cyan-300 dark:border-cyan-800 text-cyan-700 dark:text-cyan-400 px-2 py-0.5 rounded text-[10px] font-mono font-bold">
                v2.4.1 (95.8%)
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-700 dark:text-slate-300 flex items-center gap-2 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                SoH Tabular (XGB)
              </span>
              <span className="bg-emerald-100 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-800 text-emerald-700 dark:text-emerald-400 px-2 py-0.5 rounded text-[10px] font-mono font-bold">
                v1.8.0 (R²=0.982)
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-700 dark:text-slate-300 flex items-center gap-2 font-medium">
                <span className="w-2 h-2 rounded-full bg-purple-500" />
                RUL Pred. (GB)
              </span>
              <span className="bg-purple-100 dark:bg-purple-950/60 border border-purple-300 dark:border-purple-800 text-purple-700 dark:text-purple-400 px-2 py-0.5 rounded text-[10px] font-mono font-bold">
                v3.0.2 (99.97%)
              </span>
            </div>
          </div>
        </div>
      </aside>

      {/* ─── RIGHT SECTION: 4 HERO METRIC CARDS & 24H TREND (Stitch Section) ─── */}
      <section className="col-span-1 lg:col-span-8 xl:col-span-9 flex flex-col gap-6">
        
        {/* 4 Hero Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Card 1: State of Charge (KNN) */}
          <div className="app-card p-6 shadow-sm flex flex-col justify-between relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-2xl -mr-10 -mt-10 pointer-events-none" />
            <div className="flex justify-between items-start mb-2 relative z-10">
              <div>
                <div className="text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-widest mb-1 flex items-center gap-2">
                  State of Charge
                  <span className="bg-cyan-100 dark:bg-cyan-950/60 text-cyan-700 dark:text-cyan-300 px-1.5 py-0.5 rounded text-[9px] font-mono">KNN</span>
                </div>
                <div className="text-4xl font-extrabold text-slate-900 dark:text-slate-100 flex items-baseline gap-1 font-mono">
                  {socVal.toFixed(1)}<span className="text-xl text-slate-400 font-normal">%</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-[10px] text-slate-400 uppercase font-mono">R² Confidence</div>
                <div className="text-sm font-bold text-cyan-600 dark:text-cyan-400 font-mono">0.9958</div>
              </div>
            </div>

            {/* Circular Arc SVG Gauge from Stitch */}
            <div className="flex-1 flex items-center justify-center relative z-10 my-2">
              <svg className="w-44 h-44 drop-shadow-[0_0_12px_rgba(8,145,178,0.2)]" viewBox="0 0 100 100">
                <circle
                  className="text-slate-200 dark:text-slate-800"
                  cx="50"
                  cy="50"
                  fill="none"
                  r="40"
                  stroke="currentColor"
                  strokeDasharray="188.5 251.2"
                  strokeLinecap="round"
                  strokeWidth="8"
                  transform="rotate(135 50 50)"
                />
                <circle
                  className="text-cyan-600 dark:text-cyan-400 transition-all duration-700 ease-out"
                  cx="50"
                  cy="50"
                  fill="none"
                  r="40"
                  stroke="currentColor"
                  strokeDasharray={`${strokeDash} 251.2`}
                  strokeLinecap="round"
                  strokeWidth="8"
                  transform="rotate(135 50 50)"
                />
                <text className="text-slate-900 dark:text-slate-100 font-bold text-[14px]" fill="currentColor" textAnchor="middle" x="50" y="54">
                  {socVal > 20 ? "Optimal" : "Depleted"}
                </text>
              </svg>
            </div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono text-center">
              Target Range: 60.0V – 84.0V Pack Voltage
            </div>
          </div>

          {/* Card 2: State of Health (XGBOOST) */}
          <div className="app-card p-6 shadow-sm flex flex-col justify-between relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-2xl -mr-10 -mt-10 pointer-events-none" />
            <div className="flex justify-between items-start mb-2 relative z-10">
              <div>
                <div className="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-widest mb-1 flex items-center gap-2">
                  State of Health
                  <span className="bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 px-1.5 py-0.5 rounded text-[9px] font-mono">XGBOOST</span>
                </div>
                <div className="text-4xl font-extrabold text-slate-900 dark:text-slate-100 flex items-baseline gap-1 font-mono">
                  {sohVal.toFixed(1)}<span className="text-xl text-slate-400 font-normal">%</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-[10px] text-slate-400 uppercase font-mono">R² Confidence</div>
                <div className="text-sm font-bold text-emerald-600 dark:text-emerald-400 font-mono">0.9820</div>
              </div>
            </div>

            {/* Glowing 7-Bar Histogram from Stitch */}
            <div className="flex-1 my-6 relative z-10 flex items-end justify-center">
              <div className="h-28 w-full flex items-end gap-2.5 px-4">
                {[35, 50, 65, 80, 95, 75, 45].map((h, i) => {
                  const isChampion = i === 4;
                  return (
                    <div key={i} className="flex-1 bg-slate-200 dark:bg-slate-800 rounded-t-md h-full flex items-end relative overflow-hidden">
                      <div
                        className={`w-full rounded-t-md transition-all duration-700 ${
                          isChampion
                            ? "bg-emerald-600 dark:bg-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.5)]"
                            : "bg-emerald-500/40"
                        }`}
                        style={{ height: `${h}%` }}
                      />
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="flex justify-between text-[11px] text-slate-500 dark:text-slate-400 font-mono px-2">
              <span>Nominal Capacity: 150 Ah</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">Grade A Asset</span>
            </div>
          </div>

          {/* Card 3: Remaining Useful Life (GRADIENT BOOST) */}
          <div className="app-card p-6 shadow-sm flex flex-col justify-between relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-2xl -mr-10 -mt-10 pointer-events-none" />
            <div className="flex justify-between items-start mb-2 relative z-10">
              <div>
                <div className="text-xs font-bold text-purple-600 dark:text-purple-400 uppercase tracking-widest mb-1 flex items-center gap-2">
                  Remaining Useful Life
                  <span className="bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 px-1.5 py-0.5 rounded text-[9px] font-mono">GRADIENT BOOST</span>
                </div>
                <div className="text-4xl font-extrabold text-slate-900 dark:text-slate-100 flex items-baseline gap-2 font-mono">
                  {rulVal.toLocaleString()}<span className="text-xl text-slate-400 font-normal">cycles</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-[10px] text-slate-400 uppercase font-mono">R² Confidence</div>
                <div className="text-sm font-bold text-purple-600 dark:text-purple-400 font-mono">0.9997</div>
              </div>
            </div>

            {/* Stitch Degradation Bar */}
            <div className="flex-1 flex flex-col justify-end mt-4 relative z-10">
              <div className="w-full h-2.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden mb-2 relative">
                <div
                  className="h-full bg-gradient-to-r from-red-500 via-amber-500 to-purple-600 rounded-full relative transition-all duration-700"
                  style={{ width: `${Math.min(100, Math.max(10, (rulVal / 1500) * 100))}%` }}
                >
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow-md" />
                </div>
              </div>
              <div className="flex justify-between text-[10px] text-slate-500 dark:text-slate-400 font-mono">
                <span>0 (Critical Replacement)</span>
                <span>1,500 Cycles (New)</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-4 border-l-2 border-purple-500 pl-3 leading-relaxed">
                Degradation knee-point predicted in approx. <strong>{Math.max(120, rulVal - 450)} cycles</strong> under current operating C-rate.
              </p>
            </div>
          </div>

          {/* Card 4: Est. Range (XGBOOST (R)) */}
          <div className="app-card p-6 shadow-sm flex flex-col justify-between relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 rounded-full blur-2xl -mr-10 -mt-10 pointer-events-none" />
            <div className="flex justify-between items-start mb-2 relative z-10">
              <div>
                <div className="text-xs font-bold text-amber-600 dark:text-amber-400 uppercase tracking-widest mb-1 flex items-center gap-2">
                  Est. Range per Charge
                  <span className="bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 px-1.5 py-0.5 rounded text-[9px] font-mono">XGBOOST (R)</span>
                </div>
                <div className="text-4xl font-extrabold text-slate-900 dark:text-slate-100 flex items-baseline gap-2 font-mono">
                  {mileageVal.toFixed(1)}<span className="text-xl text-slate-400 font-normal">km</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-[10px] text-slate-400 uppercase font-mono">R² Confidence</div>
                <div className="text-sm font-bold text-amber-600 dark:text-amber-400 font-mono">0.9445</div>
              </div>
            </div>

            {/* Stitch Dynamic Sparkline Curve */}
            <div className="flex-1 mt-4 relative z-10 flex items-center">
              <div className="w-full relative h-24">
                <svg className="w-full h-full stroke-current" fill="none" preserveAspectRatio="none" strokeWidth="2.5" viewBox="0 0 200 80">
                  <path d="M0,70 Q20,60 40,40 T80,30 T120,50 T160,20 T200,40" stroke="#CBD5E1" strokeDasharray="4 4" />
                  <path className="text-amber-500 drop-shadow-[0_0_8px_rgba(217,119,6,0.4)]" d="M0,75 Q20,65 40,50 T80,45 T120,60 T160,35 T200,55" stroke="currentColor" />
                </svg>
                <div className="absolute left-[80%] top-[35%] w-3.5 h-3.5 bg-amber-500 rounded-full ring-4 ring-amber-500/20 shadow-md animate-pulse" />
              </div>
            </div>

            <div className="flex justify-between text-[11px] text-slate-500 dark:text-slate-400 font-mono">
              <span>Energy: 8.5 kWh/100km</span>
              <span>Efficiency Index: <strong>0.88</strong></span>
            </div>
          </div>
        </div>

        {/* 24H Aggregate Confidence Trend */}
        <div className="app-card p-6 shadow-sm">
          <div className="flex flex-wrap justify-between items-center gap-4 mb-6">
            <h3 className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-widest font-mono">
              24H Aggregate Confidence & Telemetry Trend
            </h3>
            <div className="flex items-center gap-4 font-mono text-xs text-slate-600 dark:text-slate-400">
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-1 bg-cyan-500 rounded" /> SoC (KNN)</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-1 bg-emerald-500 rounded" /> SoH (XGB)</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-1 bg-purple-500 rounded" /> RUL (GB)</span>
            </div>
          </div>

          <div className="h-28 w-full relative">
            <svg className="w-full h-full absolute inset-0" preserveAspectRatio="none" viewBox="0 0 1000 100">
              {/* Grid Lines */}
              <line className="text-slate-200 dark:text-slate-800" stroke="currentColor" strokeDasharray="4 4" strokeWidth="1" x1="0" x2="1000" y1="25" y2="25" />
              <line className="text-slate-200 dark:text-slate-800" stroke="currentColor" strokeDasharray="4 4" strokeWidth="1" x1="0" x2="1000" y1="50" y2="50" />
              <line className="text-slate-200 dark:text-slate-800" stroke="currentColor" strokeDasharray="4 4" strokeWidth="1" x1="0" x2="1000" y1="75" y2="75" />

              {/* SoC Trend Line */}
              <path d="M0,45 Q150,35 300,50 T600,40 T1000,30" fill="none" stroke="#0891B2" strokeWidth="2.5" />
              {/* SoH Trend Line */}
              <path d="M0,20 Q200,22 400,20 T800,24 T1000,22" fill="none" stroke="#059669" strokeWidth="2.5" />
              {/* RUL Trend Line */}
              <path d="M0,60 Q250,55 500,65 T750,58 T1000,62" fill="none" stroke="#7C3AED" strokeWidth="2.5" />
            </svg>
          </div>
        </div>
      </section>
    </div>
  );
};
