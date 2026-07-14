"""Testy F13 — AI Act compliance (rejestr systemu + log ujawnień)."""
from adam_modules.seniors import SeniorService
from adam_modules.seniors.schemas import SeniorCreate
from adam_modules.compliance import ComplianceService, DisclosureChannel, SYSTEM_REGISTER


def _senior(session):
    return SeniorService(session).create(
        SeniorCreate(first_name="Jan", last_name="Kowalski", phone="+48123456789")
    )


def test_system_register_has_required_fields():
    reg = ComplianceService.system_register()
    for key in ("system_name", "provider", "purpose", "risk_class",
                "human_oversight", "transparency"):
        assert key in reg
    assert reg["system_name"] == "Adam"


def test_record_disclosure_default_text(session):
    s = _senior(session)
    svc = ComplianceService(session)
    log = svc.record_disclosure(s, "conv-001", channel=DisclosureChannel.voice)
    assert log.disclosed is True
    assert log.disclosure_text and "nie jestem człowiekiem" in log.disclosure_text.lower()


def test_assert_disclosed(session):
    s = _senior(session)
    svc = ComplianceService(session)
    assert svc.assert_disclosed("conv-002") is False
    svc.record_disclosure(s, "conv-002")
    assert svc.assert_disclosed("conv-002") is True


def test_not_disclosed_flag(session):
    s = _senior(session)
    svc = ComplianceService(session)
    svc.record_disclosure(s, "conv-003", disclosed=False)
    assert svc.assert_disclosed("conv-003") is False


def test_disclosure_history(session):
    s = _senior(session)
    svc = ComplianceService(session)
    svc.record_disclosure(s, "conv-a")
    svc.record_disclosure(s, "conv-b")
    assert len(svc.disclosure_history(s.id)) == 2
