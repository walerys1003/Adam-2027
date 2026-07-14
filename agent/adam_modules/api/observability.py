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


# ------------------------------------------------------------------ security headers

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Dokłada nagłówki bezpieczeństwa do każdej odpowiedzi (ETAP 16.1).

    Zabezpiecza panel/API przed clickjackingiem, MIME-sniffingiem i wyciekiem
    referrera. HSTS włączany tylko za TLS (produkcja) — kontrolowany ENV, by nie
    psuć dev po http.

    ENV:
    - ADAM_HSTS='1'          — dołącz Strict-Transport-Security (domyślnie wył.),
    - ADAM_SECURITY_HEADERS='0' — całkowicie wyłącz (domyślnie wł.).
    """

    def __init__(self, app):
        super().__init__(app)
        self.enabled = os.getenv("ADAM_SECURITY_HEADERS", "1") != "0"
        self.hsts = os.getenv("ADAM_HSTS", "0") == "1"

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        if not self.enabled:
            return response
        h = response.headers
        h.setdefault("X-Content-Type-Options", "nosniff")
        h.setdefault("X-Frame-Options", "DENY")
        h.setdefault("Referrer-Policy", "no-referrer")
        h.setdefault("X-XSS-Protection", "0")  # nowoczesne przeglądarki — polegamy na CSP
        h.setdefault("Cache-Control", "no-store")
        # API zwraca JSON/tekst — restrykcyjny CSP wystarcza (brak inline skryptów).
        h.setdefault(
            "Content-Security-Policy",
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
        )
        if self.hsts:
            h.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return response


# ------------------------------------------------------------------ rate limit

class _TokenBucket:
    __slots__ = ("tokens", "updated")

    def __init__(self, capacity: float):
        self.tokens = capacity
        self.updated = time.monotonic()


class InMemoryRateBackend:
    """Domyślny backend rate-limit: token-bucket w pamięci procesu (per-worker).

    Wystarcza dla jednego workera / dev. Przy wielu workerach gunicorn limit
    jest per-worker — do globalnego limitu użyj RedisRateBackend.
    """

    def __init__(self, capacity: float, window_s: float):
        self.capacity = capacity
        self.window_s = window_s
        self._buckets: dict[str, _TokenBucket] = {}
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        rate = self.capacity / self.window_s
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


class RedisRateBackend:
    """Globalny rate-limit oparty o Redis (ETAP 16.2) — współdzielony przez workery.

    Algorytm: okno stałe z INCR + EXPIRE (proste i wystarczające dla ochrony API).
    **Fail-open:** każdy błąd Redisa (brak połączenia, timeout) → dopuszczamy
    żądanie i logujemy ostrzeżenie. Bezpieczeństwo dostępności > twardy limit;
    nigdy nie blokujemy ruchu z powodu awarii cache.

    `client` to obiekt zgodny z `redis.Redis` (metody `incr`, `expire`).
    Wstrzykiwany, by dało się go zamockować w testach bez serwera Redis.
    """

    def __init__(self, client, capacity: float, window_s: float):
        self._r = client
        self.capacity = int(capacity)
        self.window_s = int(window_s)

    def allow(self, key: str) -> bool:
        rk = f"adam:rl:{key}"
        try:
            count = self._r.incr(rk)
            if count == 1:
                self._r.expire(rk, self.window_s)
            return count <= self.capacity
        except Exception as exc:  # fail-open — awaria Redisa nie blokuje API
            logger.warning("rate_limit_redis_error key=%s err=%s (fail-open)", key, exc)
            return True


def _build_rate_backend(capacity: float, window_s: float):
    """Wybiera backend rate-limit wg ENV. Redis tylko gdy `ADAM_REDIS_URL` ustawione
    i biblioteka `redis` dostępna; w przeciwnym razie in-memory (fail-safe)."""
    url = os.getenv("ADAM_REDIS_URL", "").strip()
    if not url:
        return InMemoryRateBackend(capacity, window_s)
    try:
        import redis  # type: ignore

        client = redis.Redis.from_url(url, socket_connect_timeout=1, socket_timeout=1)
        logger.info("rate_limit backend=redis url=%s", url)
        return RedisRateBackend(client, capacity, window_s)
    except Exception as exc:
        logger.warning("rate_limit redis niedostępny (%s) → in-memory fallback", exc)
        return InMemoryRateBackend(capacity, window_s)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate-limit per-klient z pluggable backendem (in-memory | Redis).

    Konfiguracja ENV:
    - ADAM_RATE_LIMIT   — pojemność (żądań), domyślnie 120,
    - ADAM_RATE_WINDOW  — okno w sekundach, domyślnie 60,
    - ADAM_RATE_ENABLED — '0' wyłącza (domyślnie włączony),
    - ADAM_REDIS_URL    — jeśli ustawione, limit globalny w Redis (fail-open).
    Ścieżki wyłączone: /health, /health/live, /health/ready, /metrics, /.
    """

    def __init__(self, app, capacity: float | None = None, window_s: float | None = None,
                 backend=None):
        super().__init__(app)
        self.capacity = float(capacity or os.getenv("ADAM_RATE_LIMIT", "120"))
        self.window_s = float(window_s or os.getenv("ADAM_RATE_WINDOW", "60"))
        self.enabled = os.getenv("ADAM_RATE_ENABLED", "1") != "0"
        self._backend = backend or _build_rate_backend(self.capacity, self.window_s)
        self._exempt = {"/health", "/health/live", "/health/ready", "/metrics", "/"}

    def _key(self, request: Request) -> str:
        client = request.client.host if request.client else "unknown"
        return f"{client}"

    def _allow(self, key: str) -> bool:
        return self._backend.allow(key)

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
