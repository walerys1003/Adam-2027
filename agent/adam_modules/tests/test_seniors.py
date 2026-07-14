"""Testy F1 — profile seniorów + szyfrowanie PII."""
import pytest

from adam_modules.common.crypto import FieldCipher
from adam_modules.seniors import SeniorService
from adam_modules.seniors.models import Package, SemaphoreLevel
from adam_modules.seniors.schemas import SeniorCreate, SeniorUpdate, SeniorOut


# ---------- Szyfrowanie (F1.4) ----------
def test_cipher_roundtrip():
    c = FieldCipher("klucz-testowy")
    token = c.encrypt("44051401359")
    assert token != "44051401359"
    assert c.decrypt(token) == "44051401359"


def test_cipher_none():
    c = FieldCipher("k")
    assert c.encrypt(None) is None
    assert c.decrypt(None) is None


def test_blind_index_deterministic():
    c = FieldCipher("k")
    assert c.blind_index("48123456789") == c.blind_index("48123456789")


def test_wrong_key_fails():
    token = FieldCipher("klucz-a").encrypt("tajne")
    with pytest.raises(ValueError):
        FieldCipher("klucz-b").decrypt(token)


# ---------- CRUD (F1.3) ----------
def test_create_and_get(session):
    svc = SeniorService(session)
    s = svc.create(SeniorCreate(first_name="Jan", last_name="Kowalski",
                                package=Package.premium, phone="+48123456789"))
    assert s.id is not None
    assert s.external_id.startswith("SR-")
    assert s.full_name == "Jan Kowalski"
    # PII zaszyfrowane w kolumnie, odszyfrowane przez property
    assert s._phone_enc != "+48123456789"
    assert s.phone == "+48123456789"


def test_pii_stored_encrypted(session):
    svc = SeniorService(session)
    s = svc.create(SeniorCreate(first_name="Anna", last_name="Nowak",
                                pesel="44051401359"))
    session.commit()
    # bezpośrednio z bazy — kolumna nie zawiera jawnego PESEL
    assert s._pesel_enc is not None
    assert "44051401359" not in s._pesel_enc
    assert s.pesel == "44051401359"


def test_find_by_pesel_blind_index(session):
    svc = SeniorService(session)
    svc.create(SeniorCreate(first_name="Ewa", last_name="Wiśniewska",
                            pesel="44051401359"))
    session.commit()
    found = svc.find_by_pesel("44051401359")
    assert found is not None
    assert found.last_name == "Wiśniewska"


def test_invalid_pesel_rejected():
    with pytest.raises(ValueError):
        SeniorCreate(first_name="X", last_name="Y", pesel="12345678900")  # zła suma


def test_update(session):
    svc = SeniorService(session)
    s = svc.create(SeniorCreate(first_name="Jan", last_name="Kowalski"))
    updated = svc.update(s.id, SeniorUpdate(semaphore=SemaphoreLevel.red, district="Jeżyce"))
    assert updated.semaphore == SemaphoreLevel.red
    assert updated.district == "Jeżyce"


def test_soft_delete(session):
    svc = SeniorService(session)
    s = svc.create(SeniorCreate(first_name="Jan", last_name="Kowalski"))
    assert svc.deactivate(s.id) is True
    assert svc.get(s.id).active is False


def test_list_and_count(session):
    svc = SeniorService(session)
    for i in range(5):
        svc.create(SeniorCreate(first_name=f"S{i}", last_name="Test",
                                district="Grunwald" if i % 2 else "Wilda"))
    session.commit()
    assert svc.count() == 5
    grunwald = svc.list(district="Grunwald")
    assert len(grunwald) == 2


def test_out_schema_masks_pii(session):
    svc = SeniorService(session)
    s = svc.create(SeniorCreate(first_name="Jan", last_name="Kowalski",
                                pesel="44051401359", phone="+48123456789"))
    out = SeniorOut.from_model(s)
    assert out.pesel_masked.endswith("1359")
    assert "44051401359" not in (out.pesel_masked or "")
    assert out.phone_masked.endswith("789")


def test_age_computed(session):
    from datetime import date
    svc = SeniorService(session)
    s = svc.create(SeniorCreate(first_name="Jan", last_name="Kowalski",
                                birth_date=date(1945, 6, 1)))
    assert s.age is not None and s.age >= 79
