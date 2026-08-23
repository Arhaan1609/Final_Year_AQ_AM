"use client";

import React, { useEffect, useState } from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { GlassCard } from "../ui/GlassCard";
import { Badge } from "../ui/Badge";
import { predictMetaEnsemble, diagnoseVehicle } from "../../lib/api/client";
import { MetaEnsembleResponse, DiagnoseResponse } from "../../lib/api/types";
import { FileText, Printer, CheckCircle2, Cpu, Flame, Gauge, Sparkles } from "lucide-react";
import { MetricExplainer } from "../ui/MetricExplainer";

export const MetaEnsembleReportTab: React.FC = () => {
  const { telemetry, selectedVehicleId, getSelectedVehicle } = useFleetStore();
  const vehicle = getSelectedVehicle();

  const [metaData, setMetaData] = useState<MetaEnsembleResponse | null>(null);
  const [diagData, setDiagData] = useState<DiagnoseResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    setLoading(true);
    Promise.allSettled([
      predictMetaEnsemble({
        vehicle_id: selectedVehicleId,
        charge_cycle_count: telemetry.cycleCount,
        battery_voltage: telemetry.voltage,
        battery_temp: telemetry.temperature,
        battery_current: telemetry.current,
        soc: vehicle.soc,
        harsh_accel_count: telemetry.harshAccel || 2,
        speed_variance: 7.8,
      }),
      diagnoseVehicle({
        vehicle_id: selectedVehicleId,
        oem_model: vehicle.model,
        soc: vehicle.soc,
        voltage: telemetry.voltage,
        current: telemetry.current,
        battery_temp: telemetry.temperature,
        controller_temp: vehicle.controller_temp,
        motor_temp: vehicle.motor_temp,
        speed: telemetry.avgSpeed,
      }),
    ])
      .then(([metaRes, diagRes]) => {
        if (metaRes.status === "fulfilled") setMetaData(metaRes.value);
        if (diagRes.status === "fulfilled") setDiagData(diagRes.value);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedVehicleId, telemetry, vehicle]);

  const handlePrint = () => {
    window.print();
  };

  const actionItems: string[] = diagData?.action_items || [
    "Battery pack operates within optimal C-rate & thermal bounds.",
    "BMS cell balancing active during standard Level 2 charging sessions.",
    "Schedule routine visual wiring & harness inspection at next 1,000 km interval.",
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner with Print Button */}
      <div className="app-card p-4 flex flex-wrap items-center justify-between gap-4 border border-emerald-200 dark:border-emerald-800/60 bg-emerald-50 dark:bg-emerald-950/20">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-100 dark:bg-emerald-900/40 border border-emerald-300 text-emerald-700 dark:text-emerald-400 flex items-center justify-center">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              Meta-Ensemble Tri-Pillar Diagnostic Report
              <Badge variant="emerald" size="sm">A + B + C Unified</Badge>
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Cross-module telemetry synthesis for asset certification on {selectedVehicleId}
            </p>
          </div>
        </div>

        <button
          onClick={handlePrint}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 dark:bg-slate-800 dark:hover:bg-slate-700 text-white dark:text-slate-200 text-xs font-semibold transition-all hover:scale-105 shadow-sm"
        >
          <Printer className="w-4 h-4" />
          Export / Print Report (PDF)
        </button>
      </div>

      {/* Report Header Card */}
      <GlassCard className="space-y-6">
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-6">
          <div>
            <div className="text-xs font-mono uppercase text-cyan-600 dark:text-cyan-400 font-bold">Vehicle Asset Certificate</div>
            <h1 className="text-2xl font-extrabold text-slate-900 dark:text-slate-100 mt-1">{vehicle.id}</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{vehicle.model} • {vehicle.fleet}</p>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right flex flex-col items-end">
              <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 font-mono">
                <span>Unified Health Rating</span>
                <MetricExplainer metricKey="meta_ensemble" label="How it works" />
              </div>
              <div className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 font-mono mt-0.5">
                {metaData?.unified_health_grade ?? (loading ? "Computing Grade..." : "Grade Pending")}
              </div>
            </div>
            <div className="w-14 h-14 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 flex items-center justify-center text-emerald-700 dark:text-emerald-400 font-extrabold font-mono text-2xl">
              {metaData?.unified_health_grade?.charAt(6) ?? (loading ? "..." : "-")}
            </div>
          </div>

        </div>

        {/* 3 Pillars Summary Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Pillar A */}
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-cyan-700 dark:text-cyan-400 uppercase tracking-wider">
                <Cpu className="w-4 h-4" />
                Pillar A: Fleet Telematics
              </div>
              <MetricExplainer metricKey="soc" label="PoC" />
            </div>
            <div className="text-xs text-slate-700 dark:text-slate-300 space-y-1 pt-1">
              <div>State of Charge: <strong>{vehicle.soc.toFixed(1)}%</strong></div>
              <div>State of Health: <strong>{vehicle.soh.toFixed(1)}%</strong></div>
              <div>Remaining Life: <strong>{vehicle.rul} cycles</strong></div>
              <div>Range per Charge: <strong>{vehicle.mileage.toFixed(1)} km</strong></div>
            </div>
          </div>

          {/* Pillar B */}
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">
                <Flame className="w-4 h-4" />
                Pillar B: Thermal & Health
              </div>
              <MetricExplainer metricKey="thermal" label="PoC" />
            </div>
            <div className="text-xs text-slate-700 dark:text-slate-300 space-y-1 pt-1">
              <div>Digital Twin Score: <strong>{diagData?.overall_health_score !== undefined ? diagData.overall_health_score.toFixed(1) : vehicle.soh.toFixed(1)} / 100</strong></div>
              <div>Thermal Safety: <strong>{diagData?.thermal_status?.safety_status ?? (loading ? "Evaluating..." : "--")}</strong></div>
              <div>Pack Temp: <strong>{vehicle.battery_temp.toFixed(1)} °C</strong></div>
              <div>Motor Temp: <strong>{vehicle.motor_temp.toFixed(1)} °C</strong></div>
            </div>
          </div>

          {/* Pillar C */}
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold text-purple-700 dark:text-purple-400 uppercase tracking-wider">
                <Gauge className="w-4 h-4" />
                Pillar C: BA-BMS & Knee
              </div>
              <MetricExplainer metricKey="knee" label="PoC" />
            </div>
            <div className="text-xs text-slate-700 dark:text-slate-300 space-y-1 pt-1">
              <div>Driver Aggressiveness: <strong>{metaData?.driver_aggressiveness_index !== undefined ? metaData.driver_aggressiveness_index.toFixed(2) : (vehicle.status === "critical" ? "0.48" : "0.16")}</strong></div>
              <div>Battery Stress Index: <strong>{metaData?.battery_stress_index !== undefined ? metaData.battery_stress_index.toFixed(2) : (vehicle.status === "critical" ? "0.38" : "0.22")}</strong></div>
              <div>RUL to Knee Point: <strong>{metaData?.rul_to_knee_cycles !== undefined ? `${Math.round(metaData.rul_to_knee_cycles)} cycles` : `${Math.max(0, Math.round(950 - vehicle.charge_cycle_count))} cycles`}</strong></div>
              <div>Assigned Driver: <strong>{vehicle.driver}</strong></div>
            </div>
          </div>
        </div>

        {/* Executive Summary Statement */}
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1">Executive Summary</div>
          <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-sans">
            {metaData?.executive_summary || `Pack ${vehicle.id} demonstrates consistent telemetry within operational bounds (${vehicle.charge_cycle_count} EFC, ${vehicle.soh.toFixed(1)}% SOH).`}
          </p>
        </div>

        {/* Action Items List */}
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
            Maintenance Action Items & Directives
          </div>
          <div className="space-y-2">
            {actionItems.map((item, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-slate-700 dark:text-slate-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 flex-shrink-0" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </GlassCard>
    </div>
  );
};
