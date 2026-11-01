"""Database Models for Hospivance AI.

Supports SQLAlchemy ORM when installed, with transparent fallback
to pure-Python SQLite data objects.
"""

from datetime import datetime
from typing import Any

try:
    from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, func
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
    SQLALCHEMY_AVAILABLE = True

    class Department(Base):
        __tablename__ = "departments"
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(100), unique=True, nullable=False, index=True)
        total_beds = Column(Integer, nullable=False)
        target_occupancy_pct = Column(Float, default=80.0)
        critical_occupancy_pct = Column(Float, default=90.0)
        created_at = Column(DateTime, default=datetime.utcnow)

    class AdmissionRecord(Base):
        __tablename__ = "admissions_daily"
        id = Column(Integer, primary_key=True, index=True)
        date = Column(String(10), nullable=False, index=True)
        department_id = Column(Integer, nullable=False, index=True)
        department = Column(String(100), nullable=False, index=True)
        total_beds = Column(Integer, nullable=False)
        admissions_count = Column(Integer, nullable=False)
        discharges_count = Column(Integer, nullable=False)
        occupied_beds = Column(Integer, nullable=False)
        available_beds = Column(Integer, nullable=False)
        occupancy_rate = Column(Float, nullable=False)
        avg_wait_time_minutes = Column(Float, default=30.0)
        diverted_ambulances = Column(Integer, default=0)
        staff_on_duty = Column(Integer, default=20)
        day_of_week = Column(Integer, nullable=False)
        is_weekend = Column(Integer, default=0)
        is_holiday = Column(Integer, default=0)
        month = Column(Integer, nullable=False)
        flu_season_intensity = Column(Float, default=0.1)
        temperature_celsius = Column(Float, default=18.0)
        is_synthetic = Column(Boolean, default=True)

    class Alert(Base):
        __tablename__ = "alerts"
        id = Column(Integer, primary_key=True, index=True)
        timestamp = Column(DateTime, default=datetime.utcnow, index=True)
        department = Column(String(100), nullable=False, index=True)
        risk_level = Column(String(20), nullable=False, index=True)
        title = Column(String(200), nullable=False)
        message = Column(Text, nullable=False)
        metric_name = Column(String(100), nullable=False)
        metric_value = Column(Float, nullable=False)
        threshold_value = Column(Float, nullable=False)
        acknowledged = Column(Boolean, default=False, index=True)
        acknowledged_at = Column(DateTime, nullable=True)

    class Encounter(Base):
        __tablename__ = "encounters"
        id = Column(Integer, primary_key=True, index=True)
        encounter_id = Column(String(64), unique=True, nullable=False, index=True)
        patient_pseudonym = Column(String(64), nullable=False, index=True)
        department = Column(String(100), nullable=False)
        status = Column(String(30), default="in-progress")
        admit_date = Column(DateTime, default=datetime.utcnow)
        discharge_date = Column(DateTime, nullable=True)
        acuity_level = Column(Integer, default=3)
        reason_for_visit = Column(String(255), default="Acute care evaluation")
        is_synthetic = Column(Boolean, default=True)

except ImportError:
    SQLALCHEMY_AVAILABLE = True if False else False

    class ColumnExpr:
        def __init__(self, table_name: str, col_name: str):
            self.table_name = table_name
            self.col_name = col_name

        def __eq__(self, other):
            if other is None:
                return (f"{self.col_name} IS NULL", None)
            return (f"{self.col_name} = ?", other)

        def __ne__(self, other):
            return (f"{self.col_name} != ?", other)

        def __ge__(self, other):
            return (f"{self.col_name} >= ?", other)

        def __le__(self, other):
            return (f"{self.col_name} <= ?", other)

        def desc(self):
            return f"{self.col_name} DESC"

        def asc(self):
            return f"{self.col_name} ASC"

        def distinct(self):
            return ColumnExpr(self.table_name, f"DISTINCT {self.col_name}")

        def in_(self, items):
            placeholders = ", ".join(["?"] * len(items))
            return (f"{self.col_name} IN ({placeholders})", list(items))

        def __str__(self):
            return self.col_name

    class ModelMeta(type):
        def __getattr__(cls, name):
            return ColumnExpr(cls.__tablename__, name)

    class BaseModelFallback(metaclass=ModelMeta):
        __tablename__ = ""
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class Department(BaseModelFallback):
        __tablename__ = "departments"

    class AdmissionRecord(BaseModelFallback):
        __tablename__ = "admissions_daily"

    class Alert(BaseModelFallback):
        __tablename__ = "alerts"

    class Encounter(BaseModelFallback):
        __tablename__ = "encounters"

    class FuncMeta:
        @staticmethod
        def max(col_expr):
            class MaxExpr:
                expr = f"MAX({col_expr.col_name})"
                table_name = col_expr.table_name
            return MaxExpr()

    func = FuncMeta()
