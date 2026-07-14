"""Pakiet uwierzytelniania Adama (ETAP 11).

Wystawia:
- security: hashowanie haseł (PBKDF2-HMAC-SHA256) + JWT HS256 (zero zewn. zależności),
- store:    prosty magazyn użytkowników (dev z ENV; prod = podmiana na DB/OIDC),
- schemas:  modele Pydantic dla /api/auth.
"""
from __future__ import annotations

from .security import (
    Role,
    TokenPair,
    create_token_pair,
    decode_token,
    hash_password,
    verify_password,
)
from .store import User, UserStore, get_user_store

__all__ = [
    "Role",
    "TokenPair",
    "create_token_pair",
    "decode_token",
    "hash_password",
    "verify_password",
    "User",
    "UserStore",
    "get_user_store",
]
