"use client";

import React from "react";
import Link from "next/link";
import { Badge } from "../ui/Badge";
import { TiltCard } from "../ui/TiltCard";
import { MetricExplainer } from "../ui/MetricExplainer";
import {
  Cpu,
  Flame,
  Gauge,
  TrendingDown,
  Database,
  ShieldCheck,
  Zap,
  Activity,
  Layers,
  ArrowRight,
} from "lucide-react";

export const BentoArchitectureGrid: React.FC = () => {
  return (
    <section id="architecture" className="py-28 sm:py-36 px-6 sm:px-10 max-w-7xl mx-auto">
      {/* Section Header */}
      <div className="text-center max-w-3xl mx-auto mb-16">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-700/60 text-emerald-700 dark:text-emerald-300 text-xs font-semibold mb-4 shadow-sm">
          <Layers className="w-3.5 h-3.5 text-emerald-500" />
          <span>Tri-Pillar Cyber-Physical System</span>
        </div>
        <h2 className="text-3xl sm:text-5xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">
          Engineered for DeepTech EV Scalability
        </h2>
        <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 mt-3.5 leading-relaxed">
          From micro-second CAN packet processing to fleet-wide non-linear degradation forecasting, explore the specialized machine learning pillars with full empirical proof.
        </p>
      </div>

      {/* Bento Grid Layout with 3D Mouse Tilt & Specular Lighting */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-12 gap-6">
        {/* Bento 1: Module A (Large 7 Cols) */}
        <div className="lg:col-span-7">
          <TiltCard glowColor="rgba(6, 182, 212, 0.25)" className="h-full">
            <div className="app-card p-8 bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 flex flex-col justify-between hover:border-cyan-500/50 transition-all group h-full shadow-xl">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="w-12 h-12 rounded-2xl bg-cyan-50 dark:bg-cyan-950/60 border border-cyan-300 dark:border-cyan-800 text-cyan-600 dark:text-cyan-400 flex items-center justify-center group-hover:scale-110 transition-transform shadow-md">
                    <Cpu className="w-6 h-6" />
                  </div>
                  <div className="flex items-center gap-2">
                    <MetricExplainer metricKey="soc" label="View SOC Proof" />
                    <Badge variant="cyan" size="sm">Module A • 56 Models</Badge>
                  </div>
                </div>
                <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                  Fleet Macro State Estimation
                </h3>
                <p className="text-sm text-slate-600 dark:text-slate-300 mt-3 leading-relaxed">
                  Precision state estimation across four core battery metrics with zero algebraic data leakage: State of Charge (SOC), State of Health (SOH), Remaining Useful Life (RUL), and per-charge Driving Range (Mileage).
                </p>

                <div className="mt-8 grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <div className="text-[10px] font-mono text-slate-500">SOC Accuracy</div>
                    <div className="text-base font-extrabold text-cyan-600 dark:text-cyan-400 font-mono mt-0.5">99.58%</div>
                    <div className="text-[10px] text-slate-400 font-mono">KNN Regressor</div>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <div className="text-[10px] font-mono text-slate-500">SOH Tabular R²</div>
                    <div className="text-base font-extrabold text-emerald-600 dark:text-emerald-400 font-mono mt-0.5">0.9672</div>
                    <div className="text-[10px] text-slate-400 font-mono">XGBoost Engine</div>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <div className="text-[10px] font-mono text-slate-500">RUL Error</div>
                    <div className="text-base font-extrabold text-purple-600 dark:text-purple-400 font-mono mt-0.5">8.1 Cycles</div>
                    <div className="text-[10px] text-slate-400 font-mono">GradientBoosting</div>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <div className="text-[10px] font-mono text-slate-500">Range Error</div>
                    <div className="text-base font-extrabold text-amber-600 dark:text-amber-400 font-mono mt-0.5">5.4 km</div>
                    <div className="text-[10px] text-slate-400 font-mono">XGBoost Model</div>
                  </div>
                </div>
              </div>

              <div className="mt-8 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <Link
                  href="/dashboard"
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-cyan-600 dark:text-cyan-400 group-hover:underline"
                >
                  <span>Explore State Estimation Suite</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
                <MetricExplainer metricKey="soh" label="SOH Math Derivation" />
              </div>
            </div>
          </TiltCard>
        </div>

        {/* Bento 2: Module B (Medium 5 Cols) */}
        <div className="lg:col-span-5">
          <TiltCard glowColor="rgba(16, 185, 129, 0.25)" className="h-full">
            <div className="app-card p-8 bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 flex flex-col justify-between hover:border-emerald-500/50 transition-all group h-full shadow-xl">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="w-12 h-12 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-800 text-emerald-600 dark:text-emerald-400 flex items-center justify-center group-hover:scale-110 transition-transform shadow-md">
                    <Flame className="w-6 h-6" />
                  </div>
                  <div className="flex items-center gap-2">
                    <MetricExplainer metricKey="thermal" label="Thermal Proof" />
                    <Badge variant="emerald" size="sm">Module B • BatteryIQ</Badge>
                  </div>
                </div>
                <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                  Cyber-Physical &amp; Thermal Safety
                </h3>
                <p className="text-sm text-slate-600 dark:text-slate-300 mt-3 leading-relaxed">
                  3-Zone thermodynamic hazard classification monitoring Battery Core ($VBT$), Inverter Controller ($VCT$), and Powertrain Motor ($VMT$) with deep spatial-temporal 1D-CNN + LSTM time series analysis.
                </p>

                <div className="mt-8 space-y-2 font-mono text-xs text-slate-600 dark:text-slate-300">
                  <div className="flex justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <span>Multi-Zone Thermal F1:</span>
                    <strong className="text-emerald-500">0.997 (99.71% Acc)</strong>
                  </div>
                  <div className="flex justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <span>PyTorch 1D-CNN + LSTM:</span>
                    <strong className="text-cyan-500">RMSE 5.29%</strong>
                  </div>
                </div>
              </div>

              <div className="mt-8 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <Link
                  href="/dashboard"
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-600 dark:text-emerald-400 group-hover:underline"
                >
                  <span>View Thermal Twin Monitor</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
                <MetricExplainer metricKey="thermal" label="3-Zone Heat Equations" />
              </div>
            </div>
          </TiltCard>
        </div>

        {/* Bento 3: Module C (Medium 5 Cols) */}
        <div className="lg:col-span-5">
          <TiltCard glowColor="rgba(139, 92, 246, 0.25)" className="h-full">
            <div className="app-card p-8 bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 flex flex-col justify-between hover:border-purple-500/50 transition-all group h-full shadow-xl">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="w-12 h-12 rounded-2xl bg-purple-50 dark:bg-purple-950/60 border border-purple-300 dark:border-purple-800 text-purple-600 dark:text-purple-400 flex items-center justify-center group-hover:scale-110 transition-transform shadow-md">
                    <TrendingDown className="w-6 h-6" />
                  </div>
                  <div className="flex items-center gap-2">
                    <MetricExplainer metricKey="knee" label="Knee Proof" />
                    <Badge variant="purple" size="sm">Module C • BA-BMS</Badge>
                  </div>
                </div>
                <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                  Knee-Point Degradation Prognostics
                </h3>
                <p className="text-sm text-slate-600 dark:text-slate-300 mt-3 leading-relaxed">
                  Piecewise joint MSE optimization and a 28-feature XGBoost Booster forecasting the non-linear "Knee Point" where linear aging transitions to irreversible rapid capacity loss.
                </p>

                <div className="mt-8 space-y-2 font-mono text-xs text-slate-600 dark:text-slate-300">
                  <div className="flex justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <span>Driver Aggressiveness (AI):</span>
                    <strong className="text-purple-400">0.0 to 1.0 Index</strong>
                  </div>
                  <div className="flex justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <span>Battery Stress Index (BSI):</span>
                    <strong className="text-amber-400">Electrochemical Strain</strong>
                  </div>
                </div>
              </div>

              <div className="mt-8 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <Link
                  href="/dashboard"
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-purple-600 dark:text-purple-400 group-hover:underline"
                >
                  <span>Analyze Degradation Knee</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
                <MetricExplainer metricKey="driver_ai" label="Driver AI & BSI Formula" />
              </div>
            </div>
          </TiltCard>
        </div>

        {/* Bento 4: Dataset & Real-World Provenance (Large 7 Cols) */}
        <div className="lg:col-span-7">
          <TiltCard glowColor="rgba(245, 158, 11, 0.25)" className="h-full">
            <div className="app-card p-8 bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 flex flex-col justify-between hover:border-amber-500/50 transition-all group h-full shadow-xl">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="w-12 h-12 rounded-2xl bg-amber-50 dark:bg-amber-950/60 border border-amber-300 dark:border-amber-800 text-amber-600 dark:text-amber-400 flex items-center justify-center group-hover:scale-110 transition-transform shadow-md">
                    <Database className="w-6 h-6" />
                  </div>
                  <div className="flex items-center gap-2">
                    <MetricExplainer metricKey="dataset" label="Dataset Audit" />
                    <Badge variant="amber" size="sm">Fleet Dataset Provenance</Badge>
                  </div>
                </div>
                <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                  930+ MB Indian Commercial Fleet Telematics
                </h3>
                <p className="text-sm text-slate-600 dark:text-slate-300 mt-3 leading-relaxed">
                  Trained on high-frequency operational telemetry logs from commercial delivery electric vehicles (Euler Motors HiLoad 12.4 kWh LFP chassis) across Indian ambient weather extremes (-5°C to +48°C).
                </p>

                <div className="mt-8 grid grid-cols-3 gap-3">
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <div className="text-[10px] font-mono text-slate-500">Commercial Chassis</div>
                    <div className="text-base font-extrabold text-amber-500 font-mono mt-0.5">778 Vehicles</div>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <div className="text-[10px] font-mono text-slate-500">Telemetry Records</div>
                    <div className="text-base font-extrabold text-emerald-500 font-mono mt-0.5">50M+ Samples</div>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                    <div className="text-[10px] font-mono text-slate-500">Raw File Size</div>
                    <div className="text-base font-extrabold text-cyan-500 font-mono mt-0.5">930+ MB Data</div>
                  </div>
                </div>
              </div>

              <div className="mt-8 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <Link
                  href="/dashboard"
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-amber-600 dark:text-amber-400 group-hover:underline"
                >
                  <span>Inspect 778 Vehicle Registry</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
                <MetricExplainer metricKey="dataset" label="Inspect Data Architecture" />
              </div>
            </div>
          </TiltCard>
        </div>
      </div>
    </section>
  );
};

export default BentoArchitectureGrid;
