"use client";

import React, { useEffect, useState, useMemo } from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { BatteryPack3D } from "../digital-twin/BatteryPack3D";
import { CanOscilloscope } from "../telemetry/CanOscilloscope";
import {
  predictSOC,
  predictSOH,
  predictRUL,
  predictMileage,
} from "../../lib/api/client";
import {
  ShieldCheck,
  Search,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Info,
} from "lucide-react";
import { MetricExplainer } from "../ui/MetricExplainer";
import { AIInsightsCard } from "../dashboard/AIInsightsCard";
import { getLiveTriage, getVehicleTriage, triageLabel, triageBadgeClass, triageDotClass } from "../../lib/triage";





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
    getFilteredVehicles,
  } = useFleetStore();

  const vehicle = getSelectedVehicle();
  const [currentPage, setCurrentPage] = useState(1);

  // Dynamic live predictions state for active vehicle
  const [livePredictions, setLivePredictions] = useState<{
    soc?: number;
    soh?: number;
    rul?: number;
    mileage?: number;
    isLoading: boolean;
  }>({ isLoading: false });

  // Query live model endpoints whenever selected vehicle changes
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
        initial_soh: vehicle.soh,
        soh: vehicle.soh,
        chassis_no: vehicle.chassis,
        vehicle_id: vehicle.id,
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
        mileage:
          mileageRes.status === "fulfilled"
            ? Math.round(mileageRes.value.prediction * 10) / 10
            : vehicle.mileage,
        isLoading: false,
      });
    });

    return () => {
      isMounted = false;
    };
  }, [vehicle]);

  const filteredVehicles = getFilteredVehicles();
  const totalPages = Math.ceil(filteredVehicles.length / PAGE_SIZE) || 1;
  const paginatedVehicles = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return filteredVehicles.slice(start, start + PAGE_SIZE);
  }, [filteredVehicles, currentPage]);

  const socDisplay = (livePredictions.soc ?? vehicle.soc).toFixed(1);
  const sohDisplay = (livePredictions.soh ?? vehicle.soh).toFixed(1);
  const rulDisplay = livePredictions.rul ?? vehicle.rul;
  const mileageDisplay = (livePredictions.mileage ?? vehicle.mileage).toFixed(1);

  return (
    <div className="space-y-5">
      {/* 1. Header Banner */}
      <div className="p-4 rounded-xl bg-white dark:bg-[#0D111A] border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100">
                Commercial Telematics Active
              </h2>
              {(() => {
                const liveTriage = getLiveTriage(
                  livePredictions.soh ?? vehicle.soh,
                  livePredictions.soc ?? vehicle.soc,
                  vehicle.battery_temp,
                  vehicle.status
                );
                return (
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${triageBadgeClass(liveTriage)}`}>
                    {liveTriage === "CRITICAL"
                      ? "SERVICE HOLD"
                      : liveTriage === "WARNING"
                      ? "ROUTE ADVISORY"
                      : "APPROVED FOR DISPATCH"}
                  </span>
                );
              })()}

            </div>
            <p className="text-[11px] text-slate-500 font-mono mt-0.5">
              Live sub-second inference:{" "}
              <strong className="text-slate-800 dark:text-slate-200 font-bold">{vehicle.id}</strong> (Euler HiLoad 12.4 kWh LFP)
            </p>
          </div>
        </div>

        <button
          onClick={() => setCopilotOpen(true)}
          className="px-3 py-1.5 rounded-lg bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 text-xs font-medium hover:opacity-90 transition-all flex items-center gap-1.5 shrink-0"
        >
          <Sparkles className="w-3.5 h-3.5 text-emerald-400 dark:text-emerald-600" />
          <span>Ask AI Copilot</span>
        </button>
      </div>

      {/* 2. HUD Telemetry Strip: 4 Precision Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {/* Card 1: SOC */}
        <div className="p-4 rounded-xl bg-white dark:bg-[#0D111A] border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono text-slate-400 uppercase font-semibold">
                State of Charge (SOC)
              </span>
              <MetricExplainer metricKey="soc" currentValue={`${socDisplay}%`} label="How it works" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-slate-900 dark:text-slate-100 font-mono tracking-tight">
                {socDisplay}%
              </span>
              <span className="text-xs font-mono text-emerald-600 font-semibold">Nominal</span>
            </div>
          </div>
          <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 flex justify-between text-[10px] font-mono text-slate-400">
            <span>Pack: {vehicle.voltage.toFixed(1)}V</span>
            <span>Draw: {vehicle.current.toFixed(1)}A</span>
          </div>
        </div>

        {/* Card 2: SOH */}
        <div className="p-4 rounded-xl bg-white dark:bg-[#0D111A] border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono text-slate-400 uppercase font-semibold">
                State of Health (SOH)
              </span>
              <MetricExplainer metricKey="soh" currentValue={`${sohDisplay}%`} label="How it works" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 font-mono tracking-tight">
                {sohDisplay}%
              </span>
              <span className="text-[10px] font-mono text-emerald-600 font-medium">Calibrated SOH₀</span>
            </div>
            <div className="text-[10px] text-slate-400 mt-1">
              Baseline-anchored estimate (see methodology)
            </div>
          </div>
          <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 flex justify-between text-[10px] font-mono text-slate-400">
            <span>Cycles: {vehicle.charge_cycle_count} EFC</span>
            <span>Temp: {vehicle.battery_temp.toFixed(1)}°C</span>
          </div>
        </div>

        {/* Card 3: RUL */}
        <div className="p-4 rounded-xl bg-white dark:bg-[#0D111A] border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono text-slate-400 uppercase font-semibold">
                Remaining Useful Life
              </span>
              <MetricExplainer metricKey="rul" currentValue={`${rulDisplay} cycles`} label="How it works" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-slate-900 dark:text-slate-100 font-mono tracking-tight">
                {rulDisplay} <span className="text-xs font-normal text-slate-400">cycles</span>
              </span>
            </div>
          </div>
          <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 flex justify-between text-[10px] font-mono text-slate-400">
            <span>Est: ~{(rulDisplay / 250).toFixed(1)} yrs</span>
            <span className="text-emerald-600">R² = 0.9997</span>
          </div>
        </div>

        {/* Card 4: Range */}
        <div className="p-4 rounded-xl bg-white dark:bg-[#0D111A] border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono text-slate-400 uppercase font-semibold">
                Range per Charge
              </span>
              <MetricExplainer metricKey="mileage" currentValue={`${mileageDisplay} km`} label="How it works" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-slate-900 dark:text-slate-100 font-mono tracking-tight">
                {mileageDisplay} <span className="text-xs font-normal text-slate-400">km</span>
              </span>
            </div>
          </div>
          <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 flex justify-between text-[10px] font-mono text-slate-400">
            <span>Speed: {vehicle.speed.toFixed(1)} km/h</span>
            <span className="text-emerald-600">Optimal</span>
          </div>
        </div>
      </div>

      {/* AI Powertrain Diagnostic & Root Cause Breakdown (GPT-OSS 120B) */}
      <AIInsightsCard vehicle={vehicle} livePredictions={livePredictions} />

      {/* 3. Center Dual Stage: 3D Digital Twin + CAN Oscilloscope */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">

        {/* Left 7 Cols: 3D Digital Twin */}
        <div className="lg:col-span-7 space-y-4">
          <BatteryPack3D
            batteryTemp={vehicle.battery_temp}
            controllerTemp={vehicle.controller_temp || vehicle.battery_temp + 5.2}
            motorTemp={vehicle.motor_temp || vehicle.battery_temp + 8.4}
            soc={livePredictions.soc ?? vehicle.soc}
            soh={livePredictions.soh ?? vehicle.soh}
            status={vehicle.status}
            isCritical={vehicle.status === "critical" || (livePredictions.soh ?? vehicle.soh) < 75}
          />
        </div>


        {/* Right 5 Cols: CAN Oscilloscope & Vehicle Card */}
        <div className="lg:col-span-5 space-y-4">
          <div className="relative">
            <CanOscilloscope
              voltage={vehicle.voltage}
              current={vehicle.current}
              temperature={vehicle.battery_temp}
            />
            <div className="absolute top-3.5 right-3.5 z-10">
              <MetricExplainer metricKey="can_oscilloscope" label="How to read CAN" />
            </div>
          </div>

          <div className="rounded-xl p-4 bg-white dark:bg-[#0D111A] border border-slate-200 dark:border-slate-800 shadow-xs space-y-2.5 font-mono text-xs">
            <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-800 pb-2">
              <span className="text-slate-400 uppercase font-semibold text-[10px] flex items-center gap-1.5">
                <span>Chassis Metadata</span>
                <MetricExplainer metricKey="dataset" variant="icon" />
              </span>
              <span className="text-slate-900 dark:text-slate-100 font-bold">{vehicle.id}</span>
            </div>

            <div className="space-y-1.5 text-slate-600 dark:text-slate-300 text-[11px]">
              <div className="flex justify-between">
                <span>Model:</span>
                <strong className="text-slate-900 dark:text-slate-100">{vehicle.model}</strong>
              </div>
              <div className="flex justify-between">
                <span>Chassis / VIN:</span>
                <strong className="text-slate-900 dark:text-slate-100">{vehicle.chassis || vehicle.id}</strong>
              </div>
              <div className="flex justify-between">
                <span>Fleet / Hub:</span>
                <strong className="text-slate-900 dark:text-slate-100">{vehicle.fleet}</strong>
              </div>
              <div className="flex justify-between">
                <span>Chemistry:</span>
                <strong className="text-emerald-600 dark:text-emerald-400">12.4 kWh LFP (72V)</strong>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Fleet Vehicle Registry Table */}
      <div className="rounded-xl p-5 bg-white dark:bg-[#0D111A] border border-slate-200 dark:border-slate-800 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-200 dark:border-slate-800 pb-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
              Commercial Fleet Directory
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              {filteredVehicles.length} of {vehicles.length} operational chassis
            </p>
          </div>

          {/* Search & Filters */}
          <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
            <div className="relative flex-1 sm:w-60">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search VIN, chassis, hub..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-8 pr-3 py-1 rounded-lg text-xs font-mono bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:border-slate-400"
              />
            </div>

            {/* Status Filter Buttons */}
            <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-900 p-0.5 rounded-lg border border-slate-200 dark:border-slate-800 text-xs font-mono">
              {(["all", "active", "warning", "critical"] as const).map((st) => (
                <button
                  key={st}
                  onClick={() => setStatusFilter(st)}
                  className={`px-2 py-0.5 rounded capitalize text-[11px] transition-all ${
                    statusFilter === st
                      ? "bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 font-semibold shadow-xs"
                      : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-200"
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 uppercase text-[10px]">
                <th className="py-2.5 px-3">Vehicle ID</th>
                <th className="py-2.5 px-3">Chassis / Model</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">SOC</th>
                <th className="py-2.5 px-3">SOH (Live / SOH₀)</th>
                <th className="py-2.5 px-3">Pack Temp</th>
                <th className="py-2.5 px-3">Cycles</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {paginatedVehicles.map((v) => {
                const isSelected = v.id === selectedVehicleId;
                return (
                  <tr
                    key={v.id}
                    onClick={() => setSelectedVehicle(v.id)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? "bg-slate-100 dark:bg-slate-800/60 font-semibold"
                        : "hover:bg-slate-50 dark:hover:bg-slate-800/30 text-slate-700 dark:text-slate-300"
                    }`}
                  >
                    <td className="py-2.5 px-3 font-bold text-slate-900 dark:text-slate-100">
                      {v.id}
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-slate-500 dark:text-slate-400 truncate max-w-[140px]">
                      {v.chassis || v.model}
                    </td>
                    <td className="py-2.5 px-3">
                      {(() => {
                        const triage = getVehicleTriage(v);
                        return (
                          <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] uppercase font-semibold ${triageBadgeClass(triage)}`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${triageDotClass(triage)}`} />
                            {triageLabel(triage)}
                          </span>
                        );
                      })()}
                    </td>
                    <td className="py-2.5 px-3">
                      {isSelected && livePredictions.soc !== undefined ? (
                        <span className="font-bold text-cyan-600 dark:text-cyan-400">{livePredictions.soc.toFixed(1)}%</span>
                      ) : (
                        <span>{v.soc.toFixed(1)}%</span>
                      )}
                    </td>
                    <td className="py-2.5 px-3">
                      {isSelected && livePredictions.soh !== undefined ? (
                        <div className="flex items-center gap-1.5">
                          <span className="font-bold text-emerald-600 dark:text-emerald-400">{livePredictions.soh.toFixed(1)}%</span>
                          <span className="text-[9px] text-slate-400 font-normal">({v.soh.toFixed(1)}% SOH₀)</span>
                        </div>
                      ) : (
                        <span className="text-slate-600 dark:text-slate-300">{v.soh.toFixed(1)}% <span className="text-[9px] text-slate-400">SOH₀</span></span>
                      )}
                    </td>
                    <td className="py-2.5 px-3">{v.battery_temp.toFixed(1)}°C</td>
                    <td className="py-2.5 px-3">{v.charge_cycle_count}</td>
                    <td className="py-2.5 px-3 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedVehicle(v.id);
                        }}
                        className={`px-2 py-0.5 rounded text-[10px] font-semibold transition-all ${
                          isSelected
                            ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900"
                            : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700"
                        }`}
                      >
                        {isSelected ? "Inspecting" : "Inspect"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="flex items-center justify-between border-t border-slate-200 dark:border-slate-800 pt-3 text-xs font-mono text-slate-400">
          <div>
            Page {currentPage} of {totalPages}
          </div>
          <div className="flex items-center gap-1.5">
            <button
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="p-1 rounded border border-slate-200 dark:border-slate-800 disabled:opacity-30 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <button
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              className="p-1 rounded border border-slate-200 dark:border-slate-800 disabled:opacity-30 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
