/**
 * Unified API Data Schemas & Types for EV Battery Intelligence Platform
 */

// 1. Health
export interface HealthResponse {
  status: string;
  modules: {
    module_a_fleet: {
      SOC: boolean;
      SOH: boolean;
      RUL: boolean;
      Mileage: boolean;
    };
    module_b_battery_iq: boolean;
    module_c_babms: boolean;
  };
  timestamp: string;
}

// 2. Module A — Predictions
export interface ModelPredictionResponse {
  task: "SOC" | "SOH" | "RUL" | "Mileage";
  model_used: string;
  prediction: number;
  unit: string;
}

export interface SOCRequest {
  battery_voltage: number;
  battery_temp: number;
  battery_current: number;
  abs_current?: number;
  is_charging?: number;
  odometer?: number;
  odometer_diff?: number;
  voltage_deviation?: number;
  temp_stress_index?: number;
  drive_mode_encoded?: number;
  hour?: number;
  day_of_week?: number;
  month?: number;
  is_weekend?: number;
  is_peak?: number;
  oem_encoded?: number;
  model_encoded?: number;
}

export interface SOHRequest {
  battery_voltage: number;
  battery_temp: number;
  battery_current: number;
  abs_current?: number;
  odometer?: number;
  odometer_diff?: number;
  charge_cycle_count?: number;
  mile_avg?: number;
  miles_per_charge?: number;
  days_in_service?: number;
  degradation_factor?: number;
  temp_stress_index?: number;
  voltage_deviation?: number;
  oem_encoded?: number;
  model_encoded?: number;
}

export interface RULRequest {
  odometer?: number;
  soc_at_charge?: number;
  mile_avg?: number;
  miles_per_charge?: number;
  days_in_service?: number;
  degradation_factor?: number;
  soh_mean?: number;
  miles_per_charge_rolling_3?: number;
  miles_per_charge_rolling_5?: number;
  miles_per_charge_rolling_10?: number;
  oem_encoded?: number;
  model_encoded?: number;
}

export interface MileageRequest {
  run_kms: number;
  avg_speed: number;
  max_speed: number;
  trip_duration_hrs?: number;
  stoppage_count?: number;
  energy_efficiency?: number;
  trip_intensity?: number;
  speed_ratio?: number;
  stoppage_density?: number;
  energy_utilized?: number;
  hour?: number;
  day_of_week?: number;
  month?: number;
  is_weekend?: number;
  is_peak?: number;
  oem_encoded?: number;
  city_encoded?: number;
}

// 3. Module B — Thermal Safety & Deep SOH
export interface ThermalRequest {
  vbt: number; // Battery Temp
  vct: number; // Controller Temp
  vmt: number; // Motor Temp
  vbv: number; // Battery Voltage
  vbc: number; // Battery Current
  soc: number;
  speed: number;
}

export interface ThermalResponse {
  safety_status: "SAFE" | "WARNING" | "CRITICAL MOTOR OVERHEAT" | "CRITICAL DEEP DISCHARGE" | string;
  risk_probability: number;
  severity: "NORMAL" | "WARNING" | "CRITICAL" | string;
  active_alert: string;
  recommended_action: string;
}

export interface SOHDeepRequest {
  vehicle_id: string;
  sequence: number[][]; // 10 timesteps of [voltage, current, temp, soc]
}

export interface SOHDeepResponse {
  vehicle_id: string;
  estimated_soh_percent: number;
  capacity_state: string;
  confidence_score: number;
  requires_balancing: boolean;
}

export interface DiagnoseRequest {
  vehicle_id: string;
  oem_model: string;
  soc: number;
  voltage: number;
  current: number;
  battery_temp: number;
  controller_temp: number;
  motor_temp: number;
  speed: number;
}

export interface DiagnoseResponse {
  vehicle_id: string;
  overall_health_score: number;
  thermal_status: {
    safety_status: string;
    risk_probability: number;
    severity: string;
  };
  soh_status: {
    estimated_soh_percent: number;
    capacity_state: string;
  };
  critical_alert: boolean;
  action_items: string[];
}

// 4. Module C — Behavior & Knee Prognostics
export interface DriverBehaviorRequest {
  harsh_accel_count: number;
  harsh_brake_count: number;
  harsh_corner_count: number;
  speed_variance: number;
  avg_speed: number;
  max_speed: number;
  battery_temp_max: number;
  max_discharge_current: number;
}

export interface DriverBehaviorResponse {
  aggressiveness_index: number;
  battery_stress_index: number;
  driver_classification: string;
  estimated_annual_soh_penalty_pct: number;
  recommendations: string[];
}

export interface KneePredictionRequest {
  charge_cycle_count: number;
  capacity: number;
  voltage: number;
  battery_temp: number;
  current: number;
  soc: number;
  speed: number;
}

export interface KneePredictionResponse {
  rul_to_knee_cycles: number;
  is_post_knee: boolean;
  knee_risk_state: string;
  aging_rate_slope: number;
  bms_directive: string;
}

export interface MetaEnsembleRequest {
  vehicle_id: string;
  charge_cycle_count: number;
  battery_voltage: number;
  battery_temp: number;
  battery_current: number;
  soc: number;
  harsh_accel_count: number;
  speed_variance: number;
}

export interface MetaEnsembleResponse {
  vehicle_id: string;
  estimated_soh: number;
  rul_to_knee_cycles: number;
  driver_aggressiveness_index: number;
  battery_stress_index: number;
  unified_health_grade: string;
  executive_summary: string;
}

// 5. Vehicle Entity for UI Selection
export interface FleetVehicle {
  id: string;
  model: string;
  fleet: string;
  driver: string;
  soc: number;
  soh: number;
  rul: number;
  mileage: number;
  battery_temp: number;
  controller_temp: number;
  motor_temp: number;
  voltage: number;
  current: number;
  speed: number;
  charge_cycle_count: number;
  status: "active" | "charging" | "warning" | "critical";
  lastPing: string;
}

// 6. Copilot
export interface CopilotToolCall {
  tool: string;
  args: Record<string, any>;
  result: Record<string, any>;
}

export interface CopilotMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  timestamp: string;
  toolCalls?: CopilotToolCall[];
}

export interface CopilotResponse {
  reply: string;
  toolCalls?: CopilotToolCall[];
}
