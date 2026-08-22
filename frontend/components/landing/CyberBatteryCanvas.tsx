"use client";

import React, { useRef, useState, useEffect, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, OrbitControls } from "@react-three/drei";
import * as THREE from "three";

export interface CyberBatterySceneProps {
  temperature?: number;
  soc?: number;
  current?: number;
  isThermalWarning?: boolean;
}

// Particle stream of active telemetry electrons
function ElectronParticles({
  current = -18,
  color = "#10B981",
}: {
  current?: number;
  color?: string;
}) {
  const pointsRef = useRef<THREE.Points>(null);
  const COUNT = 60;

  const [geometry, speeds] = useMemo(() => {
    const geom = new THREE.BufferGeometry();
    const positions = new Float32Array(COUNT * 3);
    const speedArr = new Float32Array(COUNT);
    for (let i = 0; i < COUNT; i++) {
      positions[i * 3 + 0] = (Math.random() - 0.5) * 4.2;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 1.5;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 2.8;
      speedArr[i] = 0.5 + Math.random() * 1.4;
    }
    geom.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    return [geom, speedArr];
  }, []);

  const speedMultiplier = Math.max(0.3, Math.min(3.0, Math.abs(current) / 25));
  const isRegen = current > 0;

  useFrame((state, delta) => {
    if (!pointsRef.current) return;
    const attr = pointsRef.current.geometry.attributes.position;
    const pos = attr.array as Float32Array;
    for (let i = 0; i < COUNT; i++) {
      const direction = isRegen ? -1 : 1;
      pos[i * 3 + 1] += speeds[i] * delta * 0.45 * speedMultiplier * direction;
      if (pos[i * 3 + 1] > 1.2) {
        pos[i * 3 + 1] = -1.2;
      } else if (pos[i * 3 + 1] < -1.2) {
        pos[i * 3 + 1] = 1.2;
      }
    }
    attr.needsUpdate = true;
  });

  return (
    <points ref={pointsRef} geometry={geometry}>
      <pointsMaterial
        size={0.06}
        color={color}
        transparent
        opacity={0.85}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

// Cybernetic Cell Pack Model
function BatteryHologramModel({
  temperature = 32.5,
  soc = 92,
  current = -18,
  isThermalWarning = false,
}: CyberBatterySceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const pulseRingRef = useRef<THREE.Mesh>(null);
  const outerRingRef = useRef<THREE.Mesh>(null);

  // Dynamic color interpolation based on live temperature
  const cellColor = useMemo(() => {
    if (temperature > 52) return "#EF4444"; // Crimson Heat Hazard
    if (temperature > 44 || isThermalWarning) return "#F59E0B"; // Amber Warning
    if (temperature > 34) return "#06B6D4"; // Cyan Active
    return "#10B981"; // Emerald Optimal
  }, [temperature, isThermalWarning]);

  const glowIntensity = temperature > 48 ? 1.6 : temperature > 38 ? 0.9 : 0.45;

  useFrame((state, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.28;
    }
    if (pulseRingRef.current) {
      pulseRingRef.current.rotation.z -= delta * 0.45;
    }
    if (outerRingRef.current) {
      outerRingRef.current.rotation.z += delta * 0.3;
    }
  });

  return (
    <group ref={groupRef} position={[0, -0.05, 0]} rotation={[0.25, 0.35, 0]}>
      {/* Outer Anodized Acrylic Enclosure */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[3.4, 0.48, 2.2]} />
        <meshPhysicalMaterial
          color="#0B0F19"
          metalness={0.92}
          roughness={0.12}
          transmission={0.45}
          thickness={0.6}
          transparent
          opacity={0.75}
        />
      </mesh>

      {/* 10 Prismatic High-Density 3.2V LFP Cells */}
      {[-1.2, -0.6, 0.0, 0.6, 1.2].map((x, i) =>
        [-0.55, 0.55].map((z, j) => (
          <group key={`cell-${i}-${j}`} position={[x, 0.1, z]}>
            <mesh>
              <boxGeometry args={[0.5, 0.4, 0.85]} />
              <meshStandardMaterial
                color={cellColor}
                emissive={cellColor}
                emissiveIntensity={glowIntensity}
                metalness={0.82}
                roughness={0.18}
              />
            </mesh>
            {/* Terminals */}
            <mesh position={[0, 0.22, 0.22]}>
              <cylinderGeometry args={[0.065, 0.065, 0.05, 16]} />
              <meshStandardMaterial color="#38BDF8" metalness={0.9} roughness={0.1} />
            </mesh>
            <mesh position={[0, 0.22, -0.22]}>
              <cylinderGeometry args={[0.065, 0.065, 0.05, 16]} />
              <meshStandardMaterial color="#EF4444" metalness={0.9} roughness={0.1} />
            </mesh>
          </group>
        ))
      )}

      {/* Superconducting Busbars */}
      {[-0.55, 0.55].map((z, idx) => (
        <mesh key={`busbar-${idx}`} position={[0, 0.34, z]}>
          <boxGeometry args={[3.0, 0.04, 0.12]} />
          <meshStandardMaterial
            color="#F59E0B"
            metalness={0.96}
            roughness={0.04}
            emissive="#F59E0B"
            emissiveIntensity={0.35}
          />
        </mesh>
      ))}

      {/* Smart BMS Core */}
      <mesh position={[0, 0.38, 0]}>
        <boxGeometry args={[0.9, 0.15, 0.5]} />
        <meshStandardMaterial
          color="#1E293B"
          metalness={0.85}
          roughness={0.25}
          emissive={cellColor}
          emissiveIntensity={0.6}
        />
      </mesh>

      {/* Radar Target Rings */}
      <mesh ref={pulseRingRef} position={[0, -0.42, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[1.8, 1.95, 48]} />
        <meshBasicMaterial color={cellColor} transparent opacity={0.35} side={THREE.DoubleSide} />
      </mesh>
      <mesh ref={outerRingRef} position={[0, -0.44, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[2.08, 2.14, 48]} />
        <meshBasicMaterial color="#06B6D4" transparent opacity={0.2} side={THREE.DoubleSide} />
      </mesh>

      <ElectronParticles current={current} color={cellColor} />
    </group>
  );
}

export const CyberBatteryCanvas: React.FC<CyberBatterySceneProps> = ({
  temperature = 32.5,
  soc = 92.0,
  current = -18.0,
  isThermalWarning = false,
}) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-full h-[260px] sm:h-[280px] rounded-2xl bg-slate-950/70 border border-slate-800 flex items-center justify-center">
        <div className="flex items-center gap-2 text-xs font-mono text-cyan-400">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span>Mounting 3D Cybernetic Digital Twin...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-[260px] sm:h-[280px] relative rounded-2xl overflow-hidden bg-gradient-to-b from-[#0B101D] via-[#06080E] to-[#04060A] border border-slate-800 shadow-xl">
      {/* Live HUD Floating Chips */}
      <div className="absolute top-3.5 left-4 z-10 flex items-center gap-2 pointer-events-none">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-950/85 backdrop-blur-md border border-white/10 shadow-lg">
          <span
            className={`w-2 h-2 rounded-full ${
              temperature > 48 ? "bg-red-500 animate-ping" : "bg-emerald-400 animate-pulse"
            }`}
          />
          <span className="text-[11px] font-mono font-bold text-white tracking-wide">
            3D DIGITAL TWIN • 12.4 kWh LFP
          </span>
        </div>
      </div>

      <div className="absolute top-3.5 right-4 z-10 flex items-center gap-2 pointer-events-none">
        <div className="px-2.5 py-1 rounded-xl bg-slate-950/85 backdrop-blur-md border border-cyan-500/30 text-[10px] font-mono text-cyan-300 font-bold shadow-md">
          SOC {soc.toFixed(1)}%
        </div>
        <div
          className={`px-2.5 py-1 rounded-xl bg-slate-950/85 backdrop-blur-md border text-[10px] font-mono font-bold shadow-md ${
            temperature > 48
              ? "border-red-500/60 text-red-400 animate-pulse"
              : temperature > 38
              ? "border-amber-500/50 text-amber-300"
              : "border-emerald-500/40 text-emerald-300"
          }`}
        >
          {temperature.toFixed(1)}°C
        </div>
      </div>

      {/* Three.js Canvas */}
      <Canvas camera={{ position: [0, 1.8, 3.8], fov: 44 }}>
        <ambientLight intensity={1.2} />
        <directionalLight position={[8, 14, 8]} intensity={1.8} color="#FFFFFF" />
        <pointLight position={[-8, 6, -8]} intensity={1.0} color="#06B6D4" />
        <pointLight position={[0, -4, 4]} intensity={0.9} color="#10B981" />
        <Float speed={1.5} rotationIntensity={0.12} floatIntensity={0.3}>
          <BatteryHologramModel
            temperature={temperature}
            soc={soc}
            current={current}
            isThermalWarning={isThermalWarning}
          />
        </Float>
        <OrbitControls
          target={[0, 0, 0]}
          enableZoom={false}
          maxPolarAngle={Math.PI / 2}
          minPolarAngle={Math.PI / 4}
        />
      </Canvas>

      {/* Bottom Hint */}
      <div className="absolute bottom-2.5 left-1/2 -translate-x-1/2 text-[10px] font-mono text-slate-400 bg-slate-950/80 backdrop-blur-md px-3 py-0.5 rounded-full border border-white/10 pointer-events-none flex items-center gap-1.5 whitespace-nowrap">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        <span>Drag to Orbit 3D Pack • Real-Time Physics</span>
      </div>
    </div>
  );
};

export default CyberBatteryCanvas;
