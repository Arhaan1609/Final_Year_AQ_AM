"use client";

import React, { useEffect, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Float } from "@react-three/drei";
import * as THREE from "three";
import { useFleetStore } from "../../lib/store/useFleetStore";
import { Layers, Eye, Flame, RotateCw, Activity, ShieldAlert } from "lucide-react";

export type ViewMode = "thermal" | "health" | "exploded" | "wireframe";

interface BatteryPack3DProps {
  batteryTemp: number;
  controllerTemp: number;
  motorTemp: number;
  soc: number;
  soh?: number;
  status?: string;
  isCritical?: boolean;
}

// Convert temperature & degradation health to realistic automotive telemetry color
function getCellVisualColor(
  temp: number,
  cellIndex: number,
  soh: number = 95,
  isCritical: boolean = false,
  viewMode: ViewMode = "thermal"
): string {
  // If explicitly viewing Cell Health / Degradation
  if (viewMode === "health") {
    // Inner cells age slightly faster due to thermal trapped core
    const cellSoh = soh - (cellIndex % 4 === 1 || cellIndex % 4 === 2 ? 1.8 : -0.6);
    if (cellSoh < 75 || isCritical) return "#E11D48"; // Rose-Red (Critical Wear)
    if (cellSoh < 82) return "#EA580C"; // Orange (High Degradation)
    if (cellSoh < 88) return "#D97706"; // Amber (Moderate Wear)
    if (cellSoh < 94) return "#059669"; // Emerald (Good)
    return "#0891B2"; // Cyan (Pristine)
  }

  // Thermal & Hybrid Mode:
  // If battery is severely degraded (<75% or critical hold), highlight high internal resistance wear
  if (isCritical || soh < 75) {
    if (temp >= 48) return "#DC2626"; // Crimson
    if (temp >= 38) return "#EA580C"; // Orange
    // Under critical hold with degraded SOH, core cells show degraded capacity warning hues
    return cellIndex % 2 === 0 ? "#E11D48" : "#D97706"; // Rose & Amber
  }

  // Standard Thermal Gradient:
  if (temp < 32) return "#0891B2"; // Cyan (Cool Nominal)
  if (temp < 40) return "#059669"; // Emerald (Nominal Operating)
  if (temp < 50) return "#D97706"; // Amber (Warm)
  return "#DC2626"; // Crimson (Overheat)
}

function getComponentHeatColor(temp: number): string {
  if (temp < 35) return "#0891B2"; // Cyan
  if (temp < 45) return "#059669"; // Emerald
  if (temp < 55) return "#D97706"; // Amber
  return "#DC2626"; // Crimson
}

// Precision Automotive Battery Pack CAD Model
function BatteryCadModel({
  batteryTemp,
  controllerTemp,
  motorTemp,
  soc,
  soh = 95,
  status = "active",
  isCritical = false,
  viewMode,
  isRotating,
}: BatteryPack3DProps & { viewMode: ViewMode; isRotating: boolean }) {
  const groupRef = useRef<THREE.Group>(null);
  const { theme } = useFleetStore();

  useFrame((_, delta) => {
    if (groupRef.current && isRotating) {
      groupRef.current.rotation.y += delta * 0.25;
    }
  });

  const isExploded = viewMode === "exploded";
  const isWireframe = viewMode === "wireframe";

  const controllerHeatColor = getComponentHeatColor(controllerTemp);
  const motorHeatColor = getComponentHeatColor(motorTemp);

  const casingColor = theme === "dark" ? "#1E293B" : "#CBD5E1";

  return (
    <group ref={groupRef} position={[0, 0, 0]} rotation={[0.35, 0.45, 0]}>
      {/* 1. Die-Cast Aluminum Lower Chassis Tray */}
      <mesh position={[0, isExploded ? -0.4 : -0.1, 0]}>
        <boxGeometry args={[3.2, 0.2, 2.0]} />
        <meshStandardMaterial
          color={casingColor}
          metalness={0.7}
          roughness={0.3}
          wireframe={isWireframe}
        />
      </mesh>

      {/* 2. Precision 16-Cell Prismatic Module Grid (4x4) */}
      {[-1.1, -0.37, 0.37, 1.1].map((x, i) =>
        [-0.65, -0.22, 0.22, 0.65].map((z, j) => {
          const cellIndex = i * 4 + j;
          const cellOffset = ((i + j) % 3) * 0.5;
          const currentCellTemp = batteryTemp + cellOffset;
          const color = getCellVisualColor(currentCellTemp, cellIndex, soh, isCritical, viewMode);
          const explodedY = isExploded ? 0.35 + (i % 2) * 0.15 : 0.12;
          const explodedX = isExploded ? x * 1.2 : x;
          const explodedZ = isExploded ? z * 1.2 : z;

          return (
            <group key={`cell-${i}-${j}`} position={[explodedX, explodedY, explodedZ]}>
              {/* Prismatic Cell Enclosure */}
              <mesh>
                <boxGeometry args={[0.55, 0.32, 0.36]} />
                <meshStandardMaterial
                  color={viewMode === "wireframe" ? (theme === "dark" ? "#334155" : "#94A3B8") : color}
                  emissive={viewMode === "wireframe" ? "#000000" : color}
                  emissiveIntensity={viewMode === "wireframe" ? 0 : 0.45}
                  metalness={0.6}
                  roughness={0.3}
                  wireframe={isWireframe}
                />
              </mesh>
              {/* Nickel Terminals */}
              <mesh position={[0, 0.18, 0]}>
                <cylinderGeometry args={[0.04, 0.04, 0.04, 12]} />
                <meshStandardMaterial color="#E2E8F0" metalness={0.9} roughness={0.1} />
              </mesh>
            </group>
          );
        })
      )}

      {/* 3. Copper Busbars (Neat Parallel Interconnects) */}
      {[-0.65, -0.22, 0.22, 0.65].map((z, idx) => (
        <mesh
          key={`busbar-${idx}`}
          position={[0, isExploded ? 0.6 : 0.3, isExploded ? z * 1.2 : z]}
        >
          <boxGeometry args={[2.8, 0.02, 0.06]} />
          <meshStandardMaterial
            color="#D97706"
            metalness={0.9}
            roughness={0.1}
            wireframe={isWireframe}
          />
        </mesh>
      ))}

      {/* 4. Integrated Smart BMS Controller (Flush Front Housing) */}
      <mesh position={[0, isExploded ? 0.7 : 0.2, isExploded ? 1.4 : 1.15]}>
        <boxGeometry args={[1.2, 0.22, 0.4]} />
        <meshStandardMaterial
          color={viewMode === "wireframe" ? (theme === "dark" ? "#1E293B" : "#64748B") : controllerHeatColor}
          emissive={viewMode === "wireframe" ? "#000000" : controllerHeatColor}
          emissiveIntensity={viewMode === "wireframe" ? 0 : 0.4}
          metalness={0.8}
          roughness={0.2}
          wireframe={isWireframe}
        />
      </mesh>

      {/* 5. Compact Powertrain Motor Unit (Realistic Scale) */}
      <mesh
        position={[0, isExploded ? -0.2 : 0.0, isExploded ? -1.5 : -1.25]}
        rotation={[0, 0, Math.PI / 2]}
      >
        <cylinderGeometry args={[0.35, 0.35, 1.2, 24]} />
        <meshStandardMaterial
          color={viewMode === "wireframe" ? (theme === "dark" ? "#1E293B" : "#475569") : motorHeatColor}
          emissive={viewMode === "wireframe" ? "#000000" : motorHeatColor}
          emissiveIntensity={viewMode === "wireframe" ? 0 : 0.4}
          metalness={0.85}
          roughness={0.25}
          wireframe={isWireframe}
        />
      </mesh>

      {/* 6. Translucent Acrylic Protective Top Lid */}
      <mesh position={[0, isExploded ? 0.95 : 0.32, 0]}>
        <boxGeometry args={[3.2, 0.03, 2.0]} />
        <meshPhysicalMaterial
          color="#F8FAFC"
          metalness={0.1}
          roughness={0.1}
          transmission={0.8}
          thickness={0.2}
          transparent
          opacity={isWireframe ? 0.2 : 0.45}
        />
      </mesh>
    </group>
  );
}

export const BatteryPack3D: React.FC<BatteryPack3DProps> = (props) => {
  const [mounted, setMounted] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>("thermal");
  const [isRotating, setIsRotating] = useState(true);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-full h-80 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-center">
        <div className="text-xs font-mono text-slate-400">Loading 3D Twin...</div>
      </div>
    );
  }

  const isCriticalPack = props.isCritical || (props.soh !== undefined && props.soh < 75) || props.status === "critical";
  const isWarningPack = !isCriticalPack && ((props.soh !== undefined && props.soh < 85) || props.status === "warning" || props.batteryTemp > 42);

  return (
    <div className="w-full h-80 sm:h-96 relative rounded-xl overflow-hidden bg-slate-50 dark:bg-[#0D111A] border border-slate-200 dark:border-slate-800 shadow-sm">
      {/* Top Header & Interactive Mode Controls */}
      <div className="absolute top-3 left-3 right-3 z-10 flex items-center justify-between pointer-events-none">
        <div className="flex items-center gap-2">
          <div className={`px-2.5 py-1 rounded-md backdrop-blur-sm border shadow-xs flex items-center gap-1.5 ${
            isCriticalPack
              ? "bg-rose-50/95 dark:bg-rose-950/90 border-rose-300 dark:border-rose-800 text-rose-800 dark:text-rose-200"
              : isWarningPack
              ? "bg-amber-50/95 dark:bg-amber-950/90 border-amber-300 dark:border-amber-800 text-amber-800 dark:text-amber-200"
              : "bg-white/90 dark:bg-slate-900/90 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300"
          }`}>
            <span className={`w-2 h-2 rounded-full ${
              isCriticalPack
                ? "bg-rose-500 animate-pulse"
                : isWarningPack
                ? "bg-amber-500"
                : "bg-emerald-500"
            }`} />
            <span className="text-[11px] font-mono font-bold">
              16-Cell Digital Twin • 12.4 kWh {isCriticalPack ? "(SERVICE HOLD)" : isWarningPack ? "(ADVISORY)" : "(OPTIMAL)"}
            </span>
          </div>
        </div>

        {/* View Mode Buttons */}
        <div className="flex items-center gap-1 pointer-events-auto bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border border-slate-200 dark:border-slate-800 p-0.5 rounded-lg shadow-xs">
          <button
            onClick={() => setViewMode("thermal")}
            className={`px-2 py-0.5 rounded text-[10px] font-medium transition-all ${
              viewMode === "thermal"
                ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900"
                : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-100"
            }`}
          >
            Thermal
          </button>

          <button
            onClick={() => setViewMode("health")}
            className={`px-2 py-0.5 rounded text-[10px] font-medium transition-all ${
              viewMode === "health"
                ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900"
                : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-100"
            }`}
          >
            Cell Health
          </button>

          <button
            onClick={() => setViewMode("exploded")}
            className={`px-2 py-0.5 rounded text-[10px] font-medium transition-all ${
              viewMode === "exploded"
                ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900"
                : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-100"
            }`}
          >
            Exploded
          </button>

          <button
            onClick={() => setViewMode("wireframe")}
            className={`px-2 py-0.5 rounded text-[10px] font-medium transition-all ${
              viewMode === "wireframe"
                ? "bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900"
                : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-100"
            }`}
          >
            X-Ray
          </button>

          <button
            onClick={() => setIsRotating(!isRotating)}
            className="p-1 rounded text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-all"
            title="Toggle Rotation"
          >
            <RotateCw className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* 3D Canvas */}
      <Canvas camera={{ position: [0, 2.2, 4.0], fov: 42 }}>
        <ambientLight intensity={1.1} />
        <directionalLight position={[10, 15, 10]} intensity={1.4} />
        <pointLight position={[-8, 4, -8]} intensity={0.5} />
        <OrbitControls enableZoom={true} maxDistance={7} minDistance={2.5} />
        <Float speed={1.0} rotationIntensity={0.08} floatIntensity={0.2}>
          <BatteryCadModel {...props} viewMode={viewMode} isRotating={isRotating} />
        </Float>
      </Canvas>

      {/* Bottom Thermal Probe Metrics */}
      <div className="absolute bottom-3 left-3 right-3 z-10 flex items-center justify-between pointer-events-none text-[10px] font-mono">
        <div className="flex items-center gap-1.5 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border border-slate-200 dark:border-slate-800 px-2.5 py-1 rounded-md shadow-xs">
          <span className="text-slate-400">Pack Core:</span>
          <strong className={props.batteryTemp > 45 ? "text-amber-600" : isCriticalPack ? "text-rose-600 dark:text-rose-400" : "text-emerald-600 dark:text-emerald-400"}>
            {props.batteryTemp.toFixed(1)}°C
          </strong>
        </div>
        <div className="flex items-center gap-1.5 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border border-slate-200 dark:border-slate-800 px-2.5 py-1 rounded-md shadow-xs">
          <span className="text-slate-400">Inverter:</span>
          <strong className="text-cyan-600 dark:text-cyan-400">
            {props.controllerTemp.toFixed(1)}°C
          </strong>
        </div>
        <div className="flex items-center gap-1.5 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border border-slate-200 dark:border-slate-800 px-2.5 py-1 rounded-md shadow-xs">
          <span className="text-slate-400">Motor:</span>
          <strong className="text-amber-600 dark:text-amber-400">
            {props.motorTemp.toFixed(1)}°C
          </strong>
        </div>
      </div>
    </div>
  );
};
export default BatteryPack3D;
