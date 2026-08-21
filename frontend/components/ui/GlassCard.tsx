"use client";

import React from "react";
import { cn } from "../../lib/utils";
import { motion, HTMLMotionProps } from "framer-motion";

interface GlassCardProps extends HTMLMotionProps<"div"> {
  children: React.ReactNode;
  className?: string;
  glow?: "emerald" | "cyan" | "amber" | "crimson" | "purple" | "none";
  hoverEffect?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className,
  glow = "none",
  hoverEffect = false,
  ...props
}) => {
  const glowStyles = {
    none: "",
    emerald: "border-emerald-500/30 shadow-glow-emerald",
    cyan: "border-cyan-500/30 shadow-glow-cyan",
    amber: "border-amber-500/30 shadow-glow-amber",
    crimson: "border-rose-500/40 shadow-glow-crimson",
    purple: "border-purple-500/30 shadow-[0_0_25px_-5px_rgba(139,92,246,0.3)]",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        "glass-panel rounded-2xl p-5 relative overflow-hidden transition-all duration-300",
        glowStyles[glow],
        hoverEffect && "hover:border-slate-600 hover:bg-card-hover/90 cursor-default",
        className
      )}
      {...props}
    >
      {/* Subtle glass reflection highlight */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-slate-500/20 to-transparent pointer-events-none" />
      {children}
    </motion.div>
  );
};
