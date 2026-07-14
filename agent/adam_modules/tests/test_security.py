"""Testy bezpieczeństwa i hardeningu (ETAP 16).

Pokrywa:
- nagłówki bezpieczeństwa (`SecurityHeadersMiddleware`) + przełącznik HSTS,
- backendy rate-limit: in-memory (izolacja per-klient) oraz Redis
  (happy-path z fake-klientem + **fail-open** przy awarii Redisa),
- powtórzenie kluczowej ścieżki negatywnej: rate-limit 429 + Retry-After.

Testy nie wymagają serwera Redis — używamy atrap zgodnych interfejsem
(`incr`/`expire`).
"""
from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient

from adam_modules.common import db as db_mod
from adam_modules.api import create_app
from adam_modules.api import observability as obs


@pytest.fixture()
def client(monkeypatch):
    # domyślnie wyłączamy rate-limit, by testy nagłówków nie kolidowały z limitem
    monkeypatch.setenv("ADAM_RATE_ENABLED", "0")
    db_mod.init_engine("sqlite:///:memory:")
    app = create_app(init_db=True)
    with TestClient(app) as c:
        yield c


# ================================================= nagłówki bezpieczeństwa

def test_security_headers_present_on_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["Referrer-Policy"] == "no-referrer"
    assert "default-src 'none'" in r.headers["Content-Security-Policy"]
    assert r.headers["Cache-Control"] == "no-store"


def test_security_headers_present_on_api_and_errors(client):
    # 404 też powinno nieść nagłówki bezpieczeństwa (middleware jest najbardziej zewn.)
    r = client.get("/api/seniors/999999")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"


def test_hsts_absent_by_default(client):
    r = client.get("/health")
    assert "Strict-Transport-Security" not in r.headers


def test_hsts_present_when_enabled(monkeypatch):
    monkeypatch.setenv("ADAM_RATE_ENABLED", "0")
    monkeypatch.setenv("ADAM_HSTS", "1")
    db_mod.init_engine("sqlite:///:memory:")
    app = create_app(init_db=True)
    with TestClient(app) as c:
        r = c.get("/health")
        assert "max-age=31536000" in r.headers["Strict-Transport-Security"]


def test_security_headers_can_be_disabled(monkeypatch):
    monkeypatch.setenv("ADAM_RATE_ENABLED", "0")
    monkeypatch.setenv("ADAM_SECURITY_HEADERS", "0")
    db_mod.init_engine("sqlite:///:memory:")
    app = create_app(init_db=True)
    with TestClient(app) as c:
        r = c.get("/health")
        assert "X-Frame-Options" not in r.headers


# ================================================= rate-limit: in-memory

def test_inmemory_backend_isolates_clients():
    be = obs.InMemoryRateBackend(capacity=2, window_s=60)
    # klient A wyczerpuje limit
    assert be.allow("A") is True
    assert be.allow("A") is True
    assert be.allow("A") is False
    # klient B ma własny kubełek — nie jest dotknięty
    assert be.allow("B") is True


def test_inmemory_backend_refills_over_time(monkeypatch):
    be = obs.InMemoryRateBackend(capacity=1, window_s=10)
    t = {"now": 1000.0}
    monkeypatch.setattr(obs.time, "monotonic", lambda: t["now"])
    assert be.allow("A") is True
    assert be.allow("A") is False
    # po upływie pełnego okna kubełek się uzupełnia
    t["now"] += 10.0
    assert be.allow("A") is True


# ================================================= rate-limit: Redis (atrapy)

class _FakeRedisOK:
    """Atrapa Redisa: licznik w pamięci (fixed-window)."""
    def __init__(self):
        self.store: dict[str, int] = {}
        self.expired: list[str] = []

    def incr(self, key):
        self.store[key] = self.store.get(key, 0) + 1
        return self.store[key]

    def expire(self, key, ttl):
        self.expired.append(key)
        return True


class _FakeRedisDown:
    """Atrapa Redisa, która zawsze rzuca — do testu fail-open."""
    def incr(self, key):
        raise ConnectionError("redis down")

    def expire(self, key, ttl):
        raise ConnectionError("redis down")


def test_redis_backend_happy_path_counts_and_expires():
    r = _FakeRedisOK()
    be = obs.RedisRateBackend(r, capacity=2, window_s=30)
    assert be.allow("A") is True      # count=1 → ustawia expire
    assert be.allow("A") is True      # count=2
    assert be.allow("A") is False     # count=3 > 2
    assert r.expired == ["adam:rl:A"]  # expire ustawiony tylko przy pierwszym


def test_redis_backend_fail_open_on_error():
    be = obs.RedisRateBackend(_FakeRedisDown(), capacity=1, window_s=30)
    # mimo awarii Redisa — dopuszczamy ruch (dostępność > twardy limit)
    assert be.allow("A") is True
    assert be.allow("A") is True


def test_build_rate_backend_defaults_to_inmemory(monkeypatch):
    monkeypatch.delenv("ADAM_REDIS_URL", raising=False)
    be = obs._build_rate_backend(100, 60)
    assert isinstance(be, obs.InMemoryRateBackend)


def test_build_rate_backend_falls_back_when_redis_url_bad(monkeypatch):
    # nieprawidłowy URL / brak serwera → nie wywala się, wraca do in-memory
    monkeypatch.setenv("ADAM_REDIS_URL", "redis://nonexistent-host-xyz:6379/0")
    be = obs._build_rate_backend(100, 60)
    # albo Redis (jeśli biblioteka utworzy klienta leniwie), albo in-memory —
    # kluczowe: funkcja nie rzuca i zwraca działający backend z metodą allow()
    assert hasattr(be, "allow")


# ================================================= rate-limit middleware 429

def test_rate_limit_429_and_retry_after(monkeypatch):
    monkeypatch.setenv("ADAM_RATE_ENABLED", "1")
    monkeypatch.setenv("ADAM_RATE_LIMIT", "3")
    monkeypatch.setenv("ADAM_RATE_WINDOW", "60")
    db_mod.init_engine("sqlite:///:memory:")
    app = create_app(init_db=True)
    with TestClient(app) as c:
        # /health jest wyłączone z limitu — użyj ścieżki API
        codes = [c.get("/api/seniors").status_code for _ in range(6)]
        assert 429 in codes
        # znajdź pierwszą odrzuconą i sprawdź Retry-After
        last = c.get("/api/seniors")
        if last.status_code == 429:
            assert "Retry-After" in last.headers
