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
| F6 | Medication tracker | ✅ leki + harmonogram (days_mask) + dose_logs + adherence (F6.2) + MedGuard flag (F6.3) + migracja 0004 + 11 testów |
| F7 | Pamięć semantyczna (RAG) | ✅ MemoryChunk + pluggable Embedder (HashingEmbedder offline) + retrieve cosine top-k + build_context (inject do promptu F5) + forget_senior (RODO) + migracja 0005 + 13 testów |
| F8 | Crisis detection | ✅ CrisisDetector (15 triggerów z fraz PL + vitals HR/SpO2/BP) → Classification przez Guardrails + 12 testów |
| F9 | Dashboard rodzinny + notyfikacje | ✅ FamilyMember + adaptery SMS/email/push + dispatch wg poziomu (digest/immediate/bypass-DND) + DND + feed (SSE) + migracja 0006 + 9 testów |
| F10 | Wearables | ✅ adaptery Xiaomi/Apple/Garmin/Fitbit + threshold engine (auto+override) + audyt SHA-256 + migracja 0006 + 9 testów |
| F11 | Marketplace | ✅ Partner/Service/Order + 10 kategorii + weryfikacja NIP/OC + anty-fraud (suspend) + okno anulowania 30min + migracja 0006 + 15 testów |
| F12 | RODO (retencja, prawo do zapomnienia) | ✅ retencja + soft-delete + export (art.15/20) + erase cross-module (art.17) + DataProcessingLog (art.30) + migracja 0006 + 8 testów |
| F13 | AI Act compliance | ✅ SYSTEM_REGISTER (art.11/zał.IV) + DisclosureLog (art.50) + assert_disclosed + migracja 0007 + 5 testów |
| F14 | Optymalizacja mowy senioralnej | ✅ build_speech_profile (niedosłuch + tempo + wiek → tempo/głośność/pauzy/ton/powtórzenia) → inject do promptu F5 + 6 testów |
| F15 | QA (metryki jakości rozmów) | ✅ QAEvaluator (0-100: disclosure/responsiveness/ASR/przerwania/kompletność) + needs_human_review + 6 testów |
| F16 | Multi-model consensus | ✅ ConsensusEngine (≥2 źródła, fail-safe wyższy poziom przy rozbieżności, needs_review) + 6 testów |
| F17 | Integracja 112 | ✅ EmergencyService (payload: adres/wiek/leki/vitals + dispatch_summary) + 5 testów |
| F18 | Testy E2E + CI | ✅ pełny przepływ PURPLE (detekcja→consensus→guardrails→semafor→eskalacja→rodzina→112→disclosure→RODO) + scenariusze GREEN/state-machine + GitHub Actions CI (`.github/workflows/backend-ci.yml`) + 6 testów E2E |

**Łącznie: 154 testy, 7 migracji (0001–0007), CI (pytest + Alembic upgrade/downgrade). Backend F1–F18 kompletny.**
