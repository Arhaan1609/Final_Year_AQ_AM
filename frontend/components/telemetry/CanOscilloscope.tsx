"use client";

import React, { useEffect, useRef, useState } from "react";
import { Activity } from "lucide-react";

interface CanOscilloscopeProps {
  voltage: number;
  current: number;
  temperature: number;
}

export const CanOscilloscope: React.FC<CanOscilloscopeProps> = ({
  voltage,
  current,
  temperature,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [dataPoints, setDataPoints] = useState<{ v: number; i: number }[]>([]);

  // Push streaming telemetry points every 60ms with realistic vehicle CAN dynamics
  useEffect(() => {
    let tick = 0;
    const interval = setInterval(() => {
      tick += 0.2;
      const waveV = Math.sin(tick) * 0.8 + (Math.random() - 0.5) * 0.3;
      const waveI = Math.cos(tick * 0.7) * 3.5 + (Math.random() - 0.5) * 1.2;

      setDataPoints((prev) => {
        const next = [
          ...prev.slice(-40),
          {
            v: voltage + waveV,
            i: current + waveI,
          },
        ];
        return next;
      });
    }, 60);

    return () => clearInterval(interval);
  }, [voltage, current]);

  // Render smooth oscilloscope waveform with area fills on Canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear
    ctx.clearRect(0, 0, width, height);

    // Draw Grid Lines
    ctx.strokeStyle = "rgba(148, 163, 184, 0.12)";
    ctx.lineWidth = 1;
    for (let x = 0; x < width; x += 30) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += 20) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    if (dataPoints.length < 2) return;

    const step = width / (dataPoints.length - 1);

    // 1. Draw Voltage Waveform (Cyan)
    ctx.beginPath();
    dataPoints.forEach((p, idx) => {
      const x = idx * step;
      const normV = Math.max(0, Math.min(1, (p.v - 65) / 20));
      const y = height * 0.45 - normV * (height * 0.35);
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = "#0891B2";
    ctx.lineWidth = 2;
    ctx.stroke();

    // 2. Draw Current Waveform (Emerald / Amber)
    ctx.beginPath();
    dataPoints.forEach((p, idx) => {
      const x = idx * step;
      const normI = Math.max(0, Math.min(1, (p.i + 80) / 120));
      const y = height * 0.9 - normI * (height * 0.35);
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = current < -35 ? "#D97706" : "#059669";
    ctx.lineWidth = 1.5;
    ctx.stroke();
  }, [dataPoints, current]);

  return (
    <div className="w-full rounded-xl p-4 bg-white dark:bg-[#0D111A] border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between">
      <div className="flex items-center justify-between mb-2.5">
        <div className="flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400" />
          <h4 className="text-xs font-semibold text-slate-900 dark:text-slate-100">
            Real-Time CAN Oscilloscope (100ms)
          </h4>
        </div>

        <div className="flex items-center gap-3 text-[10px] font-mono">
          <div className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-600" />
            <span className="text-slate-600 dark:text-slate-400">{voltage.toFixed(1)}V</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
            <span className="text-slate-600 dark:text-slate-400">{current.toFixed(1)}A</span>
          </div>
        </div>
      </div>

      {/* Waveform Canvas */}
      <div className="relative w-full h-24 rounded-lg overflow-hidden bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800/80">
        <canvas ref={canvasRef} width={500} height={96} className="w-full h-full object-cover" />
        <div className="absolute top-1 right-1.5 text-[8px] font-mono text-slate-400">
          CAN 2.0B • 500 kbps
        </div>
      </div>
    </div>
  );
};
