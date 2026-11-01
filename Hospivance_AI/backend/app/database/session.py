"""Database session management with multi-backend and SQLite fallback support."""

import os
import sqlite3
import logging
from typing import Any
from app.config import DATABASE_URL, DEFAULT_SQLITE_URL
from app.database.models import SQLALCHEMY_AVAILABLE

logger = logging.getLogger("hospivance.database")

if SQLALCHEMY_AVAILABLE:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
    from app.database.models import Base

    def get_engine(url: str):
        connect_args = {}
        if url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
            os.makedirs(os.path.dirname(url.replace("sqlite:///", "")), exist_ok=True)
        return create_engine(url, connect_args=connect_args, pool_pre_ping=True)

    try:
        engine = get_engine(DATABASE_URL)
        with engine.connect() as conn:
            pass
        active_url = DATABASE_URL
    except Exception as e:
        logger.warning("Falling back to SQLite: %s", e)
        active_url = DEFAULT_SQLITE_URL
        engine = get_engine(active_url)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def init_db():
        Base.metadata.create_all(bind=engine)

else:
    from app.database.sqlite_adapter import SQLiteSession, DB_FILE

    active_url = DEFAULT_SQLITE_URL
    SessionLocal = SQLiteSession
    Session = Any  # type alias for route annotations

    def get_db():
        db = SQLiteSession(DB_FILE)
        try:
            yield db
        finally:
            db.close()

    def init_db():
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            total_beds INTEGER NOT NULL,
            target_occupancy_pct REAL DEFAULT 80.0,
            critical_occupancy_pct REAL DEFAULT 90.0,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS admissions_daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            department TEXT NOT NULL,
            total_beds INTEGER NOT NULL,
            admissions_count INTEGER NOT NULL,
            discharges_count INTEGER NOT NULL,
            occupied_beds INTEGER NOT NULL,
            available_beds INTEGER NOT NULL,
            occupancy_rate REAL NOT NULL,
            avg_wait_time_minutes REAL DEFAULT 30.0,
            diverted_ambulances INTEGER DEFAULT 0,
            staff_on_duty INTEGER DEFAULT 20,
            day_of_week INTEGER NOT NULL,
            is_weekend INTEGER DEFAULT 0,
            is_holiday INTEGER DEFAULT 0,
            month INTEGER NOT NULL,
            flu_season_intensity REAL DEFAULT 0.1,
            temperature_celsius REAL DEFAULT 18.0,
            is_synthetic INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            department TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            threshold_value REAL NOT NULL,
            acknowledged INTEGER DEFAULT 0,
            acknowledged_at TEXT
        );

        CREATE TABLE IF NOT EXISTS encounters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id TEXT UNIQUE NOT NULL,
            patient_pseudonym TEXT NOT NULL,
            department TEXT NOT NULL,
            status TEXT DEFAULT 'in-progress',
            admit_date TEXT,
            discharge_date TEXT,
            acuity_level INTEGER DEFAULT 3,
            reason_for_visit TEXT DEFAULT 'Acute care evaluation',
            is_synthetic INTEGER DEFAULT 1
        );
        """)
        conn.commit()
        conn.close()
        logger.info("SQLite schema initialized successfully.")
