"""
RodoService — retencja, soft-delete, eksport, prawo do zapomnienia (F12).

Polityka retencji (F12.1):
- nagrania rozmów: 30 dni
- transkrypcje: 12 miesięcy
- raporty semafora/zdrowotne: 24 miesiące

Prawo do zapomnienia (F12.2): usuwa/anonimizuje dane seniora we wszystkich
modułach (pamięć, powiadomienia, pomiary, zdarzenia) i loguje operację
w rejestrze czynności przetwarzania (art. 30 RODO).
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from adam_modules.seniors.models import Senior
from .models import DataProcessingLog, ProcessingAction, DataCategory

# Okresy retencji (dni)
RETENTION_DAYS = {
    DataCategory.recordings: 30,
    DataCategory.transcripts: 365,
    DataCategory.reports: 730,
}


class RodoService:
    def __init__(self, session: Session):
        self.session = session

    # ---- rejestr czynności ----
    def log(self, senior_id: int, action: ProcessingAction,
            category: DataCategory | None = None, actor: str | None = None,
            detail: str | None = None, legal_basis: str | None = None) -> DataProcessingLog:
        entry = DataProcessingLog(
            senior_id=senior_id, action=action, category=category,
            actor=actor, detail=detail,
            legal_basis=legal_basis or "art. 6 ust. 1 lit. b RODO",
        )
        self.session.add(entry)
        self.session.flush()
        return entry

    def audit_trail(self, senior_id: int, limit: int = 100) -> list[DataProcessingLog]:
        return list(self.session.scalars(
            select(DataProcessingLog).where(DataProcessingLog.senior_id == senior_id)
            .order_by(DataProcessingLog.id.desc()).limit(limit)
        ))

    # ---- retencja ----
    @staticmethod
    def is_expired(category: DataCategory, created_at: datetime, now: datetime | None = None) -> bool:
        days = RETENTION_DAYS.get(category)
        if days is None:
            return False
        now = now or datetime.utcnow()
        return created_at < (now - timedelta(days=days))

    # ---- eksport (prawo dostępu, art. 15/20) ----
    def export_data(self, senior: Senior, actor: str | None = None) -> dict:
        """Zwraca komplet danych seniora w formacie przenośnym (JSON-serializowalne)."""
        data: dict = {
            "senior": {
                "external_id": senior.external_id,
                "first_name": senior.first_name,
                "last_name": senior.last_name,
                "birth_date": senior.birth_date.isoformat() if senior.birth_date else None,
                "address": senior.address,
                "district": senior.district,
                "package": senior.package.value,
                "semaphore": senior.semaphore.value,
                "pesel": senior.pesel,
                "phone": senior.phone,
            },
            "exported_at": datetime.utcnow().isoformat(),
        }
        # dołącz dane z modułów, jeśli tabele istnieją
        data["memory"] = self._export_memory(senior.id)
        data["notifications"] = self._export_notifications(senior.id)
        data["vitals"] = self._export_vitals(senior.id)
        data["semaphore_events"] = self._export_semaphore(senior.id)

        self.log(senior.id, ProcessingAction.export, actor=actor,
                 detail=f"export {len(data)} sekcji", legal_basis="art. 15/20 RODO")
        return data

    def export_json(self, senior: Senior, actor: str | None = None) -> str:
        return json.dumps(self.export_data(senior, actor), ensure_ascii=False, indent=2)

    def _export_memory(self, senior_id: int) -> list[dict]:
        try:
            from adam_modules.memory.models import MemoryChunk
        except ImportError:  # pragma: no cover
            return []
        rows = self.session.scalars(select(MemoryChunk).where(MemoryChunk.senior_id == senior_id))
        return [{"kind": r.kind.value, "content": r.content, "created_at": r.created_at.isoformat() if r.created_at else None} for r in rows]

    def _export_notifications(self, senior_id: int) -> list[dict]:
        try:
            from adam_modules.family.models import Notification
        except ImportError:  # pragma: no cover
            return []
        rows = self.session.scalars(select(Notification).where(Notification.senior_id == senior_id))
        return [{"level": r.level.value, "title": r.title, "status": r.status.value} for r in rows]

    def _export_vitals(self, senior_id: int) -> list[dict]:
        try:
            from adam_modules.wearables.models import VitalReading
        except ImportError:  # pragma: no cover
            return []
        rows = self.session.scalars(select(VitalReading).where(VitalReading.senior_id == senior_id))
        return [{"type": r.vital_type.value, "value": r.value, "measured_at": r.measured_at.isoformat()} for r in rows]

    def _export_semaphore(self, senior_id: int) -> list[dict]:
        try:
            from adam_modules.semaphore.models import SemaphoreEvent
        except ImportError:  # pragma: no cover
            return []
        rows = self.session.scalars(select(SemaphoreEvent).where(SemaphoreEvent.senior_id == senior_id))
        return [{"new_level": r.new_level.value, "trigger": r.trigger.value} for r in rows]

    # ---- soft-delete ----
    def soft_delete(self, senior: Senior, actor: str | None = None) -> Senior:
        """Dezaktywuje profil bez fizycznego usunięcia (okres karencji)."""
        senior.active = False
        self.log(senior.id, ProcessingAction.soft_delete, category=DataCategory.profile, actor=actor)
        self.session.flush()
        return senior

    # ---- prawo do zapomnienia (art. 17) ----
    def erase_senior(self, senior: Senior, actor: str | None = None) -> dict:
        """
        Trwale usuwa dane powiązane i anonimizuje profil. Zwraca licznik usuniętych
        rekordów per kategoria. Rejestr czynności (DataProcessingLog) zostaje —
        jako dowód wykonania obowiązku (nie zawiera danych wrażliwych).
        """
        counts: dict[str, int] = {}
        senior_id = senior.id

        counts["memory"] = self._erase_from("adam_modules.memory.models", "MemoryChunk", senior_id)
        counts["notifications"] = self._erase_from("adam_modules.family.models", "Notification", senior_id)
        counts["family_members"] = self._erase_from("adam_modules.family.models", "FamilyMember", senior_id)
        counts["vitals"] = self._erase_from("adam_modules.wearables.models", "VitalReading", senior_id)
        counts["devices"] = self._erase_from("adam_modules.wearables.models", "WearableDevice", senior_id)
        counts["semaphore_events"] = self._erase_from("adam_modules.semaphore.models", "SemaphoreEvent", senior_id)
        counts["dose_logs"] = self._erase_from("adam_modules.medication.models", "DoseLog", senior_id)

        # anonimizacja profilu (zachowujemy wiersz dla integralności FK logów)
        senior.first_name = "ANONIM"
        senior.last_name = "ANONIM"
        senior.pesel = None
        senior.phone = None
        senior.address = None
        senior.active = False

        self.log(senior_id, ProcessingAction.erase, category=DataCategory.profile,
                 actor=actor, detail=json.dumps(counts), legal_basis="art. 17 RODO")
        self.session.flush()
        return counts

    def _erase_from(self, module_path: str, class_name: str, senior_id: int) -> int:
        import importlib
        try:
            mod = importlib.import_module(module_path)
            model = getattr(mod, class_name)
        except (ImportError, AttributeError):  # pragma: no cover
            return 0
        rows = list(self.session.scalars(select(model).where(model.senior_id == senior_id)))
        for r in rows:
            self.session.delete(r)
        self.session.flush()
        return len(rows)
