"""Prymitywy bezpieczeństwa: hasła (PBKDF2) + JWT HS256 (ETAP 11.1).

Świadomie BEZ zewnętrznych bibliotek (pyjwt/passlib) — implementacja oparta
o stdlib (`hmac`, `hashlib`, `base64`, `json`), by minimalizować zależności
i powierzchnię ataku. Algorytm tokenu: JWT HS256 (RFC 7519, podzbiór).

Produkcyjnie (Frankfurt DC) sekret pochodzi z `ADAM_JWT_SECRET` (obowiązkowo
ustawiony; w dev/test dopuszczamy fallback z ostrzeżeniem w logu).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any


# ------------------------------------------------------------------ role (RBAC)

class Role(str, Enum):
    """Role systemu Adam (RBAC). Kolejność = eskalacja uprawnień."""
    FAMILY = "family"          # członek rodziny — podgląd „swojego" seniora
    COORDINATOR = "coordinator"  # opiekun/koordynator — panel opiekuna
    ADMIN = "admin"            # administrator — panel admina, pełny dostęp

    @property
    def rank(self) -> int:
        order = {"family": 1, "coordinator": 2, "admin": 3}
        return order[self.value]

    def satisfies(self, required: "Role") -> bool:
        """Czy ta rola spełnia wymaganie (>= w hierarchii)."""
        return self.rank >= required.rank


# ------------------------------------------------------------------ hasła

_PBKDF2_ROUNDS = 200_000
_SALT_BYTES = 16


def hash_password(password: str, *, rounds: int = _PBKDF2_ROUNDS) -> str:
    """Zwraca `pbkdf2_sha256$rounds$salt_b64$hash_b64`."""
    if not password:
        raise ValueError("Hasło nie może być puste.")
    salt = secrets.token_bytes(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return "pbkdf2_sha256${}${}${}".format(
        rounds,
        base64.urlsafe_b64encode(salt).decode("ascii").rstrip("="),
        base64.urlsafe_b64encode(dk).decode("ascii").rstrip("="),
    )


def verify_password(password: str, encoded: str) -> bool:
    """Weryfikuje hasło względem zakodowanego skrótu (stały czas porównania)."""
    try:
        algo, rounds_s, salt_s, hash_s = encoded.split("$")
        if algo != "pbkdf2_sha256":
            return False
        rounds = int(rounds_s)
        salt = _b64decode(salt_s)
        expected = _b64decode(hash_s)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


# ------------------------------------------------------------------ JWT HS256

@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 0  # sekundy ważności access tokenu


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _secret() -> bytes:
    sec = os.getenv("ADAM_JWT_SECRET")
    if not sec:
        # Dev/test fallback — NIE do produkcji (deterministyczny per-proces).
        sec = "adam-dev-insecure-secret-change-me"
    return sec.encode("utf-8")


def _sign(signing_input: bytes) -> str:
    sig = hmac.new(_secret(), signing_input, hashlib.sha256).digest()
    return _b64url(sig)


def _encode(payload: dict[str, Any]) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    seg_h = _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    seg_p = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{seg_h}.{seg_p}".encode("ascii")
    return f"{seg_h}.{seg_p}.{_sign(signing_input)}"


# domyślne czasy życia (sekundy)
ACCESS_TTL = int(os.getenv("ADAM_JWT_ACCESS_TTL", "900"))      # 15 min
REFRESH_TTL = int(os.getenv("ADAM_JWT_REFRESH_TTL", "1209600"))  # 14 dni


def create_token_pair(
    *,
    sub: str,
    role: Role | str,
    senior_ids: list[str] | None = None,
    now: int | None = None,
) -> TokenPair:
    """Buduje parę access/refresh JWT dla użytkownika."""
    now = now or int(time.time())
    role_v = role.value if isinstance(role, Role) else str(role)
    base = {
        "sub": sub,
        "role": role_v,
        "senior_ids": senior_ids or [],
        "iat": now,
        "iss": "adam-api",
    }
    access = _encode({**base, "type": "access", "exp": now + ACCESS_TTL})
    refresh = _encode({**base, "type": "refresh", "exp": now + REFRESH_TTL})
    return TokenPair(access_token=access, refresh_token=refresh, expires_in=ACCESS_TTL)


class TokenError(ValueError):
    """Token nieprawidłowy, wygasły lub o złym typie."""


def decode_token(token: str, *, expected_type: str | None = None, now: int | None = None) -> dict[str, Any]:
    """Weryfikuje podpis + `exp` + (opcjonalnie) typ tokenu; zwraca payload.

    Rzuca `TokenError` (podklasa ValueError → handler API zamieni na 401/422).
    """
    now = now or int(time.time())
    try:
        seg_h, seg_p, seg_s = token.split(".")
    except ValueError:
        raise TokenError("Nieprawidłowy format tokenu.")
    signing_input = f"{seg_h}.{seg_p}".encode("ascii")
    if not hmac.compare_digest(_sign(signing_input), seg_s):
        raise TokenError("Nieprawidłowy podpis tokenu.")
    try:
        payload = json.loads(_b64decode(seg_p))
    except Exception:
        raise TokenError("Uszkodzony ładunek tokenu.")
    if int(payload.get("exp", 0)) < now:
        raise TokenError("Token wygasł.")
    if expected_type and payload.get("type") != expected_type:
        raise TokenError(f"Oczekiwano tokenu typu '{expected_type}'.")
    return payload
