"""Hospivance AI - Main FastAPI Application.

AI-Powered Hospital Bottleneck & Patient Admission Prediction System.
"""

import os
import sys
import asyncio
import random
from datetime import datetime
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.config import (
    APP_NAME,
    APP_ENV,
    CORS_ORIGINS,
    LLM_PROVIDER,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    ORGANIZER_API_BASE_URL,
)
from app.database.session import init_db, SessionLocal, active_url
from app.database.seed import seed_database_if_empty
from ml.inference import load_model_and_metadata

# Import route routers
from app.routes import (
    dashboard,
    beds,
    departments,
    predict,
    alerts,
    analytics,
    recommendations,
    reports,
    fhir,
    organizer,
)

app = FastAPI(
    title=APP_NAME,
    description="AI-powered Hospital Bottleneck and Patient Admission Prediction System",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(dashboard.router)
app.include_router(beds.router)
app.include_router(departments.router)
app.include_router(predict.router)
app.include_router(alerts.router)
app.include_router(analytics.router)
app.include_router(recommendations.router)
app.include_router(reports.router)
app.include_router(fhir.router)
app.include_router(organizer.router)


@app.on_event("startup")
def on_startup():
    """Initializes database schema, seeds demo records, and prepares ML artifacts."""
    print("=" * 60)
    print(f"Starting {APP_NAME} in {APP_ENV} mode...")
    print(f"Database: {active_url.split('@')[-1] if '@' in active_url else active_url}")
    
    # 1. Initialize DB tables
    init_db()

    # 2. Seed initial synthetic data if empty
    db = SessionLocal()
    try:
        csv_path = os.path.join(os.path.dirname(backend_dir), "data", "hospital_daily.csv")
        seed_database_if_empty(db, csv_path=csv_path)
    finally:
        db.close()

    # 3. Load or train initial ML model
    try:
        model, feats, metrics = load_model_and_metadata()
        print(f"ML Model loaded successfully ({len(feats)} features, RMSE: {metrics.get('rmse')})")
    except Exception as e:
        print(f"Warning: Could not pre-load model: {e}")

    print(f"{APP_NAME} operational. Ready to accept requests.")
    print("=" * 60)


@app.get("/health", tags=["Health"])
def health_check():
    """Liveness, database status, model readiness, and configuration flags."""
    model_ready = False
    try:
        load_model_and_metadata()
        model_ready = True
    except Exception:
        pass

    return {
        "status": "healthy",
        "app_name": APP_NAME,
        "environment": APP_ENV,
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "type": "postgresql" if "postgresql" in active_url else "sqlite",
            "connected": True,
        },
        "ml_pipeline": {
            "model_ready": model_ready,
            "algorithm": "RandomForestRegressor",
            "target": "patient_admissions",
        },
        "ai_recommendations": {
            "llm_provider": LLM_PROVIDER,
            "gemini_configured": bool(GEMINI_API_KEY),
            "openai_configured": bool(OPENAI_API_KEY),
            "fallback": "Clinical Decision Support Heuristic v2.4",
        },
        "organizer_integration": {
            "configured": bool(ORGANIZER_API_BASE_URL),
        },
        "synthetic_notice": "Uses synthetic hospital data. For operational research and demonstration only.",
    }


# WebSocket Manager for Real-time Dashboard Updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection)


ws_manager = ConnectionManager()


@app.websocket("/ws/live")
async def live_dashboard_websocket(websocket: WebSocket):
    """Simulated real-time hospital occupancy feed."""
    await ws_manager.connect(websocket)
    base_occupied = 328
    total_beds = 395
    try:
        while True:
            # Slight random walk (+/- 1-2 patients) to simulate live arrivals & discharges
            delta = random.choice([-2, -1, 0, 1, 2])
            base_occupied = max(280, min(total_beds, base_occupied + delta))
            rate = round((base_occupied / total_beds) * 100.0, 1)

            payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "simulated": True,
                "total_beds": total_beds,
                "occupied_beds": base_occupied,
                "available_beds": total_beds - base_occupied,
                "occupancy_rate": rate,
                "risk_level": "HIGH" if rate >= 90 else "MODERATE" if rate >= 75 else "LOW",
                "icu_occupied": min(30, max(24, 28 + random.choice([-1, 0, 1]))),
                "er_waiting_patients": max(8, 19 + random.choice([-2, -1, 0, 1, 2])),
            }
            await websocket.send_json(payload)
            await asyncio.sleep(4)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
