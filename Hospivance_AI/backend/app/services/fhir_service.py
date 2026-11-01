"""HL7 FHIR R4 Service for Hospivance AI."""

from datetime import datetime
from typing import Dict, Any
from app.database.session import Session
from app.database.models import Encounter


def format_dt(dt: Any) -> str:
    if not dt:
        return ""
    return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)


def get_fhir_capability_statement() -> Dict[str, Any]:
    """Returns HL7 FHIR R4 CapabilityStatement for Hospivance AI."""
    return {
        "resourceType": "CapabilityStatement",
        "id": "hospivance-fhir-capability",
        "status": "active",
        "date": datetime.utcnow().isoformat(),
        "publisher": "Hospivance AI Health Systems",
        "kind": "instance",
        "software": {
            "name": "Hospivance AI Bottleneck Prediction API",
            "version": "1.0.0"
        },
        "fhirVersion": "4.0.1",
        "format": ["json"],
        "rest": [{
            "mode": "server",
            "security": {
                "cors": True,
                "description": "Synthetic demonstration dataset - no clinical PHI stored."
            },
            "resource": [{
                "type": "Encounter",
                "interaction": [{"code": "read"}, {"code": "search-type"}],
                "searchParam": [
                    {"name": "status", "type": "token"},
                    {"name": "department", "type": "string"}
                ]
            }]
        }]
    }


def get_fhir_encounter_bundle(db: Session, limit: int = 50) -> Dict[str, Any]:
    """Generates an HL7 FHIR R4 Bundle containing synthetic Encounter resources."""
    encounters = db.query(Encounter).order_by(Encounter.admit_date.desc()).limit(limit).all()
    entries = []
    for enc in encounters:
        entries.append({
            "fullUrl": f"urn:uuid:{enc.encounter_id}",
            "resource": {
                "resourceType": "Encounter",
                "id": enc.encounter_id,
                "status": enc.status,
                "class": {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "EMER" if "Emergency" in enc.department else "IMP",
                    "display": "Emergency" if "Emergency" in enc.department else "Inpatient encounter"
                },
                "subject": {
                    "reference": f"Patient/{enc.patient_pseudonym}",
                    "display": f"Synthetic Patient {enc.patient_pseudonym}"
                },
                "period": {
                    "start": format_dt(enc.admit_date),
                    "end": format_dt(enc.discharge_date) if enc.discharge_date else None
                },
                "reasonCode": [{
                    "text": enc.reason_for_visit
                }],
                "serviceProvider": {
                    "display": f"Hospivance AI - {enc.department}"
                },
                "priority": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActPriority",
                        "code": "EM" if getattr(enc, "acuity_level", 3) <= 2 else "R",
                        "display": f"ESI Level {getattr(enc, 'acuity_level', 3)}"
                    }]
                }
            }
        })

    return {
        "resourceType": "Bundle",
        "id": "hospivance-encounter-bundle",
        "type": "searchset",
        "total": len(entries),
        "timestamp": datetime.utcnow().isoformat(),
        "meta": {
            "synthetic_notice": "ALL ENCOUNTER DATA IS GENERATED FOR DEMO/RESEARCH PURPOSES ONLY"
        },
        "entry": entries
    }
