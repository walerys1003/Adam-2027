"""Fabryka aplikacji FastAPI — warstwa API backendu Adama (ETAP 9).

Wystawia funkcje F1–F18 z `adam_modules` przez REST/JSON, tak by frontend
(panel opiekuna / admina) mógł docelowo połączyć się z prawdziwym backendem
we Frankfurt DC zamiast mocka.

Uruchomienie lokalne:
    ADAM_PII_KEY=dev uvicorn adam_modules.api.app:app --reload
"""
from __future__ import annotations

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

API_VERSION = "1.0"


def create_app(*, init_db: bool = True) -> FastAPI:
    """Buduje instancję FastAPI ze wszystkimi routerami F1–F18."""
    app = FastAPI(
        title="Adam API — backend senior-care",
        version=API_VERSION,
        description=(
            "REST API dla agenta głosowego Adam (SilverTech, Poznań). "
            "Wystawia profile seniorów, semafor bezpieczeństwa, leki, "
            "wearables, dashboard rodzinny, marketplace, RODO i compliance."
        ),
    )

    # --- middleware obserwowalności + hardening (ETAP 14 + 16) ---
    # Kolejność dodawania: ostatnio dodany = najbardziej zewnętrzny.
    # Chcemy (od zewnątrz): [SecurityHeaders] -> [CORS] -> [RequestContext] -> [RateLimit] -> app.
    from .observability import (
        RateLimitMiddleware, RequestContextMiddleware, SecurityHeadersMiddleware,
    )

    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestContextMiddleware)

    # CORS — panel opiekuna/admina (Cloudflare Pages) + dev localhost.
    origins = os.getenv(
        "ADAM_CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173",
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in origins if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Nagłówki bezpieczeństwa (ETAP 16.1) — najbardziej zewnętrzny, obejmuje wszystkie odpowiedzi.
    app.add_middleware(SecurityHeadersMiddleware)

    if init_db:
        from adam_modules.common import db as db_mod

        db_mod._ensure_init()
        db_mod.create_all()

    # ---- error handlers ----
    from adam_modules.auth.security import TokenError

    @app.exception_handler(TokenError)
    async def _token_error_handler(request: Request, exc: TokenError):
        # Błędy uwierzytelniania (złe hasło / token) → 401.
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(ValueError)
    async def _value_error_handler(request: Request, exc: ValueError):
        # Błędy walidacji domenowej (np. zły PESEL/NIP) → 422.
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    # ---- health ----
    @app.get("/health", tags=["system"])
    async def health():
        return {"status": "ok", "service": "adam-api", "version": API_VERSION}

    @app.get("/", tags=["system"])
    async def root():
        return {
            "service": "Adam API",
            "version": API_VERSION,
            "docs": "/docs",
            "health": "/health",
            "metrics": "/metrics",
        }

    @app.get("/metrics", tags=["system"])
    async def metrics_endpoint():
        # Ekspozycja metryk w formacie tekstowym (Prometheus-like).
        from .observability import render_metrics

        return PlainTextResponse(render_metrics(), media_type="text/plain; version=0.0.4")

    # ---- routery F1–F18 + auth (ETAP 11) ----
    from .routers import (
        auth as auth_router,
        seniors as seniors_router,
        safety as safety_router,
        medication as medication_router,
        wearables as wearables_router,
        family as family_router,
        marketplace as marketplace_router,
        rodo as rodo_router,
        compliance as compliance_router,
        voice as voice_router,
    )

    app.include_router(auth_router.router)
    app.include_router(seniors_router.router)
    app.include_router(safety_router.router)
    app.include_router(medication_router.router)
    app.include_router(wearables_router.router)
    app.include_router(family_router.router)
    app.include_router(marketplace_router.router)
    app.include_router(rodo_router.router)
    app.include_router(compliance_router.router)
    app.include_router(voice_router.router)

    return app


app = create_app()
