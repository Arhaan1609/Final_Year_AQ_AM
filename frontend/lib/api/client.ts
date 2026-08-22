/**
 * Unified API Client for EV Battery Intelligence Platform.
 * Supports both Live Mode (FastAPI backend at http://localhost:8000)
 * and Mock Mode (zero dependency offline demoing).
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
} from "./types";

import * as MockData from "./mock";
import { useFleetStore } from "../store/useFleetStore";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export function isMockMode(): boolean {
  if (typeof window !== "undefined") {
    const override = localStorage.getItem("USE_MOCK_OVERRIDE");
    if (override !== null) return override === "true";
  }
  return process.env.NEXT_PUBLIC_USE_MOCK === "true";
}

export function setMockModeOverride(val: boolean) {
  if (typeof window !== "undefined") {
    localStorage.setItem("USE_MOCK_OVERRIDE", String(val));
  }
}

// Artificial simulated delay for realistic feel in mock mode
async function delay(ms: number = 300): Promise<void> {
  return new Promise((res) => setTimeout(res, ms + Math.random() * 200));
}

function updateConnectionStatus(connected: boolean) {
  if (typeof window !== "undefined") {
    useFleetStore.getState().setIsLiveBackendConnected(connected);
  }
}

// Generic POST helper with automatic fallback
async function postAPI<TReq, TRes>(
  path: string,
  body: TReq,
  mockFallback: (b: TReq) => TRes
): Promise<TRes> {
  if (isMockMode()) {
    updateConnectionStatus(false);
    await delay();
    return mockFallback(body);
  }

  try {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), 6000);

    const res = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    clearTimeout(id);

    if (!res.ok) {
      throw new Error(`HTTP Error ${res.status}: ${res.statusText}`);
    }
    const data = (await res.json()) as TRes;
    updateConnectionStatus(true);
    return data;
  } catch (err) {
    console.warn(`[API Client] Live call to ${path} failed. Falling back to mock data:`, err);
    updateConnectionStatus(false);
    await delay(150);
    return mockFallback(body);
  }
}

// 1. Health
export async function getSystemHealth(): Promise<HealthResponse> {
  if (isMockMode()) {
    updateConnectionStatus(false);
    await delay(150);
    return MockData.getMockHealth();
  }
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });
    if (!res.ok) throw new Error("Health check failed");
    const data = await res.json();
    updateConnectionStatus(true);
    return data;
  } catch {
    updateConnectionStatus(false);
    return MockData.getMockHealth();
  }
}

// 2. Module A — SOC
export async function predictSOC(req: SOCRequest): Promise<ModelPredictionResponse> {
  return postAPI<SOCRequest, ModelPredictionResponse>("/predict/soc", req, MockData.getMockSOC);
}

// 3. Module A — SOH (Tabular)
export async function predictSOH(req: SOHRequest): Promise<ModelPredictionResponse> {
  return postAPI<SOHRequest, ModelPredictionResponse>("/predict/soh", req, MockData.getMockSOH);
}

// 4. Module A — RUL (Cycles)
export async function predictRUL(req: RULRequest): Promise<ModelPredictionResponse> {
  return postAPI<RULRequest, ModelPredictionResponse>("/predict/rul", req, MockData.getMockRUL);
}

// 5. Module A — Mileage (km)
export async function predictMileage(req: MileageRequest): Promise<ModelPredictionResponse> {
  return postAPI<MileageRequest, ModelPredictionResponse>("/predict/mileage", req, MockData.getMockMileage);
}

// 6. Module B — Thermal Safety
export async function predictThermal(req: ThermalRequest): Promise<ThermalResponse> {
  return postAPI<ThermalRequest, ThermalResponse>("/predict/thermal", req, MockData.getMockThermal);
}

// 7. Module B — SOH Deep (CNN-LSTM)
export async function predictSOHDeep(req: SOHDeepRequest): Promise<SOHDeepResponse> {
  return postAPI<SOHDeepRequest, SOHDeepResponse>("/predict/soh-deep", req, MockData.getMockSOHDeep);
}

// 8. Module B — Vehicle Diagnosis
export async function diagnoseVehicle(req: DiagnoseRequest): Promise<DiagnoseResponse> {
  return postAPI<DiagnoseRequest, DiagnoseResponse>("/predict/diagnose/vehicle", req, MockData.getMockDiagnose);
}

// 9. Module C — Driver Behavior
export async function predictDriverBehavior(req: DriverBehaviorRequest): Promise<DriverBehaviorResponse> {
  return postAPI<DriverBehaviorRequest, DriverBehaviorResponse>("/predict/driver-behavior", req, MockData.getMockDriverBehavior);
}

// 10. Module C — Knee Point Prognostics
export async function predictKneePoint(req: KneePredictionRequest): Promise<KneePredictionResponse> {
  return postAPI<KneePredictionRequest, KneePredictionResponse>("/predict/knee-point", req, MockData.getMockKneePoint);
}

// 11. Module C — Meta-Ensemble Holistics
export async function predictMetaEnsemble(req: MetaEnsembleRequest): Promise<MetaEnsembleResponse> {
  return postAPI<MetaEnsembleRequest, MetaEnsembleResponse>("/predict/meta-ensemble", req, MockData.getMockMetaEnsemble);
}
