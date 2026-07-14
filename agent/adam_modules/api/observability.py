"""Obserwowalność i hardening warstwy API (ETAP 14).

Zawiera:
- MetricsRegistry — lekki licznik/histogram w stylu Prometheus (bez zależności),
- RequestContextMiddleware — request-id + czas odpowiedzi + strukturalny log,
- RateLimitMiddleware — token-bucket per-klient (in-memory; prod: Redis),
- render_metrics() — ekspozycja tekstowa dla `/metrics`.

Świadomie stdlib-only (logging/time/uuid), by nie dokładać zależności.
Produkcyjnie (Frankfurt DC) rate-limit i metryki przenosi się do Redis/
Prometheus; interfejs pozostaje ten sam.
"""
from __future__ import annotations

import logging
import os
import time
import uuid
from collections import defaultdict
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("adam.api")
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(_h)
    logger.setLevel(os.getenv("ADAM_LOG_LEVEL", "INFO").upper())


# ------------------------------------------------------------------ metryki

class MetricsRegistry:
    """Minimalny rejestr metryk (liczniki + histogram czasu odpowiedzi)."""

    def __init__(self):
        self._lock = Lock()
        self._counters: dict[tuple[str, int], int] = defaultdict(int)
        self._latency_sum_ms: float = 0.0
        self._latency_count: int = 0
        self._rate_limited: int = 0

    def observe_request(self, *, method: str, status_code: int, duration_ms: float):
        with self._lock:
            self._counters[(method, status_code)] += 1
            self._latency_sum_ms += duration_ms
            self._latency_count += 1

    def inc_rate_limited(self):
        with self._lock:
            self._rate_limited += 1

    def snapshot(self) -> dict:
        with self._lock:
            avg = (self._latency_sum_ms / self._latency_count) if self._latency_count else 0.0
            return {
                "requests_total": dict(self._counters),
                "request_count": self._latency_count,
                "latency_avg_ms": round(avg, 3),
                "rate_limited_total": self._rate_limited,
            }

    def reset(self):  # pragma: no cover - dla testów
        with self._lock:
            self._counters.clear()
            self._latency_sum_ms = 0.0
            self._latency_count = 0
            self._rate_limited = 0


metrics = MetricsRegistry()


def render_metrics() -> str:
    """Ekspozycja w formacie tekstowym zbliżonym do Prometheus."""
    snap = metrics.snapshot()
    lines = [
        "# HELP adam_requests_total Liczba żądań wg metody i kodu.",
        "# TYPE adam_requests_total counter",
    ]
    for (method, code), n in sorted(snap["requests_total"].items()):
        lines.append(f'adam_requests_total{{method="{method}",code="{code}"}} {n}')
    lines += [
        "# HELP adam_request_latency_avg_ms Średni czas odpowiedzi (ms).",
        "# TYPE adam_request_latency_avg_ms gauge",
        f"adam_request_latency_avg_ms {snap['latency_avg_ms']}",
        "# HELP adam_rate_limited_total Liczba żądań odrzuconych przez rate-limit.",
        "# TYPE adam_rate_limited_total counter",
        f"adam_rate_limited_total {snap['rate_limited_total']}",
    ]
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ request context

class RequestContextMiddleware(BaseHTTPMiddleware):
    """Nadaje request-id, mierzy czas, loguje strukturalnie, zbiera metryki."""

    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:16]
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            metrics.observe_request(method=request.method, status_code=500, duration_ms=duration_ms)
            logger.exception(
                "request_error req_id=%s method=%s path=%s dur_ms=%.1f",
                req_id, request.method, request.url.path, duration_ms,
            )
            raise
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Response-Time-ms"] = f"{duration_ms:.1f}"
        metrics.observe_request(
            method=request.method, status_code=response.status_code, duration_ms=duration_ms
        )
        logger.info(
            "request req_id=%s method=%s path=%s status=%s dur_ms=%.1f",
            req_id, request.method, request.url.path, response.status_code, duration_ms,
        )
        return response


# ------------------------------------------------------------------ rate limit

class _TokenBucket:
    __slots__ = ("tokens", "updated")

    def __init__(self, capacity: float):
        self.tokens = capacity
        self.updated = time.monotonic()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token-bucket per-klient (IP+ścieżka-prefiks). In-memory (prod: Redis).

    Konfiguracja ENV:
    - ADAM_RATE_LIMIT   — pojemność (żądań), domyślnie 120,
    - ADAM_RATE_WINDOW  — okno w sekundach do pełnego uzupełnienia, domyślnie 60,
    - ADAM_RATE_ENABLED — '0' wyłącza (domyślnie włączony).
    Ścieżki wyłączone: /health, /metrics.
    """

    def __init__(self, app, capacity: float | None = None, window_s: float | None = None):
        super().__init__(app)
        self.capacity = float(capacity or os.getenv("ADAM_RATE_LIMIT", "120"))
        self.window_s = float(window_s or os.getenv("ADAM_RATE_WINDOW", "60"))
        self.enabled = os.getenv("ADAM_RATE_ENABLED", "1") != "0"
        self._buckets: dict[str, _TokenBucket] = {}
        self._lock = Lock()
        self._exempt = {"/health", "/metrics", "/"}

    def _key(self, request: Request) -> str:
        client = request.client.host if request.client else "unknown"
        return f"{client}"

    def _allow(self, key: str) -> bool:
        rate = self.capacity / self.window_s  # tokeny/s
        now = time.monotonic()
        with self._lock:
            b = self._buckets.get(key)
            if b is None:
                b = _TokenBucket(self.capacity)
                self._buckets[key] = b
            elapsed = now - b.updated
            b.tokens = min(self.capacity, b.tokens + elapsed * rate)
            b.updated = now
            if b.tokens >= 1.0:
                b.tokens -= 1.0
                return True
            return False

    async def dispatch(self, request: Request, call_next):
        if not self.enabled or request.url.path in self._exempt:
            return await call_next(request)
        if not self._allow(self._key(request)):
            metrics.inc_rate_limited()
            logger.warning("rate_limited client=%s path=%s", self._key(request), request.url.path)
            return JSONResponse(
                status_code=429,
                content={"detail": "Przekroczono limit żądań. Spróbuj później."},
                headers={"Retry-After": str(int(self.window_s))},
            )
        return await call_next(request)
