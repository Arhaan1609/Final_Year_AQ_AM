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
    emerald: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/60",
    cyan: "bg-cyan-50 text-cyan-700 border-cyan-200 dark:bg-cyan-950/40 dark:text-cyan-300 dark:border-cyan-800/60",
    amber: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800/60",
    crimson: "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800/60",
    slate: "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800/80 dark:text-slate-300 dark:border-slate-700/50",
    purple: "bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:border-purple-800/60",
  };

  const dotColors = {
    emerald: "bg-emerald-500 animate-pulse",
    cyan: "bg-cyan-500 animate-pulse",
    amber: "bg-amber-500 animate-pulse",
    crimson: "bg-rose-500 animate-pulse",
    slate: "bg-slate-400",
    purple: "bg-purple-500",
  };

  const sizeStyles = {
    sm: "px-2 py-0.5 text-[11px]",
    md: "px-2.5 py-1 text-xs",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full font-semibold border tracking-wide select-none",
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
