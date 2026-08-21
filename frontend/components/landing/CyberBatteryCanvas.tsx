"use client";

import React, { useRef, useState, useEffect, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, MeshDistortMaterial } from "@react-three/drei";
import * as THREE from "three";

interface CyberBatterySceneProps {
  temperature?: number;
  soc?: number;
}

// Particle stream of active telemetry electrons
function ElectronParticles({ count = 80 }: { count?: number }) {
  const pointsRef = useRef<THREE.Points>(null);

  const particles = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const speeds = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      positions[i * 3 + 0] = (Math.random() - 0.5) * 4.5;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 1.5;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 3.0;
      speeds[i] = 0.5 + Math.random() * 1.5;
    }
    return { positions, speeds };
  }, [count]);

  useFrame((state, delta) => {
    if (!pointsRef.current) return;
    const pos = pointsRef.current.geometry.attributes.position.array as Float32Array;
    for (let i = 0; i < count; i++) {
      pos[i * 3 + 1] += particles.speeds[i] * delta * 0.4;
      if (pos[i * 3 + 1] > 1.2) {
        pos[i * 3 + 1] = -1.2;
      }
    }
    pointsRef.current.geometry.attributes.position.needsUpdate = true;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={particles.positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.06}
        color="#10B981"
        transparent
        opacity={0.8}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

// Cybernetic Cell Pack Model
function BatteryHologramModel({ temperature = 32.5, soc = 92 }: CyberBatterySceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const pulseRingRef = useRef<THREE.Mesh>(null);

  useFrame((state, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.35;
    }
    if (pulseRingRef.current) {
      pulseRingRef.current.rotation.z -= delta * 0.5;
    }
  });

  const cellColor = temperature < 35 ? "#10B981" : temperature < 50 ? "#06B6D4" : "#F59E0B";
  const glowIntensity = temperature > 45 ? 1.2 : 0.4;

  return (
    <group ref={groupRef} position={[0, 0, 0]} rotation={[0.3, 0.4, 0]}>
      {/* Outer Cybernetic Acrylic / Anodized Frame */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[3.4, 0.5, 2.2]} />
        <meshPhysicalMaterial
          color="#0F172A"
          metalness={0.9}
          roughness={0.15}
          transmission={0.4}
          thickness={0.5}
          transparent
          opacity={0.7}
        />
      </mesh>

      {/* Grid of 12 Prismatic High-Density Cells */}
      {[-1.2, -0.6, 0.0, 0.6, 1.2].map((x, i) =>
        [-0.55, 0.55].map((z, j) => (
          <group key={`cell-${i}-${j}`} position={[x, 0.1, z]}>
            <mesh>
              <boxGeometry args={[0.5, 0.42, 0.85]} />
              <meshStandardMaterial
                color={cellColor}
                emissive={cellColor}
                emissiveIntensity={glowIntensity}
                metalness={0.8}
                roughness={0.2}
              />
            </mesh>
            {/* Cell Cap Terminal */}
            <mesh position={[0, 0.23, 0]}>
              <cylinderGeometry args={[0.08, 0.08, 0.05, 16]} />
              <meshStandardMaterial color="#38BDF8" metalness={0.9} roughness={0.1} />
            </mesh>
          </group>
        ))
      )}

      {/* Golden Super-Conducting Busbar Rails */}
      {[-0.55, 0.55].map((z, idx) => (
        <mesh key={`busbar-${idx}`} position={[0, 0.35, z]}>
          <boxGeometry args={[3.0, 0.04, 0.12]} />
          <meshStandardMaterial
            color="#F59E0B"
            metalness={0.95}
            roughness={0.05}
            emissive="#F59E0B"
            emissiveIntensity={0.3}
          />
        </mesh>
      ))}

      {/* Smart BMS Master Controller (Center-Mounted Micro-Unit) */}
      <mesh position={[0, 0.38, 0]}>
        <boxGeometry args={[0.9, 0.18, 0.5]} />
        <meshStandardMaterial
          color="#1E293B"
          metalness={0.8}
          roughness={0.3}
          emissive="#06B6D4"
          emissiveIntensity={0.5}
        />
      </mesh>

      {/* Holographic Target Rings */}
      <mesh ref={pulseRingRef} position={[0, -0.45, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[1.8, 1.95, 48]} />
        <meshBasicMaterial color="#10B981" transparent opacity={0.3} side={THREE.DoubleSide} />
      </mesh>

      <ElectronParticles count={60} />
    </group>
  );
}

export const CyberBatteryCanvas: React.FC<CyberBatterySceneProps> = ({
  temperature = 32.5,
  soc = 92.0,
}) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-full h-full min-h-[380px] rounded-3xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-center">
        <div className="flex items-center gap-2 text-xs font-mono text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          Initializing 3D Cybernetic Neural Canvas...
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full min-h-[400px] lg:min-h-[480px] relative rounded-3xl overflow-hidden bg-gradient-to-b from-slate-950/80 via-[#0A0D14]/90 to-slate-950/95 border border-slate-800/80 shadow-2xl">
      {/* Live Telemetry Overlay Badges */}
      <div className="absolute top-4 left-4 z-10 flex flex-col gap-1.5 pointer-events-none">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 backdrop-blur-md border border-slate-700/60">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[11px] font-mono font-bold text-emerald-300">
            3D DIGITAL TWIN • 12.4 kWh LFP
          </span>
        </div>
        <div className="text-[10px] font-mono text-slate-400 pl-2">
          Euler HiLoad Dual-Channel Powertrain
        </div>
      </div>

      <div className="absolute top-4 right-4 z-10 flex items-center gap-2 pointer-events-none">
        <div className="px-2.5 py-1 rounded-lg bg-emerald-950/60 border border-emerald-500/40 text-[10px] font-mono text-emerald-300 font-bold">
          SOC {soc.toFixed(1)}%
        </div>
        <div className="px-2.5 py-1 rounded-lg bg-cyan-950/60 border border-cyan-500/40 text-[10px] font-mono text-cyan-300 font-bold">
          {temperature.toFixed(1)}°C
        </div>
      </div>

      <Canvas camera={{ position: [0, 2.5, 4.2], fov: 45 }}>
        <ambientLight intensity={0.9} />
        <directionalLight position={[10, 15, 10]} intensity={1.5} color="#FFFFFF" />
        <pointLight position={[-10, 5, -10]} intensity={0.8} color="#06B6D4" />
        <pointLight position={[0, -5, 5]} intensity={0.6} color="#10B981" />
        <Float speed={1.8} rotationIntensity={0.2} floatIntensity={0.4}>
          <BatteryHologramModel temperature={temperature} soc={soc} />
        </Float>
      </Canvas>

      {/* Bottom Hint */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 text-[10px] font-mono text-slate-400 bg-slate-950/80 backdrop-blur-md px-3 py-1 rounded-full border border-slate-800 pointer-events-none">
        Active 3D Holographic Rendering • Real-time Thermal Coupling
      </div>
    </div>
  );
};
