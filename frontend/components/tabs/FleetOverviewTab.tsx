"use client";

import React, { useEffect, useState, useMemo } from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { GlassCard } from "../ui/GlassCard";
import { Badge } from "../ui/Badge";
import { AnimatedNumber } from "../ui/AnimatedNumber";
import { BatteryPack3D } from "../digital-twin/BatteryPack3D";
import { getSystemHealth, predictSOC, predictSOH, predictRUL, predictMileage } from "../../lib/api/client";
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
  ChevronLeft,
  ChevronRight,
  Radio,
  Sliders,
} from "lucide-react";

const PAGE_SIZE = 25;

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
    isMock,
  } = useFleetStore();

  const vehicle = getSelectedVehicle();
  const [customVinInput, setCustomVinInput] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [viewMode, setViewMode] = useState<"vehicle" | "fleet">("vehicle");

  // Dynamic live predictions state for the active vehicle
  const [livePredictions, setLivePredictions] = useState<{
    soc?: number;
    soh?: number;
    rul?: number;
    mileage?: number;
    isLoading: boolean;
  }>({ isLoading: false });

  // Whenever selected vehicle changes, query live model endpoints
  useEffect(() => {
    let isMounted = true;
    setLivePredictions((prev) => ({ ...prev, isLoading: true }));

    Promise.allSettled([
      predictSOC({
        battery_voltage: vehicle.voltage,
        battery_temp: vehicle.battery_temp,
        battery_current: vehicle.current,
        abs_current: Math.abs(vehicle.current),
        odometer: vehicle.charge_cycle_count * 58,
      }),
      predictSOH({
        battery_voltage: vehicle.voltage,
        battery_temp: vehicle.battery_temp,
        battery_current: vehicle.current,
        charge_cycle_count: vehicle.charge_cycle_count,
        odometer: vehicle.charge_cycle_count * 58,
      }),
      predictRUL({
        odometer: vehicle.charge_cycle_count * 58,
        soc_at_charge: vehicle.soc,
      }),
      predictMileage({
        run_kms: 45,
        avg_speed: vehicle.speed || 34,
        max_speed: (vehicle.speed || 34) + 20,
      }),
    ]).then(([socRes, sohRes, rulRes, mileageRes]) => {
      if (!isMounted) return;
      setLivePredictions({
        soc: socRes.status === "fulfilled" ? socRes.value.prediction : vehicle.soc,
        soh: sohRes.status === "fulfilled" ? sohRes.value.prediction : vehicle.soh,
        rul: rulRes.status === "fulfilled" ? Math.round(rulRes.value.prediction) : vehicle.rul,
        mileage: mileageRes.status === "fulfilled" ? Math.round(mileageRes.value.prediction * 10) / 10 : vehicle.mileage,
        isLoading: false,
      });
    });

    return () => {
      isMounted = false;
    };
  }, [vehicle.id, vehicle.voltage, vehicle.current, vehicle.battery_temp, vehicle.charge_cycle_count]);

  useEffect(() => {
    getSystemHealth().then(setHealth).catch(console.error);
  }, []);

  const filteredVehicles = getFilteredVehicles();

  // Reset to page 1 on filter change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, statusFilter, hubFilter]);

  const totalPages = Math.ceil(filteredVehicles.length / PAGE_SIZE) || 1;
  const paginatedVehicles = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return filteredVehicles.slice(start, start + PAGE_SIZE);
  }, [filteredVehicles, currentPage]);

  // Fleet-wide aggregate calculations
  const avgSoc = vehicles.reduce((a, b) => a + b.soc, 0) / vehicles.length;
  const avgSoh = vehicles.reduce((a, b) => a + b.soh, 0) / vehicles.length;
  const avgRul = vehicles.reduce((a, b) => a + b.rul, 0) / vehicles.length;
  const avgMileage = vehicles.reduce((a, b) => a + b.mileage, 0) / vehicles.length;

  const countActive = vehicles.filter((v) => v.status === "active").length;
  const countWarning = vehicles.filter((v) => v.status === "warning").length;
  const countCritical = vehicles.filter((v) => v.status === "critical").length;
  const countCharging = vehicles.filter((v) => v.status === "charging").length;

  // Values to display based on viewMode
  const displaySoc = viewMode === "vehicle" ? (livePredictions.soc ?? vehicle.soc) : avgSoc;
  const displaySoh = viewMode === "vehicle" ? (livePredictions.soh ?? vehicle.soh) : avgSoh;
  const displayRul = viewMode === "vehicle" ? (livePredictions.rul ?? vehicle.rul) : avgRul;
  const displayMileage = viewMode === "vehicle" ? (livePredictions.mileage ?? vehicle.mileage) : avgMileage;

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
    link.setAttribute("download", `Full_Enterprise_Fleet_778_Vehicles_${new Date().toISOString().slice(0, 10)}.csv`);
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
                Enterprise Telematics Dataset Active
              </span>
              <Badge variant="emerald" size="sm" dot>
                {vehicles.length.toLocaleString()} Fleet Vehicles
              </Badge>
              <Badge variant="cyan" size="sm">
                74 ML/DL Models
              </Badge>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Real-time inference pipeline active for chassis: <strong className="text-cyan-700 dark:text-cyan-300 font-mono">{vehicle.id}</strong> ({vehicle.model})
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:bg-slate-50 text-slate-700 dark:text-slate-200 text-xs font-semibold shadow-sm transition-all"
            title="Download Full Enterprise Fleet Telemetry as CSV"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
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

      {/* Mode Selector & Metric Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-1">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Radio className="w-4 h-4 text-cyan-600 dark:text-cyan-400 animate-pulse" />
            {viewMode === "vehicle" ? (
              <span>Live ML Predictions for <strong className="font-mono text-cyan-600 dark:text-cyan-400">{vehicle.id}</strong></span>
            ) : (
              <span>Fleet-Wide Aggregate Averages ({vehicles.length} Vehicles)</span>
            )}
          </h3>
          {viewMode === "vehicle" && livePredictions.isLoading && (
            <span className="text-[11px] text-cyan-600 dark:text-cyan-400 animate-pulse font-mono font-medium">
              • Computing live model inference...
            </span>
          )}
        </div>

        {/* View Switcher: Selected Vehicle vs Fleet Average */}
        <div className="flex items-center gap-1 bg-slate-200/80 dark:bg-slate-800 p-1 rounded-xl text-xs">
          <button
            onClick={() => setViewMode("vehicle")}
            className={`px-3 py-1 rounded-lg font-semibold transition-all ${
              viewMode === "vehicle"
                ? "bg-white dark:bg-slate-900 text-cyan-700 dark:text-cyan-300 shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
            }`}
          >
            Active Vehicle ({vehicle.id})
          </button>
          <button
            onClick={() => setViewMode("fleet")}
            className={`px-3 py-1 rounded-lg font-semibold transition-all ${
              viewMode === "fleet"
                ? "bg-white dark:bg-slate-900 text-cyan-700 dark:text-cyan-300 shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
            }`}
          >
            Fleet Average (778)
          </button>
        </div>
      </div>

      {/* 4 DYNAMIC KPI CARDS — Bounded directly to active vehicle or fleet average */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* SOC Card */}
        <GlassCard glow="cyan">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
            <span>{viewMode === "vehicle" ? `${vehicle.id} State of Charge` : "Fleet Avg SOC"}</span>
            <Zap className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <AnimatedNumber value={displaySoc} decimals={1} className="text-3xl text-cyan-700 dark:text-cyan-300" suffix="%" />
            <span className={`text-xs font-semibold ${displaySoc < 30 ? "text-rose-600 dark:text-rose-400" : displaySoc < 50 ? "text-amber-600 dark:text-amber-400" : "text-emerald-600 dark:text-emerald-400"}`}>
              {displaySoc < 30 ? "Low Charge" : displaySoc < 50 ? "Moderate" : "Nominal"}
            </span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5 flex items-center justify-between">
            <span>{viewMode === "vehicle" ? `Voltage: ${vehicle.voltage.toFixed(1)}V • Current: ${vehicle.current.toFixed(1)}A` : `Across ${vehicles.length} chassis`}</span>
            <Badge variant="cyan" size="sm">KNN</Badge>
          </p>
        </GlassCard>

        {/* SOH Card */}
        <GlassCard glow="emerald">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
            <span>{viewMode === "vehicle" ? `${vehicle.id} State of Health` : "Fleet Avg SOH"}</span>
            <Activity className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <AnimatedNumber value={displaySoh} decimals={1} className="text-3xl text-emerald-700 dark:text-emerald-300" suffix="%" />
            <span className={`text-xs font-semibold ${displaySoh < 82 ? "text-rose-600 dark:text-rose-400" : displaySoh < 90 ? "text-amber-600 dark:text-amber-400" : "text-emerald-600 dark:text-emerald-400"}`}>
              {displaySoh < 82 ? "Degraded" : displaySoh < 90 ? "Moderate" : "Tier 1 Health"}
            </span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5 flex items-center justify-between">
            <span>{viewMode === "vehicle" ? `Cycles: ${vehicle.charge_cycle_count} EFC • Temp: ${vehicle.battery_temp.toFixed(1)}°C` : "XGBoost & PyTorch CNN-LSTM"}</span>
            <Badge variant="emerald" size="sm">XGBoost</Badge>
          </p>
        </GlassCard>

        {/* RUL Card */}
        <GlassCard glow="purple">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
            <span>{viewMode === "vehicle" ? `${vehicle.id} Remaining Useful Life` : "Fleet Avg RUL"}</span>
            <TrendingDown className="w-4 h-4 text-purple-600 dark:text-purple-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <AnimatedNumber value={displayRul} decimals={0} className="text-3xl text-purple-700 dark:text-purple-300" suffix=" c" />
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              ~{(displayRul / 300).toFixed(1)} yrs
            </span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5 flex items-center justify-between">
            <span>{viewMode === "vehicle" ? `Cumulative Odo: ${(vehicle.charge_cycle_count * 58).toLocaleString()} km` : "Gradient Boosting Champion"}</span>
            <Badge variant="purple" size="sm">R²=0.9997</Badge>
          </p>
        </GlassCard>

        {/* Mileage / Range Card */}
        <GlassCard glow="amber">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-medium">
            <span>{viewMode === "vehicle" ? `${vehicle.id} Range per Charge` : "Fleet Avg Range"}</span>
            <Navigation className="w-4 h-4 text-amber-600 dark:text-amber-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <AnimatedNumber value={displayMileage} decimals={1} className="text-3xl text-amber-700 dark:text-amber-300" suffix=" km" />
            <span className="text-xs text-amber-600 dark:text-amber-400 font-semibold">Est. Range</span>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5 flex items-center justify-between">
            <span>{viewMode === "vehicle" ? `Speed: ${vehicle.speed?.toFixed(1) || 34.0} km/h • Efficiency: High` : "Dynamic driving cycle"}</span>
            <Badge variant="amber" size="sm">GBoost</Badge>
          </p>
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
                <span className="text-slate-500 dark:text-slate-400">Battery Pack Temp:</span>
                <span className="font-mono text-cyan-600 dark:text-cyan-400 font-semibold">{vehicle.battery_temp.toFixed(1)} °C</span>
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
              <Sliders className="w-3.5 h-3.5" />
              Tune in State Estimation Hub →
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
              Full Dataset Fleet Inventory ({vehicles.length.toLocaleString()} Real Vehicles)
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
              placeholder="Search across all 778 vehicles (e.g. DL1LAK7203, GJ05..., driver, hub)..."
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
              <option value="all">All Regional Hubs</option>
              <option value="Delhi">Delhi NCR Corridor</option>
              <option value="Ahmedabad">Ahmedabad Hubs</option>
              <option value="Surat">Surat Hubs</option>
              <option value="Vadodara">Vadodara Hubs</option>
              <option value="Rajkot">Rajkot Hubs</option>
              <option value="Mumbai">Mumbai Hubs</option>
              <option value="Pune">Pune Hubs</option>
              <option value="Bengaluru">Bengaluru Hubs</option>
              <option value="Chennai">Chennai Hubs</option>
            </select>
          </div>
        </div>

        {/* Paginated Vehicles Grid */}
        <div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 min-h-[300px]">
            {paginatedVehicles.map((v) => {
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
                    <span className="font-mono font-bold text-xs text-slate-900 dark:text-slate-100 truncate max-w-[110px]" title={v.id}>
                      {v.id}
                    </span>
                    <span
                      className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${
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
              No vehicles match "{searchQuery}". Type any custom chassis ID above and click <strong>"Lookup Chassis"</strong> to dynamically evaluate it!
            </div>
          )}
        </div>

        {/* Pagination Bar */}
        {filteredVehicles.length > PAGE_SIZE && (
          <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100 dark:border-slate-800 text-xs">
            <div className="text-slate-500 dark:text-slate-400 font-mono">
              Showing {(currentPage - 1) * PAGE_SIZE + 1}–{Math.min(currentPage * PAGE_SIZE, filteredVehicles.length)} of {filteredVehicles.length.toLocaleString()} matching vehicles
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 dark:hover:bg-slate-800 transition-all text-slate-700 dark:text-slate-300"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">
                Page {currentPage} of {totalPages}
              </span>

              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 dark:hover:bg-slate-800 transition-all text-slate-700 dark:text-slate-300"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </GlassCard>
    </div>
  );
};
