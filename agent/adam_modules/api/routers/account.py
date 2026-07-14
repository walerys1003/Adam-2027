"""Router konta i wiadomości `/api/account` (ETAP 22).

Domyka integrację frontendu (panel: Wiadomości + Konto), który do tej pory
działał na mockach. Zasoby budowane są z realnych danych backendu:

- **Wątki / wiadomości** — agregacja powiadomień rodzinnych (F9 `Notification`)
  w wątki per-senior. Każde powiadomienie → wiadomość; wątek = subject + lista
  wiadomości. Dopisanie wiadomości koordynatora tworzy nowe powiadomienie
  (kanał `panel`, tryb informacyjny), więc zapis jest trwały w DB.
- **Faktury** — wyliczane deterministycznie z pakietów aktywnych seniorów
  (cennik pakietów × liczba seniorów), 4 ostatnie okresy. Brak osobnej tabeli
  rozliczeń — to raport pochodny (spójny z modelem „organizacja płaci za
  obsługiwanych seniorów").
- **Sesje** — bieżąca sesja z tożsamości JWT (`/api/account/sessions`).

Endpointy:
- GET  /api/account/threads                 — lista wątków (z wiadomościami)
- POST /api/account/threads/{senior_ext}/messages — dopisz wiadomość do wątku
- GET  /api/account/invoices                 — faktury (pochodne)
- GET  /api/account/sessions                 — aktywne sesje (z JWT)
"""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from adam_modules.seniors.service import SeniorService
from adam_modules.family.service import FamilyService
from adam_modules.family.models import (
    FamilyRole, DeliveryMode, SemaphoreLevel,
)
from ..deps import get_db, get_current_user, CurrentUser

router = APIRouter(prefix="/api/account", tags=["account"])


# ---- schematy (zgodne z frontendowymi typami Thread/Message/Invoice/Session) ----

class MessageOut(BaseModel):
    id: str
    from_: str = Field(alias="from")
    author_name: str
    body: str
    timestamp: str
    read: bool

    model_config = {"populate_by_name": True}


class ThreadOut(BaseModel):
    id: str
    subject: str
    senior_id: str | None = None
    senior_name: str | None = None
    category: str
    last_message_at: str
    unread: int
    messages: list[MessageOut]


class MessageIn(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class InvoiceOut(BaseModel):
    id: str
    period: str
    amount: str
    status: str


class SessionOut(BaseModel):
    id: str
    device: str
    location: str
    last_active: str
    current: bool


# ---- helpery mapujące ----

_LEVEL_CATEGORY = {
    SemaphoreLevel.purple: "alert",
    SemaphoreLevel.red: "alert",
    SemaphoreLevel.yellow: "report",
    SemaphoreLevel.green: "report",
}

# 'from' wiadomości na podstawie tytułu/źródła powiadomienia
def _msg_from(title: str) -> str:
    t = (title or "").lower()
    if "adam" in t:
        return "adam"
    if "system" in t or "próg" in t or "przypomnienie" in t:
        return "system"
    return "coordinator"


def _iso(dt: datetime | None) -> str:
    return (dt or datetime.utcnow()).isoformat()


# ---- wątki / wiadomości ----

@router.get("/threads", response_model=list[ThreadOut])
def list_threads(db: Session = Depends(get_db)):
    """Buduje wątki z powiadomień rodzinnych (F9), grupując per senior."""
    svc = SeniorService(db)
    fam = FamilyService(db)
    threads: list[ThreadOut] = []

    for senior in svc.list(limit=200):
        notifs = fam.feed(senior.id, limit=50)
        if not notifs:
            continue
        # najnowsze na końcu → sortujemy rosnąco po czasie
        notifs = sorted(notifs, key=lambda n: n.created_at or datetime.utcnow())
        messages: list[MessageOut] = []
        unread = 0
        top_level = SemaphoreLevel.green
        for n in notifs:
            read = n.status.value in ("sent", "acknowledged") if hasattr(n.status, "value") else True
            if not read:
                unread += 1
            if n.level and n.level.value == "purple":
                top_level = n.level
            elif n.level and n.level.value == "red" and top_level.value != "purple":
                top_level = n.level
            messages.append(MessageOut(
                id=f"m{n.id}",
                **{"from": _msg_from(n.title)},
                author_name=n.title[:60] or "System Adam",
                body=n.body,
                timestamp=_iso(n.created_at),
                read=read,
            ))
        last = notifs[-1]
        threads.append(ThreadOut(
            id=senior.external_id,
            subject=f"{last.title} — {senior.full_name}",
            senior_id=senior.external_id,
            senior_name=senior.full_name,
            category=_LEVEL_CATEGORY.get(top_level, "coordinator"),
            last_message_at=_iso(last.created_at),
            unread=unread,
            messages=messages,
        ))

    # najnowsze wątki na górze
    threads.sort(key=lambda t: t.last_message_at, reverse=True)
    return threads


@router.post("/threads/{senior_ext}/messages", response_model=ThreadOut)
def add_message(senior_ext: str, body: MessageIn, db: Session = Depends(get_db)):
    """Dopisuje wiadomość koordynatora do wątku (trwały zapis jako Notification)."""
    svc = SeniorService(db)
    senior = svc.get_by_external(senior_ext)
    if not senior:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony.")

    fam = FamilyService(db)
    # upewnij się, że istnieje adresat (panel/koordynator) — pierwszy aktywny lub twórz techniczny
    members = fam.members(senior.id, only_active=True)
    if not members:
        recipient = fam.add_member(senior, name="Panel koordynatora", role=FamilyRole.primary)
    else:
        recipient = members[0]

    fam._make_notification(
        recipient, senior, SemaphoreLevel.green,
        mode=DeliveryMode.digest,
        title="Wiadomość koordynatora", body=body.body,
    )
    db.commit()

    # zwróć zaktualizowany wątek
    return next((t for t in list_threads(db) if t.id == senior_ext),
                ThreadOut(id=senior_ext, subject=senior.full_name, senior_id=senior_ext,
                          senior_name=senior.full_name, category="coordinator",
                          last_message_at=_iso(None), unread=0, messages=[]))


# ---- faktury (pochodne z pakietów) ----

_PACKAGE_PRICE_PLN = {"basic": 149, "family": 249, "premium": 399}


@router.get("/invoices", response_model=list[InvoiceOut])
def list_invoices(db: Session = Depends(get_db)):
    """Faktury pochodne: suma cen pakietów aktywnych seniorów × 4 ostatnie okresy."""
    svc = SeniorService(db)
    seniors = svc.list(active=True, limit=500)
    monthly = sum(_PACKAGE_PRICE_PLN.get(
        s.package.value if hasattr(s.package, "value") else str(s.package), 149
    ) for s in seniors)

    months_pl = ["styczeń", "luty", "marzec", "kwiecień", "maj", "czerwiec",
                 "lipiec", "sierpień", "wrzesień", "październik", "listopad", "grudzień"]
    now = datetime.utcnow()
    invoices: list[InvoiceOut] = []
    for i in range(4):
        m = now.month - i
        y = now.year
        while m <= 0:
            m += 12
            y -= 1
        status = "pending" if i == 0 else "paid"
        invoices.append(InvoiceOut(
            id=f"FV/{y}/{m:02d}",
            period=f"{months_pl[m - 1].capitalize()} {y}",
            amount=f"{monthly} zł",
            status=status,
        ))
    return invoices


# ---- sesje (z JWT) ----

@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(user: CurrentUser = Depends(get_current_user)):
    """Bieżąca sesja z tożsamości JWT. Backend nie utrzymuje rejestru urządzeń,
    więc zwracamy sesję aktywną (spójne, bez fikcyjnych urządzeń)."""
    return [SessionOut(
        id="current",
        device=f"Sesja API · {user.role.value}",
        location="—",
        last_active=datetime.utcnow().isoformat(),
        current=True,
    )]
