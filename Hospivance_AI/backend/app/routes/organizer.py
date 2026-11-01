"""Organizer Integration Routes for Hospivance AI."""

from fastapi import APIRouter
from app.services.organizer_sync import (
    get_organizer_status,
    test_organizer_connection,
    sync_organizer_data,
)

router = APIRouter(prefix="/api/organizer", tags=["Organizer"])


@router.get("/status")
def organizer_status():
    """Checks hackathon organizer hook configuration and connection parameters."""
    return get_organizer_status()


@router.post("/test")
def test_organizer():
    """Pings external organizer API base URL."""
    return test_organizer_connection()


@router.post("/sync")
def sync_organizer():
    """Syncs external feeds or confirms local synthetic baseline."""
    return sync_organizer_data()
