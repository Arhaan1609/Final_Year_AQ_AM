/**
 * Fleet Copilot API Client & Intelligent Intent Engine.
 * Simulates tool-calling agent interaction backed by the ML backend.
 */

import { CopilotMessage, CopilotResponse, CopilotToolCall } from "./types";
import { isMockMode, predictThermal, predictKneePoint, predictDriverBehavior, diagnoseVehicle } from "./client";
import { MOCK_VEHICLES } from "./mock";

const COPILOT_URL = process.env.NEXT_PUBLIC_COPILOT_URL || "http://localhost:8001/chat";

export async function askCopilot(
  message: string,
  history: CopilotMessage[]
): Promise<CopilotResponse> {
  const query = message.toLowerCase();

  // If live mode is on and external copilot URL is specified, try posting
  if (!isMockMode() && process.env.NEXT_PUBLIC_COPILOT_URL) {
    try {
      const res = await fetch(COPILOT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, history }),
      });
      if (res.ok) {
        return (await res.json()) as CopilotResponse;
      }
    } catch (e) {
      console.warn("External Copilot endpoint unreachable, using local AI engine:", e);
    }
  }

  // Artificial AI thinking delay
  await new Promise((r) => setTimeout(r, 600 + Math.random() * 400));

  // 1. Identify vehicle in question
  const foundVehicle = MOCK_VEHICLES.find((v) =>
    query.includes(v.id.toLowerCase())
  ) || MOCK_VEHICLES[0]; // default to first

  const toolCalls: CopilotToolCall[] = [];

  // 2. Intent: Thermal Risk / Overheating
  if (query.includes("thermal") || query.includes("heat") || query.includes("temperature") || query.includes("overheat")) {
    const thermalRes = await predictThermal({
      vbt: foundVehicle.battery_temp,
      vct: foundVehicle.controller_temp,
      vmt: foundVehicle.motor_temp,
      vbv: foundVehicle.voltage,
      vbc: foundVehicle.current,
      soc: foundVehicle.soc,
      speed: foundVehicle.speed,
    });

    toolCalls.push({
      tool: "predict_thermal",
      args: {
        vbt: foundVehicle.battery_temp,
        vct: foundVehicle.controller_temp,
        vmt: foundVehicle.motor_temp,
      },
      result: thermalRes,
    });

    if (thermalRes.severity === "CRITICAL" || thermalRes.severity === "WARNING") {
      return {
        reply: `⚠️ **Thermal Alert for ${foundVehicle.id}:**\n\nThe 200-Tree Random Forest classifier detected **${thermalRes.safety_status}** with a risk probability of **${(thermalRes.risk_probability * 100).toFixed(1)}%**.\n\n- **Battery Temp:** ${foundVehicle.battery_temp}°C\n- **Controller Temp:** ${foundVehicle.controller_temp}°C\n- **Motor Temp:** ${foundVehicle.motor_temp}°C\n\n**Action Directive:** ${thermalRes.recommended_action}`,
        toolCalls,
      };
    } else {
      return {
        reply: `✅ **Thermal Status Nominal for ${foundVehicle.id}:**\n\nAll three thermal zones (Battery: ${foundVehicle.battery_temp}°C, Controller: ${foundVehicle.controller_temp}°C, Motor: ${foundVehicle.motor_temp}°C) are well within safe bounds. Risk probability is negligible at **${(thermalRes.risk_probability * 100).toFixed(1)}%**.`,
        toolCalls,
      };
    }
  }

  // 3. Intent: Knee Point / Aging / Degradation
  if (query.includes("knee") || query.includes("aging") || query.includes("degradation") || query.includes("cycles")) {
    const kneeRes = await predictKneePoint({
      charge_cycle_count: foundVehicle.charge_cycle_count,
      capacity: foundVehicle.soh,
      voltage: foundVehicle.voltage,
      battery_temp: foundVehicle.battery_temp,
      current: foundVehicle.current,
      soc: foundVehicle.soc,
      speed: foundVehicle.speed,
    });

    toolCalls.push({
      tool: "predict_knee_point",
      args: {
        charge_cycle_count: foundVehicle.charge_cycle_count,
        capacity: foundVehicle.soh,
      },
      result: kneeRes,
    });

    return {
      reply: `📉 **Degradation Knee Prognostics for ${foundVehicle.id}:**\n\n- **Current Cycles:** ${foundVehicle.charge_cycle_count} cycles\n- **Remaining Cycles to Knee Point ($RUL_{to\\_knee}$):** **${kneeRes.rul_to_knee_cycles} cycles**\n- **State:** **${kneeRes.knee_risk_state}**\n- **Degradation Slope:** \`${kneeRes.aging_rate_slope} SOH%/cycle\`\n\n**BMS Directive:** ${kneeRes.bms_directive}`,
      toolCalls,
    };
  }

  // 4. Intent: Driver Behavior / Aggression
  if (query.includes("driver") || query.includes("behavior") || query.includes("aggression") || query.includes("stress")) {
    const behaviorRes = await predictDriverBehavior({
      harsh_accel_count: foundVehicle.status === "warning" ? 6 : 2,
      harsh_brake_count: 3,
      harsh_corner_count: 2,
      speed_variance: 8.2,
      avg_speed: foundVehicle.speed,
      max_speed: 68.0,
      battery_temp_max: foundVehicle.battery_temp + 3,
      max_discharge_current: 38.0,
    });

    toolCalls.push({
      tool: "predict_driver_behavior",
      args: {
        driver: foundVehicle.driver,
        avg_speed: foundVehicle.speed,
      },
      result: behaviorRes,
    });

    return {
      reply: `🏎️ **Driver Behavioral Profiling for ${foundVehicle.driver} (${foundVehicle.id}):**\n\n- **Aggressiveness Index ($AI$):** **${behaviorRes.aggressiveness_index} / 1.0**\n- **Battery Stress Index ($BSI$):** **${behaviorRes.battery_stress_index} / 1.0**\n- **Classification:** **${behaviorRes.driver_classification}**\n- **Projected SOH Penalty:** **-${behaviorRes.estimated_annual_soh_penalty_pct}% / year**\n\n${behaviorRes.recommendations.map((r) => `• ${r}`).join("\n")}`,
      toolCalls,
    };
  }

  // 5. Default / Fleet Health Overview Intent
  const diagRes = await diagnoseVehicle({
    vehicle_id: foundVehicle.id,
    oem_model: foundVehicle.model,
    soc: foundVehicle.soc,
    voltage: foundVehicle.voltage,
    current: foundVehicle.current,
    battery_temp: foundVehicle.battery_temp,
    controller_temp: foundVehicle.controller_temp,
    motor_temp: foundVehicle.motor_temp,
    speed: foundVehicle.speed,
  });

  toolCalls.push({
    tool: "diagnose_vehicle",
    args: { vehicle_id: foundVehicle.id },
    result: diagRes,
  });

  return {
    reply: `📊 **Diagnostic Summary for ${foundVehicle.id} (${foundVehicle.model}):**\n\n- **Overall Digital Twin Health Score:** **${diagRes.overall_health_score} / 100**\n- **State of Charge (SOC):** ${foundVehicle.soc}%\n- **State of Health (SOH):** ${foundVehicle.soh}%\n- **Remaining Useful Life:** ${foundVehicle.rul} cycles\n- **Thermal Status:** ${diagRes.thermal_status.safety_status} (${diagRes.thermal_status.severity})\n\n**Action Items:**\n${diagRes.action_items.map((item) => `• ${item}`).join("\n")}`,
    toolCalls,
  };
}
