"""Alembic env dla adam_modules — autogeneracja z Base.metadata."""
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# ścieżka do pakietu agent/
AGENT_ROOT = Path(__file__).resolve().parents[2]
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from adam_modules.common.db import Base  # noqa: E402
# import modeli, by zarejestrowały się w metadata
from adam_modules.seniors import models as _seniors  # noqa: E402,F401
from adam_modules.scheduler import models as _scheduler  # noqa: E402,F401
from adam_modules.semaphore import models as _semaphore  # noqa: E402,F401
from adam_modules.medication import models as _medication  # noqa: E402,F401
from adam_modules.memory import models as _memory  # noqa: E402,F401
from adam_modules.family import models as _family  # noqa: E402,F401
from adam_modules.wearables import models as _wearables  # noqa: E402,F401
from adam_modules.marketplace import models as _marketplace  # noqa: E402,F401
from adam_modules.rodo import models as _rodo  # noqa: E402,F401

config = context.config

# URL z env ma priorytet
_env_url = os.getenv("ADAM_DATABASE_URL")
if _env_url:
    config.set_main_option("sqlalchemy.url", _env_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True,
                      dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata,
                          render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
