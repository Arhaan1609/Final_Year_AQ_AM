"""
MCP server for the EV Battery Intelligence Platform.

Wraps the 11 existing FastAPI prediction endpoints as MCP tools, so any
MCP-capable agent (Claude Desktop, Antigravity, a custom copilot backend)
can call your live models conversationally.

Setup:
    pip install "mcp[cli]" httpx

Run standalone (for testing with the MCP inspector):
    mcp dev mcp_server.py

Run as part of your own agent backend: import `mcp` from this module and
mount it, or run it over stdio/SSE per the MCP SDK docs.

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
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(f"{BATTERY_API_BASE}{path}", json=payload)
        resp.raise_for_status()
        return resp.json()


async def _get(path: str) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f"{BATTERY_API_BASE}{path}")
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def system_health() -> dict:
    """Check whether the battery intelligence backend and all three model
    modules (fleet state, thermal safety, behavior/knee) are online."""
    return await _get("/health")


@mcp.tool()
async def predict_soc(
    battery_voltage: float = 75.8,
    battery_temp: float = 33.2,
    battery_current: float = -18.4,
    abs_current: float = 18.4,
    is_charging: int = 0,
    odometer: float = 12500.0,
    odometer_diff: float = 5.2,
    voltage_deviation: float = 0.0,
    temp_stress_index: float = 0.2,
    drive_mode_encoded: int = 1,
    hour: int = 14,
    day_of_week: int = 2,
    month: int = 6,
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
    battery_voltage: float = 75.8,
    battery_temp: float = 33.2,
    battery_current: float = -18.4,
    abs_current: float = 18.4,
    odometer: float = 12500.0,
    odometer_diff: float = 0.0,
    charge_cycle_count: float = 215.0,
    mile_avg: float = 88.0,
    miles_per_charge: float = 95.0,
    days_in_service: float = 180.0,
    degradation_factor: float = 0.0,
    temp_stress_index: float = 0.0,
    voltage_deviation: float = 0.0,
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
    odometer: float = 12500.0,
    soc_at_charge: float = 85.0,
    mile_avg: float = 88.0,
    miles_per_charge: float = 95.0,
    days_in_service: float = 180.0,
    degradation_factor: float = 0.0,
    soh_mean: float = 85.0,
    miles_per_charge_rolling_3: float = 92.0,
    miles_per_charge_rolling_5: float = 90.0,
    miles_per_charge_rolling_10: float = 88.0,
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
    avg_speed: float = 34.0,
    max_speed: float = 58.0,
    trip_duration_hrs: float = 1.5,
    stoppage_count: int = 2,
    energy_efficiency: float = 0.88,
    trip_intensity: float = 1.2,
    speed_ratio: float = 0.58,
    stoppage_density: float = 0.05,
    energy_utilized: float = 8.5,
    hour: int = 10,
    day_of_week: int = 2,
    month: int = 6,
    is_weekend: int = 0,
    is_peak: int = 1,
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
    vbt: float = 33.2,
    vct: float = 41.5,
    vmt: float = 54.0,
    vbv: float = 75.8,
    vbc: float = -18.4,
    soc: float = 82.4,
    speed: float = 34.2,
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
async def predict_soh_deep(vehicle_id: str = "GJ05CV6564", sequence: list[list[float]] = None) -> dict:
    """Deep sequential SOH estimate from a 10-step time series of
    [voltage, current, temperature, soc]."""
    if sequence is None:
        sequence = [
            [78.0, -15.0, 28.0, 85.0],
            [77.5, -18.0, 28.5, 84.0],
            [77.0, -20.0, 29.0, 83.0],
            [76.5, -22.0, 29.5, 82.0],
            [76.0, -20.0, 30.0, 81.0],
            [75.5, -18.0, 30.2, 80.0],
            [75.0, -19.0, 30.5, 79.0],
            [74.5, -20.0, 30.8, 78.0],
            [74.0, -21.0, 31.0, 77.0],
            [73.5, -22.0, 31.2, 76.0],
        ]
    return await _post("/predict/soh-deep", {"vehicle_id": vehicle_id, "sequence": sequence})


@mcp.tool()
async def diagnose_vehicle(
    vehicle_id: str = "GJ05CV6564",
    oem_model: str = "Euler HiLoad EV (12.4 kWh)",
    soc: float = 82.4,
    voltage: float = 75.8,
    current: float = -18.4,
    battery_temp: float = 33.2,
    controller_temp: float = 41.5,
    motor_temp: float = 54.0,
    speed: float = 34.2,
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
    harsh_accel_count: int = 2,
    harsh_brake_count: int = 1,
    harsh_corner_count: int = 1,
    speed_variance: float = 7.8,
    avg_speed: float = 34.2,
    max_speed: float = 58.0,
    battery_temp_max: float = 37.2,
    max_discharge_current: float = 36.0,
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
    charge_cycle_count: float = 215.0,
    capacity: float = 94.2,
    voltage: float = 75.8,
    battery_temp: float = 33.2,
    current: float = -18.4,
    soc: float = 82.4,
    speed: float = 34.2,
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
    charge_cycle_count: float = 215.0,
    battery_voltage: float = 75.8,
    battery_temp: float = 33.2,
    battery_current: float = -18.4,
    soc: float = 82.4,
    harsh_accel_count: int = 2,
    speed_variance: float = 7.8,
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
