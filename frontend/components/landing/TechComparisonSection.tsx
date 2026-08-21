"use client";

import React from "react";
import { Badge } from "../ui/Badge";
import { Check, X, ShieldAlert, ShieldCheck, Sparkles } from "lucide-react";

export const TechComparisonSection: React.FC = () => {
  const comparisonItems = [
    {
      feature: "State of Charge (SOC) Precision",
      legacy: "Coulomb counting with error drift (±6% to ±12%)",
      platform: "Leak-free KNN & Random Forest ML (99.58% R² / 1.34% RMSE)",
      highlight: true,
    },
    {
      feature: "Degradation Modeling",
      legacy: "Linear lookup tables that fail at inflection points",
      platform: "Piecewise Non-Linear Knee-Point Booster (28-Feature XGBoost)",
      highlight: true,
    },
    {
      feature: "Thermal Runway Safety",
      legacy: "Single-point threshold alarm after overheating occurs",
      platform: "3-Zone Multi-Entity Random Forest (99.71% F1, VBT/VCT/VMT)",
      highlight: true,
    },
    {
      feature: "Driver Behavioral Analysis",
      legacy: "None (BMS blind to driving aggression)",
      platform: "Normalized Driver Aggressiveness ($AI$) & Battery Stress ($BSI$)",
      highlight: false,
    },
    {
      feature: "Telemetry Ingestion Scale",
      legacy: "Static CAN diagnostics during physical service",
      platform: "Real-time 100ms sub-second streaming REST API (11 Endpoints)",
      highlight: false,
    },
    {
      feature: "Fleet-Wide Digital Twin",
      legacy: "Isolated vehicle-only controller",
      platform: "Fleet Digital Twin aggregating 778 vehicles with real-time scoring",
      highlight: true,
    },
  ];

  return (
    <section id="comparison" className="py-24 px-6 sm:px-10 max-w-7xl mx-auto">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-50 dark:bg-cyan-950/60 border border-cyan-300 dark:border-cyan-700/60 text-cyan-700 dark:text-cyan-300 text-xs font-semibold mb-4 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-cyan-500" />
          <span>Competitive Architecture Matrix</span>
        </div>
        <h2 className="text-3xl sm:text-5xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">
          Legacy BMS vs. Tri-Pillar Neural Platform
        </h2>
        <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 mt-3.5 leading-relaxed">
          Why traditional onboard battery management systems fail in commercial duty cycles, and how our cyber-physical architecture solves non-linear battery degradation.
        </p>
      </div>

      <div className="overflow-x-auto rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xl">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-950/80 text-xs font-mono uppercase text-slate-500">
              <th className="py-5 px-6 font-semibold">Capability / Dimension</th>
              <th className="py-5 px-6 font-semibold text-slate-400">Legacy Rule-Based BMS</th>
              <th className="py-5 px-6 font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50/40 dark:bg-emerald-950/30">
                EV Battery Intelligence (Ours)
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 dark:divide-slate-800 text-sm">
            {comparisonItems.map((item, idx) => (
              <tr
                key={idx}
                className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors"
              >
                <td className="py-4 px-6 font-bold text-slate-900 dark:text-slate-100">
                  {item.feature}
                </td>
                <td className="py-4 px-6 text-slate-500 dark:text-slate-400">
                  <div className="flex items-start gap-2">
                    <X className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                    <span>{item.legacy}</span>
                  </div>
                </td>
                <td className="py-4 px-6 text-slate-900 dark:text-slate-100 bg-emerald-50/20 dark:bg-emerald-950/20 font-medium">
                  <div className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5 font-bold" />
                    <span className={item.highlight ? "text-emerald-700 dark:text-emerald-300 font-semibold" : ""}>
                      {item.platform}
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};
