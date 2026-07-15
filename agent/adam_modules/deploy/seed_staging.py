#!/usr/bin/env python3
"""WP-5 — seed danych demonstracyjnych dla środowiska STAGING.

Dane seniorów zawierają PII (PESEL/telefon szyfrowane Fernet + blind index),
dlatego seed MUSI iść przez warstwę serwisową (SeniorService), a nie przez
czysty INSERT SQL — inaczej wartości nie byłyby poprawnie zaszyfrowane.

Uruchomienie (wewnątrz kontenera adam-api lub lokalnie):
    ADAM_PII_KEY=... ADAM_PII_PEPPER=... \\
    ADAM_DATABASE_URL=postgresql+psycopg://adam:adam@localhost:5432/adam \\
    python -m adam_modules.deploy.seed_staging

Idempotentny: seniorzy o istniejącym external_id/PESEL nie są duplikowani.
"""
from __future__ import annotations

import os
import sys
from datetime import date

# Uruchamialne zarówno jako moduł jak i skrypt.
if __package__ in (None, ""):  # pragma: no cover - uruchomienie jako plik
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from adam_modules.common.db import session_scope
from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.seniors.models import Package, SemaphoreLevel


# --- dane demonstracyjne (spójne z frontendowym mockiem) --------------
SEED_SENIORS = [
    dict(first_name="Halina", last_name="Wiśniewska", birth_date=date(1947, 4, 12),
         phone="+48601111111", district="Wilda", package=Package.premium,
         semaphore=SemaphoreLevel.green),
    dict(first_name="Zofia", last_name="Kaczmarek", birth_date=date(1943, 9, 3),
         phone="+48601222222", district="Jeżyce", package=Package.family,
         semaphore=SemaphoreLevel.yellow),
    dict(first_name="Irena", last_name="Wójcik", birth_date=date(1950, 1, 28),
         phone="+48601333333", district="Grunwald", package=Package.basic,
         semaphore=SemaphoreLevel.green),
    dict(first_name="Tadeusz", last_name="Nowak", birth_date=date(1939, 12, 6),
         phone="+48601444444", district="Stare Miasto", package=Package.premium,
         semaphore=SemaphoreLevel.red),
]


def run() -> int:
    created, skipped = 0, 0
    with session_scope() as session:
        svc = SeniorService(session)
        existing = {f"{s.first_name} {s.last_name}" for s in svc.list()}
        for row in SEED_SENIORS:
            name = f"{row['first_name']} {row['last_name']}"
            if name in existing:
                skipped += 1
                continue
            senior = svc.create(SeniorCreate(
                first_name=row["first_name"], last_name=row["last_name"],
                birth_date=row["birth_date"], phone=row["phone"],
                district=row["district"], package=row["package"],
            ))
            # semafor startowy — ustawiany bezpośrednio na obiekcie ORM
            senior.semaphore = row["semaphore"]
            created += 1
        # commit realizuje session_scope
    print(f"[seed_staging] utworzono={created} pominięto(istniejące)={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
