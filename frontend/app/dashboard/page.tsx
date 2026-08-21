"use client";

import React from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
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
} from "lucide-react";

export default function DashboardPage() {
  const { activeTab, setActiveTab } = useFleetStore();

  const mobileTabs = [
    { id: "fleet", label: "Fleet", icon: LayoutDashboard },
    { id: "state-est", label: "State", icon: Cpu },
    { id: "thermal", label: "Thermal", icon: Flame },
    { id: "behavior", label: "Driver", icon: Gauge },
    { id: "knee", label: "Knee", icon: TrendingDown },
    { id: "meta-ensemble", label: "Report", icon: FileText },
  ];

  return (
    <div className="space-y-6">
      {/* Mobile Horizontal Tab Scroller (visible on small screens) */}
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
  );
}
