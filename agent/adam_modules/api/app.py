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
from fastapi.responses import JSONResponse

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

    if init_db:
        from adam_modules.common import db as db_mod

        db_mod._ensure_init()
        db_mod.create_all()

    # ---- error handlers ----
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
        }

    # ---- routery F1–F18 ----
    from .routers import (
        seniors as seniors_router,
        safety as safety_router,
        medication as medication_router,
        wearables as wearables_router,
        family as family_router,
        marketplace as marketplace_router,
        rodo as rodo_router,
        compliance as compliance_router,
    )

    app.include_router(seniors_router.router)
    app.include_router(safety_router.router)
    app.include_router(medication_router.router)
    app.include_router(wearables_router.router)
    app.include_router(family_router.router)
    app.include_router(marketplace_router.router)
    app.include_router(rodo_router.router)
    app.include_router(compliance_router.router)

    return app


app = create_app()
