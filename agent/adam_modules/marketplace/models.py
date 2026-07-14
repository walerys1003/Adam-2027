"""
Modele F11 — Marketplace usług dla seniorów.

Partner — dostawca usługi (zweryfikowany NIP/OC), w jednej z 10 kategorii.
Service — konkretna usługa partnera (cena, opis).
Order   — zamówienie usługi przez seniora/opiekuna (okno anulowania 30 min).
"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import String, Integer, Float, Boolean, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from adam_modules.common.db import Base


class ServiceCategory(str, enum.Enum):
    """10 kategorii marketplace."""
    medical_care = "medical_care"          # opieka medyczna / pielęgniarska
    home_help = "home_help"                # pomoc domowa / sprzątanie
    meals = "meals"                        # catering / posiłki
    transport = "transport"                # transport / dowozy
    physiotherapy = "physiotherapy"        # rehabilitacja / fizjoterapia
    shopping = "shopping"                  # zakupy / dostawy
    companionship = "companionship"        # towarzystwo / wsparcie
    repairs = "repairs"                    # drobne naprawy
    hairdressing = "hairdressing"          # fryzjer / kosmetyka
    legal_admin = "legal_admin"            # pomoc prawna / urzędowa


class PartnerStatus(str, enum.Enum):
    pending = "pending"        # zgłoszony, przed weryfikacją
    verified = "verified"      # zweryfikowany (NIP + OC)
    suspended = "suspended"    # zawieszony (anty-fraud)
    rejected = "rejected"


class OrderStatus(str, enum.Enum):
    created = "created"            # utworzone (okno anulowania)
    confirmed = "confirmed"        # potwierdzone przez partnera
    cancelled = "cancelled"        # anulowane w oknie
    in_progress = "in_progress"
    completed = "completed"
    disputed = "disputed"          # reklamacja / anty-fraud


class Partner(Base):
    __tablename__ = "partners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(160))
    category: Mapped[ServiceCategory] = mapped_column(Enum(ServiceCategory), index=True)
    nip: Mapped[str | None] = mapped_column(String(10), nullable=True)          # NIP (10 cyfr)
    insurance_oc: Mapped[bool] = mapped_column(Boolean, default=False)          # polisa OC
    status: Mapped[PartnerStatus] = mapped_column(Enum(PartnerStatus), default=PartnerStatus.pending, index=True)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    fraud_flags: Mapped[int] = mapped_column(Integer, default=0)                # licznik sygnałów fraudu
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    services: Mapped[list["Service"]] = relationship(
        back_populates="partner", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Partner {self.name!r} {self.category.value} {self.status.value}>"


class Service(Base):
    __tablename__ = "marketplace_services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    partner_id: Mapped[int] = mapped_column(ForeignKey("partners.id"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_pln: Mapped[float] = mapped_column(Float, default=0.0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    partner: Mapped["Partner"] = relationship(back_populates="services")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Service {self.title!r} {self.price_pln}zł>"


class Order(Base):
    __tablename__ = "marketplace_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("marketplace_services.id"), index=True)
    senior_id: Mapped[int] = mapped_column(ForeignKey("seniors.id"), index=True)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.created, index=True)
    amount_pln: Mapped[float] = mapped_column(Float, default=0.0)
    note: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    cancellable_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Order s{self.senior_id} svc{self.service_id} {self.status.value}>"
