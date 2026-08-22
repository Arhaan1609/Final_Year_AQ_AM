"""
api/routers/db_routes.py — SQL Database Routes for Fleet Telemetry & Management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from pydantic import BaseModel

from api.db.database import get_db, DB_ENGINE_TYPE
from api.db.models import Vehicle, TelemetryLog, MaintenanceAlert

router = APIRouter(prefix="/api/v1/db", tags=["SQL Fleet Database"])

class VehicleOut(BaseModel):
    id: str
    model: str
    fleet: str
    driver: str
    soc: float
    soh: float
    rul: int
    mileage: float
    battery_temp: float
    controller_temp: float
    motor_temp: float
    voltage: float
    current: float
    speed: float
    charge_cycle_count: int
    status: str
    lastPing: Optional[str] = None

    class Config:
        from_attributes = True

class FleetSummaryOut(BaseModel):
    db_engine: str
    total_vehicles: int
    active_vehicles: int
    warning_vehicles: int
    critical_vehicles: int
    charging_vehicles: int
    avg_soc: float
    avg_soh: float
    avg_temp: float
    critical_thermal_count: int
    knee_risk_count: int

@router.get("/summary", response_model=FleetSummaryOut)
def get_fleet_summary(db: Session = Depends(get_db)):
    """Computes instant SQL aggregation metrics across the entire enterprise fleet."""
    total = db.query(Vehicle).count()
    active = db.query(Vehicle).filter(Vehicle.status == "active").count()
    warning = db.query(Vehicle).filter(Vehicle.status == "warning").count()
    critical = db.query(Vehicle).filter(Vehicle.status == "critical").count()
    charging = db.query(Vehicle).filter(Vehicle.status == "charging").count()

    avg_soc = db.query(func.avg(Vehicle.soc)).scalar() or 0.0
    avg_soh = db.query(func.avg(Vehicle.soh)).scalar() or 0.0
    avg_temp = db.query(func.avg(Vehicle.battery_temp)).scalar() or 0.0
    critical_thermal = db.query(Vehicle).filter(Vehicle.battery_temp >= 45.0).count()
    knee_risk = db.query(Vehicle).filter(Vehicle.charge_cycle_count >= 1000).count()

    return FleetSummaryOut(
        db_engine=DB_ENGINE_TYPE,
        total_vehicles=total,
        active_vehicles=active,
        warning_vehicles=warning,
        critical_vehicles=critical,
        charging_vehicles=charging,
        avg_soc=round(avg_soc, 2),
        avg_soh=round(avg_soh, 2),
        avg_temp=round(avg_temp, 2),
        critical_thermal_count=critical_thermal,
        knee_risk_count=knee_risk,
    )

@router.get("/vehicles")
def get_vehicles(
    query: Optional[str] = None,
    status: Optional[str] = None,
    fleet: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """SQL Paginated and filtered search across all fleet vehicles."""
    q = db.query(Vehicle)

    if query:
        term = f"%{query.strip()}%"
        q = q.filter(or_(Vehicle.id.ilike(term), Vehicle.driver.ilike(term), Vehicle.fleet.ilike(term)))

    if status and status != "all":
        q = q.filter(Vehicle.status == status)

    if fleet and fleet != "all":
        q = q.filter(Vehicle.fleet.ilike(f"%{fleet}%"))

    total = q.count()
    results = q.offset(offset).limit(limit).all()

    # Map model attribute to schema
    vehicles = []
    for v in results:
        vehicles.append({
            "id": v.id,
            "model": v.model,
            "fleet": v.fleet,
            "driver": v.driver,
            "soc": v.soc,
            "soh": v.soh,
            "rul": v.rul,
            "mileage": v.mileage,
            "battery_temp": v.battery_temp,
            "controller_temp": v.controller_temp,
            "motor_temp": v.motor_temp,
            "voltage": v.voltage,
            "current": v.current,
            "speed": v.speed,
            "charge_cycle_count": v.charge_cycle_count,
            "status": v.status,
            "lastPing": v.last_ping,
        })

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "vehicles": vehicles,
    }

@router.get("/vehicles/{vin}")
def get_vehicle_by_vin(vin: str, db: Session = Depends(get_db)):
    """Fetch complete SQL state and telemetry for a single vehicle."""
    v = db.query(Vehicle).filter(Vehicle.id.ilike(vin.strip())).first()
    if not v:
        raise HTTPException(status_code=404, detail=f"Vehicle {vin} not found in SQL database.")

    return {
        "id": v.id,
        "model": v.model,
        "fleet": v.fleet,
        "driver": v.driver,
        "soc": v.soc,
        "soh": v.soh,
        "rul": v.rul,
        "mileage": v.mileage,
        "battery_temp": v.battery_temp,
        "controller_temp": v.controller_temp,
        "motor_temp": v.motor_temp,
        "voltage": v.voltage,
        "current": v.current,
        "speed": v.speed,
        "charge_cycle_count": v.charge_cycle_count,
        "status": v.status,
        "lastPing": v.last_ping,
    }
