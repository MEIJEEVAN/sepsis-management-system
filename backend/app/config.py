"""Application configuration read from environment variables."""

import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_URL = "postgresql+psycopg://sepsis_user:sepsis_pass@localhost:5432/sepsis_db"


class Config:
    """Base configuration."""

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", _DEFAULT_URL)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "connect_args": {"application_name": "sepsis_flask"},
    }
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-secret-key-change-me-0123456789")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "60")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    # Plain libpq DSN for the raw LISTEN connection (no SQLAlchemy driver suffix).
    SSE_DSN = SQLALCHEMY_DATABASE_URI.replace("+psycopg", "")
