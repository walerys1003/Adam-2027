"""Fixtury pytest dla adam_modules."""
import os
import sys
from pathlib import Path

import pytest

# Dodaj katalog agent/ do sys.path, by `import adam_modules` działał.
AGENT_ROOT = Path(__file__).resolve().parents[2]
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

os.environ.setdefault("ADAM_PII_KEY", "test-key-adam-2027")

from adam_modules.common import db as db_mod  # noqa: E402


@pytest.fixture()
def session():
    """Świeża baza SQLite in-memory na każdy test."""
    db_mod.init_engine("sqlite:///:memory:")
    db_mod.create_all()
    s = db_mod.get_session()
    try:
        yield s
    finally:
        s.close()
