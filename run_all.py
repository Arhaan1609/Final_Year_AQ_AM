"""
run_all.py — Unified EV Battery Intelligence System Launcher (Tri-Pillar System).

Project Structure:
  Final_Year_Project_1/
  ├── modules/
  │   ├── module_a/   ← EV Fleet Prediction Pipeline (SOC/SOH/RUL/Mileage)
  │   ├── module_b/   ← BatteryIQ Engine (Thermal Safety + SOH-Deep)
  │   └── module_c/   ← Behavior-Aware BMS (AI/BSI) & Knee-Point Prognostics
  ├── api/            ← Unified FastAPI backend (11 endpoints)
  ├── data/
  │   ├── raw/        ← Raw fleet data
  │   └── processed/  ← Processed CSVs + feature sets
  ├── models/         ← Trained model files (.pkl / .keras / .pt)
  ├── results/        ← Evaluation outputs, plots, reports
  └── logs/

Usage:
  python run_all.py                    # Start unified API on port 8000
  python run_all.py --port 9000        # Custom port
  python run_all.py --cli              # Launch interactive CLI (12 prediction options)
  python run_all.py --check            # Show model status across all 3 modules
  python run_all.py --retrain          # Re-run Module A pipeline (steps 3-7) then start API
"""

import os
import sys
import argparse
import subprocess

# Ensure UTF-8 output on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_MODULE_A_DIR = os.path.join(_PROJECT_ROOT, "modules", "module_a")
_MODULE_B_DIR = os.path.join(_PROJECT_ROOT, "modules", "module_b")
_MODULE_C_DIR = os.path.join(_PROJECT_ROOT, "modules", "module_c")

sys.path.insert(0, _MODULE_A_DIR)


def _banner():
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║          EV BATTERY INTELLIGENCE — TRI-PILLAR SYSTEM LAUNCHER           ║
║                                                                          ║
║  modules/module_a: SOC | SOH | RUL | Mileage  (sklearn / XGBoost)      ║
║  modules/module_b: Thermal Safety | SOH-Deep  (PyTorch CNN-LSTM + RF)   ║
║  modules/module_c: Driver Behavior (AI/BSI) | Knee-Point Prognostics    ║
╚══════════════════════════════════════════════════════════════════════════╝
""")


def _check_models():
    """Print status of all trained models across all 8 task subfolders."""
    import config as cfg

    print("  ── Task Models  (models/) ──────────────────────────────────────────")
    task_map = {
        "SOC": ("soc", ["SOC_KNN.pkl", "scaler_soc.pkl"]),
        "SOH": ("soh", ["SOH_XGBoost.pkl", "scaler_soh.pkl"]),
        "RUL": ("rul", ["RUL_GradientBoosting.pkl", "scaler_rul.pkl"]),
        "Mileage": ("mileage", ["Mileage_XGBoost.pkl", "scaler_mileage.pkl"]),
        "Thermal Safety": ("thermal", ["thermal_rf_multizone.joblib"]),
        "SOH Deep": ("soh_deep", ["soh_hybrid_cnn_lstm.pt"]),
        "Knee Prognostics": ("knee_prognostics", ["best_xgboost_model.json", "feature_scaler.pkl"]),
        "Driver Behavior": ("driver_behavior", ["behavior_rules.json"]),
    }

    all_ok = True
    models_dir = cfg.MODELS_DIR

    for label, (subfolder, expected_files) in task_map.items():
        folder_path = os.path.join(models_dir, subfolder)
        folder_exists = os.path.exists(folder_path)
        if not folder_exists:
            print(f"  ✘  models/{subfolder:<18} (Folder missing!)")
            all_ok = False
            continue

        files = os.listdir(folder_path)
        missing = [ef for ef in expected_files if ef not in files]

        if not missing:
            total_size_kb = sum(os.path.getsize(os.path.join(folder_path, f)) for f in files if os.path.isfile(os.path.join(folder_path, f))) / 1024
            print(f"  ✔  {label:<18} models/{subfolder:<18} ({len(files)} files, {total_size_kb:.0f} KB)")
        else:
            print(f"  ✘  {label:<18} models/{subfolder:<18} (Missing: {missing})")
            all_ok = False

    print("\n  ── Data & Documentation Folders ────────────────────────────────────")
    data_folders = {
        "Raw Data":        os.path.join(_PROJECT_ROOT, "data", "raw"),
        "Processed Data":  os.path.join(_PROJECT_ROOT, "data", "processed"),
        "Documentation":   os.path.join(_PROJECT_ROOT, "docs"),
        "Results Plots":   cfg.PLOTS_DIR,
        "Results Reports": cfg.REPORTS_DIR,
        "System Logs":     cfg.LOGS_DIR,
    }
    for label, path in data_folders.items():
        exists = os.path.exists(path)
        icon = "✔" if exists else "✘"
        print(f"  {icon}  {label:<15} {path}")

    print()
    if all_ok:
        print("  ✔  All 3 modules and systems ready.\n")
    else:
        print("  ⚠  Some components missing:")
        print("     Module A models:  python modules/module_a/retrain_clean.py")
        print("     Module B weights: should be in modules/module_b/weights/")
        print("     Module C models:  should be in modules/module_c/\n")
    return all_ok


def _start_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Start the FastAPI server via uvicorn."""
    print(f"  Starting API server ...")
    print(f"  Local:  http://localhost:{port}")
    print(f"  Docs:   http://localhost:{port}/docs")
    print(f"  Health: http://localhost:{port}/health")
    print(f"  Models: http://localhost:{port}/models/status")
    print("\n  Press CTRL+C to stop.\n")

    cmd = [sys.executable, "-m", "uvicorn", "api.main:app",
           "--host", host, "--port", str(port)]
    if reload:
        cmd.append("--reload")

    subprocess.run(cmd, cwd=_PROJECT_ROOT)


def _start_cli():
    """Launch the interactive CLI prediction system."""
def _retrain_all():
    """Run master autonomous retraining pipeline across all 3 modules."""
    script = os.path.join(_PROJECT_ROOT, "retrain_all.py")
    print(f"  Launching Master Retraining Pipeline (All 3 Modules) ...\n")
    result = subprocess.run([sys.executable, script], cwd=_PROJECT_ROOT)
    return result.returncode == 0


def main():
    _banner()
    parser = argparse.ArgumentParser(description="EV Battery Intelligence — Unified Launcher")
    parser.add_argument("--cli",         action="store_true", help="Launch interactive CLI (12 prediction options)")
    parser.add_argument("--check",       action="store_true", help="Check system status across all 3 modules and exit")
    parser.add_argument("--retrain",     action="store_true", help="Re-train all models across Modules A, B, and C autonomously")
    parser.add_argument("--retrain-all", action="store_true", help="Alias for --retrain")
    parser.add_argument("--port",        type=int,  default=8000, help="API port (default: 8000)")
    parser.add_argument("--host",        type=str,  default="0.0.0.0", help="API host (default: 0.0.0.0)")
    parser.add_argument("--reload",      action="store_true", help="Enable uvicorn hot-reload (dev mode)")
    args = parser.parse_args()

    _check_models()

    if args.check:
        return

    if args.retrain or args.retrain_all:
        ok = _retrain_all()
        if not ok:
            print("  Retraining finished with errors. Fix before starting API.")
            sys.exit(1)

    if args.cli:
        _start_cli()
    else:
        _start_api(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()

