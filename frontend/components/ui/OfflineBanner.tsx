"use client";

import React, { useEffect, useState } from "react";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { getSystemHealth } from "../../lib/api/client";
import { AlertTriangle, RefreshCw, Radio } from "lucide-react";

export function OfflineBanner() {
  const { isLiveBackendConnected, setIsLiveBackendConnected } = useFleetStore();
  const [isRetrying, setIsRetrying] = useState(false);

  // Periodic health check every 10 seconds
  useEffect(() => {
    let mounted = true;

    async function checkHealth() {
      try {
        const res = await getSystemHealth();
        if (mounted && res && res.status === "ok") {
          setIsLiveBackendConnected(true);
        }
      } catch {
        if (mounted) {
          setIsLiveBackendConnected(false);
        }
      }
    }

    // Immediate initial check
    checkHealth();

    const interval = setInterval(checkHealth, 10000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [setIsLiveBackendConnected]);

  const handleManualRetry = async () => {
    setIsRetrying(true);
    try {
      const res = await getSystemHealth();
      if (res && res.status === "ok") {
        setIsLiveBackendConnected(true);
      }
    } catch {
      setIsLiveBackendConnected(false);
    } finally {
      setTimeout(() => setIsRetrying(false), 500);
    }
  };

  if (isLiveBackendConnected) {
    return null;
  }

  return (
    <div
      id="offline-banner"
      className="sticky top-0 z-[100] w-full bg-gradient-to-r from-amber-600 via-rose-600 to-amber-700 text-white px-4 py-2 shadow-lg flex items-center justify-between text-xs sm:text-sm font-semibold tracking-wide animate-in fade-in slide-in-from-top duration-300 border-b border-rose-400/40"
    >
      <div className="flex items-center gap-2.5 max-w-5xl mx-auto">
        <span className="relative flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
        </span>
        <AlertTriangle className="w-4 h-4 text-amber-100 flex-shrink-0" />
        <div>
          <span className="uppercase tracking-wider bg-black/30 px-2 py-0.5 rounded text-[11px] font-bold mr-2 border border-white/20">
            OFFLINE SIMULATION
          </span>
          <span>
            FastAPI backend (<code className="font-mono text-amber-100">localhost:8000</code>) is offline. Displaying simulated fallback telemetry.
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={handleManualRetry}
          disabled={isRetrying}
          className="flex items-center gap-1.5 px-2.5 py-1 bg-white/20 hover:bg-white/30 active:bg-white/40 rounded transition-all text-xs font-bold border border-white/30 backdrop-blur-sm cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRetrying ? "animate-spin" : ""}`} />
          {isRetrying ? "Checking..." : "Retry Connection"}
        </button>
      </div>
    </div>
  );
}
