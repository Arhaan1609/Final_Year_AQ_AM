"""
Database package for EV Battery Intelligence Platform.
Supports MySQL with automatic SQLite fallback and auto-seeding.
"""
from .database import engine, SessionLocal, get_db, init_db
from .models import Vehicle, TelemetryLog, MaintenanceAlert
