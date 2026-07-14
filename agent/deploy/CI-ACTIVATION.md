# Aktywacja CI (ETAP 20)

Plik `agent/deploy/ci.yml.ready` to gotowy, zwalidowany workflow GitHub Actions
(backend: pytest + gate pokrycia ≥85% [aktualnie 95.39%] + Alembic; frontend:
typecheck + vitest + build).

GitHub App użyty przez agenta NIE ma uprawnienia `workflows`, dlatego pliku nie
można wypchnąć bezpośrednio do `.github/workflows/`. Aby aktywować CI, wykonaj
lokalnie (konto z uprawnieniem `workflows`):

```bash
mkdir -p .github/workflows
cp agent/deploy/ci.yml.ready .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "Aktywacja CI (ETAP 20)"
git push
```

Po wypchnięciu CI uruchamia się na każdy push/PR do `main`.
