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
    emerald: "border-emerald-500/30 dark:border-emerald-500/40",
    cyan: "border-cyan-500/30 dark:border-cyan-500/40",
    amber: "border-amber-500/30 dark:border-amber-500/40",
    crimson: "border-rose-500/30 dark:border-rose-500/40",
    purple: "border-purple-500/30 dark:border-purple-500/40",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={cn(
        "app-card p-5 relative overflow-hidden transition-all duration-200",
        glowStyles[glow],
        hoverEffect && "hover:border-slate-300 dark:hover:border-slate-600 hover:shadow-md cursor-default",
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
};
