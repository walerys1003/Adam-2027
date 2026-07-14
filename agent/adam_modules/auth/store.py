"""Magazyn użytkowników (ETAP 11.2).

Dev/test: użytkownicy w pamięci, opcjonalnie zasilani z `ADAM_AUTH_USERS`
(format: `email:hasło:rola[:senior_id1|senior_id2],...`). Bez zmiennej —
wbudowany zestaw demonstracyjny (3 role).

Produkcyjnie (Frankfurt DC): podmiana na magazyn oparty o DB lub delegacja
do zewnętrznego IdP (OIDC). Interfejs `UserStore.authenticate/get` pozostaje.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from .security import Role, hash_password, verify_password


@dataclass
class User:
    email: str
    role: Role
    password_hash: str
    senior_ids: list[str] = field(default_factory=list)
    active: bool = True


class UserStore:
    """Prosty magazyn użytkowników w pamięci (dev/test)."""

    def __init__(self, users: list[User] | None = None):
        self._by_email: dict[str, User] = {}
        for u in users or []:
            self._by_email[u.email.lower()] = u

    # --- zarządzanie ---
    def add(self, *, email: str, password: str, role: Role | str,
            senior_ids: list[str] | None = None) -> User:
        role_v = role if isinstance(role, Role) else Role(str(role))
        user = User(
            email=email.lower(),
            role=role_v,
            password_hash=hash_password(password),
            senior_ids=senior_ids or [],
        )
        self._by_email[user.email] = user
        return user

    def get(self, email: str) -> User | None:
        return self._by_email.get(email.lower())

    # --- uwierzytelnianie ---
    def authenticate(self, email: str, password: str) -> User | None:
        user = self.get(email)
        if not user or not user.active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def __len__(self) -> int:  # pragma: no cover - pomocnicze
        return len(self._by_email)


# ------------------------------------------------------------------ fabryka dev

def _demo_store() -> UserStore:
    store = UserStore()
    store.add(email="admin@silvertech.pl", password="admin123", role=Role.ADMIN)
    store.add(email="opiekun@silvertech.pl", password="opiekun123", role=Role.COORDINATOR)
    store.add(email="rodzina@silvertech.pl", password="rodzina123", role=Role.FAMILY,
              senior_ids=["SR-A4772B9E"])
    return store


def _from_env(spec: str) -> UserStore:
    """Parsuje `ADAM_AUTH_USERS`: 'email:hasło:rola[:sid1|sid2],...'."""
    store = UserStore()
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split(":")
        if len(parts) < 3:
            raise ValueError(f"Zły wpis ADAM_AUTH_USERS: {chunk!r}")
        email, password, role = parts[0], parts[1], parts[2]
        sids = parts[3].split("|") if len(parts) >= 4 and parts[3] else []
        store.add(email=email, password=password, role=role, senior_ids=sids)
    return store


_store: UserStore | None = None


def get_user_store() -> UserStore:
    """Singleton magazynu użytkowników (dev). Zasilany ENV lub demo."""
    global _store
    if _store is None:
        spec = os.getenv("ADAM_AUTH_USERS")
        _store = _from_env(spec) if spec else _demo_store()
    return _store


def reset_user_store() -> None:  # pragma: no cover - dla testów
    global _store
    _store = None
