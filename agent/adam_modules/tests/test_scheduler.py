"""Testy F2 — scheduler welfare-check + retry logic."""
from datetime import time

from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.scheduler import SchedulerService, CampaignKind, CallStatus
from adam_modules.scheduler.ari import NullOriginator


def _make_senior(session):
    return SeniorService(session).create(
        SeniorCreate(first_name="Jan", last_name="Kowalski", phone="+48123456789")
    )


def test_create_campaign(session):
    svc = SchedulerService(session)
    c = svc.create_campaign("Poranny", CampaignKind.morning, time(8, 0))
    assert c.id is not None
    assert c.max_retries == 3 and c.retry_interval_s == 20
    assert c.kind == CampaignKind.morning


def test_active_campaigns(session):
    svc = SchedulerService(session)
    svc.create_campaign("A", CampaignKind.morning, time(8, 0))
    c2 = svc.create_campaign("B", CampaignKind.evening, time(20, 0))
    c2.active = False
    session.flush()
    assert len(svc.active_campaigns()) == 1


def test_call_answered_first_try(session):
    senior = _make_senior(session)
    svc = SchedulerService(session, originator=NullOriginator(should_answer=True))
    campaign = svc.create_campaign("Poranny", CampaignKind.morning, time(8, 0))
    attempt = svc.run_with_retries(campaign, senior)
    assert attempt.status == CallStatus.completed
    assert attempt.attempt_no == 1
    assert attempt.channel_id is not None


def test_retry_then_exhausted(session):
    senior = _make_senior(session)
    svc = SchedulerService(session, originator=NullOriginator(should_answer=False))
    campaign = svc.create_campaign("Poranny", CampaignKind.morning, time(8, 0), max_retries=3)
    attempt = svc.run_with_retries(campaign, senior)
    assert attempt.status == CallStatus.exhausted
    # powinny powstać 3 rekordy prób
    all_attempts = svc.attempts_for(senior.id)
    assert len(all_attempts) == 3
    assert all_attempts[-1].attempt_no == 3


def test_failed_call_retries(session):
    senior = _make_senior(session)
    svc = SchedulerService(session, originator=NullOriginator(fail=True))
    campaign = svc.create_campaign("Poranny", CampaignKind.morning, time(8, 0), max_retries=2)
    attempt = svc.run_with_retries(campaign, senior)
    assert attempt.status == CallStatus.exhausted
    assert len(svc.attempts_for(senior.id)) == 2


def test_originator_records_context(session):
    senior = _make_senior(session)
    orig = NullOriginator(should_answer=True)
    svc = SchedulerService(session, originator=orig)
    campaign = svc.create_campaign("Wieczorny", CampaignKind.evening, time(20, 0))
    svc.run_with_retries(campaign, senior)
    assert orig.calls[0]["context"] == "welfare-evening"
    assert orig.calls[0]["senior"] == senior.external_id


# ---------- APScheduler joby (F2.2) ----------
def test_welfare_scheduler_registers_jobs(session):
    from adam_modules.scheduler.jobs import WelfareScheduler
    svc = SchedulerService(session)
    svc.create_campaign("Poranny", CampaignKind.morning, time(8, 0))
    svc.create_campaign("Wieczorny", CampaignKind.evening, time(20, 0))
    session.commit()

    ws = WelfareScheduler()
    n = ws.load_all()
    assert n == 2
    assert len(ws.job_ids) == 2
    assert all(jid.startswith("campaign-") for jid in ws.job_ids)
