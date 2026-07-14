"""SeniorService — logika CRUD profili seniorów (F1)."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from adam_modules.common.crypto import get_cipher
from .models import Senior
from .schemas import SeniorCreate, SeniorUpdate


class SeniorService:
    def __init__(self, session: Session):
        self.session = session

    # ---- create ----
    def create(self, data: SeniorCreate) -> Senior:
        senior = Senior(
            external_id=f"SR-{uuid.uuid4().hex[:8].upper()}",
            first_name=data.first_name,
            last_name=data.last_name,
            birth_date=data.birth_date,
            address=data.address,
            district=data.district,
            package=data.package,
        )
        if data.pesel:
            senior.pesel = data.pesel
        if data.phone:
            senior.phone = data.phone
        self.session.add(senior)
        self.session.flush()
        return senior

    # ---- read ----
    def get(self, senior_id: int) -> Senior | None:
        return self.session.get(Senior, senior_id)

    def get_by_external(self, external_id: str) -> Senior | None:
        return self.session.scalar(
            select(Senior).where(Senior.external_id == external_id)
        )

    def find_by_pesel(self, pesel: str) -> Senior | None:
        """Wyszukiwanie po PESEL przez blind index (bez odszyfrowywania)."""
        bidx = get_cipher().blind_index(pesel)
        return self.session.scalar(select(Senior).where(Senior.pesel_bidx == bidx))

    def list(self, *, active: bool | None = None, district: str | None = None,
             limit: int = 50, offset: int = 0) -> list[Senior]:
        stmt = select(Senior)
        if active is not None:
            stmt = stmt.where(Senior.active == active)
        if district:
            stmt = stmt.where(Senior.district == district)
        stmt = stmt.order_by(Senior.last_name).limit(limit).offset(offset)
        return list(self.session.scalars(stmt))

    def count(self, *, active: bool | None = None) -> int:
        stmt = select(Senior)
        if active is not None:
            stmt = stmt.where(Senior.active == active)
        return len(list(self.session.scalars(stmt)))

    # ---- update ----
    def update(self, senior_id: int, data: SeniorUpdate) -> Senior | None:
        senior = self.get(senior_id)
        if senior is None:
            return None
        payload = data.model_dump(exclude_unset=True)
        for key in ("first_name", "last_name", "birth_date", "address",
                    "district", "package", "semaphore", "active"):
            if key in payload:
                setattr(senior, key, payload[key])
        if "phone" in payload:
            senior.phone = payload["phone"]
        self.session.flush()
        return senior

    # ---- delete (soft — RODO F12) ----
    def deactivate(self, senior_id: int) -> bool:
        senior = self.get(senior_id)
        if senior is None:
            return False
        senior.active = False
        self.session.flush()
        return True
