"use client";

import React, { useEffect, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Float, Text } from "@react-three/drei";
import * as THREE from "three";

interface BatteryPack3DProps {
  batteryTemp: number;
  controllerTemp: number;
  motorTemp: number;
  soc: number;
}

// Convert temperature to realistic color gradient (Cold Cyan -> Nominal Emerald -> Warm Amber -> Critical Red)
function getHeatColor(temp: number): string {
  if (temp < 32) return "#06B6D4"; // Cyan
  if (temp < 40) return "#10B981"; // Emerald
  if (temp < 60) return "#F59E0B"; // Amber
  return "#EF4444"; // Crimson Red
}

function PackMesh({ batteryTemp, controllerTemp, motorTemp, soc }: BatteryPack3DProps) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.25;
    }
  });

  const batteryColor = getHeatColor(batteryTemp);
  const controllerColor = getHeatColor(controllerTemp);
  const motorColor = getHeatColor(motorTemp);

  return (
    <group ref={groupRef} position={[0, 0, 0]} rotation={[0.4, 0.6, 0]}>
      {/* --- Main Battery Aluminum Enclosure --- */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[3.2, 0.45, 2.0]} />
        <meshStandardMaterial
          color="#1E293B"
          metalness={0.8}
          roughness={0.2}
          transparent
          opacity={0.65}
        />
      </mesh>

      {/* --- 8 Internal Cylindrical/Prismatic Cell Blocks --- */}
      {[-1.2, -0.4, 0.4, 1.2].map((x, i) =>
        [-0.6, 0.6].map((z, j) => (
          <mesh key={`cell-${i}-${j}`} position={[x, 0.1, z]}>
            <boxGeometry args={[0.65, 0.4, 0.9]} />
            <meshStandardMaterial
              color={batteryColor}
              emissive={batteryColor}
              emissiveIntensity={batteryTemp > 45 ? 0.8 : 0.25}
              metalness={0.5}
              roughness={0.3}
            />
          </mesh>
        ))
      )}

      {/* --- Power Electronics & Controller (Front Unit) --- */}
      <mesh position={[0, 0.4, 1.3]}>
        <boxGeometry args={[1.4, 0.35, 0.6]} />
        <meshStandardMaterial
          color={controllerColor}
          emissive={controllerColor}
          emissiveIntensity={controllerTemp > 50 ? 0.9 : 0.3}
          metalness={0.9}
          roughness={0.1}
        />
      </mesh>

      {/* --- Traction Motor (Rear Powertrain) --- */}
      <mesh position={[0, -0.1, -1.5]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.5, 0.5, 1.6, 24]} />
        <meshStandardMaterial
          color={motorColor}
          emissive={motorColor}
          emissiveIntensity={motorTemp > 65 ? 1.0 : 0.2}
          metalness={0.9}
          roughness={0.2}
        />
      </mesh>

      {/* Busbar Rails */}
      <mesh position={[0, 0.32, 0]}>
        <boxGeometry args={[2.8, 0.05, 0.15]} />
        <meshStandardMaterial color="#F59E0B" metalness={0.9} roughness={0.1} />
      </mesh>
    </group>
  );
}

export const BatteryPack3D: React.FC<BatteryPack3DProps> = (props) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-full h-64 rounded-xl bg-slate-900/50 flex items-center justify-center border border-slate-800">
        <div className="text-xs text-slate-500 font-mono">Initializing 3D Digital Twin...</div>
      </div>
    );
  }

  return (
    <div className="w-full h-[280px] rounded-2xl relative overflow-hidden bg-gradient-to-b from-[#0F172A]/40 to-[#0A0D14] border border-slate-800/80">
      {/* Top HUD overlay */}
      <div className="absolute top-3 left-4 z-10 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
        <span className="text-[11px] font-mono uppercase tracking-widest text-cyan-300 font-semibold">
          3D Digital Twin • Euler HiLoad 12.4 kWh Pack
        </span>
      </div>

      {/* Thermal Zone Legend Overlay */}
      <div className="absolute bottom-3 left-4 right-4 z-10 flex items-center justify-between text-[11px] font-mono text-slate-400 bg-slate-950/70 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-800">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: getHeatColor(props.batteryTemp) }}
            />
            Pack: {props.batteryTemp.toFixed(1)}°C
          </span>
          <span className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: getHeatColor(props.controllerTemp) }}
            />
            Controller: {props.controllerTemp.toFixed(1)}°C
          </span>
          <span className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: getHeatColor(props.motorTemp) }}
            />
            Motor: {props.motorTemp.toFixed(1)}°C
          </span>
        </div>
        <span className="text-emerald-400 font-bold">SOC {props.soc.toFixed(1)}%</span>
      </div>

      <Canvas camera={{ position: [0, 2.8, 4.5], fov: 45 }}>
        <ambientLight intensity={0.7} />
        <pointLight position={[10, 10, 10]} intensity={1.2} />
        <pointLight position={[-10, -5, -10]} intensity={0.5} color="#06B6D4" />
        <PackMesh {...props} />
        <OrbitControls enableZoom={false} autoRotate={false} maxPolarAngle={Math.PI / 2.1} />
      </Canvas>
    </div>
  );
};
