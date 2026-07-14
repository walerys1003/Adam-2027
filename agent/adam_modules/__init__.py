"""
adam_modules — backend Adama (senior-care) nadbudowany na AVA v7.3.2.

Pakiet grupuje funkcje F1–F18 opisane w docs/MASTER-PLAN.md:
  F1  profile seniorów        (adam_modules.seniors)
  F3  semafor + eskalacja     (adam_modules.semaphore)
  F6  medication tracker      (adam_modules.medications)
  F8  crisis detection        (adam_modules.crisis)
  ...

Warstwa wspólna (baza, szyfrowanie, config) żyje w adam_modules.common.
Uruchomienie docelowe: Frankfurt DC (patrz docs/BACKEND-DEPLOY.md).
"""

__version__ = "0.1.0"
