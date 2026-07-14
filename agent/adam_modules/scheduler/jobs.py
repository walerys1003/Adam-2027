"""
APScheduler joby welfare-check (F2.2).

WelfareScheduler rejestruje cron-joby dla każdej aktywnej kampanii (pora dnia
z Campaign.scheduled_time) i przy wyzwoleniu uruchamia próby połączeń dla
wszystkich aktywnych seniorów. Retry wewnątrz próby obsługuje SchedulerService.

Uruchomienie produkcyjne: proces long-running w Frankfurt DC (nie Cloudflare).
"""
from __future__ import annotations

from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from adam_modules.common.db import session_scope
from adam_modules.seniors.models import Senior
from .models import Campaign, CampaignKind
from .service import SchedulerService
from .ari import AriOriginator


class WelfareScheduler:
    def __init__(self, originator_factory: Callable[[], AriOriginator] | None = None):
        self._scheduler = BackgroundScheduler(timezone="Europe/Warsaw")
        self._originator_factory = originator_factory

    def _run_campaign(self, campaign_id: int) -> None:
        with session_scope() as session:
            campaign = session.get(Campaign, campaign_id)
            if campaign is None or not campaign.active:
                return
            originator = self._originator_factory() if self._originator_factory else None
            svc = SchedulerService(session, originator=originator)
            seniors = session.query(Senior).filter(Senior.active.is_(True)).all()
            for senior in seniors:
                if senior.phone:
                    svc.run_with_retries(campaign, senior)

    def register_campaign(self, campaign: Campaign) -> None:
        """Dodaje cron-job dla kampanii na jej scheduled_time."""
        trigger = CronTrigger(
            hour=campaign.scheduled_time.hour,
            minute=campaign.scheduled_time.minute,
        )
        self._scheduler.add_job(
            self._run_campaign, trigger=trigger, args=[campaign.id],
            id=f"campaign-{campaign.id}", replace_existing=True,
        )

    def load_all(self) -> int:
        """Rejestruje joby dla wszystkich aktywnych kampanii. Zwraca liczbę."""
        with session_scope() as session:
            campaigns = SchedulerService(session).active_campaigns()
            for c in campaigns:
                self.register_campaign(c)
            return len(campaigns)

    def start(self) -> None:  # pragma: no cover — proces długożyjący
        self._scheduler.start()

    def shutdown(self) -> None:  # pragma: no cover
        self._scheduler.shutdown(wait=False)

    @property
    def job_ids(self) -> list[str]:
        return [j.id for j in self._scheduler.get_jobs()]
