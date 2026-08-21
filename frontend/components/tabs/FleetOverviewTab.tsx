"use client";

import React, { useEffect, useState } from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { GlassCard } from "../ui/GlassCard";
import { Badge } from "../ui/Badge";
import { AnimatedNumber } from "../ui/AnimatedNumber";
import { BatteryPack3D } from "../digital-twin/BatteryPack3D";
import { getSystemHealth } from "../../lib/api/client";
import { HealthResponse } from "../../lib/api/types";
import {
  Activity,
  ShieldCheck,
  Zap,
  TrendingDown,
  Navigation,
  Sparkles,
} from "lucide-react";

export const FleetOverviewTab: React.FC = () => {
  const { vehicles, selectedVehicleId, setSelectedVehicle, getSelectedVehicle, setCopilotOpen } =
    useFleetStore();
  const vehicle = getSelectedVehicle();

  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    getSystemHealth().then(setHealth).catch(console.error);
  }, []);

  const avgSoc = vehicles.reduce((a, b) => a + b.soc, 0) / vehicles.length;
  const avgSoh = vehicles.reduce((a, b) => a + b.soh, 0) / vehicles.length;
  const avgRul = vehicles.reduce((a, b) => a + b.rul, 0) / vehicles.length;
  const avgMileage = vehicles.reduce((a, b) => a + b.mileage, 0) / vehicles.length;

  return (
    <div className="space-y-6">
      {/* Top System Health Banner */}
      <div className="app-card p-4 flex flex-wrap items-center justify-between gap-4 border border-emerald-200 dark:border-emerald-800/60 bg-emerald-50 dark:bg-emerald-950/20">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-100 dark:bg-emerald-900/40 border border-emerald-300 text-emerald-700 dark:text-emerald-400 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-slate-900 dark:text-slate-100">
                Tri-Pillar ML Engine Live
              </span>
              <Badge variant="emerald" size="sm" dot>
                74 Models Active
              </Badge>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Module A (Macro State) • Module B (Thermal Hazard RF) • Module C (BA-BMS Knee Prognostics)
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setCopilotOpen(true)}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-cyan-50 dark:bg-cyan-950/60 hover:bg-cyan-100 dark:hover:bg-cyan-900/60 text-cyan-700 dark:text-cyan-300 border border-cyan-200 dark:border-cyan-800 text-xs font-semibold transition-all hover:scale-105"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Ask AI Copilot
          </button>
        </div>
      </div>

      {/* 4 Fleet-Wide KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <GlassCard glow="cyan">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
            <span>Fleet Avg State of Charge</span>
            <Zap className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <AnimatedNumber value={avgSoc} decimals={1} className="text-3xl text-cyan-700 dark:text-cyan-300" suffix="%" />
            <span className="text-xs text-emerald-600 dark:text-emerald-400 font-semibold">Nominal</span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5">Across {vehicles.length} commercial chassis</p>
        </GlassCard>

        <GlassCard glow="emerald">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
            <span>Fleet Avg State of Health</span>
            <Activity className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <AnimatedNumber value={avgSoh} decimals={1} className="text-3xl text-emerald-700 dark:text-emerald-300" suffix="%" />
            <span className="text-xs text-emerald-600 dark:text-emerald-400 font-semibold">Tier 1 Health</span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5">XGBoost & PyTorch CNN-LSTM</p>
        </GlassCard>

        <GlassCard glow="purple">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
            <span>Fleet Avg Remaining Useful Life</span>
            <TrendingDown className="w-4 h-4 text-purple-600 dark:text-purple-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <AnimatedNumber value={avgRul} decimals={0} className="text-3xl text-purple-700 dark:text-purple-300" suffix=" c" />
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">Cycles</span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5">Gradient Boosting Champion (R²=0.9997)</p>
        </GlassCard>

        <GlassCard glow="amber">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
            <span>Fleet Avg Range per Charge</span>
            <Navigation className="w-4 h-4 text-amber-600 dark:text-amber-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <AnimatedNumber value={avgMileage} decimals={1} className="text-3xl text-amber-700 dark:text-amber-300" suffix=" km" />
            <span className="text-xs text-amber-600 dark:text-amber-400 font-semibold">Est. Range</span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5">Euler HiLoad dynamic driving cycle</p>
        </GlassCard>
      </div>

      {/* Main Row: 3D Digital Twin & Live Selected Vehicle Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 3D Digital Twin Visualization (2 Cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
              Real WebGL 3D Digital Twin • {vehicle.id}
            </h3>
            <Badge variant={vehicle.status === "critical" ? "crimson" : vehicle.status === "warning" ? "amber" : "emerald"} dot>
              {vehicle.status.toUpperCase()}
            </Badge>
          </div>

          <BatteryPack3D
            batteryTemp={vehicle.battery_temp}
            controllerTemp={vehicle.controller_temp}
            motorTemp={vehicle.motor_temp}
            soc={vehicle.soc}
          />
        </div>

        {/* Selected Vehicle Telemetry Details (1 Col) */}
        <GlassCard className="flex flex-col justify-between">
          <div>
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-mono text-cyan-700 dark:text-cyan-400 uppercase font-bold">{vehicle.id}</span>
                <h4 className="text-base font-bold text-slate-900 dark:text-slate-100 mt-0.5">{vehicle.model}</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">{vehicle.fleet}</p>
              </div>
              <Badge variant="slate" size="sm">
                Driver: {vehicle.driver.split(" ")[0]}
              </Badge>
            </div>

            <div className="mt-5 space-y-3">
              <div className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100 dark:border-slate-800">
                <span className="text-slate-500 dark:text-slate-400">Pack Voltage:</span>
                <span className="font-mono text-slate-800 dark:text-slate-200 font-semibold">{vehicle.voltage.toFixed(1)} V</span>
              </div>
              <div className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100 dark:border-slate-800">
                <span className="text-slate-500 dark:text-slate-400">Current:</span>
                <span className="font-mono text-slate-800 dark:text-slate-200 font-semibold">{vehicle.current.toFixed(1)} A</span>
              </div>
              <div className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100 dark:border-slate-800">
                <span className="text-slate-500 dark:text-slate-400">Elapsed Cycles:</span>
                <span className="font-mono text-slate-800 dark:text-slate-200 font-semibold">{vehicle.charge_cycle_count} EFC</span>
              </div>
              <div className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100 dark:border-slate-800">
                <span className="text-slate-500 dark:text-slate-400">Max Zone Temperature:</span>
                <span className="font-mono text-amber-600 dark:text-amber-400 font-semibold">{vehicle.motor_temp.toFixed(1)} °C</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <div className="text-[11px] text-slate-500 dark:text-slate-400">
              Telemetry: <span className="text-emerald-600 dark:text-emerald-400 font-medium">{vehicle.lastPing}</span>
            </div>
            <button
              onClick={() => useFleetStore.getState().setActiveTab("state-est")}
              className="text-xs font-semibold text-cyan-600 dark:text-cyan-400 hover:underline flex items-center gap-1"
            >
              Analyze Telemetry →
            </button>
          </div>
        </GlassCard>
      </div>

      {/* Vehicle Grid Selector */}
      <div>
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-3">
          Select Fleet Vehicle Chassis
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {vehicles.map((v) => {
            const isSelected = v.id === selectedVehicleId;
            return (
              <div
                key={v.id}
                onClick={() => setSelectedVehicle(v.id)}
                className={`vehicle-card p-4 rounded-xl border transition-all cursor-pointer select-none ${
                  isSelected
                    ? "bg-cyan-50 dark:bg-slate-800/90 border-cyan-500 shadow-sm"
                    : "app-card hover:border-slate-300 dark:hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono font-bold text-sm text-slate-900 dark:text-slate-100">{v.id}</span>
                  <span
                    className={`w-2.5 h-2.5 rounded-full ${
                      v.status === "critical"
                        ? "bg-rose-500 animate-pulse"
                        : v.status === "warning"
                        ? "bg-amber-500"
                        : "bg-emerald-500"
                    }`}
                  />
                </div>
                <div className="text-xs text-slate-500 dark:text-slate-400 truncate">{v.model}</div>
                <div className="mt-3 flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-600 dark:text-slate-300">SOC: <strong className="text-cyan-600 dark:text-cyan-400">{v.soc.toFixed(0)}%</strong></span>
                  <span className="text-slate-600 dark:text-slate-300">SOH: <strong className="text-emerald-600 dark:text-emerald-400">{v.soh.toFixed(0)}%</strong></span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
