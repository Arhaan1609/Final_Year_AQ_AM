"use client";

import React, { useState, useEffect } from "react";
import {
  predictSOC,
  predictSOH,
  predictThermal,
  predictDriverBehavior,
  predictKneePoint,
} from "../../lib/api/client";
import { Badge } from "../ui/Badge";
import { CyberBatteryCanvas } from "./CyberBatteryCanvas";
import { TiltCard } from "../ui/TiltCard";
import { MetricExplainer } from "../ui/MetricExplainer";
import {
  Sliders,
  RefreshCw,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  FlameKindling,
  BookOpen,
  Info,
} from "lucide-react";

export const LiveModelSandbox: React.FC = () => {
  // Telemetry Input Sliders
  const [voltage, setVoltage] = useState(76.2);
  const [temp, setTemp] = useState(31.5);
  const [current, setCurrent] = useState(-18.0);
  const [harshEvents, setHarshEvents] = useState(1);
  const [cycleCount, setCycleCount] = useState(210);
  const [activeScenario, setActiveScenario] = useState<string>("nominal");

  // Predictions State
  const [socVal, setSocVal] = useState<number>(95.8);
  const [sohVal, setSohVal] = useState<number>(99.2);
  const [thermalStatus, setThermalStatus] = useState<string>("SAFE (Benign)");
  const [thermalRisk, setThermalRisk] = useState<number>(0.0);
  const [driverAI, setDriverAI] = useState<number>(0.28);
  const [kneeCycles, setKneeCycles] = useState<number>(850);
  const [isInferencing, setIsInferencing] = useState<boolean>(false);

  // Trigger live ML inference whenever slider inputs change
  useEffect(() => {
    let active = true;
    setIsInferencing(true);

    const debounceTimer = setTimeout(() => {
      Promise.allSettled([
        // 1. SOC via KNN
        predictSOC({
          battery_voltage: voltage,
          battery_temp: temp,
          battery_current: current,
          abs_current: Math.abs(current),
          odometer: cycleCount * 58,
        }),
        // 2. SOH via XGBoost
        predictSOH({
          battery_voltage: voltage,
          battery_temp: temp,
          battery_current: current,
          charge_cycle_count: cycleCount,
          odometer: cycleCount * 58,
        }),
        // 3. Thermal Safety via Random Forest (200T)
        predictThermal({
          vbt: temp,
          vct: temp + 5.5,
          vmt: temp + 8.2,
          vbv: voltage,
          vbc: current,
          soc: socVal,
          speed: 34,
        }),
        // 4. Driver AI & BSI via BA-BMS Engine
        predictDriverBehavior({
          harsh_accel_count: harshEvents,
          harsh_brake_count: Math.max(0, harshEvents - 1),
          harsh_corner_count: 1,
          speed_variance: 25 + harshEvents * 5,
          avg_speed: 35,
          max_speed: 65,
          overspeed_count: harshEvents > 4 ? 2 : 0,
          battery_temp_max: temp,
          max_discharge_current: Math.abs(current),
          voltage_variance: 2.5,
          soc_drain_rate: 0.6,
        }),
        // 5. Knee Prognostics via XGBoost Booster
        predictKneePoint({
          charge_cycle_count: cycleCount,
          soh: sohVal,
          internal_resistance: 0.035 + cycleCount * 0.00003,
          capacity_loss_rate: 0.02 + harshEvents * 0.002,
          coulombic_efficiency: 0.99,
          avg_temp_charging: 30,
          max_temp_discharging: temp,
          temp_stress_score: 0.3,
          avg_c_rate_charge: 0.5,
          max_c_rate_discharge: 2.0,
          peak_current_events: harshEvents * 3,
          high_rate_fraction: 0.1,
          dod_mean: 75,
          dod_max: 90,
          high_dod_fraction: 0.25,
          time_at_high_soc: 4,
          time_at_low_soc: 1,
          resistance_growth_rate: 0.0001,
          soh_first_order_diff: -0.04,
          soh_second_order_diff: 0.001,
        }),
      ]).then(([socRes, sohRes, thermRes, driverRes, kneeRes]) => {
        if (!active) return;
        if (socRes.status === "fulfilled" && socRes.value?.prediction !== undefined) {
          setSocVal(socRes.value.prediction);
        }
        if (sohRes.status === "fulfilled" && sohRes.value?.prediction !== undefined) {
          setSohVal(sohRes.value.prediction);
        }
        if (thermRes.status === "fulfilled" && thermRes.value) {
          setThermalStatus(thermRes.value.safety_status ?? "SAFE (Benign)");
          setThermalRisk(thermRes.value.risk_probability ?? 0.0);
        }
        if (driverRes.status === "fulfilled" && driverRes.value) {
          const ai =
            (driverRes.value as any).aggressiveness_index ??
            (driverRes.value as any).driver_aggressiveness_index ??
            0.28;
          setDriverAI(typeof ai === "number" ? ai : 0.28);
        }
        if (kneeRes.status === "fulfilled" && kneeRes.value?.rul_to_knee_cycles !== undefined) {
          setKneeCycles(Math.round(kneeRes.value.rul_to_knee_cycles));
        }
        setIsInferencing(false);
      });
    }, 150);

    return () => {
      active = false;
      clearTimeout(debounceTimer);
    };
  }, [voltage, temp, current, harshEvents, cycleCount, socVal, sohVal]);

  const loadScenario = (scenario: "nominal" | "thermal" | "knee") => {
    setActiveScenario(scenario);
    if (scenario === "nominal") {
      setVoltage(76.5);
      setTemp(28.0);
      setCurrent(-18.0);
      setHarshEvents(1);
      setCycleCount(180);
    } else if (scenario === "thermal") {
      setVoltage(71.0);
      setTemp(53.5);
      setCurrent(-72.0);
      setHarshEvents(7);
      setCycleCount(520);
    } else if (scenario === "knee") {
      setVoltage(67.5);
      setTemp(42.0);
      setCurrent(-40.0);
      setHarshEvents(9);
      setCycleCount(1280);
    }
  };

  const isThermalWarning = temp > 45 || thermalRisk > 0.3;

  return (
    <section id="sandbox" className="py-24 sm:py-32 px-6 sm:px-10 max-w-7xl mx-auto">
      {/* Section Header */}
      <div className="text-center max-w-3xl mx-auto mb-10">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-50 dark:bg-cyan-950/60 border border-cyan-300 dark:border-cyan-700/60 text-cyan-700 dark:text-cyan-300 text-xs font-semibold mb-3 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-cyan-500" />
          <span>Interactive Telemetry &amp; 3D Model Sandbox</span>
        </div>
        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">
          Test Live Models in Real Time
        </h2>
        <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 mt-3 leading-relaxed">
          Select an examiner scenario or adjust CAN parameters below. 74 trained models execute live sub-10ms inference with real-time 3D thermal digital twin coupling.
        </p>

        {/* Unified 3-Pill Scenario Segmented Control */}
        <div className="mt-7 inline-flex items-center justify-center p-1.5 rounded-2xl bg-slate-100 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm gap-1 overflow-x-auto max-w-full">
          <button
            onClick={() => loadScenario("nominal")}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all whitespace-nowrap ${
              activeScenario === "nominal"
                ? "bg-emerald-600 text-white shadow-md shadow-emerald-500/20"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Scenario 1: Nominal (28°C)</span>
          </button>

          <button
            onClick={() => loadScenario("thermal")}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all whitespace-nowrap ${
              activeScenario === "thermal"
                ? "bg-amber-600 text-white shadow-md shadow-amber-500/20"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <FlameKindling className="w-3.5 h-3.5" />
            <span>Scenario 2: Thermal Stress (53.5°C)</span>
          </button>

          <button
            onClick={() => loadScenario("knee")}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all whitespace-nowrap ${
              activeScenario === "knee"
                ? "bg-purple-600 text-white shadow-md shadow-purple-500/20"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Scenario 3: Knee Degradation</span>
          </button>
        </div>
      </div>

      {/* Perfectly Aligned Command Center Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        {/* Left 5 Cols: Interactive Sliders Panel */}
        <div className="lg:col-span-5 app-card p-6 sm:p-7 bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-xl flex flex-col justify-between space-y-5">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3.5">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-cyan-100 dark:bg-cyan-950 text-cyan-600 dark:text-cyan-400 flex items-center justify-center font-bold shadow-sm">
                <Sliders className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">Telemetry Injector</h3>
                <p className="text-[11px] text-slate-500 font-mono">Dynamic CAN Telemetry (100ms)</p>
              </div>
            </div>
            {isInferencing && (
              <div className="flex items-center gap-1.5 text-[11px] font-mono text-emerald-500">
                <RefreshCw className="w-3 h-3 animate-spin" />
                <span>Inferencing...</span>
              </div>
            )}
          </div>

          {/* Slider 1: Battery Voltage */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-600 dark:text-slate-300">Pack Voltage (V):</span>
              <strong className="text-cyan-600 dark:text-cyan-400 font-bold">{voltage.toFixed(1)} V</strong>
            </div>
            <input
              type="range"
              min="60"
              max="84"
              step="0.5"
              value={voltage}
              onChange={(e) => setVoltage(parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>60V (Cut-off)</span>
              <span>76.8V (Nominal 24S)</span>
              <span>84.0V (Full OCV)</span>
            </div>
          </div>

          {/* Slider 2: Battery Temperature */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-600 dark:text-slate-300">Core Pack Temp (°C):</span>
              <strong
                className={
                  temp > 48
                    ? "text-red-500 font-bold animate-pulse"
                    : temp > 38
                    ? "text-amber-500 font-bold"
                    : "text-emerald-500 font-bold"
                }
              >
                {temp.toFixed(1)} °C
              </strong>
            </div>
            <input
              type="range"
              min="20"
              max="65"
              step="0.5"
              value={temp}
              onChange={(e) => setTemp(parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>20°C (Cold)</span>
              <span>35°C (Ambient)</span>
              <span>65°C (Thermal Stress)</span>
            </div>
          </div>

          {/* Slider 3: Discharge Current */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-600 dark:text-slate-300">Current Flow (A):</span>
              <strong className="text-purple-600 dark:text-purple-400 font-bold">{current.toFixed(1)} A</strong>
            </div>
            <input
              type="range"
              min="-100"
              max="40"
              step="1"
              value={current}
              onChange={(e) => setCurrent(parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>-100A (Max Draw)</span>
              <span>0A (Resting)</span>
              <span>+40A (Regen Brake)</span>
            </div>
          </div>

          {/* Slider 4: Harsh Driving Events */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-600 dark:text-slate-300">Harsh Maneuvers:</span>
              <strong className="text-amber-500 font-bold">{harshEvents} Events</strong>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="1"
              value={harshEvents}
              onChange={(e) => setHarshEvents(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>0 (Gentle Eco)</span>
              <span>5 (Aggressive)</span>
              <span>10 (Severe Strain)</span>
            </div>
          </div>

          {/* Slider 5: Charge Cycles */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-600 dark:text-slate-300">Cumulative Cycles:</span>
              <strong className="text-cyan-600 font-bold">{cycleCount} Cycles</strong>
            </div>
            <input
              type="range"
              min="0"
              max="1500"
              step="20"
              value={cycleCount}
              onChange={(e) => setCycleCount(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>0 Cycles (New)</span>
              <span>750 Cycles (Mid-Life)</span>
              <span>1500 Cycles (EoL)</span>
            </div>
          </div>
        </div>

        {/* Right 7 Cols: Live 3D Cybernetic Battery + AI Prediction Cards */}
        <div className="lg:col-span-7 flex flex-col justify-between space-y-4">
          {/* Live Reactive 3D Battery Pack Canvas */}
          <CyberBatteryCanvas
            temperature={temp}
            soc={socVal}
            current={current}
            isThermalWarning={isThermalWarning}
          />

          {/* 4 Multi-Module AI Model Responses in Balanced 2x2 Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 flex-1">
            {/* Card 1: Module A SOC */}
            <TiltCard glowColor="rgba(6, 182, 212, 0.2)" className="h-full">
              <div className="app-card p-4 sm:p-5 bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-md flex flex-col justify-between h-full group">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant="cyan" size="sm">Module A: SOC</Badge>
                    <MetricExplainer metricKey="soc" currentValue={`${socVal.toFixed(1)}%`} label="How it works" />
                  </div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400">State of Charge (Remaining Fuel)</div>
                  <div className="text-2xl sm:text-3xl font-extrabold text-cyan-600 dark:text-cyan-400 font-mono mt-1">
                    {socVal.toFixed(1)}%
                  </div>
                </div>
                <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[10px] font-mono text-slate-500">
                  <span>KNN Regressor</span>
                  <strong className="text-emerald-500">R² = 0.9958</strong>
                </div>
              </div>
            </TiltCard>

            {/* Card 2: Module A SOH */}
            <TiltCard glowColor="rgba(16, 185, 129, 0.2)" className="h-full">
              <div className="app-card p-4 sm:p-5 bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-md flex flex-col justify-between h-full group">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant="emerald" size="sm">Module A: SOH</Badge>
                    <MetricExplainer metricKey="soh" currentValue={`${sohVal.toFixed(1)}%`} label="How it works" />
                  </div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400">State of Health (Battery Life)</div>
                  <div className="text-2xl sm:text-3xl font-extrabold text-emerald-600 dark:text-emerald-400 font-mono mt-1">
                    {sohVal.toFixed(1)}%
                  </div>
                </div>
                <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[10px] font-mono text-slate-500">
                  <span>XGBoost 300T</span>
                  <strong className="text-emerald-500">{sohVal > 90 ? "Grade A" : "Degrading"}</strong>
                </div>
              </div>
            </TiltCard>

            {/* Card 3: Module B 3-Zone Thermal Safety */}
            <TiltCard glowColor={isThermalWarning ? "rgba(239, 68, 68, 0.25)" : "rgba(16, 185, 129, 0.2)"} className="h-full">
              <div
                className={`app-card p-4 sm:p-5 bg-white dark:bg-slate-900/90 border shadow-md flex flex-col justify-between h-full group ${
                  isThermalWarning
                    ? "border-amber-500/80 shadow-amber-500/10"
                    : "border-slate-200 dark:border-slate-800"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant={isThermalWarning ? "amber" : "emerald"} size="sm">Module B: Thermals</Badge>
                    <MetricExplainer metricKey="thermal" currentValue={thermalStatus} label="How it works" />
                  </div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400">3-Zone Heat Coupling (VBT/VCT/VMT)</div>
                  <div
                    className={`text-lg sm:text-xl font-extrabold font-mono mt-1 truncate ${
                      isThermalWarning ? "text-amber-500" : "text-emerald-500"
                    }`}
                  >
                    {thermalStatus}
                  </div>
                </div>
                <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[10px] font-mono text-slate-500">
                  <span>200-Tree RF</span>
                  <strong className={thermalRisk > 0.3 ? "text-amber-500" : "text-emerald-500"}>
                    Risk: {(thermalRisk * 100).toFixed(1)}%
                  </strong>
                </div>
              </div>
            </TiltCard>

            {/* Card 4: Module C Knee-Point Prognostics */}
            <TiltCard glowColor="rgba(139, 92, 246, 0.2)" className="h-full">
              <div className="app-card p-4 sm:p-5 bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-md flex flex-col justify-between h-full group">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant="purple" size="sm">Module C: Knee Point</Badge>
                    <MetricExplainer metricKey="knee" currentValue={`~${kneeCycles} cycles`} label="How it works" />
                  </div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400">Cycles Before Rapid Drop-off</div>
                  <div className="text-2xl sm:text-3xl font-extrabold text-purple-600 dark:text-purple-400 font-mono mt-1">
                    ~{kneeCycles} <span className="text-xs font-normal text-slate-400">cycles</span>
                  </div>
                </div>
                <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[10px] font-mono text-slate-500">
                  <span>28-Feat Booster</span>
                  <strong className={(driverAI ?? 0.28) > 0.6 ? "text-amber-500" : "text-cyan-500"}>
                    AI = {(driverAI ?? 0.28).toFixed(2)}
                  </strong>
                </div>
              </div>
            </TiltCard>
          </div>
        </div>
      </div>

      {/* Bottom Proof of Concept Navigation Banner */}
      <div className="mt-8 p-4 sm:p-6 rounded-2xl bg-gradient-to-r from-slate-900 to-slate-950 border border-slate-800 text-white flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-950/80 border border-cyan-800 flex items-center justify-center text-cyan-400">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-100">Scientific Verification &amp; Mathematical Proof</h4>
            <p className="text-xs text-slate-400">
              Inspect formulas, hyperparameters, and 778-vehicle dataset provenance for every feature
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <MetricExplainer metricKey="soc" label="SOC Proof" variant="button" />
          <MetricExplainer metricKey="soh" label="SOH Proof" variant="button" />
          <MetricExplainer metricKey="thermal" label="Thermal Proof" variant="button" />
          <MetricExplainer metricKey="knee" label="Knee Proof" variant="button" />
          <MetricExplainer metricKey="dataset" label="778 EV Dataset" variant="button" />
        </div>
      </div>
    </section>
  );
};

export default LiveModelSandbox;
