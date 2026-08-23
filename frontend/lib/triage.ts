/**
 * Centralized dispatch triage utility.
 * Single source of truth – same thresholds used by:
 *   - Header.tsx dropdown
 *   - FleetOverviewTab.tsx table STATUS column
 *   - OperationsView.tsx fleet switcher cards
 *   - OperationsView.tsx top banner (via isCritical / isWarning)
 *   - AIInsightsCard.tsx AI badge
 *
 * Rules (mirror copilot_service.py):
 *  CRITICAL  → SOH < 75 OR Temp > 48 OR raw status === "critical"
 *  WARNING   → SOH < 85 OR SOC < 30 OR Temp > 40 OR raw status === "warning"
 *              OR motor-battery thermal gradient > 12°C
 *  NOMINAL   → everything else
 */

export type TriageLevel = "CRITICAL" | "WARNING" | "NOMINAL";

export interface TriageVehicle {
  soh: number;
  soc: number;
  battery_temp: number;
  motor_temp?: number;
  status: string; // raw JSON status field
}

export function getVehicleTriage(v: TriageVehicle): TriageLevel {
  const thermalGradient = (v.motor_temp ?? 0) - v.battery_temp;

  if (
    v.status === "critical" ||
    v.soh < 75 ||
    v.battery_temp > 48
  ) {
    return "CRITICAL";
  }

  if (
    v.status === "warning" ||
    v.soh < 85 ||
    v.soc < 30 ||
    v.battery_temp > 40 ||
    thermalGradient > 12
  ) {
    return "WARNING";
  }

  return "NOMINAL";
}

/** Human-readable label for dropdown / table */
export function triageLabel(level: TriageLevel): string {
  if (level === "CRITICAL") return "SERVICE HOLD";
  if (level === "WARNING")  return "ADVISORY";
  return "ACTIVE";
}

/** Tailwind color classes for badge */
export function triageBadgeClass(level: TriageLevel): string {
  if (level === "CRITICAL")
    return "bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800";
  if (level === "WARNING")
    return "bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800";
  return "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800";
}

/** Tailwind dot color class for status dot */
export function triageDotClass(level: TriageLevel): string {
  if (level === "CRITICAL") return "bg-rose-500";
  if (level === "WARNING")  return "bg-amber-500";
  return "bg-emerald-500";
}
