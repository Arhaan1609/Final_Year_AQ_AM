"""
api/main.py — Unified EV Battery Intelligence FastAPI Application.

Combines Three Machine Learning Modules:
  Module A: Fleet Predictions (SOC, SOH tabular, RUL, Mileage) — sklearn & XGBoost
  Module B: Thermal Fault Safety & SOH Deep (PyTorch CNN-LSTM + Multi-Zone RF)
  Module C: Behavior-Aware BMS (AI / BSI) & Knee-Point Degradation Prognostics (XGBoost)

Usage:
  uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
  OR via master launcher:
  python run_all.py
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Ensure project root is importable
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, _PROJECT_ROOT)

from api.routers.module_a import router as router_a, load_all_module_a_models, get_model_status, get_model_names
from api.routers.module_b import router as router_b, load_module_b_engine, get_engine_status as get_engine_b_status
from api.routers.module_c import router as router_c, load_module_c_engine, get_engine_status as get_engine_c_status
from api.schemas import HealthStatusResponse


# ──────────────────────────────────────────────
#  LIFESPAN — load all models at startup
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all models when the API starts, release nothing on shutdown (they're in-process)."""
    print("\n" + "=" * 65)
    print("  EV BATTERY INTELLIGENCE API -- STARTUP (TRI-PILLAR SYSTEM)")
    print("=" * 65)

    # Module A — load sklearn/XGBoost fleet models
    print("  [Module A] Loading fleet prediction models...")
    load_all_module_a_models()
    status_a = get_model_status()
    for task, loaded in status_a.items():
        icon = "[OK]" if loaded else "[--]"
        print(f"    {icon}  {task}")

    # Module B — load BatteryIQ engine (PyTorch + sklearn)
    print("  [Module B] Loading BatteryIQ engine (CNN-LSTM + Multi-Zone RF)...")
    ok_b = load_module_b_engine()
    icon_b = "[OK]" if ok_b else "[--]"
    print(f"    {icon_b}  BatteryIQ Engine (SOH-Deep + Thermal)")

    # Module C — load BA-BMS & Knee-Point engine (XGBoost)
    print("  [Module C] Loading BA-BMS & Knee Prognostics engine...")
    ok_c = load_module_c_engine()
    icon_c = "[OK]" if ok_c else "[--]"
    print(f"    {icon_c}  BA-BMS Engine (Behavior AI/BSI + Knee Prognostics)")

    print("=" * 65)
    print(f"  API ready at http://0.0.0.0:8000")
    print(f"  Docs:       http://0.0.0.0:8000/docs")
    print("=" * 65 + "\n")

    yield  # API runs here

    print("\n  API shutting down.")


# ──────────────────────────────────────────────
#  APP INSTANCE
# ──────────────────────────────────────────────
app = FastAPI(
    title="EV Battery Intelligence API",
    description=(
        "Unified REST API combining three specialized ML & Cyber-Physical modules:\n\n"
        "**Module A** — Fleet-level EV predictions (SOC, SOH-tabular, RUL, Mileage)\n"
        "  - Trained on 930MB of real Indian fleet telematics data (50M+ records)\n"
        "  - Models: KNN, XGBoost, Gradient Boosting (sklearn / xgboost)\n\n"
        "**Module B** — Battery Health & Thermal Management (BatteryIQ Engine)\n"
        "  - Trained on 53M records from Euler HiLoad fleet\n"
        "  - SOH: Hybrid 1D-CNN + LSTM (PyTorch) — RMSE 5.29%\n"
        "  - Thermal: Multi-Zone Random Forest — F1 = 0.997\n\n"
        "**Module C** — Behavior-Aware BMS & Knee-Point Prognostics (BA-BMS)\n"
        "  - Driver Aggressiveness Index (AI) & Battery Stress Index (BSI)\n"
        "  - Knee-Point Remaining Useful Life (RUL_to_knee) via XGBoost Booster\n"
        "  - Multi-Target Meta-Ensemble"
    ),
    version="3.0.0",
    lifespan=lifespan,
)

# Allow all origins for development / demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
#  ROUTERS
# ──────────────────────────────────────────────
app.include_router(router_a)
app.include_router(router_b)
app.include_router(router_c)


# ──────────────────────────────────────────────
#  UTILITY ENDPOINTS
# ──────────────────────────────────────────────
@app.get("/", tags=["System"], summary="API Root")
def root():
    return {
        "name": "EV Battery Intelligence API",
        "version": "3.0.0",
        "modules": [
            "Module A (SOC/SOH/RUL/Mileage)",
            "Module B (Thermal/SOH-Deep/Diagnosis)",
            "Module C (Driver Behavior/Knee-Point/Ensemble)"
        ],
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthStatusResponse, tags=["System"], summary="System Health")
def health():
    """Check which models across all 3 modules are loaded and ready to serve predictions."""
    status_a = get_model_status()
    all_a = all(status_a.values())
    engine_b_ok = get_engine_b_status()
    engine_c_ok = get_engine_c_status()

    all_ok = all_a and engine_b_ok and engine_c_ok
    any_ok = any(status_a.values()) or engine_b_ok or engine_c_ok
    overall = "ok" if all_ok else ("degraded" if any_ok else "unavailable")
    
    msg_parts = []
    if not all_a:
        missing = [k for k, v in status_a.items() if not v]
        msg_parts.append(f"Module A missing: {missing}. Run modules/module_a/retrain_clean.py first.")
    if not engine_b_ok:
        msg_parts.append("Module B engine not loaded. Check modules/module_b/weights/.")
    if not engine_c_ok:
        msg_parts.append("Module C engine not loaded. Check modules/module_c/best_xgboost_model.json.")

    return HealthStatusResponse(
        status=overall,
        module_a_models=status_a,
        module_b_engine=engine_b_ok,
        module_c_engine=engine_c_ok,
        message=" | ".join(msg_parts) if msg_parts else "All 3 modules operational.",
    )


@app.get("/models/status", tags=["System"], summary="Model Inventory")
def models_status():
    """Return the full model inventory across all 3 modules."""
    status_a = get_model_status()
    names_a = get_model_names()
    return {
        "module_a": {
            "description": "Fleet-level EV prediction models (sklearn/XGBoost)",
            "models": {
                task: {
                    "loaded": status_a.get(task, False),
                    "architecture": names_a.get(task, "Trained Model"),
                }
                for task in ["SOC", "SOH", "RUL", "Mileage"]
            },
        },
        "module_b": {
            "description": "BatteryIQ Engine — Battery Health & Thermal Management (PyTorch + sklearn)",
            "engine_loaded": get_engine_b_status(),
            "models": {
                "SOH_Deep": {
                    "architecture": "Hybrid 1D-CNN + LSTM (PyTorch)",
                    "benchmark_rmse": 5.29,
                    "training_records": "20.5M Euler HiLoad",
                },
                "Thermal": {
                    "architecture": "Multi-Zone Random Forest (200 trees)",
                    "benchmark_f1": 0.997,
                    "training_records": "53M fleet alerts (50/50 balanced)",
                },
            },
        },
        "module_c": {
            "description": "Behavior-Aware BMS (BA-BMS) & Knee-Point Prognostics",
            "engine_loaded": get_engine_c_status(),
            "models": {
                "Driver_Behavior": {
                    "architecture": "BA-BMS Behavioral Indexing Engine (AI / BSI)",
                    "outputs": ["Driver Aggressiveness Index", "Battery Stress Index"],
                },
                "Knee_Point_Prognostics": {
                    "architecture": "XGBoost Booster (28 features) + StandardScaler",
                    "target": "RUL_to_knee (Cycles before accelerated capacity fade)",
                },
            },
        },
    }
