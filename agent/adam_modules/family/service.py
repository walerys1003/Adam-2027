"""
FamilyService — zarządzanie opiekunami i dostarczaniem powiadomień (F9).

Reguła dostarczania wg poziomu semafora (F9.2):
- GREEN  → brak powiadomień (rutyna).
- YELLOW → digest (zbiorczo raz dziennie), respektuje DND.
- RED    → immediate (natychmiast), respektuje DND obserwatorów, ale nie
           opiekunów primary/coordinator.
- PURPLE → bypass_dnd (zawsze, wszyscy z rolą primary/secondary/coordinator).
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from adam_modules.seniors.models import Senior, SemaphoreLevel
from .models import (
    FamilyMember, Notification, FamilyRole, NotifyChannel,
    DeliveryMode, NotificationStatus,
)
from .adapters import NotificationAdapter, NullAdapter

# Poziom → tryb dostarczania
_LEVEL_MODE = {
    SemaphoreLevel.green: None,
    SemaphoreLevel.yellow: DeliveryMode.digest,
    SemaphoreLevel.red: DeliveryMode.immediate,
    SemaphoreLevel.purple: DeliveryMode.bypass_dnd,
}

# Role, które NIE dostają alertów krytycznych (tylko podgląd)
_OBSERVER_ROLES = {FamilyRole.observer}
# Role, które ignorują DND przy RED/PURPLE
_CRITICAL_ROLES = {FamilyRole.primary, FamilyRole.coordinator}


class FamilyService:
    def __init__(self, session: Session, adapters: dict[str, NotificationAdapter] | None = None):
        self.session = session
        self.adapters = adapters or {}
        self._null = NullAdapter()

    # ---- opiekunowie ----
    def add_member(self, senior: Senior, name: str, role: FamilyRole = FamilyRole.secondary,
                   phone: str | None = None, email: str | None = None,
                   preferred_channel: NotifyChannel = NotifyChannel.sms,
                   dnd_start: int | None = None, dnd_end: int | None = None) -> FamilyMember:
        fm = FamilyMember(
            senior_id=senior.id, name=name, role=role, phone=phone, email=email,
            preferred_channel=preferred_channel, dnd_start=dnd_start, dnd_end=dnd_end,
        )
        self.session.add(fm)
        self.session.flush()
        return fm

    def members(self, senior_id: int, only_active: bool = True) -> list[FamilyMember]:
        stmt = select(FamilyMember).where(FamilyMember.senior_id == senior_id)
        if only_active:
            stmt = stmt.where(FamilyMember.active.is_(True))
        return list(self.session.scalars(stmt))

    # ---- logika DND ----
    @staticmethod
    def in_dnd(member: FamilyMember, hour: int) -> bool:
        if member.dnd_start is None or member.dnd_end is None:
            return False
        start, end = member.dnd_start, member.dnd_end
        if start <= end:
            return start <= hour < end
        # okno przez północ, np. 22->7
        return hour >= start or hour < end

    def _adapter_for(self, channel: NotifyChannel) -> NotificationAdapter:
        return self.adapters.get(channel.value, self._null)

    # ---- decyzja o odbiorcach ----
    def _recipients_for_level(self, senior_id: int, level: SemaphoreLevel) -> list[FamilyMember]:
        members = self.members(senior_id)
        if level in (SemaphoreLevel.red, SemaphoreLevel.purple):
            # obserwatorzy nie dostają alertów krytycznych
            return [m for m in members if m.role not in _OBSERVER_ROLES]
        return members

    # ---- główny fan-out ----
    def dispatch(self, senior: Senior, level: SemaphoreLevel, *, title: str, body: str,
                 hour: int | None = None) -> list[Notification]:
        """Tworzy i wysyła powiadomienia wg poziomu. GREEN → pusta lista."""
        mode = _LEVEL_MODE[level]
        if mode is None:
            return []
        hour = hour if hour is not None else datetime.utcnow().hour
        created: list[Notification] = []

        for member in self._recipients_for_level(senior.id, level):
            bypass = (mode == DeliveryMode.bypass_dnd)
            # DND: przy RED role krytyczne ignorują DND; obserwatorzy już wykluczeni
            if not bypass and self.in_dnd(member, hour):
                if not (level == SemaphoreLevel.red and member.role in _CRITICAL_ROLES):
                    # digest/immediate wstrzymane przez DND — zapisz jako pending
                    notif = self._make_notification(member, senior, level, mode, title, body,
                                                     status=NotificationStatus.pending)
                    created.append(notif)
                    continue

            notif = self._make_notification(member, senior, level, mode, title, body)
            adapter = self._adapter_for(member.preferred_channel)
            to = member.phone if member.preferred_channel in (NotifyChannel.sms, NotifyChannel.call) else member.email
            result = adapter.send(to=to or "", title=title, body=body, bypass_dnd=bypass)
            notif.status = NotificationStatus.sent if result.ok else NotificationStatus.failed
            notif.sent_at = datetime.utcnow() if result.ok else None
            created.append(notif)

        self.session.flush()
        return created

    def _make_notification(self, member: FamilyMember, senior: Senior, level: SemaphoreLevel,
                           mode: DeliveryMode, title: str, body: str,
                           status: NotificationStatus = NotificationStatus.pending) -> Notification:
        notif = Notification(
            recipient_id=member.id, senior_id=senior.id, level=level,
            channel=member.preferred_channel, mode=mode, title=title, body=body, status=status,
        )
        self.session.add(notif)
        return notif

    def acknowledge(self, notification: Notification) -> Notification:
        notification.status = NotificationStatus.acknowledged
        self.session.flush()
        return notification

    def feed(self, senior_id: int, limit: int = 50) -> list[Notification]:
        """Strumień zdarzeń do dashboardu rodzinnego (SSE /api/events czyta to)."""
        return list(self.session.scalars(
            select(Notification).where(Notification.senior_id == senior_id)
            .order_by(Notification.id.desc()).limit(limit)
        ))
