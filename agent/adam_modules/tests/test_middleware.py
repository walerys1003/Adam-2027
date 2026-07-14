"""Testy obserwowalności i hardeningu (ETAP 14) — request-id, metryki, rate-limit."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from adam_modules.common import db as db_mod
from adam_modules.api import create_app
from adam_modules.api import observability as obs


@pytest.fixture()
def client(monkeypatch):
    # rate-limit włączony domyślnie; testy per-test resetują metryki
    monkeypatch.setenv("ADAM_RATE_ENABLED", "1")
    obs.metrics.reset()
    db_mod.init_engine("sqlite:///:memory:")
    app = create_app(init_db=True)
    with TestClient(app) as c:
        yield c


def test_request_id_and_timing_headers(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.headers.get("X-Request-ID")
    assert r.headers.get("X-Response-Time-ms")


def test_request_id_propagated(client):
    r = client.get("/health", headers={"X-Request-ID": "moj-id-123"})
    assert r.headers["X-Request-ID"] == "moj-id-123"


def test_metrics_endpoint_format(client):
    client.get("/health")
    client.get("/api/seniors")
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "adam_requests_total" in r.text
    assert "adam_request_latency_avg_ms" in r.text
    assert "adam_rate_limited_total" in r.text


def test_metrics_counts_requests(client):
    obs.metrics.reset()
    for _ in range(3):
        client.get("/api/seniors")
    snap = obs.metrics.snapshot()
    assert snap["request_count"] >= 3


def test_health_and_metrics_exempt_from_rate_limit(monkeypatch):
    monkeypatch.setenv("ADAM_RATE_ENABLED", "1")
    monkeypatch.setenv("ADAM_RATE_LIMIT", "3")
    monkeypatch.setenv("ADAM_RATE_WINDOW", "60")
    obs.metrics.reset()
    db_mod.init_engine("sqlite:///:memory:")
    with TestClient(create_app(init_db=True)) as c:
        # /health wyłączony z limitu — 10 żądań nadal 200
        codes = [c.get("/health").status_code for _ in range(10)]
        assert codes.count(200) == 10


def test_rate_limit_triggers_429(monkeypatch):
    monkeypatch.setenv("ADAM_RATE_ENABLED", "1")
    monkeypatch.setenv("ADAM_RATE_LIMIT", "4")
    monkeypatch.setenv("ADAM_RATE_WINDOW", "60")
    obs.metrics.reset()
    db_mod.init_engine("sqlite:///:memory:")
    with TestClient(create_app(init_db=True)) as c:
        codes = [c.get("/api/seniors").status_code for _ in range(7)]
        assert 429 in codes
        assert codes.count(200) == 4
        # nagłówek Retry-After na 429
        r = c.get("/api/seniors")
        assert r.status_code == 429
        assert r.headers.get("Retry-After")


def test_rate_limit_disabled(monkeypatch):
    monkeypatch.setenv("ADAM_RATE_ENABLED", "0")
    obs.metrics.reset()
    db_mod.init_engine("sqlite:///:memory:")
    with TestClient(create_app(init_db=True)) as c:
        codes = [c.get("/api/seniors").status_code for _ in range(20)]
        assert codes.count(200) == 20
