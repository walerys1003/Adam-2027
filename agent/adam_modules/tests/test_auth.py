"""Testy uwierzytelniania i RBAC (ETAP 11) — JWT, login/refresh/me, role.

Pokrywa:
- security: hash/verify hasła, create/decode JWT, exp, typ tokenu, hierarchia ról,
- router /api/auth: login (200/401/422), refresh, me (200/401),
- deps: get_current_user / require_role (403).
"""
from __future__ import annotations

import time

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from adam_modules.common import db as db_mod
from adam_modules.api import create_app
from adam_modules.auth import (
    Role, create_token_pair, decode_token, hash_password, verify_password,
)
from adam_modules.auth.security import TokenError
from adam_modules.api.deps import require_role, get_current_user, CurrentUser


@pytest.fixture()
def client():
    db_mod.init_engine("sqlite:///:memory:")
    app = create_app(init_db=True)
    with TestClient(app) as c:
        yield c


# ---------- security: hasła ----------

def test_password_hash_verify():
    h = hash_password("tajne123")
    assert h.startswith("pbkdf2_sha256$")
    assert verify_password("tajne123", h)
    assert not verify_password("zle", h)


def test_password_empty_rejected():
    with pytest.raises(ValueError):
        hash_password("")


def test_verify_bad_encoding_returns_false():
    assert verify_password("x", "nonsense") is False


# ---------- security: JWT ----------

def test_token_roundtrip():
    pair = create_token_pair(sub="a@b.pl", role=Role.ADMIN, senior_ids=["SR-1"])
    p = decode_token(pair.access_token, expected_type="access")
    assert p["sub"] == "a@b.pl"
    assert p["role"] == "admin"
    assert p["senior_ids"] == ["SR-1"]
    assert pair.expires_in > 0


def test_token_expired():
    old = int(time.time()) - 10_000
    pair = create_token_pair(sub="a@b.pl", role=Role.FAMILY, now=old)
    with pytest.raises(TokenError):
        decode_token(pair.access_token, expected_type="access")


def test_token_wrong_type():
    pair = create_token_pair(sub="a@b.pl", role=Role.FAMILY)
    # access token nie przejdzie jako refresh
    with pytest.raises(TokenError):
        decode_token(pair.access_token, expected_type="refresh")


def test_token_tampered_signature():
    pair = create_token_pair(sub="a@b.pl", role=Role.FAMILY)
    bad = pair.access_token[:-4] + "AAAA"
    with pytest.raises(TokenError):
        decode_token(bad)


# ---------- role hierarchy ----------

def test_role_hierarchy():
    assert Role.ADMIN.satisfies(Role.COORDINATOR)
    assert Role.COORDINATOR.satisfies(Role.FAMILY)
    assert not Role.FAMILY.satisfies(Role.ADMIN)


def test_current_user_senior_access():
    admin = CurrentUser(email="a", role=Role.ADMIN)
    fam = CurrentUser(email="f", role=Role.FAMILY, senior_ids=["SR-1"])
    assert admin.can_access_senior("SR-999")
    assert fam.can_access_senior("SR-1")
    assert not fam.can_access_senior("SR-2")


# ---------- router /api/auth ----------

def test_login_ok(client):
    r = client.post("/api/auth/login", json={
        "email": "admin@silvertech.pl", "password": "admin123"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["role"] == "admin"
    assert body["access_token"] and body["refresh_token"]


def test_login_bad_password(client):
    r = client.post("/api/auth/login", json={
        "email": "admin@silvertech.pl", "password": "zle"})
    assert r.status_code == 401


def test_login_bad_email_422(client):
    r = client.post("/api/auth/login", json={"email": "niepoprawny", "password": "x"})
    assert r.status_code == 422


def test_me_ok(client):
    tok = client.post("/api/auth/login", json={
        "email": "opiekun@silvertech.pl", "password": "opiekun123"}).json()["access_token"]
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200
    assert r.json()["role"] == "coordinator"


def test_me_no_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_malformed_header(client):
    r = client.get("/api/auth/me", headers={"Authorization": "Token abc"})
    assert r.status_code == 401


def test_refresh_ok(client):
    ref = client.post("/api/auth/login", json={
        "email": "rodzina@silvertech.pl", "password": "rodzina123"}).json()["refresh_token"]
    r = client.post("/api/auth/refresh", json={"refresh_token": ref})
    assert r.status_code == 200
    assert r.json()["role"] == "family"
    assert r.json()["senior_ids"] == ["SR-A4772B9E"]


def test_refresh_with_access_token_rejected(client):
    acc = client.post("/api/auth/login", json={
        "email": "admin@silvertech.pl", "password": "admin123"}).json()["access_token"]
    r = client.post("/api/auth/refresh", json={"refresh_token": acc})
    assert r.status_code == 401


# ---------- require_role (na doklejonym routerze testowym) ----------

def _admin_app():
    db_mod.init_engine("sqlite:///:memory:")
    app = create_app(init_db=True)

    @app.get("/api/_test/admin-only")
    def admin_only(user: CurrentUser = Depends(require_role(Role.ADMIN))):
        return {"email": user.email}

    return app


def test_require_role_forbidden_for_lower():
    with TestClient(_admin_app()) as c:
        tok = c.post("/api/auth/login", json={
            "email": "rodzina@silvertech.pl", "password": "rodzina123"}).json()["access_token"]
        r = c.get("/api/_test/admin-only", headers={"Authorization": f"Bearer {tok}"})
        assert r.status_code == 403


def test_require_role_ok_for_admin():
    with TestClient(_admin_app()) as c:
        tok = c.post("/api/auth/login", json={
            "email": "admin@silvertech.pl", "password": "admin123"}).json()["access_token"]
        r = c.get("/api/_test/admin-only", headers={"Authorization": f"Bearer {tok}"})
        assert r.status_code == 200
        assert r.json()["email"] == "admin@silvertech.pl"
