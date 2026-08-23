"use client";

import React, { useState } from "react";
import { Info, Sparkles, HelpCircle, FileText } from "lucide-react";
import { ProofOfConceptModal } from "./ProofOfConceptModal";

interface MetricExplainerProps {
  metricKey:
    | "soc"
    | "soh"
    | "rul"
    | "thermal"
    | "knee"
    | "driver_ai"
    | "roi"
    | "dataset"
    | "mileage"
    | "can_oscilloscope"
    | "digital_twin"
    | "copilot_ai"
    | "meta_ensemble"
    | "triage"
    | string;
  currentValue?: string | number;
  label?: string;
  variant?: "badge" | "icon" | "button" | "pill";
  className?: string;
}


export const MetricExplainer: React.FC<MetricExplainerProps> = ({
  metricKey,
  currentValue,
  label = "How was this achieved?",
  variant = "badge",
  className = "",
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {variant === "badge" && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsOpen(true);
          }}
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-100 hover:bg-cyan-50 dark:bg-slate-800 dark:hover:bg-cyan-950/60 border border-slate-200 dark:border-slate-700 text-[10px] font-mono text-slate-500 hover:text-cyan-600 dark:text-slate-400 dark:hover:text-cyan-300 transition-all cursor-pointer ${className}`}
          title="Click to view Plain English explainer and Mathematical Proof of Concept"
        >
          <Sparkles className="w-2.5 h-2.5 text-cyan-500" />
          <span>{label}</span>
        </button>
      )}

      {variant === "icon" && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsOpen(true);
          }}
          className={`p-1 rounded-lg text-slate-400 hover:text-cyan-500 hover:bg-cyan-50 dark:hover:bg-cyan-950/50 transition-colors cursor-pointer ${className}`}
          title="Click to view plain-English explanation & Proof of Concept"
        >
          <HelpCircle className="w-3.5 h-3.5" />
        </button>
      )}

      {variant === "pill" && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsOpen(true);
          }}
          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-600 dark:text-cyan-400 text-xs font-mono font-semibold transition-all cursor-pointer ${className}`}
        >
          <Info className="w-3 h-3" />
          <span>{label}</span>
        </button>
      )}

      {variant === "button" && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsOpen(true);
          }}
          className={`inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-xs font-bold text-slate-700 dark:text-slate-200 transition-all cursor-pointer ${className}`}
        >
          <FileText className="w-3.5 h-3.5 text-cyan-500" />
          <span>{label}</span>
        </button>
      )}

      <ProofOfConceptModal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        metricKey={metricKey}
        currentValue={currentValue}
      />
    </>
  );
};

export default MetricExplainer;
