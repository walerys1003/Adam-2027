"""Zależności FastAPI (dependency injection) dla API Adama (ETAP 9.1).

Dostarcza sesję SQLAlchemy per-request z transakcyjnym commit/rollback,
oraz prosty guard nagłówka autoryzacyjnego (placeholder pod prawdziwe OIDC/JWT
w produkcji Frankfurt DC).
"""
from __future__ import annotations

import os
from typing import Iterator

from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from adam_modules.common import db as db_mod


def get_db() -> Iterator[Session]:
    """Sesja per-request: commit przy sukcesie, rollback przy wyjątku."""
    session = db_mod.get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    """Prosty guard klucza API.

    W środowisku bez ustawionego ADAM_API_KEY (dev/test) — przepuszcza.
    W produkcji ADAM_API_KEY musi się zgadzać z nagłówkiem X-API-Key.
    """
    expected = os.getenv("ADAM_API_KEY")
    if not expected:
        return "dev"
    if x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy lub brakujący klucz API (X-API-Key).",
        )
    return x_api_key
