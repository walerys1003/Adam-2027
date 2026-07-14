"""Router panelu admina (ETAP 35) — flota / modele / providerzy / logi.

Wszystkie endpointy wymagają roli ADMIN (RBAC F11). Stan providerów jest
wyznaczany fail-safe z ENV (bez połączeń zewnętrznych).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from adam_modules.admin import (
    AdminService, FleetStatus, ModelKind, ModelStatus, LogLevel,
)
from adam_modules.auth import Role
from ..deps import get_db, require_role

router = APIRouter(prefix="/api/admin", tags=["admin (F11/panel)"])

# Cały panel admina za rolą ADMIN.
_admin = Depends(require_role(Role.ADMIN))


# ------------------------------------------------------------------ schematy
class FleetUnitIn(BaseModel):
    code: str
    name: str
    region: str = "eu-central"
    capacity: int = 50


class FleetStatusIn(BaseModel):
    status: FleetStatus
    active_calls: int | None = None


class FleetUnitOut(BaseModel):
    id: int
    code: str
    name: str
    region: str
    status: str
    active_calls: int
    capacity: int

    @classmethod
    def of(cls, u) -> "FleetUnitOut":
        return cls(id=u.id, code=u.code, name=u.name, region=u.region,
                   status=u.status.value, active_calls=u.active_calls,
                   capacity=u.capacity)


class ModelIn(BaseModel):
    kind: ModelKind
    name: str
    provider: str
    status: ModelStatus = ModelStatus.standby
    is_primary: bool = False


class ModelOut(BaseModel):
    id: int
    kind: str
    name: str
    provider: str
    status: str
    is_primary: bool

    @classmethod
    def of(cls, m) -> "ModelOut":
        return cls(id=m.id, kind=m.kind.value, name=m.name, provider=m.provider,
                   status=m.status.value, is_primary=m.is_primary)


class ProviderOut(BaseModel):
    key: str
    kind: str
    display_name: str
    state: str
    required_env: str | None = None

    @classmethod
    def of(cls, p) -> "ProviderOut":
        return cls(key=p.key, kind=p.kind.value, display_name=p.display_name,
                   state=p.state.value, required_env=p.required_env)


class LogIn(BaseModel):
    level: LogLevel = LogLevel.info
    source: str
    message: str
    actor: str | None = None


class LogOut(BaseModel):
    id: int
    level: str
    source: str
    message: str
    actor: str | None = None

    @classmethod
    def of(cls, e) -> "LogOut":
        return cls(id=e.id, level=e.level.value, source=e.source,
                   message=e.message, actor=e.actor)


# ------------------------------------------------------------------ FLOTA
@router.post("/fleet", response_model=FleetUnitOut, dependencies=[_admin])
def create_fleet_unit(body: FleetUnitIn, db: Session = Depends(get_db)):
    unit = AdminService(db).register_unit(
        body.code, body.name, region=body.region, capacity=body.capacity
    )
    return FleetUnitOut.of(unit)


@router.get("/fleet", response_model=list[FleetUnitOut], dependencies=[_admin])
def list_fleet(db: Session = Depends(get_db)):
    return [FleetUnitOut.of(u) for u in AdminService(db).fleet()]


@router.get("/fleet/summary", dependencies=[_admin])
def fleet_summary(db: Session = Depends(get_db)):
    return AdminService(db).fleet_summary()


@router.patch("/fleet/{unit_id}", response_model=FleetUnitOut, dependencies=[_admin])
def update_fleet_status(unit_id: int, body: FleetStatusIn, db: Session = Depends(get_db)):
    try:
        unit = AdminService(db).set_unit_status(
            unit_id, body.status, active_calls=body.active_calls
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return FleetUnitOut.of(unit)


# ------------------------------------------------------------------ MODELE AI
@router.post("/models", response_model=ModelOut, dependencies=[_admin])
def create_model(body: ModelIn, db: Session = Depends(get_db)):
    entry = AdminService(db).register_model(
        body.kind, body.name, body.provider,
        status=body.status, is_primary=body.is_primary,
    )
    return ModelOut.of(entry)


@router.get("/models", response_model=list[ModelOut], dependencies=[_admin])
def list_models(kind: ModelKind | None = Query(default=None), db: Session = Depends(get_db)):
    return [ModelOut.of(m) for m in AdminService(db).models(kind)]


@router.patch("/models/{model_id}/primary", response_model=ModelOut, dependencies=[_admin])
def set_primary_model(model_id: int, db: Session = Depends(get_db)):
    try:
        entry = AdminService(db).set_primary_model(model_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return ModelOut.of(entry)


# ------------------------------------------------------------------ PROVIDERZY
@router.post("/providers/sync", response_model=list[ProviderOut], dependencies=[_admin])
def sync_providers(db: Session = Depends(get_db)):
    return [ProviderOut.of(p) for p in AdminService(db).sync_providers()]


@router.get("/providers", response_model=list[ProviderOut], dependencies=[_admin])
def list_providers(db: Session = Depends(get_db)):
    svc = AdminService(db)
    providers = svc.providers()
    if not providers:
        providers = svc.sync_providers()  # pierwszy dostęp — zainicjuj katalog
    return [ProviderOut.of(p) for p in providers]


# ------------------------------------------------------------------ LOGI
@router.post("/logs", response_model=LogOut, dependencies=[_admin])
def create_log(body: LogIn, db: Session = Depends(get_db)):
    entry = AdminService(db).log(
        body.level, body.source, body.message, actor=body.actor
    )
    return LogOut.of(entry)


@router.get("/logs", response_model=list[LogOut], dependencies=[_admin])
def list_logs(
    level: LogLevel | None = Query(default=None),
    source: str | None = Query(default=None),
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
):
    return [LogOut.of(e) for e in AdminService(db).logs(level=level, source=source, limit=limit)]
