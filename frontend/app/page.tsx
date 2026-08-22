"use client";

import React from "react";
import { LandingNavbar } from "../components/landing/LandingNavbar";
import { HeroScrollStory } from "../components/landing/HeroScrollStory";
import { LiveModelSandbox } from "../components/landing/LiveModelSandbox";
import { BentoArchitectureGrid } from "../components/landing/BentoArchitectureGrid";
import { FleetRoiCalculator } from "../components/landing/FleetRoiCalculator";
import { TechComparisonSection } from "../components/landing/TechComparisonSection";
import { FinalCallToAction } from "../components/landing/FinalCallToAction";

export default function MasterLandingPage() {
  return (
    <div className="min-h-screen bg-[var(--bg-page)] text-[var(--text-primary)] transition-colors relative selection:bg-emerald-500/20 selection:text-emerald-700 dark:selection:text-emerald-300">
      {/* 1. Apple-Style 300-Frame Pinned Hero: 3D Truck deconstructs with sleek floating HUD telemetry */}
      <HeroScrollStory />

      {/* 3. Interactive Live Telemetry & Multi-Model Sandbox */}
      <LiveModelSandbox />

      {/* 4. Enterprise Tri-Pillar DeepTech Bento Architecture Grid */}
      <BentoArchitectureGrid />

      {/* 5. Commercial Fleet ROI & Battery Lifespan Calculator */}
      <FleetRoiCalculator />

      {/* 6. Competitive Architecture Matrix (Legacy BMS vs Platform) */}
      <TechComparisonSection />

      {/* 7. High-Impact Closing Call-To-Action & Footer */}
      <FinalCallToAction />
    </div>
  );
}
