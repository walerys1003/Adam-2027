"""
F12 — RODO (ochrona danych osobowych).

Retencja (nagrania 30d / transkrypty 12m / raporty 24m), soft-delete, eksport
danych (prawo dostępu art. 15/20), prawo do zapomnienia (art. 17) z anonimizacją
profilu i usunięciem danych powiązanych. Rejestr czynności przetwarzania (art. 30).
"""
from .models import DataProcessingLog, ProcessingAction, DataCategory
from .service import RodoService, RETENTION_DAYS

__all__ = [
    "DataProcessingLog", "ProcessingAction", "DataCategory",
    "RodoService", "RETENTION_DAYS",
]
