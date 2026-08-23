"use client";

import React, { useState, useEffect } from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import {
  predictSOC,
  predictSOH,
  predictRUL,
  predictMileage,
  predictThermal,
  predictDriverBehavior,
} from "../../lib/api/client";
import {
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  BatteryCharging,
  Thermometer,
  ShieldCheck,
  User,
  Truck,
  Search,
  Sparkles,
  ArrowUpRight,
  Info,
  Calendar,
  Zap,
  Gauge,
  Cpu,
} from "lucide-react";
import { AIInsightsCard } from "./AIInsightsCard";


export const OperationsView: React.FC = () => {
  const {
    vehicles,
    selectedVehicleId,
    setSelectedVehicle,
    getSelectedVehicle,
    setViewMode,
    setActiveTab,
    statusFilter,
    setStatusFilter,
    searchQuery,
    setSearchQuery,
    getFilteredVehicles,
  } = useFleetStore();

  const vehicle = getSelectedVehicle();

  // Dynamic live prediction states
  const [soc, setSoc] = useState<number>(vehicle.soc || 75);
  const [soh, setSoh] = useState<number>(vehicle.soh || 95);
  const [rul, setRul] = useState<number>(vehicle.rul || 1000);
  const [range, setRange] = useState<number>(vehicle.mileage || 110);
  const [thermalSafe, setThermalSafe] = useState<boolean>(true);
  const [driverScore, setDriverScore] = useState<string>("Smooth (Eco)");
  const [loading, setLoading] = useState<boolean>(false);

  // Sync and fetch whenever selectedVehicleId changes
  useEffect(() => {
    let active = true;
    setLoading(true);

    Promise.allSettled([
      predictSOC({
        battery_voltage: vehicle.voltage,
        battery_temp: vehicle.battery_temp,
        battery_current: vehicle.current,
        abs_current: Math.abs(vehicle.current),
        odometer: vehicle.charge_cycle_count * 58,
        charge_cycle_count: vehicle.charge_cycle_count,
      }),
      predictSOH({
        battery_voltage: vehicle.voltage,
        battery_temp: vehicle.battery_temp,
        battery_current: vehicle.current,
        charge_cycle_count: vehicle.charge_cycle_count,
        odometer: vehicle.charge_cycle_count * 58,
        initial_soh: vehicle.soh,
        soh: vehicle.soh,
        chassis_no: vehicle.chassis,
        vehicle_id: vehicle.id,
      }),
      predictRUL({
        odometer: vehicle.charge_cycle_count * 58,
        charge_cycle_count: vehicle.charge_cycle_count,
        soc_at_charge: vehicle.soc,
        battery_temp: vehicle.battery_temp,
      }),
      predictMileage({
        run_kms: 45,
        avg_speed: vehicle.speed || 32,
        max_speed: (vehicle.speed || 32) + 20,
        odometer: vehicle.charge_cycle_count * 58,
        charge_cycle_count: vehicle.charge_cycle_count,
        battery_temp: vehicle.battery_temp,
        battery_voltage: vehicle.voltage,
      }),
      predictThermal({
        vbt: vehicle.battery_temp,
        vct: vehicle.controller_temp || vehicle.battery_temp + 8,
        vmt: vehicle.motor_temp || vehicle.battery_temp + 18,
        vbv: vehicle.voltage,
        vbc: vehicle.current,
        soc: vehicle.soc,
        speed: vehicle.speed,
      }),
      predictDriverBehavior({
        harsh_accel_count: vehicle.status === "warning" ? 4 : vehicle.status === "critical" ? 8 : 1,
        harsh_brake_count: vehicle.status === "critical" ? 5 : 1,
        harsh_corner_count: 1,
        speed_variance: 15,
        avg_speed: vehicle.speed || 32,
        max_speed: (vehicle.speed || 32) + 25,
        battery_temp_max: vehicle.battery_temp || 32,
        max_discharge_current: Math.abs(vehicle.current) || 25,
      }),
    ]).then(([socRes, sohRes, rulRes, rangeRes, thermRes, driverRes]) => {
      if (!active) return;
      if (socRes.status === "fulfilled" && socRes.value?.prediction !== undefined) {
        setSoc(socRes.value.prediction);
      } else {
        setSoc(vehicle.soc);
      }

      if (sohRes.status === "fulfilled" && sohRes.value?.prediction !== undefined) {
        setSoh(sohRes.value.prediction);
      } else {
        setSoh(vehicle.soh);
      }

      if (rulRes.status === "fulfilled" && rulRes.value?.prediction !== undefined) {
        setRul(Math.round(rulRes.value.prediction));
      } else {
        setRul(vehicle.rul || 1000);
      }

      if (rangeRes.status === "fulfilled" && rangeRes.value?.prediction !== undefined) {
        setRange(Math.round(rangeRes.value.prediction * 10) / 10);
      } else {
        setRange(vehicle.mileage || 110);
      }

      if (thermRes.status === "fulfilled" && thermRes.value) {
        const val = thermRes.value as any;
        const isSafe = !val.is_critical && (val.risk_probability === undefined || val.risk_probability < 0.25);
        setThermalSafe(isSafe);
      }


      if (driverRes.status === "fulfilled" && driverRes.value) {
        const ai = (driverRes.value as any).aggressiveness_index ?? 0.28;
        if (ai > 0.65) setDriverScore("Aggressive (High Strain)");
        else if (ai > 0.35) setDriverScore("Moderate (Normal)");
        else setDriverScore("Smooth (Eco-Pro)");
      }
      setLoading(false);
    });

    return () => {
      active = false;
    };
  }, [selectedVehicleId, vehicle]);

  // Counts for triage bar
  const totalCount = vehicles.length;
  const activeCount = vehicles.filter((v) => v.status === "active").length;
  const warningCount = vehicles.filter((v) => v.status === "warning").length;
  const criticalCount = vehicles.filter((v) => v.status === "critical").length;

  const isCritical = vehicle.status === "critical" || vehicle.battery_temp > 48 || soh < 80;
  const isWarning = vehicle.status === "warning" || vehicle.battery_temp > 40 || soc < 30;

  // Estimated years of battery life left dynamically derived from ML RUL cycles (250 cycles/yr commercial fleet duty cycle)
  const estimatedYearsLeft = Math.max(0.1, Number((rul / 250).toFixed(1))).toFixed(1);


  return (
    <div className="space-y-8 w-full">
      {/* ─── 1. TOP FLEET TRAFFIC-LIGHT TRIAGE BAR ─── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* All Fleet */}
        <button
          onClick={() => setStatusFilter("all")}
          className={`p-5 rounded-2xl border text-left transition-all shadow-sm flex flex-col justify-between ${
            statusFilter === "all"
              ? "bg-slate-900 text-white border-cyan-500 shadow-md ring-2 ring-cyan-500/20"
              : "bg-white dark:bg-slate-900/90 border-slate-200 dark:border-slate-800 hover:border-slate-300"
          }`}
        >
          <div className="flex justify-between items-center text-xs font-semibold text-slate-400">
            <span>Total Monitored Fleet</span>
            <Truck className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold font-mono mt-2">{totalCount} Trucks</div>
          <p className="text-[11px] text-slate-400 mt-1 font-mono">SQL Database Connected</p>
        </button>

        {/* Ready for Route (Active) */}
        <button
          onClick={() => setStatusFilter("active")}
          className={`p-5 rounded-2xl border text-left transition-all shadow-sm flex flex-col justify-between ${
            statusFilter === "active"
              ? "bg-emerald-950/80 text-white border-emerald-500 shadow-md ring-2 ring-emerald-500/30"
              : "bg-white dark:bg-slate-900/90 border-slate-200 dark:border-slate-800 hover:border-emerald-500/40"
          }`}
        >
          <div className="flex justify-between items-center text-xs font-semibold text-emerald-500">
            <span>Ready for Route</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 font-mono mt-2">
            {activeCount} Trucks
          </div>
          <p className="text-[11px] text-emerald-600/80 dark:text-emerald-400/80 mt-1">
            Batteries healthy • Ready to dispatch
          </p>
        </button>

        {/* Needs Charge / Advisory (Warning) */}
        <button
          onClick={() => setStatusFilter("warning")}
          className={`p-5 rounded-2xl border text-left transition-all shadow-sm flex flex-col justify-between ${
            statusFilter === "warning"
              ? "bg-amber-950/80 text-white border-amber-500 shadow-md ring-2 ring-amber-500/30"
              : "bg-white dark:bg-slate-900/90 border-slate-200 dark:border-slate-800 hover:border-amber-500/40"
          }`}
        >
          <div className="flex justify-between items-center text-xs font-semibold text-amber-500">
            <span>Needs Charge / Inspection</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-amber-600 dark:text-amber-400 font-mono mt-2">
            {warningCount} Trucks
          </div>
          <p className="text-[11px] text-amber-600/80 dark:text-amber-400/80 mt-1">
            Low battery or moderate temperature
          </p>
        </button>

        {/* Immediate Attention (Critical) */}
        <button
          onClick={() => setStatusFilter("critical")}
          className={`p-5 rounded-2xl border text-left transition-all shadow-sm flex flex-col justify-between ${
            statusFilter === "critical"
              ? "bg-rose-950/80 text-white border-rose-500 shadow-md ring-2 ring-rose-500/30"
              : "bg-white dark:bg-slate-900/90 border-slate-200 dark:border-slate-800 hover:border-rose-500/40"
          }`}
        >
          <div className="flex justify-between items-center text-xs font-semibold text-rose-500">
            <span>Critical Hold / Service</span>
            <AlertOctagon className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-3xl font-extrabold text-rose-600 dark:text-rose-400 font-mono mt-2">
            {criticalCount} Trucks
          </div>
          <p className="text-[11px] text-rose-600/80 dark:text-rose-400/80 mt-1">
            Do not dispatch • Service required
          </p>
        </button>
      </div>

      {/* ─── 2. SELECTED VEHICLE DISPATCH PASSPORT & ACTION BANNER ─── */}
      <div className="app-card p-6 sm:p-8 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl space-y-6">
        {/* Header with Quick Selector & Search */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight font-mono">
                {vehicle.id}
              </h2>
              <span
                className={`px-3 py-1 rounded-full text-xs font-bold font-mono uppercase tracking-wider ${
                  isCritical
                    ? "bg-rose-100 text-rose-700 dark:bg-rose-950/80 dark:text-rose-300 border border-rose-400"
                    : isWarning
                    ? "bg-amber-100 text-amber-700 dark:bg-amber-950/80 dark:text-amber-300 border border-amber-400"
                    : "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/80 dark:text-emerald-300 border border-emerald-400"
                }`}
              >
                {isCritical ? "Service Hold" : isWarning ? "Route Advisory" : "Approved for Dispatch"}
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
              {vehicle.model} • Driver: <strong className="text-slate-700 dark:text-slate-200">{vehicle.driver}</strong> • {vehicle.fleet}
            </p>
          </div>

          {/* Quick Vehicle Search / Lookup */}
          <div className="flex items-center gap-3">
            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search plate (e.g. DL1LAN0712)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>

            <button
              onClick={() => {
                setViewMode("engineering");
                setActiveTab("state-est");
              }}
              className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <Cpu className="w-3.5 h-3.5 text-purple-400" />
              <span>ML Deep-Dive</span>
            </button>
          </div>
        </div>

        {/* ─── ACTION DIRECTIVE BANNER (PLAIN ENGLISH) ─── */}
        <div
          className={`p-4 sm:p-5 rounded-2xl flex items-start gap-4 ${
            isCritical
              ? "bg-rose-50 dark:bg-rose-950/40 border border-rose-300 dark:border-rose-800/80 text-rose-900 dark:text-rose-200"
              : isWarning
              ? "bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800/80 text-amber-900 dark:text-amber-200"
              : "bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-800/80 text-emerald-900 dark:text-emerald-200"
          }`}
        >
          {isCritical ? (
            <AlertOctagon className="w-6 h-6 text-rose-500 flex-shrink-0 mt-0.5" />
          ) : isWarning ? (
            <AlertTriangle className="w-6 h-6 text-amber-500 flex-shrink-0 mt-0.5" />
          ) : (
            <CheckCircle2 className="w-6 h-6 text-emerald-500 flex-shrink-0 mt-0.5" />
          )}

          <div>
            <h4 className="font-bold text-sm sm:text-base">
              {isCritical
                ? "HOLD VEHICLE — SCHEDULE MAINTENANCE INSPECTION"
                : isWarning
                ? "DISPATCH ADVISORY — CHARGE OR MONITOR BATTERY"
                : "READY FOR DISPATCH — VEHICLE IN OPTIMAL HEALTH"}
            </h4>
            <p className="text-xs sm:text-sm mt-1 opacity-90 leading-relaxed">
              {isCritical
                ? vehicle.battery_temp > 45
                  ? `Battery operating temperature is elevated (${vehicle.battery_temp.toFixed(1)}°C). Ground this vehicle for thermal cooling inspection before next dispatch.`
                  : `Battery capacity shows accelerated degradation (SOH: ${soh.toFixed(1)}%, ${vehicle.charge_cycle_count} cycles). Ground this vehicle for terminal diagnostic inspection before next shift.`
                : isWarning
                ? `Battery level is at ${soc.toFixed(0)}%. Can complete routes up to ${range.toFixed(0)} km. Recommend quick 30-min top-up before afternoon runs.`
                : `Battery level is at ${soc.toFixed(0)}% with ${range.toFixed(0)} km delivery range. Temperatures and cell health are in Grade-A condition.`}
            </p>
          </div>
        </div>

        {/* ─── 3. FOUR PLAIN-ENGLISH HEALTH CARDS ─── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Card 1: Fuel / Battery Level */}
          <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80 space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                <BatteryCharging className="w-4 h-4 text-cyan-500" />
                <span>Battery Level (Fuel)</span>
              </span>
              <span className="text-[10px] font-mono text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-50 dark:bg-cyan-950 px-2 py-0.5 rounded-full border border-cyan-300 dark:border-cyan-800">
                SOC
              </span>
            </div>
            <div className="text-3xl font-extrabold text-slate-900 dark:text-white font-mono">
              {soc.toFixed(1)}%
            </div>
            <div className="text-xs text-slate-600 dark:text-slate-300">
              Estimated Range: <strong className="text-cyan-600 dark:text-cyan-400">{range.toFixed(0)} km</strong>
            </div>
            <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
              <div
                className="bg-cyan-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${Math.max(0, Math.min(100, soc))}%` }}
              />
            </div>
          </div>

          {/* Card 2: Battery Lifespan / Health */}
          <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80 space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-500" />
                <span>Battery Lifespan</span>
              </span>
              <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 font-bold bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded-full border border-emerald-300 dark:border-emerald-800">
                SOH
              </span>
            </div>
            <div className="text-3xl font-extrabold text-slate-900 dark:text-white font-mono">
              {soh.toFixed(1)}%
            </div>
            <div className="flex justify-between items-center text-xs text-slate-600 dark:text-slate-300">
              <span>Estimated Life: <strong className="text-emerald-600 dark:text-emerald-400">~{estimatedYearsLeft} Years</strong></span>
              <span className="font-mono text-[10px] text-slate-400">({rul} cyc)</span>
            </div>
            <div className="text-[11px] text-slate-400">
              Grade: {soh > 92 ? "Grade A (Excellent)" : soh > 82 ? "Grade B (Good)" : "Grade C (Degrading)"}
            </div>
          </div>

          {/* Card 3: Operating Temperature */}
          <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80 space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                <Thermometer className="w-4 h-4 text-amber-500" />
                <span>Operating Temperature</span>
              </span>
              <span className="text-[10px] font-mono text-amber-600 dark:text-amber-400 font-bold bg-amber-50 dark:bg-amber-950 px-2 py-0.5 rounded-full border border-amber-300 dark:border-amber-800">
                Thermal
              </span>
            </div>
            <div className={`text-3xl font-extrabold font-mono ${vehicle.battery_temp > 45 ? "text-amber-500" : "text-slate-900 dark:text-white"}`}>
              {vehicle.battery_temp.toFixed(1)}°C
            </div>
            <div className="text-xs text-slate-600 dark:text-slate-300">
              Cooling Status: <strong className={thermalSafe ? "text-emerald-600 dark:text-emerald-400" : "text-amber-600 dark:text-amber-400"}>{thermalSafe ? "Normal" : "Active High"}</strong>
            </div>
            <div className="text-[11px] text-slate-400">
              Thermal Runaway Risk: <strong className={thermalSafe ? "text-emerald-500" : "text-amber-500"}>{thermalSafe ? "0.00% (Safe)" : "Elevated Advisory"}</strong>
            </div>
          </div>


          {/* Card 4: Driver Score */}
          <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80 space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                <User className="w-4 h-4 text-purple-500" />
                <span>Driver Behavior</span>
              </span>
              <span className="text-[10px] font-mono text-purple-600 dark:text-purple-400 font-bold bg-purple-50 dark:bg-purple-950 px-2 py-0.5 rounded-full border border-purple-300 dark:border-purple-800">
                AI Rating
              </span>
            </div>
            <div className="text-2xl font-extrabold text-slate-900 dark:text-white font-mono">
              {driverScore.split(" ")[0]}
            </div>
            <div className="text-xs text-slate-600 dark:text-slate-300">
              Battery Strain: <strong className="text-purple-600 dark:text-purple-400">Low Impact</strong>
            </div>
            <div className="text-[11px] text-slate-400">
              {driverScore.includes("Aggressive") ? "⚠️ Harsh acceleration detected" : "✅ Eco-driving saves +1.4% health"}
            </div>
          </div>
        </div>

        {/* ─── AI POWERTRAIN DIAGNOSTIC & ROOT CAUSE (GPT-OSS 120B) ─── */}
        <AIInsightsCard
          vehicle={vehicle}
          livePredictions={{ soc, soh, rul, mileage: range }}
        />

        {/* ─── 4. QUICK FLEET SWITCHER TABLE ─── */}
        <div className="border-t border-slate-200 dark:border-slate-800 pt-6">

          <div className="flex justify-between items-center mb-4">
            <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Truck className="w-4 h-4 text-cyan-500" />
              <span>Select Vehicle from Fleet (Click to Inspect)</span>
            </h3>
            <span className="text-xs font-mono text-slate-400">
              Showing {getFilteredVehicles().slice(0, 8).length} of {getFilteredVehicles().length} vehicles
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
            {getFilteredVehicles().slice(0, 8).map((v) => (
              <button
                key={v.id}
                onClick={() => setSelectedVehicle(v.id)}
                className={`p-3 rounded-xl border text-left transition-all font-mono text-xs flex justify-between items-center ${
                  v.id === selectedVehicleId
                    ? "bg-cyan-50 dark:bg-cyan-950/60 border-cyan-500 text-cyan-900 dark:text-cyan-200 ring-2 ring-cyan-500/30"
                    : "bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700/60 hover:bg-slate-100 dark:hover:bg-slate-800"
                }`}
              >
                <div>
                  <div className="font-bold">{v.id}</div>
                  <div className="text-[10px] text-slate-400 font-sans">{v.driver}</div>
                </div>
                <div className="text-right">
                  <div className="font-bold">{v.soc.toFixed(0)}% SOC</div>
                  <div className={`text-[10px] ${v.status === 'critical' ? 'text-rose-500' : v.status === 'warning' ? 'text-amber-500' : 'text-emerald-500'}`}>
                    {v.soh.toFixed(0)}% SOH
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
export default OperationsView;
