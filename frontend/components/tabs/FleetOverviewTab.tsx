"use client";

import React, { useEffect, useState, useMemo } from "react";
import { useFleetStore, VehicleStatusFilter } from "../../lib/store/useFleetStore";
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
  Search,
  PlusCircle,
  Download,
  Filter,
  Truck,
} from "lucide-react";

export const FleetOverviewTab: React.FC = () => {
  const {
    vehicles,
    selectedVehicleId,
    setSelectedVehicle,
    getSelectedVehicle,
    setCopilotOpen,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    hubFilter,
    setHubFilter,
    getFilteredVehicles,
    lookupOrAddVehicle,
  } = useFleetStore();

  const vehicle = getSelectedVehicle();
  const [customVinInput, setCustomVinInput] = useState("");
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    getSystemHealth().then(setHealth).catch(console.error);
  }, []);

  const filteredVehicles = getFilteredVehicles();

  // Fleet-wide aggregated stats
  const avgSoc = vehicles.reduce((a, b) => a + b.soc, 0) / vehicles.length;
  const avgSoh = vehicles.reduce((a, b) => a + b.soh, 0) / vehicles.length;
  const avgRul = vehicles.reduce((a, b) => a + b.rul, 0) / vehicles.length;
  const avgMileage = vehicles.reduce((a, b) => a + b.mileage, 0) / vehicles.length;

  const countActive = vehicles.filter((v) => v.status === "active").length;
  const countWarning = vehicles.filter((v) => v.status === "warning").length;
  const countCritical = vehicles.filter((v) => v.status === "critical").length;
  const countCharging = vehicles.filter((v) => v.status === "charging").length;

  const handleAddCustomVehicle = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customVinInput.trim()) return;
    const v = lookupOrAddVehicle(customVinInput.trim());
    setSelectedVehicle(v.id);
    setCustomVinInput("");
  };

  const handleExportCSV = () => {
    const headers = "Chassis_ID,Model,Hub,Driver,SOC_Pct,SOH_Pct,RUL_Cycles,Range_KM,Battery_Temp_C,Voltage_V,Current_A,Cycles_Count,Status\n";
    const rows = vehicles
      .map(
        (v) =>
          `"${v.id}","${v.model}","${v.fleet}","${v.driver}",${v.soc},${v.soh},${v.rul},${v.mileage},${v.battery_temp},${v.voltage},${v.current},${v.charge_cycle_count},"${v.status}"`
      )
      .join("\n");
    const blob = new Blob([headers + rows], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `Enterprise_EV_Fleet_Telemetry_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

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
                Enterprise Commercial Telematics Live
              </span>
              <Badge variant="emerald" size="sm" dot>
                {vehicles.length} Fleet Vehicles
              </Badge>
              <Badge variant="cyan" size="sm">
                74 ML/DL Models
              </Badge>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Live streaming battery intelligence across Euler, Tata, Mahindra, and Piaggio fleets
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:bg-slate-50 text-slate-700 dark:text-slate-200 text-xs font-semibold shadow-sm transition-all"
            title="Download Enterprise Fleet Telemetry as CSV"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Fleet (CSV)</span>
          </button>

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
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5">Across {vehicles.length} commercial vehicles</p>
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
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5">Multi-chassis driving cycle aggregate</p>
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
            <Badge variant={vehicle.status === "critical" ? "crimson" : vehicle.status === "warning" ? "amber" : vehicle.status === "charging" ? "cyan" : "emerald"} dot>
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

      {/* Enterprise Search, Ingestion & Filter Control Panel */}
      <GlassCard className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Truck className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
              Universal Enterprise Fleet Directory ({vehicles.length} Vehicles Ingested)
            </h3>
          </div>

          {/* Quick Custom VIN / Chassis Ingestion Form */}
          <form onSubmit={handleAddCustomVehicle} className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Look up any VIN / Chassis ID..."
              value={customVinInput}
              onChange={(e) => setCustomVinInput(e.target.value)}
              className="px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-500 font-mono"
            />
            <button
              type="submit"
              className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold transition-all shadow-sm"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Lookup Chassis</span>
            </button>
          </form>
        </div>

        {/* Filter Controls Row */}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-1">
          {/* Search Box */}
          <div className="relative flex-1 min-w-[220px]">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Filter by chassis ID, driver name, OEM, or hub city..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3.5 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/80 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-500 font-sans"
            />
          </div>

          {/* Status Filter Buttons */}
          <div className="flex flex-wrap items-center gap-1.5">
            <button
              onClick={() => setStatusFilter("all")}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                statusFilter === "all"
                  ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-950 shadow-sm"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200"
              }`}
            >
              All ({vehicles.length})
            </button>
            <button
              onClick={() => setStatusFilter("active")}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                statusFilter === "active"
                  ? "bg-emerald-600 text-white shadow-sm"
                  : "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-100"
              }`}
            >
              Active ({countActive})
            </button>
            <button
              onClick={() => setStatusFilter("warning")}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                statusFilter === "warning"
                  ? "bg-amber-600 text-white shadow-sm"
                  : "bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 hover:bg-amber-100"
              }`}
            >
              Warning ({countWarning})
            </button>
            <button
              onClick={() => setStatusFilter("critical")}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                statusFilter === "critical"
                  ? "bg-rose-600 text-white shadow-sm"
                  : "bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 hover:bg-rose-100"
              }`}
            >
              Critical ({countCritical})
            </button>
            <button
              onClick={() => setStatusFilter("charging")}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
                statusFilter === "charging"
                  ? "bg-cyan-600 text-white shadow-sm"
                  : "bg-cyan-50 dark:bg-cyan-950/40 text-cyan-700 dark:text-cyan-300 hover:bg-cyan-100"
              }`}
            >
              Charging ({countCharging})
            </button>
          </div>

          {/* Hub Filter Dropdown */}
          <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-2.5 py-1 rounded-xl text-xs">
            <Filter className="w-3 h-3 text-slate-400" />
            <select
              value={hubFilter}
              onChange={(e) => setHubFilter(e.target.value)}
              className="bg-transparent text-xs font-semibold text-slate-700 dark:text-slate-300 focus:outline-none cursor-pointer"
            >
              <option value="all">All Enterprise Hubs</option>
              <option value="Ahmedabad">Ahmedabad Hubs</option>
              <option value="Surat">Surat Hubs</option>
              <option value="Vadodara">Vadodara Hubs</option>
              <option value="Rajkot">Rajkot Hubs</option>
              <option value="Mumbai">Mumbai Hubs</option>
              <option value="Pune">Pune Hubs</option>
              <option value="Bengaluru">Bengaluru Hubs</option>
              <option value="Delhi">Delhi NCR Corridor</option>
              <option value="Hyderabad">Hyderabad Hubs</option>
              <option value="Chennai">Chennai Hubs</option>
            </select>
          </div>
        </div>

        {/* Matching Vehicles Grid (Max height scrollable for 50+ vehicles) */}
        <div className="max-h-[380px] overflow-y-auto pr-1">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {filteredVehicles.map((v) => {
              const isSelected = v.id === selectedVehicleId;
              return (
                <div
                  key={v.id}
                  onClick={() => setSelectedVehicle(v.id)}
                  className={`vehicle-card p-3 rounded-xl border transition-all cursor-pointer select-none ${
                    isSelected
                      ? "bg-cyan-50 dark:bg-slate-800/90 border-cyan-500 shadow-md ring-1 ring-cyan-500"
                      : "app-card hover:border-slate-300 dark:hover:border-slate-700 hover:shadow-sm"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono font-bold text-xs text-slate-900 dark:text-slate-100">{v.id}</span>
                    <span
                      className={`w-2.5 h-2.5 rounded-full ${
                        v.status === "critical"
                          ? "bg-rose-500 animate-pulse"
                          : v.status === "warning"
                          ? "bg-amber-500"
                          : v.status === "charging"
                          ? "bg-cyan-500 animate-pulse"
                          : "bg-emerald-500"
                      }`}
                      title={v.status.toUpperCase()}
                    />
                  </div>
                  <div className="text-[11px] font-medium text-slate-700 dark:text-slate-300 truncate">{v.model}</div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">{v.fleet.split(" ")[0]} • {v.driver.split(" ")[0]}</div>
                  <div className="mt-2 pt-1.5 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[10px] font-mono">
                    <span className="text-slate-600 dark:text-slate-400">SOC: <strong className="text-cyan-600 dark:text-cyan-400">{v.soc.toFixed(0)}%</strong></span>
                    <span className="text-slate-600 dark:text-slate-400">SOH: <strong className="text-emerald-600 dark:text-emerald-400">{v.soh.toFixed(0)}%</strong></span>
                  </div>
                </div>
              );
            })}
          </div>

          {filteredVehicles.length === 0 && (
            <div className="p-8 text-center text-xs text-slate-500 dark:text-slate-400">
              No vehicles match "{searchQuery}". Type any custom chassis ID above and click <strong>"Lookup Chassis"</strong> to dynamically ingest it!
            </div>
          )}
        </div>
      </GlassCard>
    </div>
  );
};
