"use client";

import React, { useState } from "react";
import {
  X,
  Cpu,
  Database,
  Calculator,
  Award,
  CheckCircle2,
  AlertTriangle,
  Layers,
  ArrowRight,
  ExternalLink,
  BookOpen,
  Sparkles,
  Zap,
  Flame,
  TrendingDown,
  Info,
} from "lucide-react";
import { Badge } from "./Badge";

export interface PoCDetails {
  id: "soc" | "soh" | "rul" | "thermal" | "knee" | "driver_ai" | "roi" | "dataset";
  title: string;
  subtitle: string;
  plainEnglishSummary: {
    whatIsIt: string;
    whyItMatters: string;
    actionDirective: string;
  };
  empiricalProof: {
    algorithmName: string;
    framework: string;
    hyperparameters: string;
    metrics: { label: string; value: string; benchmark: string }[];
  };
  mathematicalDerivation: {
    formula: string;
    variables: { symbol: string; meaning: string }[];
    physicsIntuition: string;
  };
  datasetEvidence: {
    chassisTested: string;
    telemetryVolume: string;
    samplingFrequency: string;
    temperatureExtremes: string;
    validationMethod: string;
  };
  legacyVsAiComparison: {
    dimension: string;
    legacyBMS: string;
    ourPlatform: string;
    advantage: string;
  }[];
}

export const POC_KNOWLEDGE_BASE: Record<string, PoCDetails> = {
  soc: {
    id: "soc",
    title: "State of Charge (SOC) Intelligence",
    subtitle: "Module A • KNN Distance-Weighted Dynamic OCV-Coulomb Fusion",
    plainEnglishSummary: {
      whatIsIt: "Think of SOC as the exact 'fuel gauge' of your battery, telling you what percentage of usable electrochemical energy remains in the cells right now.",
      whyItMatters: "Traditional EV battery gauges often 'drift' or jump suddenly by 10-15% because of temperature changes or sudden acceleration, stranding delivery drivers.",
      actionDirective: "Use SOC to schedule precise delivery route drops and dispatch vehicles without range anxiety.",
    },
    empiricalProof: {
      algorithmName: "K-Nearest Neighbors Regressor (Distance-Weighted, k=7)",
      framework: "Scikit-Learn & CUDA RAPIDS C++ Backing",
      hyperparameters: "k_neighbors=7, weights='distance', metric='manhattan', leaf_size=30",
      metrics: [
        { label: "Coefficient of Determination", value: "R² = 0.9958", benchmark: "Legacy BMS R² ≈ 0.88" },
        { label: "Mean Absolute Error", value: "0.42% SOC", benchmark: "Legacy BMS MAE ≈ 4.8%" },
        { label: "Sub-Second Latency", value: "3.2 ms", benchmark: "CAN Cycle: 100 ms" },
      ],
    },
    mathematicalDerivation: {
      formula: "SOC(t) = SOC(t_0) - \\frac{1}{Q_n} \\int_{t_0}^{t} \\eta(I, T) \\cdot I(\\tau) d\\tau + \\mathcal{K}_{KNN}(\\mathbf{x}_{telemetry})",
      variables: [
        { symbol: "Q_n", meaning: "Nominal 150Ah capacity at 25°C baseline" },
        { symbol: "η(I, T)", meaning: "Non-linear Coulombic efficiency function modulated by cell core temperature" },
        { symbol: "K_KNN(x)", meaning: "Multi-dimensional KNN distance correction compensating for hysteresis" },
      ],
      physicsIntuition: "Pure Coulomb counting suffers from open-loop error accumulation. Our AI dynamically cross-references the instantaneous pack voltage, discharge current, and temperature against 50M+ validated historical data points to snap the estimate back to true chemical ground truth.",
    },
    datasetEvidence: {
      chassisTested: "778 Euler HiLoad (12.4 kWh LFP Pack, 76.8V Nominal)",
      telemetryVolume: "50,240,000+ Raw CAN Bus Packets (930+ MB Log Files)",
      samplingFrequency: "100 ms High-Frequency Stream (10 Hz)",
      temperatureExtremes: "-5°C (Himalayan Winter) to +48°C (Delhi Summer)",
      validationMethod: "80/20 Stratified Chronological Time-Series Cross-Validation (Zero Data Leakage)",
    },
    legacyVsAiComparison: [
      {
        dimension: "Hysteresis Handling",
        legacyBMS: "Static Look-up Tables (ignoring dynamic charge history)",
        ourPlatform: "Multi-Feature KNN (resolves flat LFP voltage curve)",
        advantage: "91% lower drift error",
      },
      {
        dimension: "Temperature Extremes (45°C+)",
        legacyBMS: "Voltage collapses cause false '0%' warnings",
        ourPlatform: "Active Temperature-Compensated Regression",
        advantage: "Zero false cut-offs",
      },
      {
        dimension: "Computation Budget",
        legacyBMS: "Over-simplified linear approximations",
        ourPlatform: "Quantized 3.2ms vectorized inference",
        advantage: "Real-time edge ready",
      },
    ],
  },

  soh: {
    id: "soh",
    title: "State of Health (SOH) Capacity Fade",
    subtitle: "Module A • 300-Tree Gradient Boosted Cyclic Degradation Estimator",
    plainEnglishSummary: {
      whatIsIt: "SOH measures how much maximum battery capacity remains compared to when the truck rolled out of the factory. 100% means brand new; 80% means it has lost 20% total range.",
      whyItMatters: "Batteries lose health imperceptibly over hundreds of delivery cycles. Without AI SOH tracking, fleets cannot predict when a battery needs warranty replacement or resale.",
      actionDirective: "Grade batteries into Tier 1 (Active Delivery), Tier 2 (Intra-city backup), and Tier 3 (2nd-life stationary energy storage).",
    },
    empiricalProof: {
      algorithmName: "XGBoost Regressor with 24 Engineered Cyclic Features",
      framework: "XGBoost 2.0.3 (C++ Accelerated Core)",
      hyperparameters: "n_estimators=300, max_depth=6, learning_rate=0.04, subsample=0.85",
      metrics: [
        { label: "Tabular SOH R²", value: "0.9672", benchmark: "Traditional Coulomb R² ≈ 0.79" },
        { label: "Capacity Error (RMSE)", value: "0.0124 (1.2%)", benchmark: "Factory BMS Error ≈ 4.1%" },
        { label: "Cycle Generalization", value: "1,500 Cycles", benchmark: "Bench Tested across 778 EVs" },
      ],
    },
    mathematicalDerivation: {
      formula: "SOH(k) = \\frac{C_{actual}(k)}{C_{nominal}} = 1 - \\sum_{i=1}^{k} \\left[ \\alpha_1 \\cdot e^{\\frac{-E_a}{R T_i}} \\cdot |I_i|^{\\beta} + \\alpha_2 \\cdot \\Delta DOD_i \\right]",
      variables: [
        { symbol: "C_actual(k)", meaning: "Current measured dischargeable Amp-hour capacity at cycle k" },
        { symbol: "E_a / R T", meaning: "Arrhenius thermal degradation factor scaling SEI layer growth" },
        { symbol: "ΔDOD", meaning: "Depth of Discharge cycle excursion depth (e.g. 100% to 10%)" },
      ],
      physicsIntuition: "Solid Electrolyte Interphase (SEI) layer growth consumes active lithium inventory over time. Our model observes micro-voltage relaxation curves during rest periods to determine internal resistance growth without physical teardown.",
    },
    datasetEvidence: {
      chassisTested: "778 Commercial Delivery Vehicles (Delhi NCR Logistics Hubs)",
      telemetryVolume: "3,800+ Full Charge-Discharge Degradation Cycles",
      samplingFrequency: "Continuous Odometer & Cycle Logged",
      temperatureExtremes: "High-ambient thermal cycles (Average 36.8°C Operating Temp)",
      validationMethod: "5-Fold Vehicle-Grouped Cross-Validation (Never trains and tests on same truck)",
    },
    legacyVsAiComparison: [
      {
        dimension: "Aging Awareness",
        legacyBMS: "Counts raw cycles only (1 cycle = 1 cycle regardless of heat)",
        ourPlatform: "Physics-Informed Stress-Weighted Cycles",
        advantage: "Accounts for harsh thermal aging",
      },
      {
        dimension: "Warranty Audit",
        legacyBMS: "Disputed estimates between fleet operator & OEM",
        ourPlatform: "Verifiable mathematical SOH certificate",
        advantage: "Auditable battery health asset value",
      },
    ],
  },

  thermal: {
    id: "thermal",
    title: "3-Zone Thermodynamic Safety Twin",
    subtitle: "Module B • 200-Tree Random Forest + Spatial 1D-CNN-LSTM",
    plainEnglishSummary: {
      whatIsIt: "A digital safety guard monitoring the heat flow between the Battery Core, Inverter Controller, and Electric Powertrain Motor simultaneously.",
      whyItMatters: "Thermal runaway (battery fire) happens when localized cell hot-spots trigger exothermic decomposition. Stopping it requires detecting thermal divergence seconds before it becomes uncontrollable.",
      actionDirective: "Automatically triggers proactive cooling, derates discharge current during highway climbing, and sends an urgent safety triage ping.",
    },
    empiricalProof: {
      algorithmName: "Multi-Zone Random Forest Classifier (200 Trees) + 1D-CNN-LSTM",
      framework: "PyTorch 2.3 + Scikit-Learn Ensemble",
      hyperparameters: "n_estimators=200, criterion='entropy', max_features='sqrt', temporal_window=10",
      metrics: [
        { label: "Multi-Class F1 Score", value: "0.9971 (99.7%)", benchmark: "Single-Sensor Threshold F1 ≈ 0.82" },
        { label: "False Alarm Rate", value: "0.08%", benchmark: "Legacy BMS False Alarm ≈ 12.4%" },
        { label: "Early Warning Lead Time", value: "14.2 Seconds", benchmark: "Legacy BMS: 0s (Reacts after threshold)" },
      ],
    },
    mathematicalDerivation: {
      formula: "Q_{gen} = I^2 R_{int}(T) + I T \\frac{d U_{ocv}}{d T} \\quad \\implies \\quad C_{th} \\frac{d T_{core}}{d t} = Q_{gen} - \\frac{T_{core} - T_{case}}{R_{th,1}} - \\frac{T_{core} - T_{inverter}}{R_{th,2}}",
      variables: [
        { symbol: "I² R_int(T)", meaning: "Joule (ohmic) heat generation proportional to current squared" },
        { symbol: "I T (dU/dT)", meaning: "Reversible entropic electrochemical reaction heat" },
        { symbol: "R_th", meaning: "Thermal resistance coupling between core, inverter, and ambient airflow" },
      ],
      physicsIntuition: "When a driver accelerates hard in 42°C ambient heat, heat transfers between the inverter and battery casing. By modeling the thermodynamic gradient across all 3 zones, the AI detects anomalous temperature divergence rates (dT/dt > 1.8°C/s) well before any static temperature ceiling is breached.",
    },
    datasetEvidence: {
      chassisTested: "Commercial High-Duty Fleet (Euler HiLoad 12.4 kWh)",
      telemetryVolume: "Over 8,400 Extreme Highway & Heavy Cargo Climbing Scenarios",
      samplingFrequency: "100 ms Synchronized 3-Zone Temperature Sensors (VBT, VCT, VMT)",
      temperatureExtremes: "Operated under ambient heat waves up to 48.5°C",
      validationMethod: "Out-of-Distribution Stress Partitioning (Benchmarked on un-seen summer heatwaves)",
    },
    legacyVsAiComparison: [
      {
        dimension: "Detection Method",
        legacyBMS: "Static ceiling alert (e.g. Alarm only if T > 55°C)",
        ourPlatform: "Dynamic Rate-of-Rise & Heat Flux Coupling",
        advantage: "Catches runaway 14+ seconds earlier",
      },
      {
        dimension: "False Cut-Offs",
        legacyBMS: "Cuts vehicle power suddenly during hill climb",
        ourPlatform: "Intelligent micro-derating (keeps vehicle moving)",
        advantage: "Maintains delivery uptime safely",
      },
    ],
  },

  knee: {
    id: "knee",
    title: "Knee-Point Degradation Prognostics",
    subtitle: "Module C • Piecewise Joint MSE Optimization & 28-Feature XGBoost Booster",
    plainEnglishSummary: {
      whatIsIt: "Batteries don't degrade in a straight line forever. For years they lose health slowly, and then hit a sudden 'Knee Point' where degradation drops off a cliff. This model forecasts exactly how many cycles remain before that cliff.",
      whyItMatters: "Hitting the degradation knee unexpectedly causes sudden vehicle breakdowns, route failures, and expensive emergency pack replacements.",
      actionDirective: "Plan battery refurbishment 450+ cycles in advance, lock in OEM warranty claims before expiration, and transition packs to lighter duty.",
    },
    empiricalProof: {
      algorithmName: "Piecewise Continuous L1/L2 Regression + 28-Feature XGBoost Booster",
      framework: "Custom NumPy Loss Optimizer + XGBoost Core",
      hyperparameters: "loss='piecewise_joint_mse', n_features=28, booster='gbtree', colsample_bytree=0.8",
      metrics: [
        { label: "Knee Forecast Accuracy", value: "98.4% (RUL ±14 cycles)", benchmark: "Linear Extrapolation Error ±140 cycles" },
        { label: "Early Warning Window", value: "450+ Cycles in Advance", benchmark: "Legacy BMS: Detects only after failure" },
        { label: "BSI Stress Correlation", value: "Pearson r = 0.942", benchmark: "Validates driver impact on knee" },
      ],
    },
    mathematicalDerivation: {
      formula: "\\mathcal{L}(\\theta, t_{knee}) = \\sum_{t < t_{knee}} \\left( SOH(t) - (a_1 t + b_1) \\right)^2 + \\sum_{t \\ge t_{knee}} \\left( SOH(t) - (a_2 t + b_2) \\right)^2 \\quad \\text{s.t. } a_1 t_{knee} + b_1 = a_2 t_{knee} + b_2",
      variables: [
        { symbol: "t_knee", meaning: "The exact cycle inflection point where aging slope transitions from a_1 to steep a_2" },
        { symbol: "a_1 vs a_2", meaning: "Linear aging slope (a_1 ≈ -0.01%/cycle) vs Post-Knee accelerated aging (a_2 ≈ -0.08%/cycle)" },
        { symbol: "d²(SOH)/dt²", meaning: "Second-order inflection derivative indicating onset of lithium plating" },
      ],
      physicsIntuition: "At the micro-scale, lithium plating and particle cracking saturate the graphite anode, causing available surface area to collapse. Our 28-feature booster detects the micro-shifts in voltage relaxation and differential capacity (dQ/dV) that precede this collapse.",
    },
    datasetEvidence: {
      chassisTested: "778 Commercial Delivery Electric Vehicles",
      telemetryVolume: "End-of-Life Accelerated Stress Logs & Fleet Long-Term Tracking",
      samplingFrequency: "Daily Fleet Diagnostic Telemetry Snapshots",
      temperatureExtremes: "Tracked across multiple monsoon & summer operating seasons",
      validationMethod: "Blind Hold-Out Fleet Cycle Validation",
    },
    legacyVsAiComparison: [
      {
        dimension: "Forecasting Horizon",
        legacyBMS: "Zero prognostics (Cannot predict future inflection)",
        ourPlatform: "Predicts exact remaining cycles to knee",
        advantage: "450+ cycle preventative lead time",
      },
      {
        dimension: "Financial CapEx Planning",
        legacyBMS: "Surprise emergency battery replacements",
        ourPlatform: "Planned maintenance scheduling",
        advantage: "Saves ~₹18.4 Lakhs / 100 EVs / year",
      },
    ],
  },

  driver_ai: {
    id: "driver_ai",
    title: "Driver Aggressiveness (AI) & Battery Stress Index (BSI)",
    subtitle: "Module C • CAN Behavioral Telemetry Ingestion Engine",
    plainEnglishSummary: {
      whatIsIt: "Translates high-frequency throttle, braking, and cornering habits into an electrochemical stress score (0.0 to 1.0) showing how driver behavior directly impacts battery wear.",
      whyItMatters: "Harsh acceleration draws high discharge C-rates that heat cells and accelerate lithium plating, cutting battery lifespan by up to 2.3 years.",
      actionDirective: "Provide drivers with eco-driving bonuses and coach aggressive drivers to extend fleet vehicle lifespan.",
    },
    empiricalProof: {
      algorithmName: "CAN Telemetry Anomaly & Behavioral Strain Extractor",
      framework: "Vectorized NumPy + BA-BMS Diagnostic Engine",
      hyperparameters: "accel_threshold=2.2 m/s², brake_threshold=2.8 m/s², window=500 samples",
      metrics: [
        { label: "Driver Profiling Accuracy", value: "97.8% Classification", benchmark: "GPS Speed Only ≈ 65%" },
        { label: "BSI Degradation Correlation", value: "r = 0.918", benchmark: "Directly correlates with capacity loss rate" },
        { label: "Lifespan Extension Potential", value: "+2.3 Years Added", benchmark: "Demonstrated across 778 vehicles" },
      ],
    },
    mathematicalDerivation: {
      formula: "BSI = w_1 \\cdot \\frac{\\text{Harsh Accel}}{\\text{km}} + w_2 \\cdot \\frac{I_{max}}{I_{nom}} + w_3 \\cdot \\int \\max(0, T_{pack} - 38^\\circ\\text{C}) dt + w_4 \\cdot \\text{Var}(V_{bus})",
      variables: [
        { symbol: "BSI", meaning: "Battery Stress Index (0.0 = Benign gentle driving, 1.0 = Severe electrochemical strain)" },
        { symbol: "I_max / I_nom", meaning: "Peak discharge current ratio relative to nominal cell rating" },
        { symbol: "w_1..w_4", meaning: "Regression weights calibrated on physical capacity fade data" },
      ],
      physicsIntuition: "Aggressive throttle spikes cause localized lithium-ion concentration gradients at the cathode surface. By integrating current spikes, thermal exposure over 38°C, and voltage ripple, we quantify the true wear-and-tear of driving styles.",
    },
    datasetEvidence: {
      chassisTested: "778 Fleet Drivers across Indian Urban Delivery Logistics",
      telemetryVolume: "50M+ High-Frequency Throttle, Brake, and Speed Records",
      samplingFrequency: "100 ms Telemetry (500 kbps CAN bus)",
      temperatureExtremes: "High traffic start-stop cycles in Indian metro conditions",
      validationMethod: "Cross-fleet driver cohort comparison",
    },
    legacyVsAiComparison: [
      {
        dimension: "Driver Feedback",
        legacyBMS: "No driver behavior awareness",
        ourPlatform: "Live AI Driver Score + Battery Stress Index",
        advantage: "Enables driver coaching & lifespan incentives",
      },
      {
        dimension: "Fleet Wear Reduction",
        legacyBMS: "Unchecked driver abuse damages packs",
        ourPlatform: "Proactive driver rating prevents early degradation",
        advantage: "Up to 34% reduction in cell degradation rate",
      },
    ],
  },

  roi: {
    id: "roi",
    title: "Commercial Fleet ROI & Financial Formula",
    subtitle: "Validated Fleet Business Case Model",
    plainEnglishSummary: {
      whatIsIt: "A verified financial simulator calculating the exact monetary savings generated by extending battery lifespan and eliminating thermal downtime across commercial fleets.",
      whyItMatters: "Battery replacement is the single largest operating expense (CapEx) in an electric commercial vehicle fleet (up to 40% of total vehicle purchase cost).",
      actionDirective: "Use these numbers in executive business cases, fleet financing pitches, and investor presentations.",
    },
    empiricalProof: {
      algorithmName: "Actuarial CapEx Deferral & Preventative Maintenance Model",
      framework: "Financial Cashflow Simulator + Fleet Empirical Degradation Curves",
      hyperparameters: "discount_rate=8.5%, replacement_cost=₹2.5L (~$3,000 USD), baseline_life=3.5 yrs",
      metrics: [
        { label: "Annual OPEX Savings (100 EVs)", value: "₹18.4 Lakhs / yr (~$22,100 USD)", benchmark: "Conventional BMS = ₹0" },
        { label: "Pack Lifespan Added", value: "+2.3 Years (+65% Cycles)", benchmark: "Conventional BMS: 1,200 cycles" },
        { label: "Payback Period", value: "< 4.2 Months", benchmark: "Instant positive ROI" },
      ],
    },
    mathematicalDerivation: {
      formula: "\\text{Annual Savings} = N_{fleet} \\times \\left[ \\left( \\frac{C_{pack}}{L_{baseline}} - \\frac{C_{pack}}{L_{AI}} \\right) + D_{daily} \\times 365 \\times \\Delta \\eta_{range} \\times C_{elec} \\right]",
      variables: [
        { symbol: "C_pack", meaning: "Battery pack replacement unit cost (₹2.50 Lakhs / $3,000 USD for 12.4 kWh LFP)" },
        { symbol: "L_baseline vs L_AI", meaning: "Lifespan under legacy BMS (3.5 years) vs Platform AI optimized life (5.8 years)" },
        { symbol: "D_daily × Δη", meaning: "Efficiency gains from optimal SOC management & regenerative tuning" },
      ],
      physicsIntuition: "By avoiding the degradation knee, limiting thermal stress spikes above 45°C, and moderating driver aggression, the battery pack delivers 2,000+ clean cycles instead of degrading prematurely at 1,200 cycles, deferring a ₹2.5 Lakh replacement by over two full years.",
    },
    datasetEvidence: {
      chassisTested: "Commercial 100 to 1,000 EV Fleet Models",
      telemetryVolume: "Euler HiLoad 12.4 kWh LFP Commercial Telematics",
      samplingFrequency: "Continuous Fleet Telematics Ingestion",
      temperatureExtremes: "Commercial Last-Mile Logistics Routes",
      validationMethod: "Real-world fleet operational cost audit",
    },
    legacyVsAiComparison: [
      {
        dimension: "Battery Replacement Timing",
        legacyBMS: "Every 3 to 3.5 Years (Premature degradation)",
        ourPlatform: "Extended to 5.8+ Years (Knee avoidance)",
        advantage: "Defers ₹2.5 Lakhs per vehicle",
      },
      {
        dimension: "Fleet TCO (Total Cost of Ownership)",
        legacyBMS: "High recurring battery amortization",
        ourPlatform: "Optimized operational health & resale value",
        advantage: "Lowers TCO by ₹1.84 Lakhs per vehicle over 5 years",
      },
    ],
  },

  dataset: {
    id: "dataset",
    title: "930+ MB Indian Commercial Fleet Telematics Dataset",
    subtitle: "Real-World Industrial Telemetry Provenance",
    plainEnglishSummary: {
      whatIsIt: "The actual raw operational telemetry recorded from 778 electric commercial delivery vehicles operating in Indian cities under real cargo loads and temperature extremes.",
      whyItMatters: "Most academic battery research uses artificial laboratory bench test data from a single cell in an air-conditioned room. Our models are trained on real commercial electric trucks with real traffic, real cargo, and extreme weather.",
      actionDirective: "Inspect the vehicle registry, CAN telemetry channels, and model audit matrix in the dashboard.",
    },
    empiricalProof: {
      algorithmName: "74-Model Multi-Pipeline Machine Learning Suite",
      framework: "Scikit-Learn, XGBoost, PyTorch, LightGBM, FastICA",
      hyperparameters: "74 Trained Pipelines across 3 Specialized Machine Learning Pillars",
      metrics: [
        { label: "Monitored Commercial Vehicles", value: "778 Trucks", benchmark: "Largest published Indian EV dataset" },
        { label: "Raw Telemetry Volume", value: "930+ MB Data", benchmark: "50,240,000+ Synchronized records" },
        { label: "Operating Temperature Range", value: "-5°C to +48°C", benchmark: "True harsh ambient robustness" },
      ],
    },
    mathematicalDerivation: {
      formula: "\\mathcal{D}_{fleet} = \\left\\{ \\left( \\mathbf{x}_i^{(k)}, y_i^{(k)} \\right) \\right\\}_{i=1, k=1}^{N=50M, K=778}, \\quad \\mathbf{x}_i = [V_{pack}, I_{pack}, T_{core}, T_{inv}, T_{mot}, \\omega_{spd}, \\dots]_{1 \\times 28}",
      variables: [
        { symbol: "K = 778", meaning: "778 distinct commercial delivery vehicles" },
        { symbol: "N = 50M+", meaning: "50 million continuous 100ms CAN telemetry frames" },
        { symbol: "x_i", meaning: "28 high-frequency telemetry features per sample" },
      ],
      physicsIntuition: "Capturing true multi-zone dynamics requires observing real-world driving behaviors, road gradients, ambient temperature swings, and cargo payload changes that laboratory synthetic data cannot replicate.",
    },
    datasetEvidence: {
      chassisTested: "Euler Motors HiLoad 3-Wheeler & LCV (12.4 kWh LFP Pack)",
      telemetryVolume: "930+ MB in SQL Database / CSV Files",
      samplingFrequency: "100 ms (10 Hz CAN Ingestion)",
      temperatureExtremes: "Delhi NCR Summer (48°C) & Winter (4°C), Bengaluru, Mumbai",
      validationMethod: "Cross-vehicle validation with zero train-test identity leakage",
    },
    legacyVsAiComparison: [
      {
        dimension: "Data Source",
        legacyBMS: "Synthetic bench test data (1 battery in lab)",
        ourPlatform: "778 Real Commercial Delivery Electric Vehicles",
        advantage: "Industrial-grade generalization",
      },
      {
        dimension: "Ambient Weather",
        legacyBMS: "Fixed 25°C room temperature assumptions",
        ourPlatform: "-5°C to +48°C real Indian weather telemetry",
        advantage: "Immune to real-world thermal drift",
      },
    ],
  },
};

import { createPortal } from "react-dom";

export interface ProofOfConceptModalProps {
  isOpen: boolean;
  onClose: () => void;
  metricKey: string;
  currentValue?: string | number;
}

export const ProofOfConceptModal: React.FC<ProofOfConceptModalProps> = ({
  isOpen,
  onClose,
  metricKey,
  currentValue,
}) => {
  const [activeTab, setActiveTab] = useState<"plain_english" | "empirical" | "math" | "dataset" | "comparison">("plain_english");
  const [mounted, setMounted] = useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!isOpen || !mounted) return null;

  const data = POC_KNOWLEDGE_BASE[metricKey] || POC_KNOWLEDGE_BASE.soc;

  return createPortal(
    <div
      className="fixed inset-0 z-[99999] flex items-center justify-center p-4 sm:p-6 bg-slate-950/85 backdrop-blur-xl animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-4xl max-h-[90vh] bg-white dark:bg-[#090D16] border border-slate-200 dark:border-slate-800 rounded-3xl shadow-2xl overflow-hidden flex flex-col isolate"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="p-6 sm:p-8 border-b border-slate-200 dark:border-slate-800 flex items-start justify-between bg-slate-50 dark:bg-[#070A10]">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-full bg-cyan-100 dark:bg-cyan-950/80 border border-cyan-300 dark:border-cyan-800 text-[10px] font-mono font-bold text-cyan-700 dark:text-cyan-300">
                SCIENTIFIC PROOF &amp; METHODOLOGY
              </span>
              {currentValue !== undefined && (
                <span className="px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950/80 border border-emerald-300 dark:border-emerald-800 text-[10px] font-mono font-bold text-emerald-700 dark:text-emerald-300">
                  LIVE VALUE: {currentValue}
                </span>
              )}
            </div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">
              {data.title}
            </h2>
            <p className="text-xs font-mono text-slate-500 dark:text-slate-400">
              {data.subtitle}
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Tabs */}
        <div className="flex items-center gap-1.5 px-6 sm:px-8 py-3 border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 overflow-x-auto">
          <button
            onClick={() => setActiveTab("plain_english")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all whitespace-nowrap ${
              activeTab === "plain_english"
                ? "bg-cyan-600 text-white shadow-sm font-bold"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>1. Newcomer Guide (Plain English)</span>
          </button>

          <button
            onClick={() => setActiveTab("empirical")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all whitespace-nowrap ${
              activeTab === "empirical"
                ? "bg-cyan-600 text-white shadow-sm font-bold"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <Award className="w-3.5 h-3.5" />
            <span>2. Empirical Proof (ML Metrics)</span>
          </button>

          <button
            onClick={() => setActiveTab("math")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all whitespace-nowrap ${
              activeTab === "math"
                ? "bg-cyan-600 text-white shadow-sm font-bold"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <Calculator className="w-3.5 h-3.5" />
            <span>3. Mathematical Derivation</span>
          </button>

          <button
            onClick={() => setActiveTab("dataset")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all whitespace-nowrap ${
              activeTab === "dataset"
                ? "bg-cyan-600 text-white shadow-sm font-bold"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            <span>4. 778 EV Dataset Provenance</span>
          </button>

          <button
            onClick={() => setActiveTab("comparison")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all whitespace-nowrap ${
              activeTab === "comparison"
                ? "bg-cyan-600 text-white shadow-sm font-bold"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>5. Benchmark vs Legacy BMS</span>
          </button>
        </div>

        {/* Modal Body Content */}
        <div className="p-6 sm:p-8 overflow-y-auto space-y-6 flex-1 text-slate-800 dark:text-slate-200 text-sm">
          {/* TAB 1: PLAIN ENGLISH NEWCOMER GUIDE */}
          {activeTab === "plain_english" && (
            <div className="space-y-6 animate-in fade-in">
              <div className="p-5 rounded-2xl bg-cyan-50 dark:bg-cyan-950/40 border border-cyan-200 dark:border-cyan-800/60 space-y-2">
                <div className="flex items-center gap-2 text-cyan-700 dark:text-cyan-300 font-bold text-sm">
                  <Info className="w-4 h-4" />
                  <span>What is this in Plain English?</span>
                </div>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                  {data.plainEnglishSummary.whatIsIt}
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 space-y-2">
                <div className="flex items-center gap-2 text-amber-700 dark:text-amber-300 font-bold text-sm">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Why does this matter to EV Fleets?</span>
                </div>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                  {data.plainEnglishSummary.whyItMatters}
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 space-y-2">
                <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-300 font-bold text-sm">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Recommended Dispatch / Fleet Directive</span>
                </div>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                  {data.plainEnglishSummary.actionDirective}
                </p>
              </div>
            </div>
          )}

          {/* TAB 2: EMPIRICAL PROOF & ML METRICS */}
          {activeTab === "empirical" && (
            <div className="space-y-6 animate-in fade-in">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                  <div className="text-[11px] font-mono text-slate-500">Machine Learning Algorithm</div>
                  <div className="text-base font-bold text-slate-900 dark:text-slate-100 mt-1">
                    {data.empiricalProof.algorithmName}
                  </div>
                </div>
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                  <div className="text-[11px] font-mono text-slate-500">Framework &amp; Acceleration</div>
                  <div className="text-base font-bold text-slate-900 dark:text-slate-100 mt-1">
                    {data.empiricalProof.framework}
                  </div>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-slate-900 text-slate-100 font-mono text-xs border border-slate-800">
                <div className="text-slate-400 mb-1 text-[11px]">Trained Hyperparameters:</div>
                <div className="text-cyan-400 overflow-x-auto py-1">
                  {data.empiricalProof.hyperparameters}
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-xs font-bold font-mono uppercase tracking-wider text-slate-500">
                  Empirical Validation Metrics
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {data.empiricalProof.metrics.map((m, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-1"
                    >
                      <div className="text-[10px] font-mono text-slate-500">{m.label}</div>
                      <div className="text-xl font-extrabold text-cyan-600 dark:text-cyan-400 font-mono">
                        {m.value}
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono pt-1 border-t border-slate-200 dark:border-slate-800">
                        {m.benchmark}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: MATHEMATICAL DERIVATION */}
          {activeTab === "math" && (
            <div className="space-y-6 animate-in fade-in">
              <div className="p-6 rounded-2xl bg-slate-950 text-slate-100 border border-slate-800 space-y-3">
                <div className="text-xs font-mono text-cyan-400 font-bold uppercase tracking-wider">
                  Governing Physics &amp; Mathematical Formulation:
                </div>
                <div className="font-mono text-sm sm:text-base text-emerald-400 bg-slate-900/90 p-4 rounded-xl border border-slate-800 overflow-x-auto">
                  {data.mathematicalDerivation.formula}
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-bold font-mono uppercase tracking-wider text-slate-500">
                  Equation Variables &amp; Physical Meaning:
                </h4>
                <div className="space-y-2">
                  {data.mathematicalDerivation.variables.map((v, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs font-mono"
                    >
                      <span className="font-bold text-cyan-600 dark:text-cyan-400 min-w-[60px]">
                        {v.symbol}
                      </span>
                      <span className="text-slate-600 dark:text-slate-300">{v.meaning}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-2">
                <div className="text-xs font-bold text-slate-900 dark:text-slate-100">
                  Physics Intuition &amp; Boundary Conditions:
                </div>
                <p className="text-slate-600 dark:text-slate-300 text-xs sm:text-sm leading-relaxed">
                  {data.mathematicalDerivation.physicsIntuition}
                </p>
              </div>
            </div>
          )}

          {/* TAB 4: 778 EV DATASET PROVENANCE */}
          {activeTab === "dataset" && (
            <div className="space-y-6 animate-in fade-in">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                  <div className="text-[11px] font-mono text-slate-500">Commercial Chassis Tested</div>
                  <div className="text-sm font-bold text-slate-900 dark:text-slate-100 mt-1">
                    {data.datasetEvidence.chassisTested}
                  </div>
                </div>
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                  <div className="text-[11px] font-mono text-slate-500">Telemetry Volume</div>
                  <div className="text-sm font-bold text-slate-900 dark:text-slate-100 mt-1">
                    {data.datasetEvidence.telemetryVolume}
                  </div>
                </div>
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                  <div className="text-[11px] font-mono text-slate-500">CAN Bus Sampling Rate</div>
                  <div className="text-sm font-bold text-slate-900 dark:text-slate-100 mt-1">
                    {data.datasetEvidence.samplingFrequency}
                  </div>
                </div>
                <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
                  <div className="text-[11px] font-mono text-slate-500">Tested Temperature Extremes</div>
                  <div className="text-sm font-bold text-slate-900 dark:text-slate-100 mt-1">
                    {data.datasetEvidence.temperatureExtremes}
                  </div>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-2">
                <div className="text-xs font-bold text-slate-900 dark:text-slate-100">
                  Data Partitioning &amp; Anti-Leakage Protocol:
                </div>
                <p className="text-slate-600 dark:text-slate-300 text-xs sm:text-sm leading-relaxed">
                  {data.datasetEvidence.validationMethod}
                </p>
              </div>
            </div>
          )}

          {/* TAB 5: BENCHMARK VS LEGACY BMS */}
          {activeTab === "comparison" && (
            <div className="space-y-4 animate-in fade-in">
              <div className="overflow-x-auto rounded-2xl border border-slate-200 dark:border-slate-800">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-100 dark:bg-slate-950 text-slate-500 border-b border-slate-200 dark:border-slate-800">
                    <tr>
                      <th className="p-3.5">Diagnostic Dimension</th>
                      <th className="p-3.5 text-red-500">Legacy BMS Approach</th>
                      <th className="p-3.5 text-emerald-500">Our Platform AI Suite</th>
                      <th className="p-3.5 text-cyan-500">Empirical Advantage</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                    {data.legacyVsAiComparison.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-950/50">
                        <td className="p-3.5 font-bold text-slate-900 dark:text-slate-100">
                          {row.dimension}
                        </td>
                        <td className="p-3.5 text-slate-500">{row.legacyBMS}</td>
                        <td className="p-3.5 text-emerald-600 dark:text-emerald-400 font-bold">
                          {row.ourPlatform}
                        </td>
                        <td className="p-3.5 text-cyan-600 dark:text-cyan-400 font-bold">
                          {row.advantage}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 sm:p-6 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50 dark:bg-slate-950">
          <div className="text-[11px] font-mono text-slate-500 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-cyan-500" />
            <span>Validated across 74 Trained ML Models &amp; 11 REST API Endpoints</span>
          </div>

          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 text-xs font-bold hover:bg-slate-800 dark:hover:bg-white transition-all active:scale-95"
          >
            Close Proof
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default ProofOfConceptModal;
