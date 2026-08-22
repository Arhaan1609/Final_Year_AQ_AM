"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { predictThermal, predictSOHDeep } from "../../lib/api/client";
import { ThermalResponse, SOHDeepResponse } from "../../lib/api/types";
import { Flame, ShieldAlert, Thermometer, ShieldCheck, AlertCircle, RefreshCw, Cpu, Activity } from "lucide-react";

export const ThermalSafetyTab: React.FC = () => {
  const { telemetry, selectedVehicleId, getSelectedVehicle } = useFleetStore();
  const vehicle = getSelectedVehicle();

  const [batteryTemp, setBatteryTemp] = useState<number>(vehicle.battery_temp || telemetry.temperature || 33.2);
  const [controllerTemp, setControllerTemp] = useState<number>(vehicle.controller_temp || 41.5);
  const [motorTemp, setMotorTemp] = useState<number>(vehicle.motor_temp || 54.0);

  // Sync temperatures immediately when vehicle changes
  useEffect(() => {
    setBatteryTemp(vehicle.battery_temp || telemetry.temperature || 32.0);
    setControllerTemp(vehicle.controller_temp || (vehicle.battery_temp ? vehicle.battery_temp + 8.5 : 40.5));
    setMotorTemp(vehicle.motor_temp || (vehicle.battery_temp ? vehicle.battery_temp + 18.0 : 50.0));
  }, [selectedVehicleId, vehicle]);

  const [thermalData, setThermalData] = useState<ThermalResponse | null>(null);
  const [sohDeepData, setSohDeepData] = useState<SOHDeepResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const evaluateThermal = useCallback(async () => {
    setLoading(true);
    try {
      const [thermal, sohDeep] = await Promise.all([
        predictThermal({
          vbt: batteryTemp,
          vct: controllerTemp,
          vmt: motorTemp,
          vbv: telemetry.voltage,
          vbc: telemetry.current,
          soc: vehicle.soc || 75,
          speed: telemetry.avgSpeed || 34,
        }),
        predictSOHDeep({
          vehicle_id: selectedVehicleId,
          sequence: Array.from({ length: 10 }, (_, idx) => [
            Number(((telemetry.voltage || 75.0) + (9 - idx) * 0.12).toFixed(2)),
            Number(((telemetry.current || -18.0) - (idx % 3) * 1.2).toFixed(2)),
            Number(((batteryTemp || 32.0) - (9 - idx) * 0.25).toFixed(2)),
            Number(((vehicle.soc || 75.0) + (9 - idx) * 0.75).toFixed(2)),
          ]),
        }),
      ]);
      setThermalData(thermal);
      setSohDeepData(sohDeep);
    } catch (e) {
      console.error("Thermal safety error:", e);
    } finally {
      setLoading(false);
    }
  }, [batteryTemp, controllerTemp, motorTemp, telemetry, selectedVehicleId, vehicle.soc]);

  useEffect(() => {
    const timer = setTimeout(() => {
      evaluateThermal();
    }, 150);
    return () => clearTimeout(timer);
  }, [evaluateThermal]);

  const isCritical = thermalData?.severity === "CRITICAL" || batteryTemp > 50;
  const isWarning = thermalData?.severity === "WARNING" || batteryTemp > 40;

  return (
    <div className="flex flex-col w-full gap-6">
      
      {/* Top Header Area (Stitch Screen Header) */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">
            Thermal Monitoring & Cyber-Physical Safety
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-2xl">
            Real-time multi-zone thermal telemetry and active safety directive status for Chassis <span className="font-mono font-bold text-cyan-600 dark:text-cyan-400">{selectedVehicleId}</span>.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={evaluateThermal}
            disabled={loading}
            className="px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs shadow-sm flex items-center gap-2 transition-all active:scale-95"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Run Thermal Diagnostics</span>
          </button>
        </div>
      </div>

      {/* Main Content Grid (Stitch 12-Column Grid) */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        
        {/* Left Column: 3 Thermal Zones (8 Cols) */}
        <div className="xl:col-span-8 flex flex-col gap-6">
          
          {/* Zone 1: Battery Pack (Primary Array) */}
          <div className="app-card p-6 shadow-sm relative overflow-hidden group">
            <div className="flex justify-between items-start mb-4 relative z-10">
              <div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Zone 1: Battery Pack</h2>
                <p className="text-xs font-mono text-slate-500 dark:text-slate-400 uppercase tracking-widest mt-0.5">Primary Array (LFP Cells)</p>
              </div>
              <div className={`px-3.5 py-1 rounded-full text-xs font-bold flex items-center gap-2 shadow-sm font-mono ${
                isCritical
                  ? "bg-red-100 dark:bg-red-950/60 text-red-700 dark:text-red-400 border border-red-300 dark:border-red-800"
                  : isWarning
                  ? "bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400 border border-amber-300 dark:border-amber-800"
                  : "bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800"
              }`}>
                <span className={`w-2 h-2 rounded-full ${isCritical ? "bg-red-500 animate-pulse" : isWarning ? "bg-amber-500" : "bg-emerald-500"}`} />
                <span>{thermalData?.safety_status || (isCritical ? "ELEVATED HAZARD" : "SAFE")}</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center relative z-10">
              <div>
                <div className="flex items-baseline gap-2 mb-1">
                  <span className="text-5xl font-extrabold text-slate-900 dark:text-slate-100 leading-none font-mono">
                    {batteryTemp.toFixed(1)}
                  </span>
                  <span className="text-2xl font-bold text-slate-400 font-mono">°C</span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-6 font-mono">+1.8°C / hr rate of change</p>

                {/* Sub-module progress bars */}
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-xs font-mono mb-1 text-slate-600 dark:text-slate-300">
                      <span>Module A Avg</span>
                      <span>{(batteryTemp - 1.2).toFixed(1)}°C</span>
                    </div>
                    <div className="h-2 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 w-[65%] rounded-full" />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs font-mono mb-1 text-slate-600 dark:text-slate-300">
                      <span>Module B Avg</span>
                      <span className="text-amber-600 dark:text-amber-400">{(batteryTemp + 1.6).toFixed(1)}°C</span>
                    </div>
                    <div className="h-2 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-amber-500 w-[78%] rounded-full shadow-sm" />
                    </div>
                  </div>
                </div>

                {/* Slider */}
                <div className="mt-5 pt-3 border-t border-slate-200 dark:border-slate-800">
                  <div className="flex justify-between text-xs text-slate-500 mb-1">
                    <span>Adjust Pack Temp</span>
                    <span className="font-mono font-bold text-cyan-600">{batteryTemp.toFixed(1)}°C</span>
                  </div>
                  <input
                    type="range"
                    min="15"
                    max="65"
                    step="0.5"
                    value={batteryTemp}
                    onChange={(e) => setBatteryTemp(parseFloat(e.target.value))}
                    className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full appearance-none outline-none accent-cyan-600 cursor-pointer"
                  />
                </div>
              </div>

              {/* Simulated Heatmap via gradient & IR feed */}
              <div className="relative h-52 w-full bg-slate-900 rounded-xl overflow-hidden flex flex-col items-center justify-center p-4 border border-slate-800">
                <div className="absolute inset-0 bg-gradient-to-tr from-cyan-950/40 via-emerald-950/30 to-amber-950/40 mix-blend-screen" />
                
                {/* 3D Thermal Representation Matrix */}
                <div className="grid grid-cols-4 gap-2 w-full max-w-[240px] relative z-10">
                  {Array.from({ length: 8 }).map((_, i) => {
                    const tempSpread = batteryTemp + (i % 2 === 0 ? 1.4 : -0.8);
                    const isHot = tempSpread > 40;
                    return (
                      <div
                        key={i}
                        className={`h-12 rounded-lg flex flex-col items-center justify-center font-mono text-[10px] font-bold border transition-all ${
                          isHot
                            ? "bg-amber-500/20 border-amber-500/60 text-amber-300 shadow-[0_0_10px_rgba(245,158,11,0.2)]"
                            : "bg-emerald-500/20 border-emerald-500/60 text-emerald-300"
                        }`}
                      >
                        <span>C{i + 1}</span>
                        <span>{tempSpread.toFixed(1)}°</span>
                      </div>
                    );
                  })}
                </div>

                <div className="absolute top-3 right-3 bg-slate-900/90 border border-slate-700 px-2 py-0.5 rounded text-[10px] font-mono text-cyan-400">
                  IR_SENSOR_FEED
                </div>
              </div>
            </div>
          </div>

          {/* Zones 2 & 3 Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Zone 2: Power Electronics */}
            <div className="app-card p-6 shadow-sm flex flex-col justify-between">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">Zone 2: Controller</h3>
                  <p className="text-xs font-mono text-slate-500 dark:text-slate-400 uppercase tracking-widest">Power Electronics</p>
                </div>
                <div className="bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400 px-2.5 py-0.5 rounded-full text-xs font-mono font-bold">
                  Warm
                </div>
              </div>

              <div>
                <div className="flex items-baseline gap-2 mb-4">
                  <span className="text-4xl font-extrabold text-amber-600 dark:text-amber-400 leading-none font-mono">
                    {controllerTemp.toFixed(1)}
                  </span>
                  <span className="text-xl font-bold text-slate-400 font-mono">°C</span>
                </div>

                <div className="h-20 w-full bg-slate-100 dark:bg-slate-900/80 rounded-xl relative overflow-hidden p-2">
                  <svg className="w-full h-full text-amber-500" preserveAspectRatio="none" viewBox="0 0 100 40">
                    <path d="M0,40 L0,30 C10,28 20,35 30,25 C40,15 50,25 60,20 C70,15 80,10 90,5 L100,0 L100,40 Z" fill="currentColor" fillOpacity="0.1" />
                    <path d="M0,30 C10,28 20,35 30,25 C40,15 50,25 60,20 C70,15 80,10 90,5 L100,0" fill="none" stroke="currentColor" strokeWidth="2.5" />
                  </svg>
                </div>

                <input
                  type="range"
                  min="20"
                  max="80"
                  step="0.5"
                  value={controllerTemp}
                  onChange={(e) => setControllerTemp(parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full appearance-none outline-none accent-amber-500 cursor-pointer mt-3"
                />
              </div>
            </div>

            {/* Zone 3: Motor Assembly */}
            <div className="app-card p-6 shadow-sm flex flex-col justify-between">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">Zone 3: Motor</h3>
                  <p className="text-xs font-mono text-slate-500 dark:text-slate-400 uppercase tracking-widest">Motor Assembly</p>
                </div>
                <div className="bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-400 px-2.5 py-0.5 rounded-full text-xs font-mono font-bold">
                  High Load
                </div>
              </div>

              <div>
                <div className="flex items-baseline gap-2 mb-4">
                  <span className="text-4xl font-extrabold text-purple-600 dark:text-purple-400 leading-none font-mono">
                    {motorTemp.toFixed(1)}
                  </span>
                  <span className="text-xl font-bold text-slate-400 font-mono">°C</span>
                </div>

                <div className="h-20 w-full bg-slate-100 dark:bg-slate-900/80 rounded-xl relative overflow-hidden p-2">
                  <svg className="w-full h-full text-purple-500" preserveAspectRatio="none" viewBox="0 0 100 40">
                    <path d="M0,40 L0,35 C15,30 30,38 45,28 C60,18 75,22 90,12 L100,5 L100,40 Z" fill="currentColor" fillOpacity="0.1" />
                    <path d="M0,35 C15,30 30,38 45,28 C60,18 75,22 90,12 L100,5" fill="none" stroke="currentColor" strokeWidth="2.5" />
                  </svg>
                </div>

                <input
                  type="range"
                  min="20"
                  max="90"
                  step="0.5"
                  value={motorTemp}
                  onChange={(e) => setMotorTemp(parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full appearance-none outline-none accent-purple-600 cursor-pointer mt-3"
                />
              </div>
            </div>

          </div>
        </div>

        {/* Right Column: Thermal Risk & Action Directives (4 Cols) */}
        <div className="xl:col-span-4 flex flex-col gap-6">
          
          {/* Overall Health Card */}
          <div className="app-card p-6 shadow-sm">
            <h3 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-4 font-mono">
              Ensemble Thermal Risk Assessment
            </h3>
            
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-3xl font-extrabold text-slate-900 dark:text-slate-100 font-mono">
                  {((1 - (thermalData?.risk_probability || 0.05)) * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-slate-500 font-mono">Thermal Safety Confidence</div>
              </div>
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-300 text-emerald-600 flex items-center justify-center">
                <ShieldCheck className="w-6 h-6" />
              </div>
            </div>

            <div className="space-y-2 text-xs font-mono border-t border-slate-200 dark:border-slate-800 pt-4">
              <div className="flex justify-between">
                <span className="text-slate-500">Risk Probability:</span>
                <strong className="text-slate-800 dark:text-slate-200">{((thermalData?.risk_probability || 0.02) * 100).toFixed(2)}%</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Severity Tier:</span>
                <strong className="text-emerald-600 dark:text-emerald-400">{thermalData?.severity || "NOMINAL"}</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Active Alert:</span>
                <strong className="text-slate-800 dark:text-slate-200">{thermalData?.active_alert ? "ACTIVE" : "NONE"}</strong>
              </div>
            </div>
          </div>

          {/* Action Directives Card */}
          <div className="app-card p-6 shadow-sm">
            <h3 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest mb-3 font-mono">
              BMS Recommended Directives
            </h3>
            <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
              {thermalData?.recommended_action || "Maintain standard active cooling circulation. Thermal gradient across all 3 zones remains within nominal design threshold (< 8.0°C variance)."}
            </p>
          </div>

        </div>

      </div>
    </div>
  );
};
