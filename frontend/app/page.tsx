"use client";

import React from "react";
import { LandingNavbar } from "../components/landing/LandingNavbar";
import { HeroSection } from "../components/landing/HeroSection";
import { AppleScrollSequence } from "../components/landing/AppleScrollSequence";
import { ScrollIntelligenceStory } from "../components/landing/ScrollIntelligenceStory";
import { LiveModelSandbox } from "../components/landing/LiveModelSandbox";
import { BentoArchitectureGrid } from "../components/landing/BentoArchitectureGrid";
import { FleetRoiCalculator } from "../components/landing/FleetRoiCalculator";
import { TechComparisonSection } from "../components/landing/TechComparisonSection";
import { FinalCallToAction } from "../components/landing/FinalCallToAction";

export default function MasterLandingPage() {
  return (
    <div className="min-h-screen bg-[var(--bg-page)] text-[var(--text-primary)] transition-colors relative selection:bg-emerald-500/20 selection:text-emerald-700 dark:selection:text-emerald-300">
      {/* 1. Sleek Floating Header */}
      <LandingNavbar />

      {/* 2. Venture-Grade Hero with 3D Cybernetic Canvas */}
      <HeroSection />

      {/* 3. Apple-Style 300-Frame Pinned Canvas Scroll Sequence */}
      <AppleScrollSequence />

      {/* 4. Pinned 4-Stage Scroll-Scrubbed Intelligence Pipeline */}
      <ScrollIntelligenceStory />

      {/* 5. Interactive Live Telemetry & Model Sandbox */}
      <LiveModelSandbox />

      {/* 6. Enterprise Tri-Pillar Bento Grid */}
      <BentoArchitectureGrid />

      {/* 7. Commercial Fleet ROI & Lifespan Calculator */}
      <FleetRoiCalculator />

      {/* 8. Competitive Architecture Matrix (Legacy BMS vs Platform) */}
      <TechComparisonSection />

      {/* 9. High-Conversion Closing Section */}
      <FinalCallToAction />
    </div>
  );
}
