/**
 * Centralized dispatch triage utility — TWO distinct functions:
 *
 * 1. getStaticTriage(v)
 *    ─ Used by: Header dropdown, Fleet table STATUS column, fleet switcher cards
 *    ─ Source: raw JSON `status` field only ("active" / "warning" / "critical")
 *    ─ Reason: we cannot run live ML on all 778 vehicles simultaneously;
 *              the fleet database `status` is already the fleet operator's
 *              assessment and is the correct reference for the directory.
 *
 * 2. getLiveTriage(soh, soc, temp, motorTemp, rawStatus)
 *    ─ Used by: OperationsView banner, AIInsightsCard badge (selected vehicle only)
 *    ─ Source: live ML predictions + same threshold rules as copilot_service.py
 *    ─ Rules:
 *        CRITICAL  → SOH < 75  OR  Temp > 48  OR  raw status === "critical"
 *        WARNING   → SOH < 85  OR  SOC < 30   OR  Temp > 40
 *                    OR motor-battery gradient > 12°C  OR raw status === "warning"
 *        NOMINAL   → everything else
 */

export type TriageLevel = "CRITICAL" | "WARNING" | "NOMINAL";

export interface TriageVehicle {
  soh: number;
  soc: number;
  battery_temp: number;
  motor_temp?: number;
  status: string; // raw JSON status field: "active" | "warning" | "critical"
}

// ─── 1. STATIC TRIAGE (fleet-wide, no live ML) ──────────────────────────────
// Uses only the raw `status` field from fleet_vehicles.json.
// This is what the dropdown and fleet table should show for all 778 vehicles.

export function getStaticTriage(v: Pick<TriageVehicle, "status">): TriageLevel {
  if (v.status === "critical") return "CRITICAL";
  if (v.status === "warning")  return "WARNING";
  return "NOMINAL";
}

// ─── 2. LIVE TRIAGE (selected vehicle only, uses ML-predicted values) ────────
// Used in OperationsView banner and AIInsightsCard for the currently selected
// vehicle where SOC/SOH/temp come from live ML predictions.

export function getLiveTriage(
  soh: number,
  soc: number,
  temp: number,
  motorTemp: number | undefined,
  rawStatus: string
): TriageLevel {
  const gradient = (motorTemp ?? 0) - temp;

  if (rawStatus === "critical" || soh < 75 || temp > 48) {
    return "CRITICAL";
  }
  if (
    rawStatus === "warning" ||
    soh < 85 ||
    soc < 30 ||
    temp > 40 ||
    gradient > 12
  ) {
    return "WARNING";
  }
  return "NOMINAL";
}

// ─── Legacy alias (for callers that still use getVehicleTriage) ──────────────
// Maps to STATIC triage to avoid breaking anything.
export function getVehicleTriage(v: Pick<TriageVehicle, "status">): TriageLevel {
  return getStaticTriage(v);
}

// ─── Label helpers ───────────────────────────────────────────────────────────

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
