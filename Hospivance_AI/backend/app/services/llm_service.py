"""LLM and Clinical Operations Recommendation Service for Hospivance AI.

Integrates Google Gemini API and OpenAI API with an intelligent,
domain-rich hospital operations rule-based recommendation fallback engine.
"""

import json
import logging
import requests
from typing import Dict, Any, List
from app.config import (
    LLM_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

logger = logging.getLogger("hospivance.llm")


def generate_rule_based_recommendations(forecast_data: Dict[str, Any]) -> Dict[str, Any]:
    """Domain-expert rule-based clinical operations recommendation generator."""
    summary = forecast_data.get("summary", {})
    dept_forecasts = forecast_data.get("department_forecasts", [])
    peak_occ = summary.get("peak_occupancy_rate", 85.0)
    high_risk_depts = summary.get("high_risk_departments", [])

    recommendations: List[Dict[str, Any]] = []

    # ICU Analysis
    icu_dept = next((d for d in dept_forecasts if "ICU" in d["department"]), None)
    if icu_dept and icu_dept.get("projected_occupancy_rate", 0) >= 90.0:
        recommendations.append({
            "id": "REC-ICU-01",
            "category": "Bed Management & Step-down",
            "priority": "HIGH",
            "department": "Intensive Care Unit (ICU)",
            "title": "Initiate Rapid ICU Step-Down Review",
            "action": "Audit current ICU census for at least 3-4 medically stable patients qualifying for Step-Down or Telemetry General Ward transfer.",
            "rationale": f"ICU projected at {icu_dept['projected_occupancy_rate']}% occupancy ({icu_dept['available_beds']} beds left). Transferring stable patients creates critical buffer.",
            "expected_impact": "Recovers 2-3 critical beds within 6 hours without compromising clinical safety."
        })
        recommendations.append({
            "id": "REC-SURG-02",
            "category": "Elective Surgical Buffering",
            "priority": "HIGH",
            "department": "Surgery",
            "title": "Hold Non-Emergent Post-Op ICU Surgeries",
            "action": "Coordinate with Chief of Surgery to reschedule 2 elective major vascular/spinal cases requiring guaranteed post-op ICU beds.",
            "rationale": "Prevents emergency ICU boarding in PACU and avoids surgical cancellations while patient is prepped.",
            "expected_impact": "Saves 2 guaranteed ICU beds for unpredicted incoming emergency arrivals."
        })

    # Emergency Room Analysis
    er_dept = next((d for d in dept_forecasts if "Emergency" in d["department"]), None)
    if er_dept and (er_dept.get("projected_occupancy_rate", 0) >= 85.0 or "Emergency Room" in high_risk_depts):
        recommendations.append({
            "id": "REC-ER-01",
            "category": "Staffing & Nurse Float Pool",
            "priority": "HIGH",
            "department": "Emergency Room",
            "title": "Deploy Float Pool Nurses to Fast-Track & Triage",
            "action": "Reassign 2 float pool RNs and 1 Emergency Medicine Advanced Practice Provider to Triage and Rapid Assessment Pod.",
            "rationale": f"Projected ER admissions ({er_dept['predicted_admissions']} patients) will strain intake triage, risking ambulance diversion.",
            "expected_impact": "Reduces door-to-provider time by an estimated 25-35% and prevents offload delays."
        })

    # General Ward & Discharge Logistics
    gw_dept = next((d for d in dept_forecasts if "General" in d["department"]), None)
    if gw_dept:
        recommendations.append({
            "id": "REC-GW-01",
            "category": "Discharge Lounge & Flow Logistics",
            "priority": "MEDIUM",
            "department": "General Ward",
            "title": "Activate Morning Discharge Lounge Acceleration",
            "action": "Ensure all attending physicians prioritize morning discharge orders by 10:00 AM, routing cleared patients to the Transit Lounge.",
            "rationale": "Afternoon bed crunches are driven by bed turnover lag. Clearing beds by 11:00 AM matches incoming afternoon admissions.",
            "expected_impact": "Accelerates bed availability by 2.5 hours on average, relieving ER boarding."
        })

    # Pediatrics & Seasonal Surge
    peds_dept = next((d for d in dept_forecasts if "Pediatrics" in d["department"]), None)
    if peds_dept and peds_dept.get("projected_occupancy_rate", 0) >= 80.0:
        recommendations.append({
            "id": "REC-PED-01",
            "category": "Respiratory Equipment & Protocols",
            "priority": "MEDIUM",
            "department": "Pediatrics",
            "title": "Pre-stage Pediatric High-Flow Cannulas and Inhalers",
            "action": "Request Central Supply to stage 10 pediatric respiratory kits and verify RT on-call staffing.",
            "rationale": "Seasonal pediatric respiratory conditions peak in the evening hours.",
            "expected_impact": "Eliminates treatment delay for acute broncho-spasm patients upon admission."
        })

    # Overall Hospital Briefing
    risk_summary = summary.get("overall_risk_level", "MODERATE")
    briefing = (
        f"### Hospital Operations Executive Briefing\n\n"
        f"**System Status: {risk_summary} OVERCROWDING RISK**\n\n"
        f"The AI forecasting engine predicts a peak system occupancy of **{peak_occ}%** over the horizon, "
        f"with **{summary.get('total_projected_admissions', 0)} total projected admissions**. "
        f"Primary operational bottlenecks are identified in: **{', '.join(high_risk_depts) if high_risk_depts else 'No critical bottlenecks'}**.\n\n"
        f"**Key Operational Drivers:**\n"
        f"- Influx volume is concentrated during afternoon intake hours.\n"
        f"- Bed kinetics indicate discharge delays are currently the primary bottleneck multiplier.\n"
        f"- Immediate proactive intervention in patient placement and discharge lounge routing is recommended to maintain surge readiness."
    )

    return {
        "source": "clinical-rules-fallback",
        "model": "Hospivance Operations Heuristic Engine v2.4",
        "executive_briefing": briefing,
        "recommendations": recommendations,
        "action_items_count": len(recommendations),
    }


def call_gemini_api(prompt: str, forecast_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calls Google Gemini API using REST endpoint."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    "You are the Hospivance AI Clinical Operations Intelligence Director. "
                    "Analyze the provided hospital admission forecast and provide an executive operational briefing "
                    "and a structured JSON array of 3-5 prioritized recommendations covering Staffing, Bed Placement, "
                    "Surgical Scheduling, and Triage Routing. Format response as JSON with keys 'executive_briefing' and 'recommendations'.\n\n"
                    f"Forecast Data:\n{json.dumps(forecast_data, indent=2)}"
                )
            }]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1024,
            "responseMimeType": "application/json"
        }
    }
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    parsed = json.loads(text)
    return {
        "source": "gemini-api",
        "model": GEMINI_MODEL,
        "executive_briefing": parsed.get("executive_briefing", ""),
        "recommendations": parsed.get("recommendations", []),
        "action_items_count": len(parsed.get("recommendations", [])),
    }


def call_openai_api(prompt: str, forecast_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calls OpenAI API."""
    import urllib.request
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are Hospivance AI Clinical Operations Assistant. Output valid JSON with 'executive_briefing' and 'recommendations'."
            },
            {
                "role": "user",
                "content": f"Forecast Data:\n{json.dumps(forecast_data, indent=2)}"
            }
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
        res = json.loads(response.read().decode("utf-8"))
        content = json.loads(res["choices"][0]["message"]["content"])
        return {
            "source": "openai-api",
            "model": OPENAI_MODEL,
            "executive_briefing": content.get("executive_briefing", ""),
            "recommendations": content.get("recommendations", []),
            "action_items_count": len(content.get("recommendations", [])),
        }


def get_recommendations(forecast_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generates recommendations with automatic LLM fallback."""
    # Check Gemini API
    if GEMINI_API_KEY and LLM_PROVIDER in ("gemini", "all"):
        try:
            return call_gemini_api("Analyze forecast", forecast_data)
        except Exception as e:
            logger.warning("Gemini API call failed (%s). Falling back to rule-based engine.", e)

    # Check OpenAI API
    if OPENAI_API_KEY and LLM_PROVIDER in ("openai", "all"):
        try:
            return call_openai_api("Analyze forecast", forecast_data)
        except Exception as e:
            logger.warning("OpenAI API call failed (%s). Falling back to rule-based engine.", e)

    # Default robust rule-based fallback
    return generate_rule_based_recommendations(forecast_data)
