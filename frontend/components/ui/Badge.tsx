import React from "react";
import { cn } from "../../lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "emerald" | "cyan" | "amber" | "crimson" | "slate" | "purple";
  size?: "sm" | "md";
  className?: string;
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "slate",
  size = "md",
  className,
  dot = false,
}) => {
  const variantStyles = {
    emerald: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    cyan: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    amber: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    crimson: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    slate: "bg-slate-800/80 text-slate-300 border-slate-700/50",
    purple: "bg-purple-500/10 text-purple-300 border-purple-500/20",
  };

  const dotColors = {
    emerald: "bg-emerald-400 animate-pulse",
    cyan: "bg-cyan-400 animate-pulse",
    amber: "bg-amber-400 animate-pulse",
    crimson: "bg-rose-400 animate-pulse",
    slate: "bg-slate-400",
    purple: "bg-purple-400",
  };

  const sizeStyles = {
    sm: "px-2 py-0.5 text-[11px]",
    md: "px-2.5 py-1 text-xs",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full font-medium border tracking-wide select-none",
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {dot && <span className={cn("w-1.5 h-1.5 rounded-full", dotColors[variant])} />}
      {children}
    </span>
  );
};
