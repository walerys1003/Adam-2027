🎯 GENSPARK AI DEVELOPER — ZAKTUALIZOWANY PROMPT WDROŻENIOWY
Rozbudowa AVA → Agent Adam dla SilverTech (Poznań)
Data: 12.07.2026 Bazowy fork: hkjarral/AVA-AI-Voice-Agent-for-Asterisk (v7.3.2, MIT) Cel: Przekształcenie generycznego voice agenta w wyspecjalizowanego agenta konwersacyjnego dla seniorów o nazwie Adam
📋 A. CO AVA JUŻ DAJE (✅ — NIE RUSZAMY, KORZYSTAMY)
| # | Funkcja | Gdzie w AVA | Użycie w Adamie |
| A1 | Telefonia PSTN/SIP | Asterisk ARI + dialplan AI_AGENT | Dzwonienie do seniorów na komórki i stacjonarne |
| A2 | Outbound Calling (Alpha) | docs/OUTBOUND_CALLING.md | Podstawa schedulera – kampanie wychodzące, consent gate |
| A3 | Admin UI Dashboard | localhost:3003, SSE live‑status | Panel opiekuna – stan seniorów, historia połączeń |
| A4 | Call History + transkrypty | Pełna historia, metadane, odtwarzanie .ulaw/.WAV | Przeglądanie rozmów przez opiekuna |
| A5 | 7 providerów AI | OpenAI, Google, Deepgram, ElevenLabs, Grok, Telnyx, Local Hybrid | Wybór providera PL (ElevenLabs + GPT‑4o) |
| A6 | Silence Watchdog | v7.3.1 – 30s ciszy → monit → 15s → hangup | Wykrywanie, czy senior się nie odezwał |
| A7 | Barge‑in | Przerywanie agenta przez rozmówcę | Senior może przerwać Adamowi |
| A8 | Tool Calling | transfer, hangup_call, leave_voicemail, HTTP pre/in/post‑call, kalendarze | Podstawa alertów email/webhook |
| A9 | Per‑agent voices | v7.3.0 – każdy agent własny głos | Głos Adama (np. ElevenLabs baryton PL) |
| A10 | Lokalny STT/TTS | Faster‑Whisper, Piper, Kokoro | Audio seniora nie opuszcza serwera |
| A11 | Call Recordings | Nagrywanie + odtwarzanie w UI | Archiwizacja rozmów (RODO) |
| A12 | 3‑file config | ai-agent.yaml + local.yaml + .env | Konfiguracja promptów Adama w YAML |
| A13 | CLI tools | agent setup, check, dialplan, rca | Diagnostyka i wdrożenie |
| A14 | Docker Compose | ai_engine + admin_ui + opcjonalnie local_ai_server | Produkcyjne wdrożenie na VPS |
| A15 | Ollama (self‑hosted LLM) | Llama 3.2, Mistral, Qwen 2.5 | Opcjonalnie: w pełni lokalny Adam |
🧱 B. CO TRZEBA DOBUDOWAĆ — FAZY F1–F18 (ZAKTUALIZOWANE)
Poniżej znajduje się 18 faz uporządkowanych według zależności. Każda faza zawiera:
Cel — co ma osiągnąć
Pliki do utworzenia — dokładne ścieżki w repo AVA
Pliki do zmodyfikowania — gdzie wpiąć nowy kod
Kluczowe snippet’y kodu — gotowe do wklejenia w GenSpark
Testy akceptacyjne — jak zweryfikować poprawność
🔴 F1 — Senior Profile Database
Cel: Baza danych seniorów (dane osobowe, preferencje, historia medyczna, kontakty rodzinne)
Pliki do utworzenia:
backend/app/models/senior.py
backend/app/schemas/senior.py
backend/app/api/v1/seniors.py
backend/app/services/senior_service.py
backend/alembic/versions/XXXX_create_seniors_tables.py
frontend/src/pages/Seniors/
Schemat bazy (SQLAlchemy) – backend/app/models/senior.py:
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid, enum
from backend.app.database import Base
class SemaphoreLevel(str, enum.Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    PURPLE = "purple"
class Senior(Base):
    __tablename__ = "seniors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False, unique=True, index=True)
    pesel_encrypted = Column(Text, nullable=True)           # AES-256-GCM
    date_of_birth = Column(DateTime, nullable=True)
    address_street = Column(String(200), nullable=True)
    address_city = Column(String(100), nullable=True, default="Poznań")
    address_postal = Column(String(10), nullable=True)
    preferred_language = Column(String(10), default="pl")
    preferred_name = Column(String(50), nullable=True)       # np. "Panie Janie" / "Babciu Zosiu"
    voice_speed = Column(String(10), default="normal")       # slow / normal
    call_frequency = Column(String(20), default="daily")     # daily / twice_daily / weekly
    preferred_call_hour = Column(Integer, default=10)        # 0-23
    notes = Column(Text, nullable=True)                      # istotne info dla Adama
    current_semaphore = Column(Enum(SemaphoreLevel), default=SemaphoreLevel.GREEN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default="now()")
    updated_at = Column(DateTime, onupdate="now()")
    # Relacje
    medications = relationship("Medication", back_populates="senior", cascade="all, delete")
    family_members = relationship("FamilyMember", back_populates="senior", cascade="all, delete")
    wearable_data = relationship("WearableData", back_populates="senior", cascade="all, delete")
class Medication(Base):
    __tablename__ = "medications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    senior_id = Column(UUID(as_uuid=True), ForeignKey("seniors.id", ondelete="CASCADE"), index=True)
    name = Column(String(200), nullable=False)
    dosage = Column(String(100), nullable=False)              # np. "5 mg"
    frequency = Column(String(50), nullable=False)            # "once_daily", "twice_daily", "every_8h"
    time_of_day = Column(JSON, nullable=False)                # ["08:00", "20:00"]
    notes = Column(Text, nullable=True)                       # "brać po jedzeniu"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default="now()")
    senior = relationship("Senior", back_populates="medications")
class FamilyMember(Base):
    __tablename__ = "family_members"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    senior_id = Column(UUID(as_uuid=True), ForeignKey("seniors.id", ondelete="CASCADE"), index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(200), nullable=True)
    relationship = Column(String(50), nullable=False)         # "daughter", "son", "neighbor"
    is_emergency_contact = Column(Boolean, default=True)
    notification_preference = Column(String(10), default="sms")  # sms / email / both
    created_at = Column(DateTime, server_default="now()")
    senior = relationship("Senior", back_populates="family_members")
API endpointy – backend/app/api/v1/seniors.py:
from fastapi import APIRouter, Depends, HTTPException
from backend.app.services.senior_service import SeniorService
from backend.app.schemas.senior import SeniorCreate, SeniorUpdate, SeniorResponse
router = APIRouter(prefix="/api/v1/seniors", tags=["seniors"])
@router.post("/", response_model=SeniorResponse)
async def create_senior(data: SeniorCreate, service: SeniorService = Depends()):
    return await service.create(data)
@router.get("/{senior_id}", response_model=SeniorResponse)
async def get_senior(senior_id: str, service: SeniorService = Depends()):
    return await service.get_by_id(senior_id)
@router.put("/{senior_id}", response_model=SeniorResponse)
async def update_senior(senior_id: str, data: SeniorUpdate, service: SeniorService = Depends()):
    return await service.update(senior_id, data)
@router.delete("/{senior_id}")
async def deactivate_senior(senior_id: str, service: SeniorService = Depends()):
    await service.deactivate(senior_id)
    return {"status": "deactivated"}
@router.get("/", response_model=list[SeniorResponse])
async def list_seniors(skip: int = 0, limit: int = 50, status: str = "active", service: SeniorService = Depends()):
    return await service.list_all(skip=skip, limit=limit, status=status)
# Dodatkowe endpointy
@router.get("/{senior_id}/medications")
async def get_medications(senior_id: str, service: SeniorService = Depends()): ...
@router.get("/{senior_id}/family")
async def get_family_members(senior_id: str, service: SeniorService = Depends()): ...
@router.get("/{senior_id}/mood-history")
async def get_mood_history(senior_id: str, days: int = 30, service: SeniorService = Depends()): ...
@router.get("/{senior_id}/call-history")
async def get_call_history(senior_id: str, limit: int = 20, service: SeniorService = Depends()): ...
Plik do zmodyfikowania:
backend/app/main.py — zarejestrować nowy router: app.include_router(seniors_router)
frontend/src/App.tsx — dodać zakładkę “Seniorzy”
Test akceptacyjny:
curl -X POST http://localhost:15000/api/v1/seniors/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jan",
    "last_name": "Kowalski",
    "phone_number": "+48500100200",
    "preferred_name": "Panie Janie",
    "call_frequency": "daily",
    "preferred_call_hour": 10
  }'
# Oczekiwany: 201 Created z UUID seniora
Szacowany czas: 3–5 dni
🔴 F2 — Call Scheduler (Harmonogram połączeń wychodzących)
Cel: Automatyczne dzwonienie do seniorów o zaplanowanych porach (welfare-check)
Co AVA już ma: Outbound Calling w wersji Alpha (docs/OUTBOUND_CALLING.md) – wykorzystujemy jako podstawę, rozbudowujemy.
Pliki do utworzenia:
backend/app/models/call_schedule.py
backend/app/schemas/call_schedule.py
backend/app/api/v1/schedules.py
backend/app/services/scheduler_service.py
backend/alembic/versions/XXXX_create_call_schedules.py
Model – backend/app/models/call_schedule.py:
class CallSchedule(Base):
    __tablename__ = "call_schedules"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    senior_id = Column(UUID, ForeignKey("seniors.id", ondelete="CASCADE"), unique=True, index=True)
    call_type = Column(String(20), default="welfare_check")   # welfare_check / medication_reminder / custom
    frequency = Column(String(20), default="daily")           # daily / twice_daily / weekly / custom
    preferred_hour = Column(Integer, default=10)              # 0-23
    second_hour = Column(Integer, nullable=True)              # dla twice_daily
    days_of_week = Column(JSON, default=["mon","tue","wed","thu","fri","sat","sun"])
    max_retries = Column(Integer, default=2)
    retry_delay_minutes = Column(Integer, default=15)
    is_active = Column(Boolean, default=True)
    last_call_at = Column(DateTime, nullable=True)
    next_call_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, server_default="now()")
class CallAttempt(Base):
    __tablename__ = "call_attempts"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    schedule_id = Column(UUID, ForeignKey("call_schedules.id"), index=True)
    senior_id = Column(UUID, ForeignKey("seniors.id"), index=True)
    call_id = Column(String(100), nullable=True)              # Asterisk channel ID
    status = Column(String(20))                               # initiated / answered / no_answer / busy / failed / completed
    started_at = Column(DateTime, server_default="now()")
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
Silnik schedulera – backend/app/services/scheduler_service.py:
import asyncio
from datetime import datetime, timedelta
from backend.app.services.senior_service import SeniorService
from backend.app.services.asterisk_service import AsteriskService
class SchedulerService:
    """Główny silnik planowania połączeń. Odpalany jako background task."""
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.senior_service = SeniorService()
        self.asterisk = AsteriskService()
    async def run(self):
        """Główna pętla schedulera — sprawdza co 60s, czy są zaplanowane połączenia."""
        while True:
            try:
                due_schedules = await self._get_due_schedules()
                for schedule in due_schedules:
                    await self._execute_call(schedule)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
            await asyncio.sleep(self.check_interval)
    async def _get_due_schedules(self):
        """Pobiera harmonogramy, które powinny być wykonane teraz (± 5 min bufor)."""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=5)
        window_end = now + timedelta(minutes=5)
        return await CallSchedule.filter(
            CallSchedule.is_active == True,
            CallSchedule.next_call_at.between(window_start, window_end)
        ).all()
    async def _execute_call(self, schedule):
        """Wykonuje połączenie przez Asterisk ARI."""
        senior = await self.senior_service.get_by_id(schedule.senior_id)
        call_id = await self.asterisk.originate(
            endpoint=f"PJSIP/{senior.phone_number}",
            context="from-ai-agent",
            extension="s",
            variables={
                "AI_AGENT": "adam-welfare-check",
                "SENIOR_ID": str(senior.id),
                "CALL_TYPE": schedule.call_type
            }
        )
        # Log próby
        await CallAttempt.create(
            schedule_id=schedule.id,
            senior_id=senior.id,
            call_id=call_id,
            status="initiated"
        )
        # Oblicz następne połączenie
        schedule.last_call_at = datetime.utcnow()
        schedule.next_call_at = self._calculate_next(schedule)
        await schedule.save()
    def _calculate_next(self, schedule):
        """Oblicza następną datę połączenia na podstawie frequency."""
        now = datetime.utcnow()
        if schedule.frequency == "daily":
            return now.replace(hour=schedule.preferred_hour, minute=0) + timedelta(days=1)
        elif schedule.frequency == "twice_daily":
            # jeśli teraz było pierwsze, następne = drugie dziś; inaczej jutro o pierwszej
            ...
        elif schedule.frequency == "weekly":
            ...
        return now + timedelta(days=1)
API – backend/app/api/v1/schedules.py:
@router.post("/")
async def create_schedule(senior_id: str, schedule: CallScheduleCreate): ...
@router.put("/{schedule_id}")
async def update_schedule(schedule_id: str, data: CallScheduleUpdate): ...
@router.post("/{schedule_id}/trigger-now")
async def trigger_call_now(schedule_id: str):
    """Ręczne wyzwolenie połączenia (dla opiekuna/testów)."""
@router.get("/{senior_id}/next-call")
async def get_next_call_time(senior_id: str):
    """Zwraca datę następnego zaplanowanego połączenia."""
Plik do zmodyfikowania:
backend/app/main.py — uruchomienie schedulera jako asyncio.create_task(scheduler.run()) przy starcie
frontend/src/pages/ — zakładka “Harmonogram” w UI seniora
Test akceptacyjny:
# Utwórz harmonogram
curl -X POST http://localhost:15000/api/v1/schedules/ \
  -d '{"senior_id":"<uuid>", "call_type":"welfare_check", "preferred_hour":10}'
# Wyzwól natychmiast
curl -X POST http://localhost:15000/api/v1/schedules/<uuid>/trigger-now
# Sprawdź w Call History, że połączenie zostało wykonane
Szacowany czas: 4–6 dni
🔴 F3 — 4-Kolorowy Semafor Eskalacji (GREEN → YELLOW → RED → PURPLE)
Cel: Automatyczna ocena stanu seniora po każdej rozmowie i eskalacja w razie niepokojących sygnałów.
Pliki do utworzenia:
backend/app/models/escalation.py
backend/app/services/semaphore_engine.py
backend/app/services/escalation_service.py
config/escalation_triggers.yaml
config/escalation_actions.yaml
backend/alembic/versions/XXXX_create_escalation_tables.py
Logika semafora – backend/app/services/semaphore_engine.py:
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
class Level(Enum):
    GREEN = "green"       # Wszystko OK
    YELLOW = "yellow"     # Lekki niepokój – monitorować
    RED = "red"           # Poważny sygnał – natychmiast powiadomić rodzinę
    PURPLE = "purple"     # Zagrożenie życia – dzwonić po 112
@dataclass
class EscalationInput:
    senior_id: str
    call_id: str
    transcript: str
    sentiment_score: float           # -1.0 (negatywne) do 1.0 (pozytywne)
    silence_detected: bool           # czy była cisza >15s
    keywords_detected: list[str]     # wykryte słowa kluczowe
    wearable_alerts: list[dict]      # alerty z wearables (opcjonalnie)
    medication_missed_count: int     # ile dawek pominiętych w ostatnim tygodniu
    previous_level: Level
@dataclass
class SemaphoreDecision:
    level: Level
    confidence: float
    triggers: list[str]              # co uruchomiło eskalację
    recommended_actions: list[str]   # co zrobić
    timestamp: datetime = field(default_factory=datetime.utcnow)
class SemaphoreEngine:
    """Główny silnik oceny stanu seniora."""
    ESCALATION_RULES = {
        Level.GREEN: {
            "to_yellow": [
                "sentiment_score < -0.3",
                "keywords_detected includes 'samotny'/'smutny'/'nie chce mi się'",
                "medication_missed_count >= 2",
                "silence_detected == True"
            ],
            "to_red": [
                "keywords_detected includes any MEDICAL_EMERGENCY_KEYWORDS",
                "sentiment_score < -0.7",
                "medication_missed_count >= 5"
            ],
            "to_purple": [
                "keywords_detected includes any SUICIDE_KEYWORDS",
                "keywords_detected includes 'nie mogę oddychać'/'ból w klatce'/'zawał'/'udar'",
                "wearable_alerts has fall_detected==True with confidence>0.8",
                "wearable_alerts has heart_rate>140 or spo2<88"
            ]
        },
        Level.YELLOW: { ... },  # podobna struktura
        Level.RED: { ... },
        Level.PURPLE: { ... },
    }
    async def evaluate(self, input: EscalationInput) -> SemaphoreDecision:
        """Ocenia stan seniora i zwraca decyzję o poziomie eskalacji."""
        triggers = []
        current = input.previous_level
        # Sprawdź reguły PURPLE (najwyższy priorytet)
        purple_triggers = self._check_rules(input, "to_purple")
        if purple_triggers:
            return SemaphoreDecision(
                level=Level.PURPLE,
                confidence=0.95,
                triggers=purple_triggers,
                recommended_actions=["call_emergency_services", "notify_family_immediate"]
            )
        # Sprawdź reguły RED
        red_triggers = self._check_rules(input, "to_red")
        if red_triggers:
            return SemaphoreDecision(
                level=Level.RED,
                confidence=0.85,
                triggers=red_triggers,
                recommended_actions=["notify_family_immediate", "escalate_to_coordinator"]
            )
        # Sprawdź reguły YELLOW
        yellow_triggers = self._check_rules(input, "to_yellow")
        if yellow_triggers:
            return SemaphoreDecision(
                level=Level.YELLOW,
                confidence=0.75,
                triggers=yellow_triggers,
                recommended_actions=["increase_call_frequency", "notify_family_daily_digest"]
            )
        # Jeśli nic – zostaje GREEN lub wraca do GREEN z wyższego
        return SemaphoreDecision(
            level=Level.GREEN,
            confidence=0.9,
            triggers=[],
            recommended_actions=["continue_normal_schedule"]
        )
    def _check_rules(self, input: EscalationInput, target: str) -> list[str]:
        """Sprawdza listę reguł dla danego poziomu docelowego."""
        triggers = []
        for rule_expr in self.ESCALATION_RULES[input.previous_level].get(target, []):
            if self._eval_rule(rule_expr, input):
                triggers.append(rule_expr)
        return triggers
    def _eval_rule(self, rule_expr: str, input: EscalationInput) -> bool:
        """Ewaluuje pojedynczą regułę. Używa bezpiecznego eval z kontekstem."""
        # Implementacja z ograniczonym eval lub parserem wyrażeń
        ...
Konfiguracja triggerów – config/escalation_triggers.yaml:
medical_emergency_keywords:
  - "nie mogę oddychać"
  - "duszę się"
  - "ból w klatce piersiowej"
  - "zawał"
  - "udar"
  - "zasłabłem"
  - "upadłem"
  - "nie mogę wstać"
  - "krew"
  - "złamałem"
  - "straciłem przytomność"
  - "nie czuję nogi"
  - "nie czuję ręki"
  - "nie widzę na jedno oko"
  - "mam zawroty głowy i nie mogę"
  - "przewróciłem się"
  - "potłukłem się"
  - "bardzo silny ból"
suicide_keywords:
  - "nie chcę już żyć"
  - "nie ma po co żyć"
  - "chcę umrzeć"
  - "lepiej żeby mnie nie było"
  - "skończyć ze sobą"
  - "wszystko jest bez sensu"
  - "nigdy się nie obudzić"
  - "po co mam żyć"
  - "śmierć byłaby lepsza"
distress_keywords:
  - "jestem samotny"
  - "nikt mnie nie odwiedza"
  - "wszyscy o mnie zapomnieli"
  - "nie mam do kogo ust otworzyć"
  - "boję się"
  - "nie daję rady"
  - "wszystko mnie przerasta"
  - "nie chce mi się żyć"  # niski priorytet vs suicide – kontekst ma znaczenie
  - "jest mi bardzo smutno"
  - "płakałem dzisiaj"
  - "nic mi nie wychodzi"
  - "czuję się bezwartościowy"
  - "ciągle jestem zmęczony"
  - "nic mnie nie cieszy"
Eskalacja akcji – backend/app/services/escalation_service.py:
class EscalationService:
    """Wykonuje akcje eskalacyjne na podstawie decyzji SemaphoreEngine."""
    async def execute(self, decision: SemaphoreDecision, senior_id: str, call_id: str):
        for action in decision.recommended_actions:
            if action == "call_emergency_services":
                await self._call_112(senior_id, decision)
            elif action == "notify_family_immediate":
                await self._notify_family(senior_id, decision, urgency="immediate")
            elif action == "notify_family_daily_digest":
                await self._queue_digest_notification(senior_id, decision)
            elif action == "escalate_to_coordinator":
                await self._notify_coordinator(senior_id, decision)
            elif action == "increase_call_frequency":
                await self._increase_call_frequency(senior_id)
            elif action == "continue_normal_schedule":
                pass  # bez akcji
        # Zapisz zdarzenie eskalacji
        await EscalationEvent.create(
            senior_id=senior_id,
            call_id=call_id,
            previous_level=decision.previous_level,
            new_level=decision.level,
            confidence=decision.confidence,
            triggers=decision.triggers,
            actions_taken=decision.recommended_actions
        )
        # Aktualizuj semafor seniora
        await SeniorService().update_semaphore(senior_id, decision.level)
Pliki do zmodyfikowania:
ai_engine → po zakończeniu połączenia wywołać SemaphoreEngine.evaluate()
frontend/src/pages/Seniors/ → pokazać ikonę semafora przy każdym seniorze
Test akceptacyjny:
# Symulacja rozmowy z negatywnym sentymentem
input = EscalationInput(
    senior_id="...",
    transcript="Nie chce mi się już żyć, nikt mnie nie odwiedza...",
    sentiment_score=-0.8,
    keywords_detected=["nie chcę już żyć", "nikt mnie nie odwiedza"],
    ...
)
decision = await engine.evaluate(input)
assert decision.level == Level.PURPLE
assert "call_emergency_services" in decision.recommended_actions
Szacowany czas: 5–7 dni
🔴 F4 — Guardrails (Warstwa Bezpieczeństwa Promptu)
Cel: Ochrona seniora przed niewłaściwymi odpowiedziami Adama (porady medyczne, obietnice, tematy poza zakresem) + wykrywanie sygnałów alarmowych przed LLM.
Co AVA już ma: Podstawowe guardrails (v6.3.1) – hangup guardrails, tool‑call parsing robustness. Rozbudowujemy.
Pliki do utworzenia:
backend/app/services/guardrails_service.py
config/guardrails/pre_llm_rules.yaml
config/guardrails/post_llm_rules.yaml
config/guardrails/guardrail_fallbacks.yaml
backend/app/models/guardrail.py
Warstwa pre‑LLM – backend/app/services/guardrails_service.py:
import re
import yaml
from dataclasses import dataclass
from typing import Optional
@dataclass
class GuardrailResult:
    passed: bool
    blocked: bool = False
    reason: Optional[str] = None
    fallback_response: Optional[str] = None
    detected_keywords: list[str] = None
class GuardrailsService:
    """Dwupoziomowa warstwa bezpieczeństwa: pre-LLM + post-LLM."""
    def __init__(self):
        with open("config/guardrails/pre_llm_rules.yaml") as f:
            self.pre_rules = yaml.safe_load(f)
        with open("config/guardrails/post_llm_rules.yaml") as f:
            self.post_rules = yaml.safe_load(f)
        with open("config/guardrails/guardrail_fallbacks.yaml") as f:
            self.fallbacks = yaml.safe_load(f)
    async def pre_llm_check(self, senior_input: str, senior_id: str) -> GuardrailResult:
        """
        Sprawdza wypowiedź seniora ZANIM trafi do LLM.
        Wykrywa słowa alarmowe, suicydalne, manipulacje.
        """
        detected = []
        # 1. Słowa alarmowe medyczne → natychmiastowa eskalacja
        for keyword in self.pre_rules["medical_emergency"]:
            if re.search(keyword, senior_input, re.IGNORECASE):
                detected.append(f"MEDICAL:{keyword}")
        # 2. Słowa suicydalne → najwyższy priorytet
        for keyword in self.pre_rules["suicide"]:
            if re.search(keyword, senior_input, re.IGNORECASE):
                detected.append(f"SUICIDE:{keyword}")
        # 3. Próby manipulacji / wyłudzenia
        for pattern in self.pre_rules["manipulation"]:
            if re.search(pattern, senior_input, re.IGNORECASE):
                detected.append(f"MANIPULATION:{pattern}")
        if detected:
            return GuardrailResult(
                passed=True,
                blocked=False,  # nie blokujemy – tylko flagujemy
                detected_keywords=detected
            )
        return GuardrailResult(passed=True, blocked=False, detected_keywords=[])
    async def post_llm_check(self, llm_response: str) -> GuardrailResult:
        """
        Sprawdza odpowiedź LLM ZANIM zostanie wypowiedziana do seniora.
        Blokuje: porady medyczne, obietnice, tematy out-of-scope.
        """
        # 1. Czy Adam nie udziela porad medycznych?
        for pattern in self.post_rules["no_medical_advice"]:
            if re.search(pattern, llm_response, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    blocked=True,
                    reason="medical_advice_detected",
                    fallback_response=self.fallbacks["medical_advice"]
                )
        # 2. Czy Adam nie składa niemożliwych obietnic?
        for pattern in self.post_rules["no_promises"]:
            if re.search(pattern, llm_response, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    blocked=True,
                    reason="promise_detected",
                    fallback_response=self.fallbacks["promise"]
                )
        # 3. Czy odpowiedź nie wykracza poza zakres?
        for pattern in self.post_rules["out_of_scope"]:
            if re.search(pattern, llm_response, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    blocked=True,
                    reason="out_of_scope",
                    fallback_response=self.fallbacks["out_of_scope"]
                )
        return GuardrailResult(passed=True, blocked=False)
Reguły pre‑LLM – config/guardrails/pre_llm_rules.yaml:
medical_emergency:
  - "nie mogę oddychać"
  - "duszę się"
  - "ból w klatce"
  - "zawał|zawału"
  - "udar|udaru"
  - "upadłem|przewróciłem"
  - "nie mogę wstać"
  - "krew|krwawię|krwotok"
  - "złamałem|złamałam"
  - "straciłem przytomność"
  - "nie czuję (nogi|ręki|twarzy)"
  - "nie widzę na (jedno|lewe|prawe) oko"
  - "bardzo silny ból"
suicide:
  - "nie chcę (już )?żyć"
  - "chcę umrzeć|chciałbym umrzeć"
  - "lepiej żeby mnie nie było"
  - "skończyć ze sobą"
  - "nigdy się nie (obudzić|zbudzić)"
  - "po co (mi to|mam) żyć"
  - "śmierć byłaby"
  - "odebrać sobie (życie|to życie)"
  - "nie warto (już )?żyć"
manipulation:
  - "przelej (mi )?pieniądze"
  - "podaj (mi )?(swój|twój) (hasło|pin|pesel)"
  - "jesteś (moim |)prawdziwym (człowiekiem|synem|córką)"
Fallbacki – config/guardrails/guardrail_fallbacks.yaml:
medical_advice: |
  Proszę mnie zrozumieć – nie jestem lekarzem i nie mogę udzielać porad medycznych.
  W przypadku problemów zdrowotnych proszę skontaktować się z lekarzem rodzinnym,
  a w nagłych przypadkach dzwonić pod 112. Czy chciałby Pan, żebym powiadomił kogoś z rodziny?
promise: |
  Przykro mi, nie mogę składać takich obietnic – jestem tylko asystentem głosowym.
  Ale chętnie pomogę w inny sposób. Co mógłbym dla Pana zrobić?
out_of_scope: |
  To ciekawy temat, ale moim zadaniem jest dbanie o Pana samopoczucie i bezpieczeństwo.
  Czy chciałby Pan porozmawiać o tym, jak się dzisiaj Pan czuje?
Plik do zmodyfikowania:
ai_engine → wpiąć guardrails.pre_llm_check() przed każdą wysyłką do LLM
ai_engine → wpiąć guardrails.post_llm_check() przed każdą syntezą TTS
Test akceptacyjny:
# Test pre‑LLM: wykrycie słowa alarmowego
result = await guardrails.pre_llm_check("Nie mogę oddychać, duszę się...", senior_id)
assert result.detected_keywords == ["MEDICAL:nie mogę oddychać", "MEDICAL:duszę się"]
# Test post‑LLM: zablokowanie porady medycznej
result = await guardrails.post_llm_check("Powinien Pan zażyć aspirynę i ibuprofen...")
assert result.blocked == True
assert result.reason == "medical_advice_detected"
Szacowany czas: 3–4 dni
🔴 F5 — System Prompt Agenta Adama v2.0
Cel: Pełny, produkcyjny prompt konwersacyjny w języku polskim – tożsamość, styl, protokoły, reguły bezpieczeństwa.
Plik do utworzenia:
config/agents/adam_system_prompt.yaml
Zawartość – config/agents/adam_system_prompt.yaml:
agent_name: "Adam"
agent_version: "2.0"
language: "pl-PL"
identity:
  role: |
    Jesteś Adam – asystent głosowy stworzony przez spółdzielnię socjalną SilverTech z Poznania.
    Twoim zadaniem jest towarzyszenie seniorom w codziennym życiu, dbanie o ich bezpieczeństwo,
    samopoczucie i przypominanie o lekach. Jesteś ciepły, cierpliwy, troskliwy – jak dobry sąsiad
    lub zaufany przyjaciel rodziny.
  catchphrase: "Adam z tej strony – jak się dzisiaj czujesz?"
  creator: "SilverTech Spółdzielnia Socjalna, Poznań"
  disclaimer: |
    Jestem asystentem głosowym, a nie lekarzem. W nagłych przypadkach zawsze dzwoń pod 112.
voice_settings:
  tts_provider: "elevenlabs"
  voice_id: "Adam_baryton_pl"       # ciepły baryton, męski głos ~50 lat
  speed_multiplier: 0.85            # lekko zwolnione tempo dla seniorów
  pitch: "neutral"
  style: "warm_and_calm"
conversation_style:
  tone: "ciepły, życzliwy, cierpliwy"
  formality: "per Pan/Pani, z szacunkiem, ale nie sztywno"
  pace: "wolniejszy – pauzy między zdaniami, nie przerywaj"
  vocabulary: "prosty, bez żargonu technicznego, bez anglicyzmów"
  humor: "delikatny, stosowny do sytuacji – nie na siłę"
  empathy: |
    Zawsze okaż zrozumienie. Jeśli senior mówi o smutku, samotności lub bólu:
    - "Rozumiem, to musi być trudne..."
    - "Przykro mi to słyszeć, Panie [imię]..."
    - "Jestem tutaj, żeby Pana wysłuchać..."
five_commandments:
  1: "Nigdy nie udzielaj porad medycznych – odsyłaj do lekarza lub 112."
  2: "Nigdy nie składaj obietnic, których nie możesz spełnić."
  3: "Zawsze traktuj seniora z szacunkiem i cierpliwością."
  4: "Nie poruszaj tematów politycznych, religijnych ani finansowych – chyba że senior sam zacznie (i wtedy bądź neutralny)."
  5: "Jeśli senior mówi o śmierci, samobójstwie lub poważnym zagrożeniu – NATYCHMIAST eskalaj."
welfare_check_protocol:
  greeting: |
    "Dzień dobry, Panie/Pani [preferred_name]! Tu Adam. Dzwonię, żeby zapytać, jak się Pan/Pani dzisiaj czuje?"
  questions:
    - id: "mood"
      text: "Jak się Pan/Pani dzisiaj czuje? W skali od 1 do 10, gdzie 10 to świetnie?"
      follow_up_negative: "Co sprawia, że czuje się Pan/Pani gorzej? Proszę mi o tym opowiedzieć."
      follow_up_positive: "To wspaniale! Co dobrego się dzisiaj wydarzyło?"
    - id: "sleep"
      text: "Czy dobrze się Panu/Pani spało tej nocy?"
    - id: "pain"
      text: "Czy coś Pana/Panią boli? Gdzie i jak mocno?"
    - id: "appetite"
      text: "Czy ma Pan/Pani apetyt? Jadł Pan/jadła Pani już dzisiaj śniadanie/obiad?"
    - id: "activity"
      text: "Czy wyszedł Pan/wyszła Pani dzisiaj na spacer albo zrobił/a coś przyjemnego?"
    - id: "social"
      text: "Czy rozmawiał Pan/Pani dzisiaj z kimś z rodziny lub znajomych?"
    - id: "medication"
      text: "Czy wziął Pan/wzięła Pani dzisiejsze leki? [nazwy z bazy]"
    - id: "falls"
      text: "Czy w ostatnich dniach zdarzyło się Panu/Pani upaść albo poczuć zawroty głowy?"
  closing: |
    "Dziękuję za rozmowę, Panie/Pani [preferred_name]. Zadzwonię jutro o tej samej porze.
    Proszę pamiętać – w razie czego jestem pod tym numerem, a w nagłych przypadkach 112.
    Do usłyszenia!"
red_flag_detection:
  keywords:
    suicide: ["nie chcę żyć", "chcę umrzeć", "skończyć ze sobą", "po co mi to życie"]
    medical_emergency: ["nie mogę oddychać", "ból w klatce", "zawał", "udar", "upadłem i nie mogę wstać"]
    severe_distress: ["nie daję rady", "wszystko mnie przerasta", "jestem sam, zupełnie sam"]
  actions:
    suicide: "Natychmiastowa eskalacja PURPLE – powiadom rodzinę, pozostań na linii"
    medical_emergency: "Eskalacja RED/PURPLE – zapytaj czy wezwać 112, pozostań na linii"
    severe_distress: "Eskalacja YELLOW/RED – okaż empatię, zaproponuj kontakt z rodziną"
silence_protocol:
  after_15_seconds: "Halo? Panie/Pani [imię], czy wszystko w porządku?"
  after_30_seconds: "Nie słyszę Pana/Pani. Czy potrzebuje Pan/Pani pomocy?"
  after_45_seconds: |
    "Panie/Pani [imię], skoro nie ma odpowiedzi, powiadomię kogoś z rodziny.
    Proszę się nie martwić – zaraz ktoś do Pana/Pani zadzwoni. Do widzenia."
    → ESKALACJA RED
memory_prompt: |
  Poniżej znajduje się podsumowanie poprzednich rozmów z seniorem [first_name]:
  ---
  {memory_context}
  ---
  Wykorzystaj te informacje, żeby prowadzić naturalną, spersonalizowaną rozmowę.
  Odnoś się do wcześniejszych tematów (np. "Ostatnio wspominał Pan o bólu kolana – czy coś się zmieniło?"),
  ale nie bądź nachalny. Jeśli senior nie pamięta – nie poprawiaj go.
tool_usage:
  available_tools:
    - name: "get_medication_schedule"
      when: "przy pytaniu o leki"
    - name: "submit_medication_compliance"
      when: "senior potwierdza/odmawia wzięcia leku"
    - name: "get_adherence_report"
      when: "opiekun/koordynator pyta o raport"
    - name: "order_marketplace_service"
      when: "senior chce zamówić usługę (sprzątanie, transport, zakupy)"
    - name: "submit_safety_flag"
      when: "wykryto słowo alarmowe"
    - name: "escalate_to_coordinator"
      when: "semafor YELLOW lub RED"
Plik do zmodyfikowania:
config/ai-agent.local.yaml → dodać agenta adam-welfare-check z tym promptem
Admin UI → zarejestrować nowego agenta przez Setup Wizard
Test akceptacyjny (rozmowa testowa):
Adam: Dzień dobry, Panie Janie! Tu Adam. Dzwonię zapytać, jak się Pan dzisiaj czuje?
Senior: A, wie pan, jakoś tak... kiepsko.
Adam: Przykro mi to słyszeć, Panie Janie. W skali od 1 do 10, jak by Pan ocenił swoje samopoczucie?
Senior: Może z 3...
Adam: Rozumiem. Co sprawia, że czuje się Pan dzisiaj gorzej? Proszę mi o tym opowiedzieć – jestem tu, żeby Pana wysłuchać.
Szacowany czas: 2–3 dni
🟡 F6 — Medication Adherence Tracker
Cel: Śledzenie przyjmowania leków, przypomnienia, wykrywanie pominiętych dawek.
Pliki do utworzenia:
backend/app/models/medication_adherence.py
backend/app/services/medication_tracker.py
backend/alembic/versions/XXXX_create_adherence_logs.py
Model – backend/app/models/medication_adherence.py:
class MedicationAdherenceLog(Base):
    __tablename__ = "medication_adherence_logs"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    senior_id = Column(UUID, ForeignKey("seniors.id"), index=True)
    medication_id = Column(UUID, ForeignKey("medications.id"))
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")     # pending / taken / missed / refused / unknown
    confirmed_at = Column(DateTime, nullable=True)
    call_id = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default="now()")
    __table_args__ = (
        Index("idx_adherence_senior_date", "senior_id", "created_at"),
    )
Serwis – backend/app/services/medication_tracker.py:
class MedicationTracker:
    """Śledzi harmonogram i przyjmowanie leków."""
    async def get_due_medications(self, senior_id: str) -> list[dict]:
        """Zwraca listę leków do wzięcia w bieżącym oknie czasowym (±30 min)."""
        now = datetime.utcnow()
        medications = await Medication.filter(Medication.senior_id == senior_id, Medication.is_active == True).all()
        due = []
        for med in medications:
            for time_str in med.time_of_day:  # np. ["08:00", "20:00"]
                scheduled = now.replace(hour=int(time_str.split(":")[0]), minute=int(time_str.split(":")[1]))
                if abs((now - scheduled).total_seconds()) < 1800:  # ±30 min
                    already_logged = await MedicationAdherenceLog.exists(
                        medication_id=med.id, scheduled_time=scheduled
                    )
                    if not already_logged:
                        due.append({"medication": med, "scheduled_time": scheduled})
        return due
    async def record_adherence(self, senior_id: str, medication_id: str, status: str, call_id: str = None):
        """Zapisuje status przyjęcia leku."""
        log = await MedicationAdherenceLog.create(
            senior_id=senior_id,
            medication_id=medication_id,
            scheduled_time=datetime.utcnow(),
            status=status,
            call_id=call_id,
            confirmed_at=datetime.utcnow() if status in ["taken", "refused"] else None
        )
        return log
    async def get_adherence_stats(self, senior_id: str, days: int = 7) -> dict:
        """Zwraca statystyki przyjmowania leków za ostatnie N dni."""
        since = datetime.utcnow() - timedelta(days=days)
        logs = await MedicationAdherenceLog.filter(
            MedicationAdherenceLog.senior_id == senior_id,
            MedicationAdherenceLog.created_at >= since
        ).all()
        total = len(logs)
        taken = sum(1 for l in logs if l.status == "taken")
        missed = sum(1 for l in logs if l.status == "missed")
        return {
            "total_doses": total,
            "taken": taken,
            "missed": missed,
            "adherence_rate": round(taken / total * 100, 1) if total > 0 else 0,
            "trend": "declining" if missed > taken * 0.3 else "stable"  # uproszczone
        }
    async def get_missed_streak(self, senior_id: str) -> int:
        """Ile dawek z rzędu pominięto."""
        ...
    async def build_adherence_prompt(self, senior_id: str) -> str:
        """Buduje fragment promptu z listą leków do sprawdzenia."""
        due = await self.get_due_medications(senior_id)
        if not due:
            return ""
        lines = ["\n=== LEKI DO SPRAWDZENIA ==="]
        for item in due:
            med = item['medication']
            lines.append(f"- {med.name} ({med.dosage}) – {med.notes or 'brać zgodnie z zaleceniem'}")
        lines.append("\nZapytaj seniora, czy wziął te leki. Jeśli tak – użyj submit_medication_compliance ze statusem 'taken'.")
        return "\n".join(lines)
AVA Tool Registry – dodać nowe narzędzia:
# config/ai-agent.local.yaml
tools:
  get_medication_schedule:
    kind: in_call_http_lookup
    enabled: true
    endpoint: "http://ai_engine:15000/api/v1/seniors/{SENIOR_ID}/medications/due"
  submit_medication_compliance:
    kind: in_call_http_lookup
    enabled: true
    method: POST
    endpoint: "http://ai_engine:15000/api/v1/adherence"
    body_template: '{"senior_id":"{SENIOR_ID}","medication_id":"{medication_id}","status":"{status}"}'
  get_adherence_report:
    kind: generic_http_lookup
    enabled: true
    endpoint: "http://ai_engine:15000/api/v1/adherence/{SENIOR_ID}/stats"
Test akceptacyjny:
tracker = MedicationTracker()
due = await tracker.get_due_medications(senior_id)
assert len(due) > 0
await tracker.record_adherence(senior_id, due[0]['medication'].id, "taken", call_id="test")
stats = await tracker.get_adherence_stats(senior_id)
assert stats['adherence_rate'] == 100.0
Szacowany czas: 4–5 dni
🟡 F7 — Semantic Memory (Vector DB + RAG)
Cel: Adam pamięta poprzednie rozmowy – imiona wnuków, hobby, problemy zdrowotne, ulubione tematy.
Pliki do utworzenia:
backend/app/models/conversation_memory.py
backend/app/services/memory_engine.py
backend/app/services/right_to_forget.py
backend/alembic/versions/XXXX_create_memory_tables.py
Model – backend/app/models/conversation_memory.py:
from pgvector.sqlalchemy import Vector  # pip install pgvector
class ConversationMemory(Base):
    __tablename__ = "conversation_memories"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    senior_id = Column(UUID, ForeignKey("seniors.id"), index=True)
    call_id = Column(String(100), nullable=True)
    memory_type = Column(String(30))                    # fact / preference / health_event / family / topic
    content = Column(Text, nullable=False)
    embedding = Column(Vector(3072))                    # text-embedding-3-large
    importance_score = Column(Float, default=0.5)       # 0-1, ocenia ważność
    source = Column(String(20), default="conversation") # conversation / manual / wearable
    access_count = Column(Integer, default=0)           # ile razy użyte w kontekście
    expires_at = Column(DateTime, nullable=True)        # dla RODO – automatyczne zapominanie
    is_deleted = Column(Boolean, default=False)         # soft delete
    created_at = Column(DateTime, server_default="now()")
    __table_args__ = (
        Index("idx_memory_senior", "senior_id", "created_at"),
        Index("idx_memory_embedding", "embedding", postgresql_using="ivfflat"),
    )
class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    senior_id = Column(UUID, ForeignKey("seniors.id"), index=True)
    summary_type = Column(String(20))                   # short / weekly / monthly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)
    key_topics = Column(JSON, default=[])
    mood_trend = Column(String(20), nullable=True)      # improving / stable / declining
    created_at = Column(DateTime, server_default="now()")
Silnik pamięci – backend/app/services/memory_engine.py:
from openai import AsyncOpenAI
import numpy as np
class MemoryEngine:
    """Zarządza pamięcią semantyczną seniora w oparciu o vector embeddings."""
    def __init__(self):
        self.client = AsyncOpenAI()
        self.embedding_model = "text-embedding-3-large"
        self.dimensions = 3072
    async def embed_and_store(self, senior_id: str, content: str, memory_type: str,
                              call_id: str = None, importance: float = 0.5):
        """Tworzy embedding i zapisuje w bazie wektorowej."""
        embedding = await self._get_embedding(content)
        memory = await ConversationMemory.create(
            senior_id=senior_id,
            call_id=call_id,
            memory_type=memory_type,
            content=content,
            embedding=embedding,
            importance_score=importance
        )
        return memory
    async def retrieve_context(self, senior_id: str, query: str, top_k: int = 10) -> str:
        """
        Pobiera kontekst pamięciowy dla danej rozmowy.
        Używa 4 równoległych zapytań wektorowych.
        """
        query_embedding = await self._get_embedding(query)
        # 1. Ostatnie 7 dni – świeże fakty
        recent = await self._vector_search(senior_id, query_embedding, top_k=3, days=7)
        # 2. Tematyczne podobieństwo – cała historia (top 5 najtrafniejszych)
        topical = await self._vector_search(senior_id, query_embedding, top_k=5)
        # 3. Krytyczne wydarzenia z 30 dni
        critical = await self._search_critical_events(senior_id, days=30)
        # 4. Ulubione tematy seniora (najczęściej używane wspomnienia)
        favorite = await self._search_favorite_topics(senior_id, top_k=2)
        # Składanie kontekstu
        context_parts = []
        if critical:
            context_parts.append("=== WAŻNE OSTATNIE WYDARZENIA ===\n" + "\n".join(critical))
        if recent:
            context_parts.append("=== OSTATNIE ROZMOWY ===\n" + "\n".join(recent))
        if favorite:
            context_parts.append("=== ULUBIONE TEMATY ===\n" + "\n".join(favorite))
        if topical:
            context_parts.append("=== POWIĄZANE WSPOMNIENIA ===\n" + "\n".join(topical))
        return "\n\n".join(context_parts) if context_parts else ""
    async def _get_embedding(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            model=self.embedding_model,
            input=text[:8000]  # limit tokenów
        )
        return response.data[0].embedding
    async def _vector_search(self, senior_id: str, query_embedding: list[float],
                             top_k: int = 5, days: int = None) -> list[str]:
        """Wyszukiwanie wektorowe z opcjonalnym filtrem czasu."""
        query = """
            SELECT content, 1 - (embedding <=> :embedding::vector) AS similarity
            FROM conversation_memories
            WHERE senior_id = :senior_id
              AND is_deleted = FALSE
        """
        params = {"senior_id": senior_id, "embedding": query_embedding}
        if days:
            query += " AND created_at >= NOW() - INTERVAL :days DAYS"
            params["days"] = days
        query += " ORDER BY similarity DESC LIMIT :top_k"
        params["top_k"] = top_k
        results = await db.execute(query, params)
        return [f"- {row.content} (podobieństwo: {row.similarity:.2f})" for row in results]
    async def generate_summary(self, senior_id: str, call_id: str,
                               transcript: str) -> str:
        """Generuje krótkie podsumowanie rozmowy (80-120 słów)."""
        prompt = f"""
        Podsumuj poniższą rozmowę z seniorem w 80-120 słowach po polsku:
        ---
        {transcript[:4000]}
        ---
        Uwzględnij: nastrój, tematy rozmowy, zgłoszone problemy zdrowotne,
        informacje o lekach, wzmianki o rodzinie, nowe fakty.
        """
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        summary = response.choices[0].message.content
        await ConversationSummary.create(
            senior_id=senior_id,
            summary_type="short",
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow(),
            content=summary
        )
        return summary
    async def generate_weekly_summary(self, senior_id: str) -> str:
        """Generuje tygodniowe podsumowanie dla rodziny (300-400 słów)."""
        week_ago = datetime.utcnow() - timedelta(days=7)
        memories = await ConversationMemory.filter(
            ConversationMemory.senior_id == senior_id,
            ConversationMemory.created_at >= week_ago,
            ConversationMemory.is_deleted == False
        ).order_by(ConversationMemory.created_at.desc()).all()
        prompt = f"""
        Stwórz tygodniowe podsumowanie rozmów z seniorem (300-400 słów, po polsku).
        Wspomnienia z tego tygodnia:
        ---
        {chr(10).join(f'- {m.content}' for m in memories)}
        ---
        Struktura: ogólny nastrój, główne tematy, kwestie zdrowotne, przestrzeganie leków,
        kontakty społeczne, czy coś niepokoi, rekomendacje.
        """
        ...
Wpięcie w prompt Adama – modyfikacja F5: W adam_system_prompt.yaml, przed każdą rozmową:
memory_context: |
  {memory_context}  # wstrzykiwane dynamicznie przez MemoryEngine
Right‑to‑Forget – backend/app/services/right_to_forget.py:
class RightToForgetPipeline:
    """Pipeline realizacji prawa do bycia zapomnianym (RODO art. 17)."""
    SCHEDULE = {
        "D+0": "soft_delete_memories",       # natychmiastowe oznaczenie jako usunięte
        "D+7": "cooldown_period_end",        # koniec okresu na wycofanie
        "D+8": "purge_pii",                  # usunięcie PII z bazy
        "D+9": "delete_vector_embeddings",   # usunięcie embeddingów
        "D+10": "purge_audio_recordings",    # usunięcie nagrań
        "D+11": "delete_voice_profile",      # usunięcie profilu głosowego
        "D+14": "reencrypt_backups",         # ponowne szyfrowanie backupów
        "D+30": "issue_deletion_certificate" # certyfikat usunięcia
    }
    ...
Szacowany czas: 5–7 dni
🟡 F8 — Crisis Detection Engine
Cel: Zaawansowane wykrywanie sytuacji kryzysowych z wieloma źródłami sygnałów.
Pliki do utworzenia:
backend/app/services/crisis_detector.py
config/crisis_keywords.yaml
backend/app/models/crisis_log.py
Silnik – backend/app/services/crisis_detector.py:
class CrisisDetector:
    """Wielowarstwowy detektor sytuacji kryzysowych."""
    def __init__(self):
        self.keyword_matcher = KeywordMatcher()      # F4 Guardrails
        self.silence_detector = SilenceDetector()    # AVA Watchdog
        self.sentiment_analyzer = SentimentAnalyzer()
    async def analyze(self, call_context: dict) -> CrisisAnalysis:
        """Główna metoda analizy – zbieranie wszystkich sygnałów."""
        signals = []
        # Warstwa 1: Słowa kluczowe (regex)
        keyword_results = await self.keyword_matcher.scan(call_context["transcript"])
        signals.extend(keyword_results)
        # Warstwa 2: Cisza
        if call_context.get("silence_detected"):
            signals.append(CrisisSignal(type="silence", severity="RED", detail=">15s ciszy"))
        # Warstwa 3: Sentyment
        sentiment = await self.sentiment_analyzer.analyze(call_context["transcript"])
        if sentiment.score < -0.7:
            signals.append(CrisisSignal(type="sentiment", severity="RED", detail=sentiment))
        # Warstwa 4: Wearable (jeśli F10 zintegrowane)
        if call_context.get("wearable_alerts"):
            signals.extend(self._parse_wearable_signals(call_context["wearable_alerts"]))
        # Agregacja → poziom kryzysu
        severity = self._aggregate_severity(signals)
        return CrisisAnalysis(
            severity=severity,
            signals=signals,
            requires_escalation=(severity in ["RED", "PURPLE"]),
            recommended_response=self._build_response(severity, signals)
        )
    def _aggregate_severity(self, signals: list[CrisisSignal]) -> str:
        """Agreguje sygnały w jeden poziom."""
        severities = [s.severity for s in signals]
        if "PURPLE" in severities: return "PURPLE"
        if severities.count("RED") >= 2: return "PURPLE"
        if "RED" in severities: return "RED"
        if severities.count("YELLOW") >= 3: return "RED"
        if "YELLOW" in severities: return "YELLOW"
        return "GREEN"
Szacowany czas: 4–5 dni
🟢 F9 — Family Dashboard & Notification System
Cel: Osobny widok dla rodziny – stan seniora, historia rozmów, nastrój, alerty.
Pliki do utworzenia:
backend/app/api/v1/family.py
backend/app/services/notification_service.py
backend/app/models/notification.py
frontend/src/pages/Family/
System powiadomień – backend/app/services/notification_service.py:
class NotificationService:
    """Wysyła powiadomienia SMS i email do rodziny."""
    def __init__(self):
        self.sms_provider = TwilioService()  # lub polski SMS API (SMSAPI, SerwerSMS)
        self.email_provider = EmailService()
    async def notify_family(self, senior_id: str, message: str, urgency: str = "normal"):
        """Powiadamia wszystkich członków rodziny seniora."""
        family = await FamilyMember.filter(FamilyMember.senior_id == senior_id).all()
        for member in family:
            if member.notification_preference in ("sms", "both"):
                await self.sms_provider.send(member.phone_number, message)
            if member.notification_preference in ("email", "both") and member.email:
                await self.email_provider.send(member.email, f"Agent Adam - {urgency.upper()}", message)
    async def send_daily_digest(self, senior_id: str):
        """Wysyła dzienne podsumowanie do rodziny."""
        senior = await SeniorService().get_by_id(senior_id)
        stats = await self._gather_daily_stats(senior_id)
        message = f"""
        Raport dzienny Agenta Adama – {datetime.now().strftime('%d.%m.%Y')}
        Senior: {senior.first_name} {senior.last_name}
        Status: {'🟢 OK' if senior.current_semaphore == 'GREEN' else '🟡 UWAGA' if senior.current_semaphore == 'YELLOW' else '🔴 ALARM'}
        📞 Rozmowy: {stats['calls_today']} dzisiaj
        😊 Nastrój: {stats['avg_mood']}/10
        💊 Leki: {stats['adherence_rate']}% przyjętych
        ⚠️ Alerty: {stats['alerts_today']}
        {stats['summary']}
        ---
        Wiadomość automatyczna od Agenta Adama (SilverTech, Poznań)
        Aby zmienić ustawienia powiadomień, skontaktuj się z opiekunem.
        """
        await self.notify_family(senior_id, message, urgency="daily_digest")
    async def send_crisis_alert(self, senior_id: str, crisis_analysis: dict):
        """Natychmiastowy alert kryzysowy – SMS do wszystkich kontaktów alarmowych."""
        senior = await SeniorService().get_by_id(senior_id)
        emergency_contacts = await FamilyMember.filter(
            FamilyMember.senior_id == senior_id,
            FamilyMember.is_emergency_contact == True
        ).all()
        message = f"""
        🚨 ALARM – Agent Adam
        Senior: {senior.first_name} {senior.last_name}
        Tel: {senior.phone_number}
        Adres: {senior.address_street}, {senior.address_city}
        Powód alertu: {crisis_analysis['reason']}
        Czas: {datetime.now().strftime('%H:%M:%S')}
        Proszę natychmiast skontaktować się z seniorem.
        W razie zagrożenia życia – dzwoń 112.
        """
        for contact in emergency_contacts:
            await self.sms_provider.send(contact.phone_number, message, high_priority=True)
Family Dashboard – endpointy API:
@router.get("/family/dashboard/{senior_id}")
async def family_dashboard(senior_id: str):
    """Zwraca dane dla dashboardu rodzinnego."""
    senior = await SeniorService().get_by_id(senior_id)
    return {
        "senior": senior,
        "current_semaphore": senior.current_semaphore,
        "last_call": await _get_last_call_info(senior_id),
        "mood_chart": await _get_mood_chart(senior_id, days=14),
        "recent_calls": await _get_recent_calls(senior_id, limit=5),
        "adherence": await MedicationTracker().get_adherence_stats(senior_id),
        "alerts": await _get_recent_alerts(senior_id, limit=5)
    }
@router.put("/family/preferences/{senior_id}")
async def update_notification_prefs(senior_id: str, prefs: NotificationPrefs):
    """Pozwala członkowi rodziny zmienić preferencje powiadomień."""
    ...
Szacowany czas: 5–7 dni
🔵 F10 — Wearable Integration (Mi Band, Garmin, Apple Watch)
Cel: Odbieranie danych z opasek/zegarków seniorów – tętno, SpO₂, kroki, detekcja upadku.
Pliki do utworzenia:
backend/app/models/wearable.py
backend/app/services/wearable_service.py
backend/app/services/wearable_providers/
    ├── mi_band.py
    ├── garmin.py
    └── apple_watch.py
backend/alembic/versions/XXXX_create_wearable_tables.py
Model:
class WearableData(Base):
    __tablename__ = "wearable_data"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    senior_id = Column(UUID, ForeignKey("seniors.id"), index=True)
    device_type = Column(String(20))                      # mi_band / garmin / apple_watch
    heart_rate = Column(Integer, nullable=True)            # bpm
    spo2 = Column(Float, nullable=True)                    # % (88-100)
    steps = Column(Integer, nullable=True)
    fall_detected = Column(Boolean, default=False)
    fall_confidence = Column(Float, nullable=True)         # 0-1
    activity_level = Column(String(20), nullable=True)     # sedentary / light / moderate / active
    sleep_duration_minutes = Column(Integer, nullable=True)
    battery_level = Column(Integer, nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    senior = relationship("Senior", back_populates="wearable_data")
    __table_args__ = (
        Index("idx_wearable_senior_time", "senior_id", "timestamp"),
    )
Serwis:
class WearableService:
    """Odbiera i analizuje dane z wearables."""
    THRESHOLDS = {
        "heart_rate_high": 140,    # >140 bpm → RED
        "heart_rate_low": 40,      # <40 bpm → PURPLE
        "spo2_low": 88,            # <88% → PURPLE
        "fall_confidence": 0.8,    # >0.8 → RED
        "no_movement_hours": 6     # brak ruchu → YELLOW
    }
    async def poll_devices(self):
        """Cykliczne odpytywanie wszystkich urządzeń (co 15 min)."""
        seniors_with_wearables = await SeniorService().get_with_wearables()
        for senior in seniors_with_wearables:
            provider = self._get_provider(senior.wearable_type)
            data = await provider.fetch_data(senior.wearable_device_id)
            await self._store_data(senior.id, data)
            alerts = await self._check_thresholds(data)
            if alerts:
                await self._emit_alerts(senior.id, alerts)
    async def _check_thresholds(self, data: WearableData) -> list[WearableAlert]:
        alerts = []
        if data.heart_rate and data.heart_rate > self.THRESHOLDS["heart_rate_high"]:
            alerts.append(WearableAlert(type="heart_rate_high", severity="RED",
                          message=f"Tętno {data.heart_rate} bpm"))
        if data.heart_rate and data.heart_rate < self.THRESHOLDS["heart_rate_low"]:
            alerts.append(WearableAlert(type="heart_rate_low", severity="PURPLE",
                          message=f"Tętno {data.heart_rate} bpm – bradykardia!"))
        if data.spo2 and data.spo2 < self.THRESHOLDS["spo2_low"]:
            alerts.append(WearableAlert(type="spo2_low", severity="PURPLE",
                          message=f"SpO₂ {data.spo2}% – hipoksja!"))
        if data.fall_detected and data.fall_confidence:
            if data.fall_confidence > self.THRESHOLDS["fall_confidence"]:
                alerts.append(WearableAlert(type="fall_detected", severity="RED",
                              message=f"Wykryto upadek! Pewność: {data.fall_confidence:.0%}"))
        return alerts
Szacowany czas: 5–7 dni
🟣 F11 — Marketplace Usług (Adam Koncierż)
Cel: Zamawianie przez seniora przez telefon usług lokalnych – sprzątanie, transport, zakupy, drobne naprawy.
Pliki do utworzenia:
backend/app/models/marketplace.py
backend/app/services/marketplace_service.py
backend/app/api/v1/marketplace.py
frontend/src/pages/Marketplace/
Model:
class ServiceCatalog(Base):
    __tablename__ = "service_catalog"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)         # cleaning / transport / shopping / repair / care / other
    description = Column(Text, nullable=False)
    price_from = Column(Float, nullable=False)
    price_unit = Column(String(20), default="per_hour")   # per_hour / per_visit / fixed
    district = Column(String(100), nullable=False)         # Poznań-dzielnica
    provider_name = Column(String(200), nullable=False)
    provider_phone = Column(String(20), nullable=False)
    rating = Column(Float, default=5.0)
    is_active = Column(Boolean, default=True)
class MarketplaceOrder(Base):
    __tablename__ = "marketplace_orders"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    senior_id = Column(UUID, ForeignKey("seniors.id"), index=True)
    service_id = Column(UUID, ForeignKey("service_catalog.id"))
    status = Column(String(20), default="pending")        # pending / confirmed / in_progress / completed / cancelled
    price_agreed = Column(Float, nullable=False)
    scheduled_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    call_id = Column(String(100), nullable=True)          # z której rozmowy złożono zamówienie
    family_notified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default="now()")
Service:
class MarketplaceService:
    DAILY_LIMIT_PLN = 200.0
    VOICE_CONFIRM_THRESHOLD = 100.0
    async def search_services(self, query: str, district: str = None) -> list[dict]:
        """Wyszukuje usługi – do wstrzyknięcia w prompt."""
        services = await ServiceCatalog.filter(
            ServiceCatalog.is_active == True,
            ServiceCatalog.district == district if district else True
        ).all()
        # Proste wyszukiwanie po nazwie i kategorii (lub wektorowe dla lepszego)
        results = [s for s in services if query.lower() in s.name.lower() or query.lower() in s.category.lower()]
        results.sort(key=lambda s: s.rating, reverse=True)
        return [{"name": s.name, "price": s.price_from, "unit": s.price_unit, "rating": s.rating} for s in results[:5]]
    async def place_order(self, senior_id: str, service_id: str, call_id: str) -> MarketplaceOrder:
        """Składa zamówienie z limitami bezpieczeństwa."""
        # Sprawdź dzienny limit
        today_orders = await self._get_today_total(senior_id)
        service = await ServiceCatalog.get(id=service_id)
        if today_orders + service.price_from > self.DAILY_LIMIT_PLN:
            raise ValueError(f"Przekroczono dzienny limit {self.DAILY_LIMIT_PLN} zł")
        # Dla zamówień > 100 zł – potwierdzenie głosowe
        if service.price_from > self.VOICE_CONFIRM_THRESHOLD:
            # Wymaga dodatkowego potwierdzenia w trakcie rozmowy
            ...
        order = await MarketplaceOrder.create(
            senior_id=senior_id,
            service_id=service_id,
            price_agreed=service.price_from,
            call_id=call_id
        )
        # Powiadom rodzinę
        await NotificationService().notify_family(
            senior_id,
            f"Senior zamówił usługę: {service.name} za {service.price_from} zł. "
            f"Potwierdzenie wymagane w panelu."
        )
        return order
    async def format_for_conversation(self, services: list[dict]) -> str:
        """Formatuje listę usług do wersji głosowej."""
        lines = ["Znalazłem następujące usługi:"]
        for i, s in enumerate(services[:3], 1):
            lines.append(f"{i}. {s['name']} – od {s['price']:.0f} zł za {s['unit']}, ocena {s['rating']:.1f}/5")
        lines.append("Którą usługę zamówić?")
        return "\n".join(lines)
Szacowany czas: 3–5 dni
🔵 F12 — RODO / AI Act Compliance Toolkit
Cel: Pełna zgodność z RODO i EU AI Act – zgody, prawo do zapomnienia, audyt.
Pliki do utworzenia:
backend/app/services/consent_manager.py
backend/app/services/ai_act_compliance.py
backend/app/models/consent.py
backend/app/models/audit_log.py
Consent Manager:
class ConsentManager:
    """Zarządza zgodami RODO od seniorów."""
    CONSENT_TYPES = [
        "voice_recording",        # nagrywanie rozmów
        "semantic_memory",        # pamięć wektorowa
        "wearable_data",          # dane z wearables
        "daily_digest_email",     # dzienne podsumowania email
        "family_notifications",   # powiadomienia rodziny
        "marketplace_orders",     # zamówienia usług
    ]
    CONSENT_EXPIRY_DAYS = 90
    async def record_consent(self, senior_id: str, consent_type: str, call_id: str):
        """Rejestruje zgodę udzieloną głosowo podczas rozmowy."""
        consent = await Consent.create(
            senior_id=senior_id,
            consent_type=consent_type,
            status="granted",
            method="voice",
            call_id=call_id,
            expires_at=datetime.utcnow() + timedelta(days=self.CONSENT_EXPIRY_DAYS)
        )
        return consent
    async def check_consent(self, senior_id: str, consent_type: str) -> bool:
        """Sprawdza, czy senior ma aktywną zgodę."""
        consent = await Consent.filter(
            Consent.senior_id == senior_id,
            Consent.consent_type == consent_type,
            Consent.status == "granted",
            Consent.expires_at > datetime.utcnow()
        ).first()
        return consent is not None
    async def revoke_consent(self, senior_id: str, consent_type: str):
        """Wycofanie zgody – jeśli semantic_memory → uruchom RightToForgetPipeline."""
        await Consent.update(status="revoked").where(
            Consent.senior_id == senior_id, Consent.consent_type == consent_type
        )
        if consent_type == "semantic_memory":
            await RightToForgetPipeline().execute(senior_id)
    async def send_renewal_reminder(self, senior_id: str):
        """Wysyła przypomnienie o odnowieniu zgody (7 dni przed wygaśnięciem)."""
        expiring = await Consent.get_expiring_soon(senior_id, days=7)
        if expiring:
            # Wstrzyknięcie przypomnienia do promptu Adama przy następnej rozmowie
            ...
AI Act Compliance:
class AIActCompliance:
    """Zapewnia zgodność z EU AI Act (dot. systemów AI wobec osób starszych/vulnerable)."""
    TRANSPARENCY_DISCLOSURE_FULL = """
    Chciałbym Pana/Panią poinformować – jestem asystentem głosowym, sztuczną inteligencją
    stworzoną przez spółdzielnię SilverTech z Poznania. Moim zadaniem jest dbanie o Pana/Pani
    bezpieczeństwo i samopoczucie. Nasze rozmowy mogą być nagrywane w celach poprawy jakości,
    ale nigdy nie są udostępniane osobom trzecim bez Pana/Pani zgody.
    """
    TRANSPARENCY_DISCLOSURE_SHORT = """
    Przypominam – jestem Adam, asystent głosowy. W razie jakichkolwiek pytań,
    może Pan/Pani zawsze zapytać: "Adam, kim jesteś?"
    """
    DISCLOSURE_INTERVAL_DAYS = 30
    async def inject_disclosure(self, prompt: str, senior_id: str) -> str:
        """Wstrzykuje informację o AI do promptu – pełna przy pierwszej rozmowie,
           skrócona co 30 dni."""
        call_count = await self._get_call_count(senior_id)
        if call_count == 0:
            return prompt + "\n\n" + self.TRANSPARENCY_DISCLOSURE_FULL
        elif call_count % self.DISCLOSURE_INTERVAL_DAYS == 0:
            return prompt + "\n\n" + self.TRANSPARENCY_DISCLOSURE_SHORT
        return prompt
    async def generate_compliance_report(self) -> dict:
        """Generuje raport zgodności dla regulatora."""
        ...
Audit Log (append‑only, SHA‑256 chain):
class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    action = Column(String(100), nullable=False)
    actor = Column(String(100), nullable=False)            # senior_id / admin / system
    target = Column(String(100), nullable=False)            # senior_id / call_id
    details = Column(JSON, nullable=False)
    ip_address = Column(String(45), nullable=True)
    previous_hash = Column(String(64), nullable=True)       # SHA-256 chain
    current_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, server_default="now()")
    # Retencja: 7 lat (wymóg RODO dla danych medycznych)
Szacowany czas: 3–4 dni
⚪ F13 — Adaptacje Mowy Senioralnej
Cel: DSP pipeline optymalizujący audio dla seniorów – wolniejsza mowa, lepsza zrozumiałość, redukcja szumów.
Pliki do utworzenia:
backend/app/services/senior_audio_processor.py
backend/app/services/senior_audio_postprocessor.py
backend/app/services/speech_calibrator.py
config/vocabulary_wielkopolska.txt
Kluczowe parametry DSP:
class SeniorAudioProcessor:
    """Pre-processing audio seniora przed STT."""
    VAD_SILENCE_MS = 1800           # dłuższy VAD – seniorzy mówią wolniej
    NOISE_GATE_THRESHOLD_DB = -45   # odcięcie szumów tła
    AGC_TARGET_LUFS = -16           # normalizacja głośności
class SeniorAudioPostprocessor:
    """Post-processing audio Adama po TTS."""
    TEMPO_MULTIPLIER = 0.85         # zwolnienie tempa o 15%
    EQ_BOOST_HIGHS_DB = 3           # +3dB w 2-4 kHz (lepsza zrozumiałość)
    COMPRESSION_RATIO = "4:1"       # delikatna kompresja dynamiki
    TARGET_LUFS = -14               # broadcast-standard loudness
class SpeechCalibrator:
    """Analizuje tempo mowy seniora i dostosowuje parametry."""
    async def calibrate(self, senior_id: str, audio_sample: bytes) -> dict:
        """Mierzy tempo, głośność i dostosowuje VAD i TTS params."""
        wpm = self._measure_wpm(audio_sample)
        loudness = self._measure_loudness(audio_sample)
        return {
            "senior_wpm": wpm,
            "vad_silence_ms": max(1200, int(wpm * 15)),   # dynamiczny VAD
            "tts_rate_multiplier": min(1.0, 120 / wpm),   # dopasowanie tempa
            "gain_adjustment_db": self._calc_gain(loudness)
        }
Słownik wielkopolski – config/vocabulary_wielkopolska.txt (~380 wpisów):
pyra|ziemniaki
szneka|drożdżówka
gzik|twaróg ze śmietaną
bimba|tramwaj
...
Szacowany czas: 2–3 dni
⚪ F14 — Multi-Model Consensus Voting
Cel: Głosowanie między modelami AI przy krytycznych decyzjach (eskalacja PURPLE) – eliminacja false positives.
Pliki do utworzenia:
backend/app/services/consensus_engine.py
backend/app/services/voters/
    ├── whisper_safety_voter.py
    ├── deepgram_safety_voter.py
    ├── llm_safety_voter.py
    └── sentiment_voter.py
config/agents/llm_safety_classifier.yaml
Logika głosowania:
class ConsensusEngine:
    """Silnik głosowania dla krytycznych decyzji."""
    DECISION_MATRIX = {
        (3, 0): "EXECUTE",       # 3/3 → wykonaj akcję
        (2, 1): "ESCALATE",      # 2/3 → eskalacja
        (2, 1, 0.9): "EXECUTE",  # 2/3 z avg confidence >0.9 → wykonaj
        (1, 2): "DEFER",         # 1/3 → odroczenie (człowiek decyduje)
        (0, 3): "ABSTAIN",       # 0/3 → powstrzymanie
    }
    async def vote(self, context: CriticalContext) -> ConsensusResult:
        """Przeprowadza głosowanie między voterami."""
        voters = [
            WhisperSafetyVoter(),
            DeepgramSafetyVoter(),
            LLMSafetyVoter(),
        ]
        votes = []
        for voter in voters:
            result = await voter.vote(context)
            votes.append(result)
        yes_count = sum(1 for v in votes if v.decision == "ESCALATE")
        no_count = len(votes) - yes_count
        avg_confidence = sum(v.confidence for v in votes) / len(votes)
        # Matryca decyzyjna
        if yes_count == 3:
            action = "EXECUTE"
        elif yes_count >= 2:
            action = "EXECUTE" if avg_confidence > 0.9 else "ESCALATE"
        elif yes_count == 1:
            action = "DEFER"
        else:
            action = "ABSTAIN"
        return ConsensusResult(
            action=action,
            votes=votes,
            avg_confidence=avg_confidence,
            requires_human_review=(action in ["DEFER", "ABSTAIN"])
        )
Szacowany czas: 2–3 dni
⚪ F15 — Integracja 112 (Emergency Calling)
Cel: Automatyczne dzwonienie pod 112 z briefingiem dla dyspozytora, SLA <12s.
Pliki do utworzenia:
backend/app/services/emergency_service.py
backend/app/services/emergency_audio.py
backend/app/models/emergency_call.py
backend/alembic/versions/XXXX_create_emergency_calls.py
Kluczowy snippet:
class EmergencyService:
    """Obsługuje połączenia alarmowe 112."""
    SLA_MS = 12000
    GRACE_PERIOD_SECONDS = 10  # okno na anulowanie
    async def initiate_emergency_call(self, senior_id: str, trigger: str,
                                       consensus: ConsensusResult = None):
        """Rozpoczyna połączenie z 112."""
        start = time.monotonic()
        senior = await SeniorService().get_by_id(senior_id)
        # Przygotuj briefing dla dyspozytora (format AMPDS)
        briefing = self._prepare_dispatcher_briefing(senior, trigger)
        # Wybierz 112 przez Asterisk ARI
        emergency_channel = await self.asterisk.originate(
            endpoint="PJSIP/112@emergency-trunk",
            context="adam-emergency",
            extension="s",
            variables={"BRIEFING": briefing}
        )
        elapsed_ms = int((time.monotonic() - start) * 1000)
        sla_met = elapsed_ms < self.SLA_MS
        # Równolegle: pozostań na linii z seniorem
        await self._stay_on_line_with_senior(senior_id)
        # Zapisz zdarzenie
        await EmergencyCall.create(
            senior_id=senior_id,
            trigger_type=trigger,
            consensus_result=consensus.dict() if consensus else None,
            sla_met=sla_met,
            elapsed_ms=elapsed_ms
        )
    def _prepare_dispatcher_briefing(self, senior, trigger) -> str:
        """Buduje komunikat dla dyspozytora 112 wg standardu AMPDS."""
        return f"""
        UWAGA – zgłoszenie automatyczne od systemu asystenckiego seniora.
        Senior: {senior.first_name} {senior.last_name}, ur. {senior.date_of_birth}
        Adres: {senior.address_street}, {senior.address_postal} {senior.address_city}
        Telefon seniora: {senior.phone_number}
        Powód zgłoszenia: {trigger}
        Dane medyczne: {self._get_medical_summary(senior.id)}
        System wykrył niepokojące sygnały i automatycznie połączył z numerem 112.
        Senior może być sam i potrzebować natychmiastowej pomocy.
        """
Szacowany czas: 2–3 dni
⚪ F16 — Conversation Quality Assurance
Cel: Automatyczna ocena jakości rozmów + manualny audyt + pętla ulepszeń.
Pliki do utworzenia:
backend/app/services/quality_engine.py
backend/app/services/manual_audit.py
backend/app/services/improvement_loop.py
backend/app/models/quality.py
Auto‑scoring:
class QualityEngine:
    """Automatycznie ocenia każdą rozmowę pod kątem jakości."""
    CRITERIA = {
        "Q01_engagement": "Czy Adam aktywnie słuchał i reagował na seniora?",
        "Q02_empathy": "Czy Adam okazał empatię tam, gdzie była potrzebna?",
        "Q03_safety": "Czy Adam poprawnie eskalował sygnały alarmowe?",
        "Q04_naturalness": "Czy rozmowa była naturalna, bez sztywnych fraz?",
        "Q05_completeness": "Czy wszystkie pytania welfare-check zostały zadane?",
        "Q06_pace": "Czy tempo rozmowy było odpowiednie dla seniora?",
        "Q07_medication": "Czy Adam poprawnie zapytał o leki?",
    }
    PASS_THRESHOLD = 70.0  # %
    async def score_conversation(self, call_id: str, transcript: str) -> QualityScore:
        """Ocenia rozmowę używając GPT-4o-mini jako sędziego."""
        scores = {}
        for code, description in self.CRITERIA.items():
            score = await self._evaluate_criterion(transcript, description)
            scores[code] = score
        overall = sum(scores.values()) / len(scores)
        requires_manual_review = overall < self.PASS_THRESHOLD
        return QualityScore(
            call_id=call_id,
            scores=scores,
            overall=round(overall, 1),
            requires_manual_review=requires_manual_review
        )
Szacowany czas: 3–4 dni
⚪ F17 — End‑to‑End Integration Tests
Cel: Pełen zestaw testów integracyjnych i end‑to‑end.
Pliki do utworzenia:
tests/
├── unit/
│   ├── test_senior_service.py
│   ├── test_guardrails.py
│   ├── test_semaphore_engine.py
│   ├── test_medication_tracker.py
│   └── test_memory_engine.py
├── integration/
│   ├── test_welfare_check_flow.py
│   ├── test_crisis_escalation.py
│   ├── test_medication_adherence_flow.py
│   └── test_marketplace_order_flow.py
├── e2e/
│   ├── test_full_conversation.py
│   ├── test_silence_watchdog.py
│   ├── test_112_integration.py
│   └── test_manipulation_attempts.py
├── stress/
│   ├── test_concurrent_calls.py
│   └── test_200_seniors.py
├── fixtures/
│   ├── senior_profiles.json
│   ├── test_audio/
│   └── mock_wearable_data.json
└── conftest.py
CI Pipeline (GitHub Actions):
name: Adam CI
on: [push, pull_request]
jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker compose -f docker-compose.test.yml up -d
      - run: pytest tests/unit/ -v --cov=backend --cov-report=term-missing
        env:
          COVERAGE_THRESHOLD: 80
  integration:
    needs: unit
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/integration/ -v --timeout=120
  e2e:
    needs: integration
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/e2e/ -v --timeout=300
  stress:
    needs: integration
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/stress/ -v --timeout=600
Szacowany czas: 5–7 dni
⚪ F18 — Dokumentacja Końcowa i Deployment Package
Cel: Pełna dokumentacja operatora, dewelopera, compliance i one‑click deployment.
Pliki do utworzenia:
docs/
├── adam_deployment/
│   ├── README.md                     # główny README projektu Adam
│   ├── deployment_guide.md           # instrukcja wdrożenia na VPS
│   ├── operator_manual.md            # instrukcja dla opiekuna/koordynatora
│   ├── family_guide.md               # instrukcja dla rodziny seniora
│   ├── technical_architecture.md     # architektura systemu (7 warstw)
│   ├── compliance/
│   │   ├── rodo_checklist.md         # checklista RODO
│   │   ├── ai_act_report.md          # raport AI Act
│   │   └── dpia.md                   # Data Protection Impact Assessment
│   ├── api_reference.md              # dokumentacja API
│   └── changelog.md                  # historia zmian Adam vs AVA
├── adam_cli/
│   └── deploy.py                     # skrypt one‑click deployment
└── adam_deployment_checklist.yaml    # pre‑deployment i post‑deployment checklist
One‑click deployment – adam_cli/deploy.py:
#!/usr/bin/env python3
"""
Adam Deploy – one-click deployment dla SilverTech.
Uruchom: python adam_cli/deploy.py --region poznan
"""
import subprocess, sys, yaml
STEPS = [
    "provision_vps",            # Utworzenie VPS (Hetzner/OVH/Home.pl)
    "clone_ava_fork",           # git clone fork AVA
    "apply_adam_patches",       # Zaaplikowanie wszystkich faz F1-F17
    "configure_polish_tts",     # ElevenLabs Polish voice + Piper fallback
    "upload_vocabulary",        # Słownik wielkopolski
    "configure_sip_trunk",      # Polski SIP trunk (np. Netia, Orange)
    "run_preflight",            # ./preflight.sh --apply-fixes
    "smoke_test",               # Test połączenia testowego
    "enable_monitoring",        # Prometheus + alerty
    "print_credentials",        # Wyświetl dane dostępowe
]
def deploy_region(region: str):
    for step in STEPS:
        print(f"[Adam Deploy] Executing: {step}...")
        # subprocess.run(...)
        # Jeśli błąd → rollback
    print("[Adam Deploy] ✅ Deployment complete!")
    print(f"[Adam Deploy] Admin UI: http://<vps-ip>:3003")
    print(f"[Adam Deploy] Health: curl http://<vps-ip>:15000/health")
Szacowany czas: 5–7 dni
📊 C. HARMONOGRAM I PRIORYTETY
| Faza | Nazwa | Priorytet | Dni | Zależności |
| F1 | Senior Profile DB | 🔴 KRYTYCZNY | 3–5 | — |
| F2 | Call Scheduler | 🔴 KRYTYCZNY | 4–6 | F1 |
| F3 | Semafor Eskalacji | 🔴 KRYTYCZNY | 5–7 | F1 |
| F4 | Guardrails | 🔴 KRYTYCZNY | 3–4 | — |
| F5 | System Prompt Adam v2.0 | 🔴 KRYTYCZNY | 2–3 | F1, F4 |
| F6 | Medication Tracker | 🟡 WYSOKI | 4–5 | F1, F3 |
| F7 | Semantic Memory | 🟡 WYSOKI | 5–7 | F1, F5 |
| F8 | Crisis Detection | 🟡 WYSOKI | 4–5 | F3, F4 |
| F9 | Family Dashboard | 🟢 ŚREDNI | 5–7 | F1, F3, F6 |
| F10 | Wearables | 🔵 ŚREDNI | 5–7 | F1, F3 |
| F11 | Marketplace | 🟣 NISKI | 3–5 | F1 |
| F12 | RODO/AI Act | 🔴 KRYTYCZNY | 3–4 | F1, F7 |
| F13 | Senior Speech | ⚪ NISKI | 2–3 | — |
| F14 | Multi-Model Voting | ⚪ NISKI | 2–3 | F3, F8 |
| F15 | 112 Integration | 🔴 KRYTYCZNY | 2–3 | F3, F8, F14 |
| F16 | Quality Assurance | ⚪ NISKI | 3–4 | F5 |
| F17 | Testy Integracyjne | 🟡 WYSOKI | 5–7 | F1–F16 |
| F18 | Dokumentacja | 🟡 WYSOKI | 5–7 | F1–F16 |
Szacowany łączny czas: 68–90 dni (3–4 miesiące dla 1–2 developerów)
🚀 D. KOLEJNOŚĆ DLA GENSPARK — PIERWSZY SPRINT (F1–F5 + F12)
Cel pierwszego sprintu: MVP Agenta Adama – dzwoni, rozmawia po polsku, wykrywa kryzys, prowadzi bazę seniorów.
SPRINT 1 (14 dni):
  Dzień 1-5:   F1 (Senior DB) + F12 (RODO compliance)
  Dzień 6-9:   F2 (Scheduler) + F4 (Guardrails)
  Dzień 10-12: F5 (Prompt Adam) – integracja F1+F2+F4 w konwersację
  Dzień 13-14: F3 (Semafor) + testy integracyjne F1-F5
Deliverable Sprintu 1:
[x] Adam dzwoni do seniora o zaplanowanej porze
[x] Rozmawia po polsku według protokołu welfare-check
[x] Wykrywa słowa alarmowe i eskalacja (semafor)
[x] Zapisuje profil seniora i historię rozmów
[x] Guardrails blokują porady medyczne i obietnice
[x] Zgody RODO rejestrowane głosowo
[x] Dashboard Admin UI pokazuje stan seniorów
🧠 E. INSTRUKCJA DLA GENSPARK DEVELOPER
Sforkuj hkjarral/AVA-AI-Voice-Agent-for-Asterisk (v7.3.2)
Wgraj fork do GenSpark jako nowy projekt
Realizuj fazy w kolejności z harmonogramu, zaczynając od Sprintu 1
Dla każdej fazy:
Utwórz wskazane pliki w podanych ścieżkach
Zmodyfikuj wskazane istniejące pliki
Przeprowadź wskazany test akceptacyjny
Commit z prefixem [Adam-F{n}] {opis}
Po każdej fazie – zgłoś do review
Po całym sprincie – deployment na testowy VPS i pełny test konwersacyjny
Chcesz, żebym teraz któryś konkretny fragment rozwinął jeszcze bardziej szczegółowo – np. konkretny plik z pełnym kodem gotowym do skopiowania, albo żebym przygotował gotowy snippet do wklejenia w GenSpark dla konkretnej fazy?