import React, { useState } from "react";
import { useFallbackStore } from "../../lib/fallbackLogger";
import { AlertTriangle, ShieldCheck, Trash2, X, ChevronUp, ChevronDown } from "lucide-react";

export const FallbackAuditDrawer: React.FC = () => {
  const { events, isOpen, setIsOpen, clearEvents } = useFallbackStore();
  const [minimized, setMinimized] = useState(true);

  // Hidden in production builds if needed, or toggled via discrete floating badge
  return (
    <div className="fixed bottom-4 left-4 z-50 font-sans">
      {minimized ? (
        <button
          onClick={() => setMinimized(false)}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full shadow-lg border text-xs font-mono transition-all ${
            events.length === 0
              ? "bg-slate-900/90 text-emerald-400 border-emerald-500/30 hover:bg-slate-800"
              : "bg-rose-950/90 text-rose-300 border-rose-500/50 hover:bg-rose-900 animate-pulse"
          }`}
          title="Data Authenticity & Fallback Sentinel"
        >
          {events.length === 0 ? (
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          ) : (
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
          )}
          <span>
            {events.length === 0 ? "Data Sentinel: Clean (0)" : `Fallback Alert (${events.length})`}
          </span>
        </button>
      ) : (
        <div className="w-96 max-h-[380px] bg-slate-900/95 text-slate-100 border border-slate-700 rounded-2xl shadow-2xl backdrop-blur-md flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-2">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-slate-800/80 border-b border-slate-700">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-bold font-mono uppercase tracking-wider text-slate-200">
                Fallback Audit Sentinel
              </span>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-mono font-bold ${
                events.length === 0 ? "bg-emerald-950 text-emerald-400 border border-emerald-800" : "bg-rose-950 text-rose-400 border border-rose-800"
              }`}>
                {events.length} Warnings
              </span>
            </div>
            <div className="flex items-center gap-1">
              {events.length > 0 && (
                <button
                  onClick={clearEvents}
                  className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-slate-200"
                  title="Clear Log"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              )}
              <button
                onClick={() => setMinimized(true)}
                className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-slate-200"
              >
                <ChevronDown className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Event List */}
          <div className="p-3 overflow-y-auto max-h-[300px] space-y-2 text-xs font-mono">
            {events.length === 0 ? (
              <div className="py-8 text-center text-slate-400 space-y-2">
                <ShieldCheck className="w-8 h-8 text-emerald-500 mx-auto opacity-80" />
                <div className="font-semibold text-slate-300">100% Real Data Stream Active</div>
                <div className="text-[11px] text-slate-500 max-w-[240px] mx-auto">
                  No default values or synthetic fallbacks have fired during this session.
                </div>
              </div>
            ) : (
              events.map((evt) => (
                <div
                  key={evt.id}
                  className="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/80 space-y-1"
                >
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="font-bold text-cyan-300">{evt.component}</span>
                    <span className="text-slate-500">{evt.timestamp}</span>
                  </div>
                  <div className="text-slate-300">
                    Field: <strong className="text-amber-300">{evt.field}</strong>
                  </div>
                  <div className="text-[11px] text-slate-400 flex items-center gap-2">
                    <span>Received: <code className="text-rose-300">{evt.receivedValue}</code></span>
                    <span>→</span>
                    <span>Default: <code className="text-emerald-300">{evt.defaultedTo}</code></span>
                  </div>
                  <div className="text-[10px] text-slate-500 italic">{evt.reason}</div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};
