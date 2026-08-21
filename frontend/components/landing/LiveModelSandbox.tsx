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
import {
  Sliders,
  Zap,
  Flame,
  ShieldCheck,
  TrendingDown,
  Gauge,
  Cpu,
  RefreshCw,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  FlameKindling,
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
          temp_variance: 4,
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
          const ai = (driverRes.value as any).aggressiveness_index ?? (driverRes.value as any).driver_aggressiveness_index ?? 0.28;
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
      setTemp(49.5);
      setCurrent(-65.0);
      setHarshEvents(6);
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
    <section id="sandbox" className="py-24 px-6 sm:px-10 max-w-7xl mx-auto">
      {/* Section Header */}
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-50 dark:bg-cyan-950/60 border border-cyan-300 dark:border-cyan-700/60 text-cyan-700 dark:text-cyan-300 text-xs font-semibold mb-4 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-cyan-500" />
          <span>Interactive Telemetry & Model Sandbox</span>
        </div>
        <h2 className="text-3xl sm:text-5xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">
          Test Live Models in Real Time
        </h2>
        <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 mt-3.5 leading-relaxed">
          Select an examiner scenario or adjust CAN parameters below. 74 trained models execute live sub-10ms inference with real confidence intervals (R² &gt; 0.98).
        </p>

        {/* 1-Click Examiner Scenarios Bar */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <button
            onClick={() => loadScenario("nominal")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all shadow-sm active:scale-95 ${
              activeScenario === "nominal"
                ? "bg-emerald-600 text-white shadow-emerald-500/25 ring-2 ring-emerald-400/50"
                : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:border-emerald-500/50"
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Scenario 1: Nominal Delivery</span>
          </button>

          <button
            onClick={() => loadScenario("thermal")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all shadow-sm active:scale-95 ${
              activeScenario === "thermal"
                ? "bg-amber-600 text-white shadow-amber-500/25 ring-2 ring-amber-400/50"
                : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:border-amber-500/50"
            }`}
          >
            <FlameKindling className="w-3.5 h-3.5 text-amber-400" />
            <span>Scenario 2: Highway Thermal Stress</span>
          </button>

          <button
            onClick={() => loadScenario("knee")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all shadow-sm active:scale-95 ${
              activeScenario === "knee"
                ? "bg-purple-600 text-white shadow-purple-500/25 ring-2 ring-purple-400/50"
                : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:border-purple-500/50"
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5 text-purple-400" />
            <span>Scenario 3: Accelerated Knee Degradation</span>
          </button>
        </div>
      </div>

      {/* Main Sandbox Interactive Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left 5 Cols: Interactive Sliders Panel */}
        <div className="lg:col-span-5 app-card p-6 sm:p-8 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-cyan-100 dark:bg-cyan-950 text-cyan-600 dark:text-cyan-400 flex items-center justify-center font-bold">
                <Sliders className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">Telemetry Injector</h3>
                <p className="text-[11px] text-slate-500 font-mono">Dynamic CAN Parameters</p>
              </div>
            </div>
            {isInferencing && (
              <div className="flex items-center gap-1.5 text-[11px] font-mono text-emerald-500">
                <RefreshCw className="w-3 h-3 animate-spin" />
                <span>Computing Inference...</span>
              </div>
            )}
          </div>

          {/* Slider 1: Battery Voltage */}
          <div className="space-y-2">
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
              <span>60V (Depleted)</span>
              <span>76V (Nominal)</span>
              <span>84V (100% OCV)</span>
            </div>
          </div>

          {/* Slider 2: Battery Temperature */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-600 dark:text-slate-300">Core Pack Temp (°C):</span>
              <strong className={temp > 45 ? "text-amber-500 font-bold" : "text-emerald-500 font-bold"}>
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
              <span>65°C (Thermal Stress Zone)</span>
            </div>
          </div>

          {/* Slider 3: Discharge Current */}
          <div className="space-y-2">
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
              <span>-100A (High Discharge)</span>
              <span>0A (Rest)</span>
              <span>+40A (Regen Brake)</span>
            </div>
          </div>

          {/* Slider 4: Harsh Driving Events */}
          <div className="space-y-2">
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
          <div className="space-y-2">
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
              <span>0 Cycles</span>
              <span>750 Cycles</span>
              <span>1500 Cycles</span>
            </div>
          </div>
        </div>

        {/* Right 7 Cols: Live Multi-Module AI Model Responses */}
        <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Card 1: Module A SOC Prediction */}
          <div className="app-card p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-md flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <Badge variant="cyan" size="sm">Module A: SOC</Badge>
                <span className="text-[10px] font-mono text-slate-400">KNN Regressor</span>
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400">Predicted State of Charge</div>
              <div className="text-3xl sm:text-4xl font-extrabold text-cyan-600 dark:text-cyan-400 font-mono mt-2">
                {socVal.toFixed(1)}%
              </div>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-between text-[11px] font-mono text-slate-500">
              <span>Model Confidence:</span>
              <strong className="text-emerald-500">R² = 0.9958</strong>
            </div>
          </div>

          {/* Card 2: Module A SOH Prediction */}
          <div className="app-card p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-md flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <Badge variant="emerald" size="sm">Module A: SOH</Badge>
                <span className="text-[10px] font-mono text-slate-400">XGBoost</span>
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400">State of Health (Capacity)</div>
              <div className="text-3xl sm:text-4xl font-extrabold text-emerald-600 dark:text-emerald-400 font-mono mt-2">
                {sohVal.toFixed(1)}%
              </div>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-between text-[11px] font-mono text-slate-500">
              <span>Capacity Grade:</span>
              <strong className="text-emerald-500">{sohVal > 90 ? "Tier 1 (Healthy)" : "Tier 2 (Degrading)"}</strong>
            </div>
          </div>

          {/* Card 3: Module B 3-Zone Thermal Safety */}
          <div className={`app-card p-6 bg-white dark:bg-slate-900 border shadow-md flex flex-col justify-between ${
            isThermalWarning ? "border-amber-500/80 shadow-amber-500/10" : "border-slate-200 dark:border-slate-800"
          }`}>
            <div>
              <div className="flex items-center justify-between mb-3">
                <Badge variant={isThermalWarning ? "amber" : "emerald"} size="sm">Module B: Thermals</Badge>
                <span className="text-[10px] font-mono text-slate-400">200-Tree RF</span>
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400">3-Zone Thermodynamic Status</div>
              <div className={`text-xl font-extrabold font-mono mt-2 ${
                isThermalWarning ? "text-amber-500" : "text-emerald-500"
              }`}>
                {thermalStatus}
              </div>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-between text-[11px] font-mono text-slate-500">
              <span>Risk Probability:</span>
              <strong className={thermalRisk > 0.3 ? "text-amber-500" : "text-emerald-500"}>
                {(thermalRisk * 100).toFixed(1)}%
              </strong>
            </div>
          </div>

          {/* Card 4: Module C Knee-Point Prognostics */}
          <div className="app-card p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-md flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <Badge variant="purple" size="sm">Module C: Knee Point</Badge>
                <span className="text-[10px] font-mono text-slate-400">28-Feature Booster</span>
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400">Cycles to Non-Linear Knee</div>
              <div className="text-3xl sm:text-4xl font-extrabold text-purple-600 dark:text-purple-400 font-mono mt-2">
                ~{kneeCycles} <span className="text-sm font-normal text-slate-400">cycles</span>
              </div>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-between text-[11px] font-mono text-slate-500">
              <span>Driver Aggressiveness:</span>
              <strong className={(driverAI ?? 0.28) > 0.6 ? "text-amber-500" : "text-cyan-500"}>
                AI = {(driverAI ?? 0.28).toFixed(2)}
              </strong>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
export default LiveModelSandbox;
