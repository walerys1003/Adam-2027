"""
Warstwa bazy danych (SQLAlchemy 2.0).

Docelowo PostgreSQL (Frankfurt DC), lokalnie/test SQLite.
URL sterowany zmienną ADAM_DATABASE_URL (domyślnie sqlite in-memory dla testów).
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    """Bazowa klasa deklaratywna dla wszystkich modeli Adama."""


_engine = None
_SessionFactory: sessionmaker | None = None


def init_engine(url: str | None = None, echo: bool = False):
    """Inicjalizuje silnik i fabrykę sesji. Idempotentne."""
    global _engine, _SessionFactory
    url = url or os.getenv("ADAM_DATABASE_URL", "sqlite:///:memory:")
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine_kwargs: dict = {"echo": echo, "future": True, "connect_args": connect_args}
    # SQLite in-memory: wszystkie sesje muszą współdzielić JEDNO połączenie,
    # inaczej każda sesja dostaje pustą bazę (brak tabel). Wymagane dla API,
    # które otwiera nową sesję per-request.
    if url.startswith("sqlite") and (":memory:" in url or url == "sqlite://"):
        engine_kwargs["poolclass"] = StaticPool
    _engine = create_engine(url, **engine_kwargs)
    _SessionFactory = sessionmaker(bind=_engine, expire_on_commit=False, class_=Session)
    return _engine


def _ensure_init():
    if _SessionFactory is None:
        init_engine()


def get_session() -> Session:
    """Zwraca nową sesję (wywołujący odpowiada za close)."""
    _ensure_init()
    assert _SessionFactory is not None
    return _SessionFactory()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Kontekst transakcyjny: commit przy sukcesie, rollback przy błędzie."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_all():
    """Tworzy wszystkie tabele (dev/test; produkcja używa Alembic)."""
    _ensure_init()
    assert _engine is not None
    # import modeli, by zarejestrowały się w Base.metadata
    from adam_modules.seniors import models as _senior_models  # noqa: F401
    from adam_modules.scheduler import models as _sched_models  # noqa: F401
    from adam_modules.semaphore import models as _sem_models  # noqa: F401
    from adam_modules.medication import models as _med_models  # noqa: F401
    from adam_modules.memory import models as _memory_models  # noqa: F401
    from adam_modules.family import models as _family_models  # noqa: F401
    from adam_modules.wearables import models as _wear_models  # noqa: F401
    from adam_modules.marketplace import models as _market_models  # noqa: F401
    from adam_modules.rodo import models as _rodo_models  # noqa: F401
    from adam_modules.compliance import models as _compliance_models  # noqa: F401
    from adam_modules.emergency import models as _emergency_models  # noqa: F401
    from adam_modules.qa import models as _qa_models  # noqa: F401
    from adam_modules.admin import models as _admin_models  # noqa: F401

    Base.metadata.create_all(_engine)
