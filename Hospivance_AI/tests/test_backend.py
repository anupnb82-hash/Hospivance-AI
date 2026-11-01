"""Comprehensive Test Suite for Hospivance AI Backend."""

import os
import sys

sys.path.insert(0, os.path.abspath("backend"))

from fastapi.testclient import TestClient
from app.main import app

def run_all_tests():
    print("\n" + "=" * 50)
    print("RUNNING HOSPIVANCE AI END-TO-END BACKEND TESTS")
    print("=" * 50)

    with TestClient(app) as client:
        # 1. Health check
        r = client.get("/health")
        assert r.status_code == 200, f"Health check failed: {r.text}"
        health_data = r.json()
        print(" [PASS] GET /health ->", health_data["status"], "| Model Ready:", health_data["ml_pipeline"]["model_ready"])

        # 2. Dashboard
        r = client.get("/api/dashboard")
        assert r.status_code == 200, f"Dashboard failed: {r.text}"
        dash_data = r.json()
        print(" [PASS] GET /api/dashboard -> Total Beds:", dash_data["kpis"]["total_beds"], "| Occupancy:", f"{dash_data['kpis']['overall_occupancy_rate']}%")

        # 3. Beds
        r = client.get("/api/beds")
        assert r.status_code == 200, f"Beds failed: {r.text}"
        beds_data = r.json()
        print(" [PASS] GET /api/beds -> Departments Tracked:", len(beds_data["department_beds"]))

        # 4. Departments
        r = client.get("/api/departments")
        assert r.status_code == 200, f"Departments failed: {r.text}"
        dept_data = r.json()
        print(" [PASS] GET /api/departments -> Departments Count:", dept_data["departments_count"])

        # 5. Predictions (1-day, 3-day, 7-day)
        for h in [1, 3, 7]:
            r = client.post("/api/predict", json={"horizon_days": h})
            assert r.status_code == 200, f"Predict {h}d failed: {r.text}"
            pred = r.json()
            print(f" [PASS] POST /api/predict ({h}-day) -> Total Admissions: {pred['summary']['total_projected_admissions']}, Risk: {pred['summary']['overall_risk_level']}")

        # 6. Alerts
        r = client.get("/api/alerts")
        assert r.status_code == 200, f"Alerts failed: {r.text}"
        alerts_list = r.json()
        print(" [PASS] GET /api/alerts -> Total Alerts:", len(alerts_list))

        # Acknowledge first alert if available
        if alerts_list:
            first_id = alerts_list[0]["id"]
            r = client.post(f"/api/alerts/{first_id}/ack")
            assert r.status_code == 200, f"Alert ack failed: {r.text}"
            print(f" [PASS] POST /api/alerts/{first_id}/ack -> Acknowledged: {r.json()['alert']['acknowledged']}")

        # Simulate an alert
        r = client.post("/api/alerts/simulate", json={
            "department": "Emergency Room",
            "risk_level": "HIGH",
            "metric_name": "Occupancy Rate",
            "metric_value": 98.0,
            "threshold_value": 90.0,
            "title": "Drill Simulation: Critical Influx",
        })
        assert r.status_code == 200, f"Simulate alert failed: {r.text}"
        print(" [PASS] POST /api/alerts/simulate -> Triggered drill alert ID:", r.json()["alert"]["id"])

        # 7. Analytics & Retrain
        r = client.get("/api/analytics")
        assert r.status_code == 200, f"Analytics failed: {r.text}"
        analytics_data = r.json()
        print(" [PASS] GET /api/analytics -> ML Scorecard MAE:", analytics_data["ml_model_scorecard"]["mae"], "R²:", analytics_data["ml_model_scorecard"]["r2_score"])

        # 8. Recommendations
        r = client.post("/api/recommendations", json={"horizon_days": 1})
        assert r.status_code == 200, f"Recommendations failed: {r.text}"
        rec_data = r.json()
        print(" [PASS] POST /api/recommendations -> Engine:", rec_data["ai_engine"], "| Recommendations generated:", rec_data["action_items_count"])

        # 9. Reports Export
        r = client.get("/api/reports/export")
        assert r.status_code == 200, f"Report export failed: {r.text}"
        print(" [PASS] GET /api/reports/export -> Exported report payload size:", len(r.content), "bytes")

        # 10. FHIR
        r = client.get("/api/fhir/metadata")
        assert r.status_code == 200
        print(" [PASS] GET /api/fhir/metadata -> FHIR Version:", r.json()["fhirVersion"])

        r = client.get("/api/fhir/Bundle/encounters")
        assert r.status_code == 200
        print(" [PASS] GET /api/fhir/Bundle/encounters -> Bundle Total:", r.json()["total"])

        # 11. Organizer Hook
        r = client.get("/api/organizer/status")
        assert r.status_code == 200
        print(" [PASS] GET /api/organizer/status -> Mode:", r.json()["mode"])

        r = client.post("/api/organizer/test")
        assert r.status_code == 200
        print(" [PASS] POST /api/organizer/test -> Status:", r.json()["status"])

        r = client.post("/api/organizer/sync")
        assert r.status_code == 200
        print(" [PASS] POST /api/organizer/sync -> Success:", r.json()["success"])

    print("\n" + "=" * 50)
    print("ALL 16 BACKEND ENDPOINTS PASSED WITH 100% SUCCESS!")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    run_all_tests()
