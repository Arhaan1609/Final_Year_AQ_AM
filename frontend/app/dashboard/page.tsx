"use client";

import React from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { OperationsView } from "../../components/dashboard/OperationsView";
import { FleetOverviewTab } from "../../components/tabs/FleetOverviewTab";
import { StateEstimationTab } from "../../components/tabs/StateEstimationTab";
import { ThermalSafetyTab } from "../../components/tabs/ThermalSafetyTab";
import { DriverProfilingTab } from "../../components/tabs/DriverProfilingTab";
import { KneePrognosticsTab } from "../../components/tabs/KneePrognosticsTab";
import { MetaEnsembleReportTab } from "../../components/tabs/MetaEnsembleReportTab";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Cpu,
  Flame,
  Gauge,
  TrendingDown,
  FileText,
  Briefcase,
  Layers,
  Sparkles,
} from "lucide-react";

export default function DashboardPage() {
  const { activeTab, setActiveTab, viewMode, setViewMode } = useFleetStore();

  const mobileTabs = [
    { id: "fleet", label: "Fleet Hub", icon: LayoutDashboard },
    { id: "state-est", label: "Module A: State", icon: Cpu },
    { id: "thermal", label: "Module B: Thermal", icon: Flame },
    { id: "behavior", label: "Module C: Driver", icon: Gauge },
    { id: "knee", label: "Module C: Knee", icon: TrendingDown },
    { id: "meta-ensemble", label: "Meta Ensemble", icon: FileText },
  ];

  return (
    <div className="space-y-6">
      {/* ─── ROLE-BASED MODE SWITCHER HEADER ─── */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-500 flex items-center justify-center text-white font-bold shadow-md shadow-emerald-500/20">
            {viewMode === "operations" ? <Briefcase className="w-5 h-5" /> : <Cpu className="w-5 h-5" />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                {viewMode === "operations" ? "Fleet Operations Command" : "Engineering ML Diagnostics"}
              </h1>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-100 text-cyan-800 dark:bg-cyan-950 dark:text-cyan-300">
                {viewMode === "operations" ? "Non-EV Friendly" : "74 ML Models"}
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {viewMode === "operations"
                ? "Simplified traffic-light dispatch triage, battery range, and maintenance directives."
                : "Deep mathematical features, neural weights, and multi-target ensemble inference."}
            </p>
          </div>
        </div>

        {/* View Mode Toggle Switch */}
        <div className="flex items-center p-1 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
          <button
            onClick={() => setViewMode("operations")}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              viewMode === "operations"
                ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm"
                : "text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <Briefcase className="w-3.5 h-3.5 text-cyan-500" />
            <span>Operations View</span>
          </button>

          <button
            onClick={() => setViewMode("engineering")}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              viewMode === "engineering"
                ? "bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm"
                : "text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <Cpu className="w-3.5 h-3.5 text-purple-500" />
            <span>Engineering View</span>
          </button>
        </div>
      </div>

      {/* ─── RENDER CONTENT ACCORDING TO VIEW MODE ─── */}
      {viewMode === "operations" ? (
        <OperationsView />
      ) : (
        <div className="space-y-6">
          {/* Engineering Tab Scroller for Mobile */}
          <div className="flex md:hidden items-center gap-2 overflow-x-auto pb-2 border-b border-slate-200 dark:border-slate-800">
            {mobileTabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                    isActive
                      ? "bg-cyan-50 dark:bg-cyan-950/60 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-800"
                      : "bg-white dark:bg-slate-900 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-800"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Main Tab Render with Page Transition */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              {activeTab === "fleet" && <FleetOverviewTab />}
              {activeTab === "state-est" && <StateEstimationTab />}
              {activeTab === "thermal" && <ThermalSafetyTab />}
              {activeTab === "behavior" && <DriverProfilingTab />}
              {activeTab === "knee" && <KneePrognosticsTab />}
              {activeTab === "meta-ensemble" && <MetaEnsembleReportTab />}
            </motion.div>
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
