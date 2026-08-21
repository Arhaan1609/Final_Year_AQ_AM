"""
MCP server for the EV Battery Intelligence Platform.

Wraps the 11 existing FastAPI prediction endpoints as MCP tools, so any
MCP-capable agent (Claude Desktop, Antigravity, a custom copilot backend)
can call your live models conversationally.

Setup:
    pip install -r requirements.txt

Run standalone (for testing with the MCP inspector):
    python mcp_server.py

Requires your FastAPI backend (run_all.py) already running on
BATTERY_API_BASE (default http://localhost:8000).
"""

import os
import httpx

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    try:
        from mcp.server import MCPServer as FastMCP
    except ImportError:
        from mcp.server.mcpserver import MCPServer as FastMCP

BATTERY_API_BASE = os.environ.get("BATTERY_API_BASE", "http://localhost:8000")

mcp = FastMCP("ev-battery-intelligence")


async def _post(path: str, payload: dict) -> dict:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{BATTERY_API_BASE}{path}", json=payload)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        return {"error": str(e), "path": path, "status": "backend_unreachable_or_failed"}


async def _get(path: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{BATTERY_API_BASE}{path}")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        return {"error": str(e), "path": path, "status": "backend_unreachable_or_failed"}


@mcp.tool()
async def system_health() -> dict:
    """Check whether the battery intelligence backend and all three model
    modules (fleet state, thermal safety, behavior/knee) are online."""
    return await _get("/health")


@mcp.tool()
async def predict_soc(
    battery_voltage: float = 74.0,
    battery_temp: float = 32.0,
    battery_current: float = -20.0,
    abs_current: float = 20.0,
    is_charging: int = 0,
    odometer: float = 12500.0,
    odometer_diff: float = 5.2,
    voltage_deviation: float = 2.0,
    temp_stress_index: float = 0.28,
    drive_mode_encoded: int = 1,
    hour: int = 14,
    day_of_week: int = 3,
    month: int = 2,
    is_weekend: int = 0,
    is_peak: int = 1,
    oem_encoded: int = 0,
    model_encoded: int = 0,
) -> dict:
    """Predict State of Charge (SOC %) for a vehicle from current telemetry."""
    payload = {
        "battery_voltage": battery_voltage,
        "battery_temp": battery_temp,
        "battery_current": battery_current,
        "abs_current": abs_current,
        "is_charging": is_charging,
        "odometer": odometer,
        "odometer_diff": odometer_diff,
        "voltage_deviation": voltage_deviation,
        "temp_stress_index": temp_stress_index,
        "drive_mode_encoded": drive_mode_encoded,
        "hour": hour,
        "day_of_week": day_of_week,
        "month": month,
        "is_weekend": is_weekend,
        "is_peak": is_peak,
        "oem_encoded": oem_encoded,
        "model_encoded": model_encoded,
    }
    return await _post("/predict/soc", payload)


@mcp.tool()
async def predict_soh(
    battery_voltage: float = 74.0,
    battery_temp: float = 30.0,
    battery_current: float = -15.0,
    abs_current: float = 15.0,
    odometer: float = 15000.0,
    odometer_diff: float = 10.0,
    charge_cycle_count: float = 250.0,
    mile_avg: float = 75.0,
    miles_per_charge: float = 110.0,
    days_in_service: float = 300.0,
    degradation_factor: float = 0.05,
    temp_stress_index: float = 0.2,
    voltage_deviation: float = 2.0,
    oem_encoded: int = 0,
    model_encoded: int = 0,
) -> dict:
    """Predict State of Health (SOH %) — battery capacity remaining vs new."""
    payload = {
        "battery_voltage": battery_voltage,
        "battery_temp": battery_temp,
        "battery_current": battery_current,
        "abs_current": abs_current,
        "odometer": odometer,
        "odometer_diff": odometer_diff,
        "charge_cycle_count": charge_cycle_count,
        "mile_avg": mile_avg,
        "miles_per_charge": miles_per_charge,
        "days_in_service": days_in_service,
        "degradation_factor": degradation_factor,
        "temp_stress_index": temp_stress_index,
        "voltage_deviation": voltage_deviation,
        "oem_encoded": oem_encoded,
        "model_encoded": model_encoded,
    }
    return await _post("/predict/soh", payload)


@mcp.tool()
async def predict_rul(
    odometer: float = 15000.0,
    soc_at_charge: float = 85.0,
    mile_avg: float = 75.0,
    miles_per_charge: float = 110.0,
    days_in_service: float = 300.0,
    degradation_factor: float = 0.05,
    soh_mean: float = 92.0,
    miles_per_charge_rolling_3: float = 112.0,
    miles_per_charge_rolling_5: float = 110.0,
    miles_per_charge_rolling_10: float = 108.0,
    oem_encoded: int = 0,
    model_encoded: int = 0,
) -> dict:
    """Predict Remaining Useful Life in charge cycles."""
    payload = {
        "odometer": odometer,
        "soc_at_charge": soc_at_charge,
        "mile_avg": mile_avg,
        "miles_per_charge": miles_per_charge,
        "days_in_service": days_in_service,
        "degradation_factor": degradation_factor,
        "soh_mean": soh_mean,
        "miles_per_charge_rolling_3": miles_per_charge_rolling_3,
        "miles_per_charge_rolling_5": miles_per_charge_rolling_5,
        "miles_per_charge_rolling_10": miles_per_charge_rolling_10,
        "oem_encoded": oem_encoded,
        "model_encoded": model_encoded,
    }
    return await _post("/predict/rul", payload)


@mcp.tool()
async def predict_mileage(
    run_kms: float = 45.0,
    avg_speed: float = 32.0,
    max_speed: float = 55.0,
    trip_duration_hrs: float = 1.4,
    stoppage_count: int = 3,
    energy_efficiency: float = 0.18,
    trip_intensity: float = 44.8,
    speed_ratio: float = 0.58,
    stoppage_density: float = 2.14,
    energy_utilized: float = 8.1,
    hour: int = 11,
    day_of_week: int = 2,
    month: int = 2,
    is_weekend: int = 0,
    is_peak: int = 0,
    oem_encoded: int = 0,
    city_encoded: int = 0,
) -> dict:
    """Predict driving range in km for the current charge."""
    payload = {
        "run_kms": run_kms,
        "avg_speed": avg_speed,
        "max_speed": max_speed,
        "trip_duration_hrs": trip_duration_hrs,
        "stoppage_count": stoppage_count,
        "energy_efficiency": energy_efficiency,
        "trip_intensity": trip_intensity,
        "speed_ratio": speed_ratio,
        "stoppage_density": stoppage_density,
        "energy_utilized": energy_utilized,
        "hour": hour,
        "day_of_week": day_of_week,
        "month": month,
        "is_weekend": is_weekend,
        "is_peak": is_peak,
        "oem_encoded": oem_encoded,
        "city_encoded": city_encoded,
    }
    return await _post("/predict/mileage", payload)


@mcp.tool()
async def predict_thermal(
    vbt: float = 35.0,
    vct: float = 42.0,
    vmt: float = 55.0,
    vbv: float = 74.0,
    vbc: float = -20.0,
    soc: float = 80.0,
    speed: float = 30.0,
) -> dict:
    """Assess multi-zone thermal safety (battery/controller/motor) and return
    risk probability, severity, and recommended action."""
    payload = {
        "vbt": vbt,
        "vct": vct,
        "vmt": vmt,
        "vbv": vbv,
        "vbc": vbc,
        "soc": soc,
        "speed": speed,
    }
    return await _post("/predict/thermal", payload)


@mcp.tool()
async def predict_soh_deep(
    vehicle_id: str = "GJ05CV6564",
    sequence: list[list[float]] = None,
) -> dict:
    """Deep sequential SOH estimate from a 10-step time series of
    [voltage, current, temperature, soc]."""
    if sequence is None:
        sequence = [
            [78.0, -15.0, 28.0, 85.0], [77.5, -18.0, 28.5, 84.0],
            [77.0, -20.0, 29.0, 83.0], [76.5, -22.0, 29.5, 82.0],
            [76.0, -20.0, 30.0, 81.0], [75.5, -18.0, 30.2, 80.0],
            [75.0, -19.0, 30.5, 79.0], [74.5, -20.0, 30.8, 78.0],
            [74.0, -21.0, 31.0, 77.0], [73.5, -22.0, 31.2, 76.0]
        ]
    return await _post("/predict/soh-deep", {"vehicle_id": vehicle_id, "sequence": sequence})


@mcp.tool()
async def diagnose_vehicle(
    vehicle_id: str = "GJ05CV6564",
    oem_model: str = "Euler HiLoad",
    soc: float = 82.0,
    voltage: float = 76.0,
    current: float = -18.0,
    battery_temp: float = 30.0,
    controller_temp: float = 40.0,
    motor_temp: float = 52.0,
    speed: float = 35.0,
) -> dict:
    """Full digital-twin diagnosis: overall health score, thermal status,
    SOH status, and action items for one vehicle."""
    payload = {
        "vehicle_id": vehicle_id,
        "oem_model": oem_model,
        "soc": soc,
        "voltage": voltage,
        "current": current,
        "battery_temp": battery_temp,
        "controller_temp": controller_temp,
        "motor_temp": motor_temp,
        "speed": speed,
    }
    return await _post("/predict/diagnose/vehicle", payload)


@mcp.tool()
async def predict_driver_behavior(
    harsh_accel_count: int = 3,
    harsh_brake_count: int = 2,
    harsh_corner_count: int = 1,
    speed_variance: float = 8.5,
    avg_speed: float = 38.0,
    max_speed: float = 68.0,
    battery_temp_max: float = 36.0,
    max_discharge_current: float = 35.0,
) -> dict:
    """Predict driver aggressiveness index and battery stress index from
    driving-pattern telemetry."""
    payload = {
        "harsh_accel_count": harsh_accel_count,
        "harsh_brake_count": harsh_brake_count,
        "harsh_corner_count": harsh_corner_count,
        "speed_variance": speed_variance,
        "avg_speed": avg_speed,
        "max_speed": max_speed,
        "battery_temp_max": battery_temp_max,
        "max_discharge_current": max_discharge_current,
    }
    return await _post("/predict/driver-behavior", payload)


@mcp.tool()
async def predict_knee_point(
    charge_cycle_count: float = 200.0,
    capacity: float = 94.0,
    voltage: float = 73.8,
    battery_temp: float = 33.0,
    current: float = -20.0,
    soc: float = 75.0,
    speed: float = 36.0,
) -> dict:
    """Predict remaining cycles to the degradation knee point (where aging
    turns from linear to rapid/irreversible)."""
    payload = {
        "charge_cycle_count": charge_cycle_count,
        "capacity": capacity,
        "voltage": voltage,
        "battery_temp": battery_temp,
        "current": current,
        "soc": soc,
        "speed": speed,
    }
    return await _post("/predict/knee-point", payload)


@mcp.tool()
async def meta_ensemble_report(
    vehicle_id: str = "GJ05CV6564",
    charge_cycle_count: float = 200.0,
    battery_voltage: float = 73.8,
    battery_temp: float = 33.0,
    battery_current: float = -20.0,
    soc: float = 75.0,
    harsh_accel_count: int = 3,
    speed_variance: float = 8.5,
) -> dict:
    """Unified fleet health report combining all three modules (state,
    thermal, behavior) into one grade and executive summary."""
    payload = {
        "vehicle_id": vehicle_id,
        "charge_cycle_count": charge_cycle_count,
        "battery_voltage": battery_voltage,
        "battery_temp": battery_temp,
        "battery_current": battery_current,
        "soc": soc,
        "harsh_accel_count": harsh_accel_count,
        "speed_variance": speed_variance,
    }
    return await _post("/predict/meta-ensemble", payload)


if __name__ == "__main__":
    mcp.run()
