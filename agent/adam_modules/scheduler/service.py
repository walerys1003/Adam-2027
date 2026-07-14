"""
SchedulerService — logika kampanii i prób połączeń (F2).

Kluczowa logika retry: przy no_answer/failed ponawiamy do max_retries razy
co retry_interval_s sekund. Po wyczerpaniu prób → status exhausted, co jest
sygnałem do eskalacji semafora (F3, EscalationLadder).
"""
from __future__ import annotations

from datetime import datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from adam_modules.seniors.models import Senior
from .models import Campaign, CallAttempt, CampaignKind, CallStatus
from .ari import AriOriginator, NullOriginator


class SchedulerService:
    def __init__(self, session: Session, originator: AriOriginator | None = None):
        self.session = session
        self.originator = originator or NullOriginator()

    # ---- kampanie ----
    def create_campaign(self, name: str, kind: CampaignKind, scheduled_time: time,
                        max_retries: int = 3, retry_interval_s: int = 20) -> Campaign:
        c = Campaign(name=name, kind=kind, scheduled_time=scheduled_time,
                     max_retries=max_retries, retry_interval_s=retry_interval_s)
        self.session.add(c)
        self.session.flush()
        return c

    def active_campaigns(self) -> list[Campaign]:
        return list(self.session.scalars(select(Campaign).where(Campaign.active.is_(True))))

    # ---- próby połączeń ----
    def schedule_attempt(self, campaign: Campaign, senior: Senior) -> CallAttempt:
        attempt = CallAttempt(
            campaign_id=campaign.id, senior_id=senior.id,
            attempt_no=1, status=CallStatus.pending,
        )
        self.session.add(attempt)
        self.session.flush()
        return attempt

    def _place_call(self, attempt: CallAttempt, campaign: Campaign, senior: Senior) -> CallStatus:
        attempt.status = CallStatus.dialing
        attempt.started_at = datetime.utcnow()
        result = self.originator.originate(
            senior.phone or "", senior_external_id=senior.external_id,
            context=f"welfare-{campaign.kind.value}",
        )
        if result.ok:
            attempt.channel_id = result.channel_id
            attempt.status = CallStatus.answered
        elif result.reason == "no_answer":
            attempt.status = CallStatus.no_answer
        else:
            attempt.status = CallStatus.failed
        self.session.flush()
        return attempt.status

    def run_with_retries(self, campaign: Campaign, senior: Senior) -> CallAttempt:
        """
        Wykonuje próbę + retry aż do sukcesu lub wyczerpania max_retries.
        Zwraca ostatni CallAttempt (answered/completed lub exhausted).
        Nie śpi realnie — interwał jest atrybutem kampanii (harmonogram robi APScheduler).
        """
        attempt = self.schedule_attempt(campaign, senior)
        for n in range(1, campaign.max_retries + 1):
            attempt.attempt_no = n
            status = self._place_call(attempt, campaign, senior)
            if status == CallStatus.answered:
                attempt.status = CallStatus.completed
                attempt.ended_at = datetime.utcnow()
                self.session.flush()
                return attempt
            # kolejna próba jako nowy rekord (audyt każdej próby)
            if n < campaign.max_retries:
                attempt = CallAttempt(
                    campaign_id=campaign.id, senior_id=senior.id,
                    attempt_no=n + 1, status=CallStatus.pending,
                )
                self.session.add(attempt)
                self.session.flush()
        # wyczerpano próby → eskalacja
        attempt.status = CallStatus.exhausted
        attempt.ended_at = datetime.utcnow()
        self.session.flush()
        return attempt

    def attempts_for(self, senior_id: int) -> list[CallAttempt]:
        return list(self.session.scalars(
            select(CallAttempt).where(CallAttempt.senior_id == senior_id)
            .order_by(CallAttempt.id)
        ))
