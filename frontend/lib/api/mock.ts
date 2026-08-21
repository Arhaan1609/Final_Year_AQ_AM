/**
 * Realistic Mock Data Generator for EV Battery Intelligence Platform.
 * Supports offline demoing with realistic variance and simulated latency.
 */

import {
  HealthResponse,
  ModelPredictionResponse,
  SOCRequest,
  SOHRequest,
  RULRequest,
  MileageRequest,
  ThermalRequest,
  ThermalResponse,
  SOHDeepRequest,
  SOHDeepResponse,
  DiagnoseRequest,
  DiagnoseResponse,
  DriverBehaviorRequest,
  DriverBehaviorResponse,
  KneePredictionRequest,
  KneePredictionResponse,
  MetaEnsembleRequest,
  MetaEnsembleResponse,
  FleetVehicle,
} from "./types";

// Static fleet of commercial vehicles
// Enterprise Fleet Generation Helper
const HUBS = [
  { city: "Ahmedabad", name: "Ahmedabad Logistics Hub 1", prefix: "GJ01" },
  { city: "Surat", name: "Surat Textile Express Hub", prefix: "GJ05" },
  { city: "Vadodara", name: "Vadodara Pharma Cold-Chain", prefix: "GJ06" },
  { city: "Rajkot", name: "Rajkot Heavy Freight Hub", prefix: "GJ03" },
  { city: "Mumbai", name: "Mumbai Central Cargo Hub", prefix: "MH01" },
  { city: "Pune", name: "Pune Auto Cluster Depot", prefix: "MH12" },
  { city: "Bengaluru", name: "Bengaluru Tech Logistics Hub", prefix: "KA03" },
  { city: "Delhi NCR", name: "Delhi NCR Northern Corridor", prefix: "DL01" },
  { city: "Hyderabad", name: "Hyderabad Cyber Fleet Depot", prefix: "TS09" },
  { city: "Chennai", name: "Chennai Port Transit Facility", prefix: "TN09" },
];

const OEM_MODELS = [
  { model: "Euler HiLoad EV (12.4 kWh)", capacity: 12.4, nominalV: 76.8 },
  { model: "Tata Ace EV (8.2 kWh)", capacity: 8.2, nominalV: 74.0 },
  { model: "Mahindra Treo Zor (7.37 kWh)", capacity: 7.37, nominalV: 72.0 },
  { model: "Piaggio Ape E-City (5.4 kWh)", capacity: 5.4, nominalV: 51.2 },
  { model: "Altigreen neEV (11.0 kWh)", capacity: 11.0, nominalV: 76.8 },
  { model: "Ashok Leyland Bada Dost EV (15.0 kWh)", capacity: 15.0, nominalV: 96.0 },
];

const DRIVER_NAMES = [
  "Rajesh Sharma", "Amit Patel", "Vikram Desai", "Sunil Verma", "Hardik Shah",
  "Mehul Dave", "Sanjay Joshi", "Dinesh Parmar", "Pradeep Yadav", "Naresh Rathod",
  "Kiran Reddy", "Anil Kulkarni", "Manoj Singh", "Prakash Rao", "Vinod Nair",
  "Ramesh Gupta", "Suresh Kumar", "Santosh Jha", "Deepak Solanki", "Ajay Chauhan",
  "Girish Bhatt", "Ravi Shankar", "Mahesh Chandra", "Jignesh Thakor", "Chetan Mehta",
];

function buildEnterpriseFleet(): FleetVehicle[] {
  const fleet: FleetVehicle[] = [];

  // 1. Primary Benchmark Vehicles
  fleet.push(
    {
      id: "GJ05CV6564",
      model: "Euler HiLoad EV (12.4 kWh)",
      fleet: "Ahmedabad Logistics Hub 1",
      driver: "Rajesh Sharma",
      soc: 82.4,
      soh: 94.2,
      rul: 1180,
      mileage: 108.5,
      battery_temp: 33.2,
      controller_temp: 41.5,
      motor_temp: 54.0,
      voltage: 75.8,
      current: -18.4,
      speed: 34.2,
      charge_cycle_count: 215,
      status: "active",
      lastPing: "Just now",
    },
    {
      id: "GJ05CU1234",
      model: "Euler HiLoad EV (12.4 kWh)",
      fleet: "Ahmedabad Express Cargo",
      driver: "Amit Patel",
      soc: 45.1,
      soh: 88.6,
      rul: 760,
      mileage: 92.0,
      battery_temp: 42.8,
      controller_temp: 56.2,
      motor_temp: 71.4,
      voltage: 71.2,
      current: -38.2,
      speed: 48.0,
      charge_cycle_count: 512,
      status: "warning",
      lastPing: "2 mins ago",
    },
    {
      id: "GJ05BT9988",
      model: "Mahindra Treo Zor",
      fleet: "Surat Last-Mile Delivery",
      driver: "Vikram Desai",
      soc: 96.0,
      soh: 98.4,
      rul: 1450,
      mileage: 118.2,
      battery_temp: 29.5,
      controller_temp: 36.0,
      motor_temp: 46.5,
      voltage: 78.4,
      current: 12.0,
      speed: 0.0,
      charge_cycle_count: 85,
      status: "charging",
      lastPing: "1 min ago",
    },
    {
      id: "GJ05AX4321",
      model: "Euler HiLoad EV (12.4 kWh)",
      fleet: "Vadodara Pharma Cold-Chain",
      driver: "Sunil Verma",
      soc: 24.5,
      soh: 81.3,
      rul: 310,
      mileage: 84.5,
      battery_temp: 48.6,
      controller_temp: 64.0,
      motor_temp: 82.5,
      voltage: 68.4,
      current: -45.0,
      speed: 55.0,
      charge_cycle_count: 890,
      status: "critical",
      lastPing: "30 secs ago",
    }
  );

  // 2. Generate 46 additional realistic enterprise chassis (Total 50)
  for (let i = 5; i <= 50; i++) {
    const hub = HUBS[(i - 1) % HUBS.length];
    const oem = OEM_MODELS[(i - 1) % OEM_MODELS.length];
    const driver = DRIVER_NAMES[(i - 1) % DRIVER_NAMES.length];

    const alpha1 = String.fromCharCode(65 + ((i * 3) % 26));
    const alpha2 = String.fromCharCode(65 + ((i * 7) % 26));
    const num = String(1000 + ((i * 137) % 9000));
    const id = `${hub.prefix}${alpha1}${alpha2}${num}`;

    // Status distribution: 70% active, 15% warning, 10% charging, 5% critical
    const statusRand = ((i * 17) % 100);
    let status: FleetVehicle["status"] = "active";
    if (statusRand > 92) status = "critical";
    else if (statusRand > 75) status = "warning";
    else if (statusRand > 65) status = "charging";

    const cycles = 50 + ((i * 29) % 950);
    const soh = Math.max(76.0, 99.5 - (cycles * 0.022) + ((i % 5) * 0.4));
    const soc = status === "charging" ? 92.0 + (i % 8) : 20.0 + ((i * 19) % 75);
    const tempBase = status === "critical" ? 47.0 : status === "warning" ? 41.0 : 30.0 + (i % 7);
    const speed = status === "charging" ? 0 : 25 + ((i * 7) % 35);
    const current = status === "charging" ? 15.0 + (i % 10) : -(12.0 + ((i * 5) % 35));
    const voltage = oem.nominalV + (soc / 100) * 6.0 - 3.0;
    const rul = Math.max(150, Math.floor(1500 - cycles * 1.3));
    const mileage = 75 + (soh * 0.42);

    fleet.push({
      id,
      model: oem.model,
      fleet: hub.name,
      driver,
      soc: Math.round(soc * 10) / 10,
      soh: Math.round(soh * 10) / 10,
      rul,
      mileage: Math.round(mileage * 10) / 10,
      battery_temp: Math.round(tempBase * 10) / 10,
      controller_temp: Math.round((tempBase + 8.5) * 10) / 10,
      motor_temp: Math.round((tempBase + 18.0) * 10) / 10,
      voltage: Math.round(voltage * 10) / 10,
      current: Math.round(current * 10) / 10,
      speed: Math.round(speed * 10) / 10,
      charge_cycle_count: cycles,
      status,
      lastPing: `${(i % 5) + 1} mins ago`,
    });
  }

  return fleet;
}

export const MOCK_VEHICLES: FleetVehicle[] = buildEnterpriseFleet();

// Dynamic Custom Vehicle Resolver for any search query
export function getOrCreateCustomVehicle(chassisQuery: string): FleetVehicle {
  const cleanId = chassisQuery.trim().toUpperCase();
  const existing = MOCK_VEHICLES.find(
    (v) => v.id.toUpperCase() === cleanId || v.id.includes(cleanId)
  );
  if (existing) return existing;

  // On-demand provision a new digital twin for any custom chassis!
  const customVehicle: FleetVehicle = {
    id: cleanId,
    model: "Enterprise Commercial EV (Custom Pack)",
    fleet: "National Dynamic Fleet Registry",
    driver: "Enterprise Operator",
    soc: 78.5,
    soh: 92.4,
    rul: 1050,
    mileage: 104.0,
    battery_temp: 32.5,
    controller_temp: 40.0,
    motor_temp: 52.0,
    voltage: 75.2,
    current: -19.5,
    speed: 35.0,
    charge_cycle_count: 240,
    status: "active",
    lastPing: "Just now (Live Query)",
  };

  MOCK_VEHICLES.unshift(customVehicle);
  return customVehicle;
}

// Helper: random jitter
function jitter(base: number, percent: number = 2): number {
  const delta = base * (percent / 100) * (Math.random() * 2 - 1);
  return Number((base + delta).toFixed(2));
}

// 1. Health
export function getMockHealth(): HealthResponse {
  return {
    status: "ok",
    modules: {
      module_a_fleet: { SOC: true, SOH: true, RUL: true, Mileage: true },
      module_b_battery_iq: true,
      module_c_babms: true,
    },
    timestamp: new Date().toISOString(),
  };
}

// 2. Module A — SOC
export function getMockSOC(req: SOCRequest): ModelPredictionResponse {
  // Approximate open-circuit voltage model
  let est = ((req.battery_voltage - 64.0) / (82.0 - 64.0)) * 100;
  est = Math.max(5, Math.min(100, est));
  return {
    task: "SOC",
    model_used: "KNN (K-Nearest Neighbors)",
    prediction: jitter(est, 1.5),
    unit: "%",
  };
}

// 3. Module A — SOH Tabular
export function getMockSOH(req: SOHRequest): ModelPredictionResponse {
  const cycle = req.charge_cycle_count || 200;
  const fade = (cycle / 1500) * 20; // 20% loss over 1500 cycles
  const est = Math.max(70, Math.min(100, 100 - fade));
  return {
    task: "SOH",
    model_used: "XGBoost Regressor",
    prediction: jitter(est, 0.8),
    unit: "%",
  };
}

// 4. Module A — RUL
export function getMockRUL(req: RULRequest): ModelPredictionResponse {
  const odo = req.odometer || 15000;
  const remaining = Math.max(50, 1500 - Math.floor(odo / 30));
  return {
    task: "RUL",
    model_used: "Gradient Boosting",
    prediction: jitter(remaining, 2),
    unit: "cycles",
  };
}

// 5. Module A — Mileage
export function getMockMileage(req: MileageRequest): ModelPredictionResponse {
  const baseRange = 110;
  const speedPenalty = (req.avg_speed / 50) * 12;
  const est = Math.max(40, baseRange - speedPenalty);
  return {
    task: "Mileage",
    model_used: "XGBoost Regressor",
    prediction: jitter(est, 2),
    unit: "km",
  };
}

// 6. Module B — Thermal Safety
export function getMockThermal(req: ThermalRequest): ThermalResponse {
  const maxTemp = Math.max(req.vbt, req.vct, req.vmt);
  
  if (req.vmt > 75 || req.vbt > 50) {
    return {
      safety_status: "CRITICAL MOTOR OVERHEAT",
      risk_probability: 0.89,
      severity: "CRITICAL",
      active_alert: `High thermal hazard: Motor at ${req.vmt}°C exceeds safety threshold of 75°C.`,
      recommended_action: "Trigger immediate power derating (50% max current) and initiate coolant purge.",
    };
  } else if (req.vbt > 42 || req.vct > 55 || req.vmt > 65) {
    return {
      safety_status: "WARNING",
      risk_probability: 0.42,
      severity: "WARNING",
      active_alert: `Elevated thermal zone: Battery at ${req.vbt}°C approaching maximum operating tolerance.`,
      recommended_action: "Engage auxiliary cooling fans and advise driver to avoid heavy acceleration.",
    };
  } else {
    return {
      safety_status: "SAFE",
      risk_probability: 0.04,
      severity: "NORMAL",
      active_alert: "All 3 thermal zones (Battery, Inverter, Motor) within optimal parameters.",
      recommended_action: "Standard operation; thermal equilibrium maintained.",
    };
  }
}

// 7. Module B — SOH Deep (PyTorch CNN-LSTM)
export function getMockSOHDeep(req: SOHDeepRequest): SOHDeepResponse {
  return {
    vehicle_id: req.vehicle_id || "GJ05CV6564",
    estimated_soh_percent: jitter(92.4, 1.2),
    capacity_state: "Optimal (Tier 1)",
    confidence_score: 0.954,
    requires_balancing: false,
  };
}

// 8. Module B — Full Vehicle Diagnosis
export function getMockDiagnose(req: DiagnoseRequest): DiagnoseResponse {
  const thermal = getMockThermal({
    vbt: req.battery_temp,
    vct: req.controller_temp,
    vmt: req.motor_temp,
    vbv: req.voltage,
    vbc: req.current,
    soc: req.soc,
    speed: req.speed,
  });

  const isCritical = thermal.severity === "CRITICAL";
  const baseScore = isCritical ? 62 : thermal.severity === "WARNING" ? 78 : 94.5;

  return {
    vehicle_id: req.vehicle_id,
    overall_health_score: jitter(baseScore, 2),
    thermal_status: {
      safety_status: thermal.safety_status,
      risk_probability: thermal.risk_probability,
      severity: thermal.severity,
    },
    soh_status: {
      estimated_soh_percent: jitter(93.8, 1),
      capacity_state: isCritical ? "Degraded (Tier 3)" : "Optimal (Tier 1)",
    },
    critical_alert: isCritical,
    action_items: isCritical
      ? [
          "Immediate inspection of cooling circuit recommended.",
          "Limit discharge current to prevent accelerated thermal degradation.",
        ]
      : [
          "Battery pack operating at nominal thermal equilibrium.",
          "Cell balance acceptable across sub-modules.",
        ],
  };
}

// 9. Module C — Driver Behavior
export function getMockDriverBehavior(req: DriverBehaviorRequest): DriverBehaviorResponse {
  const totalEvents = req.harsh_accel_count * 2 + req.harsh_brake_count * 1.5 + req.harsh_corner_count;
  let ai = Math.min(1.0, Math.max(0.05, totalEvents / 15 + (req.speed_variance / 20)));
  let bsi = Math.min(1.0, Math.max(0.08, ai * 0.7 + (req.max_discharge_current / 100) * 0.3));

  ai = Number(ai.toFixed(3));
  bsi = Number(bsi.toFixed(3));

  let classification = "Smooth & Energy-Conscious";
  let penalty = 0.8;

  if (ai > 0.65) {
    classification = "Aggressive Fleet Operator";
    penalty = 4.7;
  } else if (ai > 0.35) {
    classification = "Moderate Commuter";
    penalty = 2.1;
  }

  return {
    aggressiveness_index: ai,
    battery_stress_index: bsi,
    driver_classification: classification,
    estimated_annual_soh_penalty_pct: penalty,
    recommendations: [
      ai > 0.5
        ? "Advise driver to moderate rapid throttle tip-in to protect battery longevity."
        : "Driver behavior maintains optimal electrochemical longevity.",
      `Peak current discharge of ${req.max_discharge_current}A induces ${bsi > 0.5 ? 'elevated' : 'nominal'} cell stress.`,
    ],
  };
}

// 10. Module C — Knee Point
export function getMockKneePoint(req: KneePredictionRequest): KneePredictionResponse {
  const cycle = req.charge_cycle_count || 200;
  const estimatedKneeCycle = 950;
  const remaining = Math.max(0, estimatedKneeCycle - cycle);
  const isPost = cycle >= estimatedKneeCycle;

  return {
    rul_to_knee_cycles: jitter(remaining, 3),
    is_post_knee: isPost,
    knee_risk_state: isPost
      ? "Post-Knee Accelerated Degradation"
      : remaining < 200
      ? "Approaching Knee Onset (<200 cycles)"
      : "Pre-Knee Safe Degradation Regime",
    aging_rate_slope: isPost ? -0.058 : -0.016,
    bms_directive: isPost
      ? "Apply conservative charging limits (0.5C max). Inspect pack for cell capacity divergence."
      : "Standard CC-CV fast charging permitted.",
  };
}

// 11. Module C — Meta-Ensemble
export function getMockMetaEnsemble(req: MetaEnsembleRequest): MetaEnsembleResponse {
  const knee = getMockKneePoint({
    charge_cycle_count: req.charge_cycle_count,
    capacity: 94.0,
    voltage: req.battery_voltage,
    battery_temp: req.battery_temp,
    current: req.battery_current,
    soc: req.soc,
    speed: 35.0,
  });

  const behavior = getMockDriverBehavior({
    harsh_accel_count: req.harsh_accel_count,
    harsh_brake_count: 2,
    harsh_corner_count: 1,
    speed_variance: req.speed_variance,
    avg_speed: 36.0,
    max_speed: 65.0,
    battery_temp_max: req.battery_temp + 3,
    max_discharge_current: 35.0,
  });

  return {
    vehicle_id: req.vehicle_id,
    estimated_soh: jitter(94.5, 1),
    rul_to_knee_cycles: knee.rul_to_knee_cycles,
    driver_aggressiveness_index: behavior.aggressiveness_index,
    battery_stress_index: behavior.battery_stress_index,
    unified_health_grade: knee.is_post_knee ? "Grade C (Aging Risk)" : behavior.aggressiveness_index > 0.6 ? "Grade B (Wear Alert)" : "Grade A (Optimal)",
    executive_summary: `Vehicle ${req.vehicle_id} operating in ${knee.knee_risk_state}. Driver classified as ${behavior.driver_classification} with ${knee.rul_to_knee_cycles} cycles remaining to degradation knee.`,
  };
}
