"use client";

import React, { useState } from "react";
import { Badge } from "../ui/Badge";
import { TiltCard } from "../ui/TiltCard";
import { MetricExplainer } from "../ui/MetricExplainer";
import { DollarSign, ShieldCheck, Zap, TrendingUp, Sparkles, ArrowRight, Truck } from "lucide-react";
import Link from "next/link";

export const FleetRoiCalculator: React.FC = () => {
  const [fleetSize, setFleetSize] = useState<number>(100);
  const [dailyKm, setDailyKm] = useState<number>(85);
  const [batteryPackCost, setBatteryPackCost] = useState<number>(250000); // 2.5 Lakhs INR (~$3,000 USD)

  // Calculations
  // Conventional battery replacement interval: ~3.5 years (1200 cycles)
  // AI-Optimized replacement interval: ~5.8 years (2000 cycles with knee avoidance & thermal throttling)
  const yearsExtended = 2.3;
  const annualSavingsPerEV =
    batteryPackCost / 3.5 - batteryPackCost / 5.8 + dailyKm * 365 * 0.45; // Includes range efficiency + replacement deferral
  const totalFleetAnnualSavings = Math.round(annualSavingsPerEV * fleetSize);
  const totalSavingsLakhs = (totalFleetAnnualSavings / 100000).toFixed(1);
  const carbonMitigatedTons = Math.round(fleetSize * dailyKm * 365 * 0.00012);

  return (
    <section id="roi" className="py-28 sm:py-36 px-6 sm:px-10 max-w-7xl mx-auto">
      <div className="text-center max-w-3xl mx-auto mb-16">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-700/60 text-emerald-700 dark:text-emerald-300 text-xs font-semibold mb-4 shadow-sm">
          <TrendingUp className="w-3.5 h-3.5 text-emerald-500" />
          <span>Commercial EV Fleet Business Case</span>
        </div>
        <h2 className="text-3xl sm:text-5xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">
          Quantify Your Fleet ROI &amp; Lifespan Gain
        </h2>
        <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 mt-3.5 leading-relaxed">
          Simulate how knee-point prognostics, driver strain moderation, and thermal safety extend pack longevity and reduce fleet operational expenditure.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-10 shadow-2xl">
        {/* Left 6 Cols: Sliders */}
        <div className="lg:col-span-6 space-y-6">
          <div className="border-b border-slate-200 dark:border-slate-800 pb-4">
            <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">
              Fleet Operational Parameters
            </h3>
            <p className="text-xs text-slate-500 font-mono">
              Adjust variables to reflect your commercial fleet operations
            </p>
          </div>

          {/* Slider 1: Fleet Size */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-600 dark:text-slate-300">Commercial Fleet Size:</span>
              <strong className="text-emerald-600 dark:text-emerald-400 text-sm font-bold">
                {fleetSize} Commercial EVs
              </strong>
            </div>
            <input
              type="range"
              min="10"
              max="1000"
              step="10"
              value={fleetSize}
              onChange={(e) => setFleetSize(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>10 Vehicles</span>
              <span>500 Vehicles</span>
              <span>1,000+ Vehicles</span>
            </div>
          </div>

          {/* Slider 2: Daily Distance */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-600 dark:text-slate-300">Average Daily Distance:</span>
              <strong className="text-cyan-600 dark:text-cyan-400 text-sm font-bold">
                {dailyKm} km / vehicle / day
              </strong>
            </div>
            <input
              type="range"
              min="30"
              max="200"
              step="5"
              value={dailyKm}
              onChange={(e) => setDailyKm(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>30 km (Intracity)</span>
              <span>100 km (High Duty)</span>
              <span>200 km (Courier Express)</span>
            </div>
          </div>

          {/* Slider 3: Battery Pack Cost */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-600 dark:text-slate-300">Battery Pack Replacement Unit Cost:</span>
              <strong className="text-purple-600 dark:text-purple-400 text-sm font-bold">
                ₹{(batteryPackCost / 100000).toFixed(1)} Lakhs (~${Math.round(batteryPackCost / 83)})
              </strong>
            </div>
            <input
              type="range"
              min="150000"
              max="500000"
              step="25000"
              value={batteryPackCost}
              onChange={(e) => setBatteryPackCost(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>₹1.5L (3-Wheeler)</span>
              <span>₹2.5L (HiLoad LCV)</span>
              <span>₹5.0L (Heavy Duty)</span>
            </div>
          </div>
        </div>

        {/* Right 6 Cols: Real-time ROI Savings Cards with 3D Mouse Tilt */}
        <div className="lg:col-span-6">
          <TiltCard glowColor="rgba(16, 185, 129, 0.3)">
            <div className="bg-slate-950 text-white rounded-2xl p-6 sm:p-8 space-y-6 border border-slate-800 shadow-2xl">
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-xs font-mono uppercase tracking-wider text-emerald-400 font-semibold">
                    Projected Annual OPEX Savings
                  </div>
                  <div className="text-4xl sm:text-5xl font-extrabold text-white font-mono mt-1">
                    ₹{totalSavingsLakhs} <span className="text-xl font-normal text-slate-400">Lakhs / yr</span>
                  </div>
                  <div className="text-xs text-slate-400 font-mono mt-1">
                    ~${Math.round(totalFleetAnnualSavings / 83).toLocaleString()} USD Annual Net Fleet Benefit
                  </div>
                </div>
                <MetricExplainer
                  metricKey="roi"
                  currentValue={`₹${totalSavingsLakhs} Lakhs/yr`}
                  label="View Financial Formula"
                  variant="badge"
                />
              </div>

              <div className="grid grid-cols-2 gap-4 border-t border-slate-800 pt-6">
                <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
                  <div className="text-[10px] font-mono text-slate-400">Pack Lifespan Added</div>
                  <div className="text-2xl font-extrabold text-emerald-400 font-mono mt-1">
                    +{yearsExtended} Years
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">Deferred CapEx</div>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
                  <div className="text-[10px] font-mono text-slate-400">Thermal Fault Prevention</div>
                  <div className="text-2xl font-extrabold text-cyan-400 font-mono mt-1">
                    99.71%
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">Multi-Zone Safety</div>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
                  <div className="text-[10px] font-mono text-slate-400">Degradation Knee Buffer</div>
                  <div className="text-2xl font-extrabold text-purple-400 font-mono mt-1">
                    450+ Cycles
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">Early Warning Lead</div>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
                  <div className="text-[10px] font-mono text-slate-400">Emissions Mitigated</div>
                  <div className="text-2xl font-extrabold text-amber-400 font-mono mt-1">
                    {carbonMitigatedTons} Tons
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">CO2 eq / Year</div>
                </div>
              </div>

              <Link
                href="/dashboard"
                className="w-full inline-flex items-center justify-center gap-2 py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-bold text-xs shadow-md transition-all hover:scale-[1.02] active:scale-95"
              >
                <span>Deploy Model Suite for Your Fleet</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </TiltCard>
        </div>
      </div>
    </section>
  );
};

export default FleetRoiCalculator;
