"""Application Configuration for Hospivance AI."""

import os
from typing import List
from dotenv import load_dotenv

# Load .env from project root or backend/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

APP_NAME: str = os.getenv("APP_NAME", "Hospivance AI")
APP_ENV: str = os.getenv("APP_ENV", "development")

# Database URL with SQLite fallback
DEFAULT_SQLITE_URL = f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'hospivance.db'))}"
DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

CORS_ORIGINS: List[str] = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]

SIMULATE_REALTIME: bool = os.getenv("SIMULATE_REALTIME", "true").lower() in ("true", "1", "yes")

# LLM Providers (backend only)
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Hackathon Organizer Integration
ORGANIZER_API_BASE_URL: str = os.getenv("ORGANIZER_API_BASE_URL", "")
ORGANIZER_API_KEY: str = os.getenv("ORGANIZER_API_KEY", "")
ORGANIZER_API_AUTH_HEADER: str = os.getenv("ORGANIZER_API_AUTH_HEADER", "Authorization")
ORGANIZER_API_AUTH_SCHEME: str = os.getenv("ORGANIZER_API_AUTH_SCHEME", "Bearer")
ORGANIZER_PATH_ADMISSIONS: str = os.getenv("ORGANIZER_PATH_ADMISSIONS", "/admissions")
ORGANIZER_PATH_BEDS: str = os.getenv("ORGANIZER_PATH_BEDS", "/beds")
ORGANIZER_PATH_DEPARTMENTS: str = os.getenv("ORGANIZER_PATH_DEPARTMENTS", "/departments")
