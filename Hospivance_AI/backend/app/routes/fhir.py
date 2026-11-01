"""HL7 FHIR R4 Routes for Hospivance AI."""

from fastapi import APIRouter, Depends, Query
from app.database.session import Session
from app.database.session import get_db
from app.services.fhir_service import get_fhir_capability_statement, get_fhir_encounter_bundle

router = APIRouter(prefix="/api/fhir", tags=["FHIR"])


@router.get("/metadata")
def fhir_capability():
    """Returns HL7 FHIR R4 CapabilityStatement."""
    return get_fhir_capability_statement()


@router.get("/Bundle/encounters")
def fhir_encounters(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Returns HL7 FHIR R4 Encounter bundle."""
    return get_fhir_encounter_bundle(db, limit=limit)
