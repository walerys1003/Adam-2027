"""Router rodziny/notyfikacji (F9) — opiekunowie, dispatch, feed + SSE /events."""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from adam_modules.seniors import SeniorService
from adam_modules.seniors.models import SemaphoreLevel
from adam_modules.family import (
    FamilyService, FamilyRole, NotifyChannel, MemoryAdapter,
)
from ..deps import get_db

router = APIRouter(prefix="/api/seniors/{senior_id}/family", tags=["family (F9)"])


def _senior_or_404(db: Session, senior_id: int):
    senior = SeniorService(db).get(senior_id)
    if senior is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    return senior


class MemberIn(BaseModel):
    name: str
    role: FamilyRole = FamilyRole.secondary
    phone: str | None = None
    email: str | None = None
    preferred_channel: NotifyChannel = NotifyChannel.sms
    dnd_start: int | None = None
    dnd_end: int | None = None


class MemberOut(BaseModel):
    id: int
    name: str
    role: str
    phone: str | None = None
    email: str | None = None
    preferred_channel: str
    active: bool


class DispatchIn(BaseModel):
    level: SemaphoreLevel
    title: str
    body: str
    hour: int | None = None


class NotificationOut(BaseModel):
    id: int
    recipient_id: int
    level: str
    channel: str
    mode: str
    title: str
    body: str
    status: str


def _member_out(m) -> MemberOut:
    return MemberOut(id=m.id, name=m.name, role=m.role.value, phone=m.phone,
                     email=m.email, preferred_channel=m.preferred_channel.value,
                     active=m.active)


def _notif_out(n) -> NotificationOut:
    return NotificationOut(id=n.id, recipient_id=n.recipient_id, level=n.level.value,
                           channel=n.channel.value, mode=n.mode.value, title=n.title,
                           body=n.body, status=n.status.value)


@router.get("/members", response_model=list[MemberOut])
def list_members(senior_id: int, db: Session = Depends(get_db)):
    _senior_or_404(db, senior_id)
    return [_member_out(m) for m in FamilyService(db).members(senior_id)]


@router.post("/members", response_model=MemberOut, status_code=201)
def add_member(senior_id: int, data: MemberIn, db: Session = Depends(get_db)):
    senior = _senior_or_404(db, senior_id)
    m = FamilyService(db).add_member(
        senior, name=data.name, role=data.role, phone=data.phone, email=data.email,
        preferred_channel=data.preferred_channel, dnd_start=data.dnd_start, dnd_end=data.dnd_end,
    )
    db.flush()
    return _member_out(m)


@router.post("/dispatch", response_model=list[NotificationOut])
def dispatch(senior_id: int, data: DispatchIn, db: Session = Depends(get_db)):
    senior = _senior_or_404(db, senior_id)
    adapters = {
        "sms": MemoryAdapter(), "email": MemoryAdapter(),
        "push": MemoryAdapter(), "call": MemoryAdapter(),
    }
    svc = FamilyService(db, adapters=adapters)
    notifs = svc.dispatch(senior, data.level, title=data.title, body=data.body, hour=data.hour)
    db.flush()
    return [_notif_out(n) for n in notifs]


@router.get("/feed", response_model=list[NotificationOut])
def feed(senior_id: int, limit: int = 50, db: Session = Depends(get_db)):
    _senior_or_404(db, senior_id)
    return [_notif_out(n) for n in FamilyService(db).feed(senior_id, limit=limit)]


@router.get("/events")
async def events(senior_id: int, db: Session = Depends(get_db)):
    """SSE — strumień zdarzeń dla dashboardu rodzinnego (F9 /api/events).

    Wysyła aktualny feed jako serię zdarzeń SSE i utrzymuje połączenie
    heartbeatem. Frontend konsumuje przez EventSource.
    """
    _senior_or_404(db, senior_id)
    notifs = FamilyService(db).feed(senior_id, limit=50)
    payload = [_notif_out(n).model_dump() for n in notifs]

    async def gen():
        yield f"event: snapshot\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
        # jeden heartbeat, by dowieść utrzymania połączenia (w prod: pętla live)
        await asyncio.sleep(0)
        yield "event: heartbeat\ndata: {}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
