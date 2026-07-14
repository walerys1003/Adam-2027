#!/usr/bin/env sh
# ==================================================================
# Adam API — entrypoint kontenera (ETAP 15.2)
# 1) czeka na bazę (opcjonalnie), 2) migracje Alembic do head,
# 3) start gunicorn + uvicorn workers.
# ==================================================================
set -eu

: "${ADAM_API_WORKERS:=4}"
: "${ADAM_API_BIND:=0.0.0.0:8787}"
: "${ADAM_RUN_MIGRATIONS:=1}"

echo "[adam-api] start; bind=${ADAM_API_BIND} workers=${ADAM_API_WORKERS}"

if [ "${ADAM_RUN_MIGRATIONS}" = "1" ]; then
    echo "[adam-api] applying Alembic migrations (head)…"
    # env.py czyta ADAM_DATABASE_URL — migracje na docelowej bazie (PostgreSQL prod)
    ( cd /app/adam_modules/migrations && python -m alembic upgrade head )
    echo "[adam-api] migrations OK"
else
    echo "[adam-api] ADAM_RUN_MIGRATIONS=0 — pomijam migracje"
fi

echo "[adam-api] launching gunicorn…"
exec gunicorn adam_modules.api.app:app \
    -k uvicorn.workers.UvicornWorker \
    -w "${ADAM_API_WORKERS}" \
    -b "${ADAM_API_BIND}" \
    --access-logfile - \
    --error-logfile - \
    --timeout 60 \
    --graceful-timeout 30
