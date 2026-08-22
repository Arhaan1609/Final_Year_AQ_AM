"""
api/db/database.py — Resilient Database Connection Layer.
Attempts to connect to MySQL (database 'EV') and gracefully falls back to SQLite if MySQL is unreachable.
"""

import os
import json
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configurable MySQL Parameters
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "EV")

if MYSQL_PASSWORD:
    MYSQL_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
else:
    MYSQL_URL = f"mysql+pymysql://{MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

SQLITE_URL = "sqlite:///./fleet_intelligence.db"

Base = declarative_base()

def create_db_engine():
    """Attempts MySQL connection, fallback to SQLite on auth or connection error."""
    # 1. Try MySQL if configured
    try:
        engine = create_engine(MYSQL_URL, pool_recycle=3600, pool_pre_ping=True)
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"  [Database] Connected to MySQL: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")
        return engine, "mysql"
    except Exception as mysql_err:
        print(f"  [Database] MySQL not reachable ({mysql_err.__class__.__name__}). Using high-speed SQLite persistence.")
        engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
        return engine, "sqlite"

engine, DB_ENGINE_TYPE = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """FastAPI Dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes tables and seeds 800+ real vehicles from fleet_vehicles.json if empty."""
    from .models import Vehicle
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        count = db.query(Vehicle).count()
        if count == 0:
            print("  [Database] Seeding 800+ fleet vehicles into SQL database...")
            json_path = os.path.join(
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
                "frontend", "public", "data", "fleet_vehicles.json"
            )
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    records = json.load(f)
                    vehicles = []
                    for r in records:
                        v = Vehicle(
                            id=r.get("id"),
                            model=r.get("model", "Euler HiLoad EV"),
                            fleet=r.get("fleet", "NCR Hub"),
                            driver=r.get("driver", "Fleet Operator"),
                            soc=float(r.get("soc", 75.0)),
                            soh=float(r.get("soh", 95.0)),
                            rul=int(r.get("rul", 1200)),
                            mileage=float(r.get("mileage", 110.0)),
                            battery_temp=float(r.get("battery_temp", 32.0)),
                            controller_temp=float(r.get("controller_temp", 40.0)),
                            motor_temp=float(r.get("motor_temp", 50.0)),
                            voltage=float(r.get("voltage", 75.0)),
                            current=float(r.get("current", -15.0)),
                            speed=float(r.get("speed", 30.0)),
                            charge_cycle_count=int(r.get("charge_cycle_count", 150)),
                            status=r.get("status", "active"),
                            last_ping=r.get("lastPing", "Just now"),
                        )
                        vehicles.append(v)
                    db.bulk_save_objects(vehicles)
                    db.commit()
                    print(f"  [Database] Successfully seeded {len(vehicles)} vehicles into SQL database!")
        else:
            print(f"  [Database] SQL database verified ({count} vehicles loaded).")
    except Exception as e:
        print(f"  [Database] Seed error: {e}")
        db.rollback()
    finally:
        db.close()
