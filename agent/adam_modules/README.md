# adam_modules — backend Adama (F1–F18)

Pakiet Pythona nadbudowany na AVA v7.3.2, realizujący funkcje senior-care Adama.
Uruchomienie docelowe: **Frankfurt DC** (patrz `docs/BACKEND-DEPLOY.md`).

## Struktura

```
adam_modules/
├── common/           # warstwa wspólna
│   ├── db.py         # SQLAlchemy 2.0 (Base, session_scope, init_engine)
│   └── crypto.py     # FieldCipher — szyfrowanie PII (RODO) + blind index
├── seniors/          # F1 — profile seniorów
│   ├── models.py     # model Senior (PII szyfrowane: PESEL/telefon)
│   ├── schemas.py    # Pydantic v2 (walidacja PESEL/telefon)
│   └── service.py    # SeniorService (CRUD + find_by_pesel przez blind index)
├── migrations/       # Alembic (0001_seniors)
└── tests/            # pytest
```

## Instalacja

```bash
cd agent
pip install -r adam_modules/requirements.txt
```

## Migracje

```bash
cd adam_modules/migrations
ADAM_DATABASE_URL="postgresql://user:pass@host/adam" alembic upgrade head
```

Lokalnie (SQLite): `alembic upgrade head` (domyślny `adam_dev.db`).

## Testy

```bash
cd agent
python3 -m pytest adam_modules/tests/ -q
```

## Zmienne środowiskowe

| Zmienna | Opis | Domyślnie |
|---------|------|-----------|
| `ADAM_DATABASE_URL` | URL bazy (PG w produkcji) | `sqlite:///:memory:` |
| `ADAM_PII_KEY` | Klucz szyfrowania PII (base64 32B lub sekret) | dev-insecure |
| `ADAM_PII_PEPPER` | Pieprz do blind index | `adam-pepper` |

## Status funkcji

| # | Funkcja | Status |
|---|---------|--------|
| F1 | Profile seniorów (PII szyfrowane) | ✅ modele + schematy + serwis + migracja + testy |
| F2 | Scheduler welfare-check | ✅ kampanie + retry 3×/20s + APScheduler + ARI wrapper + 7 testów |
| F3–F5 | Semafor + eskalacja + guardrails + prompt | ✅ SemaphoreEngine (17 triggerów, state machine) + EscalationLadder (RED/PURPLE) + Guardrails (anty-halucynacja) + System Prompt (AI Act disclosure) + migracja 0003 + 26 testów |
| F6 | Medication tracker | ⏳ |
| F7 | Pamięć semantyczna (RAG) | ⏳ |
| F8 | Crisis detection | ⏳ |
| F9 | Dashboard rodzinny + notyfikacje | ⏳ |
| F10 | Wearables | ⏳ |
| F11 | Marketplace | ⏳ |
| F12 | RODO (retencja, prawo do zapomnienia) | ⏳ |
| F13–F18 | AI Act / mowa / QA / consensus / 112 / E2E | ⏳ |
