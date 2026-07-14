"""Zależności FastAPI (dependency injection) dla API Adama (ETAP 9.1).

Dostarcza sesję SQLAlchemy per-request z transakcyjnym commit/rollback,
oraz prosty guard nagłówka autoryzacyjnego (placeholder pod prawdziwe OIDC/JWT
w produkcji Frankfurt DC).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Iterator

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from adam_modules.common import db as db_mod
from adam_modules.auth import Role, decode_token
from adam_modules.auth.security import TokenError


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


# ------------------------------------------------------------------ RBAC (ETAP 11.3)

@dataclass
class CurrentUser:
    """Tożsamość wyekstrahowana z access-tokenu JWT."""
    email: str
    role: Role
    senior_ids: list[str] = field(default_factory=list)

    def can_access_senior(self, external_id: str) -> bool:
        """ADMIN/COORDINATOR — wszyscy; FAMILY — tylko przypisani seniorzy."""
        if self.role.satisfies(Role.COORDINATOR):
            return True
        return external_id in self.senior_ids


def _bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Brak nagłówka Authorization: Bearer <token>.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authorization.split(" ", 1)[1].strip()


def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    """Weryfikuje access-token JWT i zwraca tożsamość (401 przy błędzie)."""
    token = _bearer_token(authorization)
    try:
        payload = decode_token(token, expected_type="access")
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return CurrentUser(
        email=payload["sub"],
        role=Role(payload["role"]),
        senior_ids=list(payload.get("senior_ids") or []),
    )


def require_role(required: Role):
    """Fabryka zależności: wymaga roli >= `required` (hierarchia RBAC)."""

    def _dep(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not user.role.satisfies(required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Wymagana rola co najmniej '{required.value}'.",
            )
        return user

    return _dep
