"""Router uwierzytelniania `/api/auth` (ETAP 11.2).

Endpoints:
- POST /api/auth/login    — email+hasło → para JWT (access/refresh)
- POST /api/auth/refresh  — refresh token → nowa para JWT
- GET  /api/auth/me       — profil zalogowanego (z access tokenu)

W produkcji (Frankfurt DC) login można podmienić na przekierowanie do OIDC;
kontrakt odpowiedzi (TokenPair) pozostaje.
"""
from __future__ import annotations

import re

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

from adam_modules.auth import (
    Role,
    create_token_pair,
    decode_token,
    get_user_store,
)
from adam_modules.auth.security import TokenError
from ..deps import get_current_user, CurrentUser

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ---- schematy ----

class LoginIn(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)

    @field_validator("email")
    @classmethod
    def _check_email(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("Nieprawidłowy adres e-mail.")
        return v.lower()


class RefreshIn(BaseModel):
    refresh_token: str = Field(min_length=1)


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    role: str
    senior_ids: list[str] = []


class MeOut(BaseModel):
    email: str
    role: str
    senior_ids: list[str] = []


# ---- endpointy ----

@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn):
    store = get_user_store()
    user = store.authenticate(body.email, body.password)
    if not user:
        # 401 przez TokenError→handler; spójny komunikat (brak user enumeration).
        raise TokenError("Nieprawidłowy e-mail lub hasło.")
    pair = create_token_pair(
        sub=user.email, role=user.role, senior_ids=user.senior_ids
    )
    return TokenOut(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        expires_in=pair.expires_in,
        role=user.role.value,
        senior_ids=user.senior_ids,
    )


@router.post("/refresh", response_model=TokenOut)
async def refresh(body: RefreshIn):
    payload = decode_token(body.refresh_token, expected_type="refresh")
    role = Role(payload["role"])
    sids = list(payload.get("senior_ids") or [])
    pair = create_token_pair(sub=payload["sub"], role=role, senior_ids=sids)
    return TokenOut(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        expires_in=pair.expires_in,
        role=role.value,
        senior_ids=sids,
    )


@router.get("/me", response_model=MeOut)
async def me(user: CurrentUser = Depends(get_current_user)):
    return MeOut(email=user.email, role=user.role.value, senior_ids=user.senior_ids)
