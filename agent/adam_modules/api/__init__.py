"""Warstwa API (FastAPI) backendu Adama — ETAP 9."""
from .app import create_app, app, API_VERSION

__all__ = ["create_app", "app", "API_VERSION"]
