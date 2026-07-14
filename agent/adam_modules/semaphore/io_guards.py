"""Guardrails I/O (F4, ETAP 24) — trójwarstwowa ochrona rozmowy.

Dotychczasowy `guardrails.Guardrails.validate()` chroni WYNIK klasyfikacji semafora.
Ten moduł dokłada dwie brakujące warstwy wymagane przez specyfikację F4:

1. **InputGuard (pre-LLM)** — sanityzacja wejścia seniora, ZANIM trafi do LLM:
   - wykrycie prób prompt-injection / jailbreak („udawaj lekarza", „zignoruj instrukcje"),
   - wykrycie i maskowanie PII w treści (PESEL, telefon, e-mail, numer karty),
   - obcięcie nadmiernej długości (ochrona przed floodem kontekstu).

2. **OutputGuard (post-LLM)** — weryfikacja odpowiedzi Adama, ZANIM trafi do seniora:
   - blokada porad diagnostycznych / medycznych (Adam nie jest lekarzem),
   - blokada podawania konkretnych dawek leków (halucynacja groźna dla życia),
   - blokada obietnic/gwarancji medycznych,
   - wymuszenie bezpiecznego przekierowania do człowieka/służb, gdy trzeba.

Wszystko jest czystą logiką (regex + reguły), w 100% testowalne bez sieci i fail-safe:
w razie wątpliwości guard raczej ZABLOKUJE/ZAMASKUJE niż przepuści ryzykowną treść.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class GuardAction(str, Enum):
    ALLOW = "allow"           # treść bezpieczna, przepuszczona bez zmian
    SANITIZED = "sanitized"   # treść przepuszczona, ale zmodyfikowana (np. zamaskowane PII)
    BLOCKED = "blocked"       # treść zablokowana — użyj `safe_replacement`


@dataclass
class InputGuardResult:
    action: GuardAction
    text: str                                  # tekst po sanityzacji (do LLM)
    flags: list[str] = field(default_factory=list)
    pii_masked: int = 0

    @property
    def injection_detected(self) -> bool:
        return "prompt_injection" in self.flags


@dataclass
class OutputGuardResult:
    action: GuardAction
    text: str                                  # tekst do wypowiedzenia seniorowi
    flags: list[str] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return self.action == GuardAction.BLOCKED


# --------------------------------------------------------------------- InputGuard

# Wzorce prób manipulacji / jailbreak (PL + typowe EN, bo modele bywają wielojęzyczne)
_INJECTION_PATTERNS = [
    r"zignoruj\s+(wszystkie\s+)?(poprzednie\s+)?(instrukcje|polecenia|zasady)",
    r"udawaj[,\s]+(że\s+)?(jesteś|że jesteś)\s+(lekarz|doktor|człowiek|kim)",
    r"zapomnij\s+(o\s+)?(swoich\s+)?(instrukcj|zasad|regu)",
    r"nie\s+jesteś\s+(już\s+)?(ai|sztuczn|asystent)",
    r"od\s+teraz\s+(jesteś|będziesz)\b",
    r"przełącz\s+się\s+w\s+tryb",
    r"ignore\s+(all\s+)?(previous\s+)?(instructions|rules)",
    r"you\s+are\s+(now\s+)?(a\s+)?(doctor|human|dan)\b",
    r"pretend\s+(to\s+be|you\s+are)",
    r"system\s*prompt",
    r"reveal\s+your\s+(instructions|prompt|system)",
    r"pokaż\s+(swój\s+)?(prompt|instrukcj|system)",
]
_INJECTION_RE = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]

# PII — maskowanie w treści zanim trafi do LLM/logów
_PII_PATTERNS = {
    "pesel": re.compile(r"\b\d{11}\b"),
    "phone": re.compile(r"(?<!\d)(?:\+48\s?)?(?:\d[\s-]?){9}(?!\d)"),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "card": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
}
_PII_MASK = {
    "pesel": "[PESEL]",
    "phone": "[TELEFON]",
    "email": "[EMAIL]",
    "card": "[KARTA]",
}

MAX_INPUT_CHARS = 2000


class InputGuard:
    """Warstwa pre-LLM: sanityzacja wejścia seniora przed wysłaniem do modelu."""

    @staticmethod
    def sanitize(text: str) -> InputGuardResult:
        flags: list[str] = []
        original = text or ""
        cleaned = original

        # 1. obcięcie nadmiernej długości (ochrona kontekstu)
        if len(cleaned) > MAX_INPUT_CHARS:
            cleaned = cleaned[:MAX_INPUT_CHARS]
            flags.append("truncated")

        # 2. maskowanie PII (kolejność: card→pesel→phone→email, by uniknąć kolizji)
        masked = 0
        for key in ("card", "pesel", "phone", "email"):
            pattern = _PII_PATTERNS[key]

            def _sub(_m):
                nonlocal masked
                masked += 1
                return _PII_MASK[key]

            cleaned = pattern.sub(_sub, cleaned)
        if masked:
            flags.append("pii_masked")

        # 3. wykrycie prompt-injection / jailbreak
        injection = any(rx.search(original) for rx in _INJECTION_RE)
        if injection:
            flags.append("prompt_injection")
            # nie usuwamy treści (senior mógł zażartować), ale oznaczamy —
            # DialogEngine zdecyduje o bezpiecznej odpowiedzi zamiast wywołania LLM.
            action = GuardAction.SANITIZED
            return InputGuardResult(action=action, text=cleaned, flags=flags, pii_masked=masked)

        action = GuardAction.SANITIZED if flags else GuardAction.ALLOW
        return InputGuardResult(action=action, text=cleaned, flags=flags, pii_masked=masked)


# --------------------------------------------------------------------- OutputGuard

# Adam NIE może stawiać diagnoz ani zalecać dawek — to rola lekarza/farmaceuty.
_DIAGNOSIS_PATTERNS = [
    r"\b(ma\s+pan|ma\s+pani|to\s+jest|to\s+są|cierpi\s+pan|cierpi\s+pani)\b.{0,40}\b"
    r"(zawał|udar|nowotwór|rak|cukrzyc|zapaleni|zakażeni|nadciśnieni|arytmi)\w*",
    r"\bdiagnoz\w+",
    r"\bna\s+pewno\s+(to\s+)?(jest|ma\s+pan|ma\s+pani)\b",
]
# Podawanie konkretnych dawek (halucynacja groźna dla życia)
_DOSAGE_PATTERNS = [
    r"\b\d+\s?(mg|ml|g|mcg|µg|j\.?m\.?|tabletk\w*|kropl\w*)\b",
    r"\bprosz[ęe]\s+(wzi[ąa]ć|za[żz]y[ćc]|przyj[ąa]ć)\s+\d+",
    r"\bzwi[ęe]ksz\w*\s+dawk",
    r"\bzmniejsz\w*\s+dawk",
    r"\bodstaw\w*\s+(lek|tabletk)",
]
# Obietnice/gwarancje medyczne
_PROMISE_PATTERNS = [
    r"\bgwarantuj\w+",
    r"\bna\s+pewno\s+(pan|pani\s+)?(wyzdrowiej|przejdzie|minie|b[ęe]dzie\s+dobrze)",
    r"\bnic\s+si[ęe]\s+nie\s+stanie\b",
    r"\bto\s+nic\s+powa[żz]nego\b",
]

_DIAGNOSIS_RE = [re.compile(p, re.IGNORECASE) for p in _DIAGNOSIS_PATTERNS]
_DOSAGE_RE = [re.compile(p, re.IGNORECASE) for p in _DOSAGE_PATTERNS]
_PROMISE_RE = [re.compile(p, re.IGNORECASE) for p in _PROMISE_PATTERNS]

# Bezpieczna, zgodna z rolą odpowiedź zastępcza (gdy blokujemy wyjście LLM)
SAFE_MEDICAL_REPLACEMENT = (
    "Nie jestem lekarzem i nie mogę oceniać stanu zdrowia ani zalecać leków czy dawek. "
    "Jeśli coś Pana/Panią niepokoi, przekażę to zespołowi opieki, a w razie pilnej potrzeby "
    "skontaktuję ze służbami. Czy chce Pan/Pani, żebym powiadomił opiekuna?"
)
SAFE_INJECTION_REPLACEMENT = (
    "Jestem Adam, asystent głosowy — i nim pozostanę. Chętnie porozmawiam o Pana/Pani "
    "samopoczuciu i codziennych sprawach. Jak się Pan/Pani dziś czuje?"
)


class OutputGuard:
    """Warstwa post-LLM: weryfikacja odpowiedzi Adama przed wypowiedzeniem."""

    @staticmethod
    def review(text: str) -> OutputGuardResult:
        original = text or ""
        flags: list[str] = []

        if any(rx.search(original) for rx in _DOSAGE_RE):
            flags.append("dosage_advice")
        if any(rx.search(original) for rx in _DIAGNOSIS_RE):
            flags.append("diagnosis")
        if any(rx.search(original) for rx in _PROMISE_RE):
            flags.append("medical_promise")

        if flags:
            # fail-safe: blokujemy i podstawiamy bezpieczną odpowiedź zgodną z rolą
            return OutputGuardResult(
                action=GuardAction.BLOCKED,
                text=SAFE_MEDICAL_REPLACEMENT,
                flags=flags,
            )
        return OutputGuardResult(action=GuardAction.ALLOW, text=original, flags=flags)
