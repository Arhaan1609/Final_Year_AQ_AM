/**
 * Centralized dispatch triage utility.
 *
 * DESIGN RATIONALE (derived from fleet_vehicles.json analysis):
 * ─────────────────────────────────────────────────────────────
 * The dataset contains 778 vehicles. The `status` field was set during
 * dataset generation and exactly encodes the correct triage:
 *   - "active"   → 407 vehicles (Ready for Route)
 *   - "warning"  → 346 vehicles (Route Advisory)
 *   - "critical" →  25 vehicles (Service Hold)
 *
 * Key data facts that informed this design:
 *   - SOH range: 79.3%–99.3% (min=79.3, no vehicle below 75%)
 *   - Motor-battery gradient > 12°C: 775/778 vehicles (gradient rule is noise — DO NOT USE)
 *   - Only 1 vehicle has SOC < 25%; 53 have SOC < 30%
 *   - No vehicle has battery_temp > 45°C in the dataset
 *
 * Therefore:
 *   ✅ `status` field is the authoritative classification for ALL 778 vehicles
 *      (dropdown, fleet table, fleet switcher cards, count badges)
 *
 *   ✅ For the SELECTED VEHICLE only, live ML predictions can ESCALATE the
 *      triage level if they exceed safety thresholds — never de-escalate.
 *      e.g. if ML live-predicts SOH dropped to 74% mid-session, override to CRITICAL.
 *      But never show ADVISORY for an "active" vehicle just because SOH=84%.
 *
 *   ❌ DO NOT apply SOH < 85 / SOC < 30 / gradient thresholds fleet-wide.
 *      These values exist normally in the fleet and would wrongly flag everyone.
 */

export type TriageLevel = "CRITICAL" | "WARNING" | "NOMINAL";

// ─── 1. STATIC TRIAGE (fleet-wide, all 778 vehicles) ─────────────────────────
// Uses the raw `status` field as authoritative source. This is what the
// dropdown, fleet table, switcher cards, and count badges must use.

export function getStaticTriage(status: string): TriageLevel {
  if (status === "critical") return "CRITICAL";
  if (status === "warning")  return "WARNING";
  return "NOMINAL";
}

// ─── 2. LIVE TRIAGE (selected vehicle only, uses ML-predicted values) ─────────
// Starts from the static status and ONLY escalates if live ML predictions
// show a significant safety exceedance. Never de-escalates (live ML can't
// improve a vehicle the fleet already marked critical/warning).
//
// Escalation rules (conservative — only clear safety violations):
//   CRITICAL escalation: live SOH < 74%  OR  live Temp > 52°C
//   WARNING  escalation: live SOH < 79%  OR  live SOC < 20%  OR  live Temp > 46°C
//
// These are TIGHTER than the static ranges on purpose:
// live ML must be clearly worse than fleet baseline to override.

export function getLiveTriage(
  soh: number,
  soc: number,
  temp: number,
  rawStatus: string
): TriageLevel {
  const base = getStaticTriage(rawStatus);

  // Hard safety escalation — always apply regardless of base
  if (soh < 74 || temp > 52) return "CRITICAL";

  // Escalate from NOMINAL → WARNING only on clear violations
  if (base === "NOMINAL") {
    if (soh < 79 || soc < 20 || temp > 46) return "WARNING";
  }

  // Escalate from WARNING → CRITICAL only on extreme violations
  if (base === "WARNING") {
    if (soh < 74 || temp > 52) return "CRITICAL";
  }

  return base;
}

// ─── Backwards-compat alias ───────────────────────────────────────────────────
export function getVehicleTriage(v: { status: string }): TriageLevel {
  return getStaticTriage(v.status);
}

// ─── Label helpers ────────────────────────────────────────────────────────────

export function triageLabel(level: TriageLevel): string {
  if (level === "CRITICAL") return "SERVICE HOLD";
  if (level === "WARNING")  return "ADVISORY";
  return "ACTIVE";
}

export function triageBadgeClass(level: TriageLevel): string {
  if (level === "CRITICAL")
    return "bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800";
  if (level === "WARNING")
    return "bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800";
  return "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800";
}

export function triageDotClass(level: TriageLevel): string {
  if (level === "CRITICAL") return "bg-rose-500";
  if (level === "WARNING")  return "bg-amber-500";
  return "bg-emerald-500";
}
