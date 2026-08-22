"""
api/db/models.py — SQLAlchemy ORM models for EV Fleet Intelligence.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String(64), primary_key=True, index=True)
    model = Column(String(128), default="Euler HiLoad EV (12.4 kWh)")
    fleet = Column(String(128), default="Delhi NCR Fleet")
    driver = Column(String(128), default="Fleet Driver")
    soc = Column(Float, default=75.0)
    soh = Column(Float, default=95.0)
    rul = Column(Integer, default=1200)
    mileage = Column(Float, default=110.0)
    battery_temp = Column(Float, default=32.0)
    controller_temp = Column(Float, default=40.0)
    motor_temp = Column(Float, default=50.0)
    voltage = Column(Float, default=75.0)
    current = Column(Float, default=-15.0)
    speed = Column(Float, default=30.0)
    charge_cycle_count = Column(Integer, default=150)
    status = Column(String(32), default="active", index=True) # active, warning, critical, charging
    last_ping = Column(String(64), default="Just now")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String(64), ForeignKey("vehicles.id"), index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    voltage = Column(Float)
    current = Column(Float)
    battery_temp = Column(Float)
    speed = Column(Float)
    soc_predicted = Column(Float)
    soh_predicted = Column(Float)
    thermal_status = Column(String(64))

class MaintenanceAlert(Base):
    __tablename__ = "maintenance_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String(64), ForeignKey("vehicles.id"), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    severity = Column(String(32), default="WARNING") # INFO, WARNING, CRITICAL
    category = Column(String(64)) # THERMAL, KNEE_DEGRADATION, DRIVER_STRAIN, SOH_DROP
    message = Column(Text)
    resolved = Column(Integer, default=0) # 0 = active, 1 = resolved
