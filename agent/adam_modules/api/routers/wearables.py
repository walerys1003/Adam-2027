"""Router wearables (F10) — urządzenia, ingest pomiarów, najnowsze vitals, breaches."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from adam_modules.seniors import SeniorService
from adam_modules.wearables import (
    WearableService, WearableVendor, VitalType,
)
from ..deps import get_db

router = APIRouter(prefix="/api/seniors/{senior_id}/wearables", tags=["wearables (F10)"])


def _senior_or_404(db: Session, senior_id: int):
    senior = SeniorService(db).get(senior_id)
    if senior is None:
        raise HTTPException(status_code=404, detail="Senior nie znaleziony")
    return senior


class DeviceIn(BaseModel):
    vendor: WearableVendor
    external_id: str
    model: str | None = None


class DeviceOut(BaseModel):
    id: int
    vendor: str
    external_id: str
    model: str | None = None
    last_sync_at: datetime | None = None


class ReadingIn(BaseModel):
    device_id: int
    vital_type: VitalType
    value: float
    measured_at: datetime | None = None


class ReadingOut(BaseModel):
    id: int
    vital_type: str
    value: float
    measured_at: datetime
    breached: bool
    integrity_ok: bool


@router.get("/devices", response_model=list[DeviceOut])
def list_devices(senior_id: int, db: Session = Depends(get_db)):
    _senior_or_404(db, senior_id)
    return [
        DeviceOut(id=d.id, vendor=d.vendor.value, external_id=d.external_id,
                  model=d.model, last_sync_at=d.last_sync_at)
        for d in WearableService(db).devices(senior_id)
    ]


@router.post("/devices", response_model=DeviceOut, status_code=201)
def register_device(senior_id: int, data: DeviceIn, db: Session = Depends(get_db)):
    senior = _senior_or_404(db, senior_id)
    dev = WearableService(db).register_device(senior, data.vendor, data.external_id, data.model)
    db.flush()
    return DeviceOut(id=dev.id, vendor=dev.vendor.value, external_id=dev.external_id,
                     model=dev.model, last_sync_at=dev.last_sync_at)


@router.post("/readings", response_model=ReadingOut, status_code=201)
def ingest_reading(senior_id: int, data: ReadingIn, db: Session = Depends(get_db)):
    _senior_or_404(db, senior_id)
    svc = WearableService(db)
    device = next((d for d in svc.devices(senior_id) if d.id == data.device_id), None)
    if device is None:
        raise HTTPException(status_code=404, detail="Urządzenie nie znalezione dla tego seniora")
    r = svc.ingest_reading(device, data.vital_type, data.value, data.measured_at)
    db.flush()
    return ReadingOut(id=r.id, vital_type=r.vital_type.value, value=r.value,
                      measured_at=r.measured_at, breached=r.breached,
                      integrity_ok=svc.verify_integrity(r))


@router.get("/latest/{vital_type}", response_model=ReadingOut)
def latest(senior_id: int, vital_type: VitalType, db: Session = Depends(get_db)):
    _senior_or_404(db, senior_id)
    svc = WearableService(db)
    r = svc.latest(senior_id, vital_type)
    if r is None:
        raise HTTPException(status_code=404, detail="Brak pomiarów tego typu")
    return ReadingOut(id=r.id, vital_type=r.vital_type.value, value=r.value,
                      measured_at=r.measured_at, breached=r.breached,
                      integrity_ok=svc.verify_integrity(r))


@router.get("/breaches", response_model=list[ReadingOut])
def breaches(senior_id: int, limit: int = 50, db: Session = Depends(get_db)):
    _senior_or_404(db, senior_id)
    svc = WearableService(db)
    return [
        ReadingOut(id=r.id, vital_type=r.vital_type.value, value=r.value,
                   measured_at=r.measured_at, breached=r.breached,
                   integrity_ok=svc.verify_integrity(r))
        for r in svc.breaches(senior_id, limit=limit)
    ]
