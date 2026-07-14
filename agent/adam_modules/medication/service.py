"""
MedicationService — zarządzanie lekami, harmonogramem, logami dawek
oraz liczenie adherence (F6.2).

MedGuard (F6.3): pominięta dawka mapuje się na trigger semafora
`missed_medication` (poziom żółty). Powtarzające się pominięcia w krótkim
oknie mogą podnieść poziom — decyzja należy do SemaphoreEngine (F3);
tu udostępniamy metody detekcji i wskaźnik adherence jako sygnał wejściowy.
"""
from __future__ import annotations

from datetime import datetime, time, timedelta

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from adam_modules.seniors.models import Senior
from .models import Medication, MedicationSchedule, DoseLog, DoseStatus, MedForm
from .schemas import MedicationCreate, MedicationUpdate, AdherenceReport

# Po ilu minutach zaplanowana, nieprzyjęta dawka staje się `missed`.
MISSED_AFTER_MINUTES = 90
# Ile pominięć w oknie (dni) traktujemy jako sygnał podwyższonego ryzyka.
MEDGUARD_MISSED_THRESHOLD = 3
MEDGUARD_WINDOW_DAYS = 7


class MedicationService:
    def __init__(self, session: Session):
        self.session = session

    # ---- leki ----
    def create(self, senior: Senior, data: MedicationCreate) -> Medication:
        med = Medication(
            senior_id=senior.id,
            name=data.name,
            dosage=data.dosage,
            form=data.form,
            instructions=data.instructions,
            prescriber=data.prescriber,
        )
        for sch in data.schedules:
            med.schedules.append(
                MedicationSchedule(at_time=sch.at_time, days_mask=sch.days_mask)
            )
        self.session.add(med)
        self.session.flush()
        return med

    def get(self, med_id: int) -> Medication | None:
        return self.session.get(Medication, med_id)

    def update(self, med: Medication, data: MedicationUpdate) -> Medication:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(med, field, value)
        self.session.flush()
        return med

    def list_for_senior(self, senior_id: int, only_active: bool = True) -> list[Medication]:
        stmt = select(Medication).where(Medication.senior_id == senior_id)
        if only_active:
            stmt = stmt.where(Medication.active.is_(True))
        return list(self.session.scalars(stmt))

    def deactivate(self, med: Medication) -> Medication:
        med.active = False
        self.session.flush()
        return med

    # ---- harmonogram / dawki ----
    def add_schedule(self, med: Medication, at_time: time, days_mask: int = 0b1111111) -> MedicationSchedule:
        sch = MedicationSchedule(medication_id=med.id, at_time=at_time, days_mask=days_mask)
        self.session.add(sch)
        self.session.flush()
        return sch

    def generate_doses_for_day(self, senior_id: int, day: datetime) -> list[DoseLog]:
        """Tworzy zaplanowane DoseLog dla wszystkich harmonogramów danego dnia."""
        weekday = day.weekday()
        created: list[DoseLog] = []
        for med in self.list_for_senior(senior_id):
            for sch in med.schedules:
                if not sch.active or not sch.occurs_on(weekday):
                    continue
                scheduled_at = datetime.combine(day.date(), sch.at_time)
                exists = self.session.scalar(
                    select(DoseLog).where(
                        and_(
                            DoseLog.medication_id == med.id,
                            DoseLog.scheduled_at == scheduled_at,
                        )
                    )
                )
                if exists:
                    continue
                dose = DoseLog(
                    medication_id=med.id,
                    senior_id=senior_id,
                    scheduled_at=scheduled_at,
                    status=DoseStatus.scheduled,
                )
                self.session.add(dose)
                created.append(dose)
        self.session.flush()
        return created

    def mark_taken(self, dose: DoseLog, when: datetime | None = None) -> DoseLog:
        when = when or datetime.utcnow()
        # spóźnienie ponad próg → late
        delta_min = (when - dose.scheduled_at).total_seconds() / 60.0
        dose.status = DoseStatus.late if delta_min > MISSED_AFTER_MINUTES else DoseStatus.taken
        dose.taken_at = when
        self.session.flush()
        return dose

    def mark_skipped(self, dose: DoseLog, note: str | None = None) -> DoseLog:
        dose.status = DoseStatus.skipped
        dose.note = note
        self.session.flush()
        return dose

    def sweep_missed(self, now: datetime | None = None) -> list[DoseLog]:
        """Oznacza jako `missed` dawki zaplanowane, których termin minął + próg."""
        now = now or datetime.utcnow()
        cutoff = now - timedelta(minutes=MISSED_AFTER_MINUTES)
        stmt = select(DoseLog).where(
            and_(
                DoseLog.status == DoseStatus.scheduled,
                DoseLog.scheduled_at < cutoff,
            )
        )
        missed = list(self.session.scalars(stmt))
        for dose in missed:
            dose.status = DoseStatus.missed
        self.session.flush()
        return missed

    # ---- adherence (F6.2) ----
    def adherence(self, senior_id: int, since: datetime, until: datetime | None = None) -> AdherenceReport:
        until = until or datetime.utcnow()
        stmt = select(DoseLog).where(
            and_(
                DoseLog.senior_id == senior_id,
                DoseLog.scheduled_at >= since,
                DoseLog.scheduled_at <= until,
            )
        )
        logs = list(self.session.scalars(stmt))
        taken = sum(1 for d in logs if d.status == DoseStatus.taken)
        late = sum(1 for d in logs if d.status == DoseStatus.late)
        missed = sum(1 for d in logs if d.status == DoseStatus.missed)
        skipped = sum(1 for d in logs if d.status == DoseStatus.skipped)
        total = len(logs)
        denom = total - skipped
        rate = (taken + late) / denom if denom > 0 else 1.0
        return AdherenceReport(
            senior_id=senior_id,
            total_doses=total,
            taken=taken,
            missed=missed,
            late=late,
            skipped=skipped,
            adherence_rate=round(rate, 4),
        )

    # ---- MedGuard (F6.3) ----
    def medguard_flag(self, senior_id: int, now: datetime | None = None) -> bool:
        """True, gdy liczba pominięć w oknie MEDGUARD_WINDOW_DAYS przekracza próg."""
        now = now or datetime.utcnow()
        since = now - timedelta(days=MEDGUARD_WINDOW_DAYS)
        stmt = select(DoseLog).where(
            and_(
                DoseLog.senior_id == senior_id,
                DoseLog.status == DoseStatus.missed,
                DoseLog.scheduled_at >= since,
            )
        )
        missed_count = len(list(self.session.scalars(stmt)))
        return missed_count >= MEDGUARD_MISSED_THRESHOLD
