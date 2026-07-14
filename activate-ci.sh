#!/usr/bin/env bash
#
# activate-ci.sh — aktywacja workflow "Adam CI" (ETAP 34).
#
# DLACZEGO TEN SKRYPT ISTNIEJE
#   Token GitHub App, przez który pracuje agent, nie ma uprawnienia `workflow`,
#   więc nie mógł wypchnąć pliku do .github/workflows/. Definicja CI leży zatem
#   w repo pod ci-templates/adam-ci.yml. Ten skrypt kopiuje ją do docelowej
#   lokalizacji .github/workflows/adam-ci.yml, commituje i wypycha — używając
#   TWOICH uprawnień właściciela repo (scope `repo` + `workflow`).
#
# UŻYCIE
#   Uruchom z KATALOGU GŁÓWNEGO sklonowanego repozytorium:
#       bash activate-ci.sh
#   albo:
#       chmod +x activate-ci.sh && ./activate-ci.sh
#
#   Tryb bez wypychania (tylko przygotuj commit lokalnie):
#       bash activate-ci.sh --no-push
#
# WYMAGANIA
#   - uruchamiane wewnątrz repo Adam-2027 (git),
#   - uwierzytelnienie kontem z uprawnieniem `workflow`
#     (Personal Access Token classic ze scope `repo` + `workflow`,
#      albo GitHub CLI `gh auth login` z tym scope).
#
set -euo pipefail

# ── kolory (wyłączane, gdy brak terminala) ─────────────────────────────
if [ -t 1 ]; then
  R=$'\e[31m'; G=$'\e[32m'; Y=$'\e[33m'; B=$'\e[34m'; N=$'\e[0m'
else
  R=""; G=""; Y=""; B=""; N=""
fi
info()  { echo "${B}▸${N} $*"; }
ok()    { echo "${G}✓${N} $*"; }
warn()  { echo "${Y}!${N} $*"; }
err()   { echo "${R}✗${N} $*" >&2; }

PUSH=1
for arg in "$@"; do
  case "$arg" in
    --no-push) PUSH=0 ;;
    -h|--help)
      sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) err "Nieznany argument: $arg (użyj --no-push lub --help)"; exit 2 ;;
  esac
done

SRC="ci-templates/adam-ci.yml"
DEST_DIR=".github/workflows"
DEST="$DEST_DIR/adam-ci.yml"

# ── 1) sanity: jesteśmy w repo git? ────────────────────────────────────
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  err "To nie jest repozytorium git."
  err "Najpierw wejdź do sklonowanego repo, np.:"
  err "    git clone https://github.com/walerys1003/Adam-2027.git"
  err "    cd Adam-2027 && bash activate-ci.sh"
  exit 1
fi

# przejdź do katalogu głównego repo (żeby ścieżki względne działały)
cd "$(git rev-parse --show-toplevel)"
ok "Repozytorium: $(basename "$(pwd)")  (gałąź: $(git rev-parse --abbrev-ref HEAD))"

# ── 2) sanity: źródłowy plik istnieje? ─────────────────────────────────
if [ ! -f "$SRC" ]; then
  err "Brak pliku źródłowego: $SRC"
  err "Pobierz najnowszy stan gałęzi (git pull) i spróbuj ponownie."
  exit 1
fi
ok "Znaleziono szablon workflow: $SRC"

# ── 3) czyste drzewo robocze (unikamy przypadkowego wciągnięcia zmian) ──
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  warn "Drzewo robocze ma niezacommitowane zmiany (śledzone pliki)."
  warn "Skrypt zacommituje TYLKO plik workflow, ale zalecane jest czyste drzewo."
fi

# ── 4) skopiuj do .github/workflows/ (bez stopki instrukcyjnej) ─────────
mkdir -p "$DEST_DIR"
# usuwamy z docelowego pliku blok-stopkę „INSTALACJA…” (linie od markera w dół),
# żeby aktywny workflow był czysty; jeśli markera brak — kopiujemy 1:1.
if grep -q "INSTALACJA: skopiuj ten plik" "$SRC"; then
  # utnij plik na linii poprzedzającej blok-stopkę „# ──…/# INSTALACJA…”.
  # znajdź numer linii pierwszego separatora bezpośrednio przed markerem.
  marker_line="$(grep -n "INSTALACJA: skopiuj ten plik" "$SRC" | head -1 | cut -d: -f1)"
  # cofnij się nad ewentualną pustą linię i separator komentarza
  cut_line="$marker_line"
  prev="$((marker_line - 1))"
  if sed -n "${prev}p" "$SRC" | grep -q "^# ─"; then cut_line="$prev"; fi
  prev="$((cut_line - 1))"
  if [ -z "$(sed -n "${prev}p" "$SRC")" ]; then cut_line="$prev"; fi
  head -n "$((cut_line - 1))" "$SRC" > "$DEST"
  # fallback na czystą kopię, gdyby coś poszło nie tak:
  if [ ! -s "$DEST" ]; then cp "$SRC" "$DEST"; fi
else
  cp "$SRC" "$DEST"
fi
ok "Skopiowano do: $DEST"

# ── 5) walidacja YAML (jeśli dostępny python) ──────────────────────────
if command -v python3 >/dev/null 2>&1; then
  if python3 -c "import yaml,sys; yaml.safe_load(open('$DEST')); print('ok')" >/dev/null 2>&1; then
    ok "YAML poprawny."
  else
    warn "Nie udało się zwalidować YAML (brak modułu pyyaml?) — pomijam."
  fi
fi

# ── 6) commit ──────────────────────────────────────────────────────────
git add "$DEST"
if git diff --cached --quiet; then
  warn "Brak zmian do zacommitowania — workflow jest już aktualny."
else
  git commit -m "ETAP 34 — aktywacja Adam CI (workflow → .github/workflows/adam-ci.yml)"
  ok "Utworzono commit."
fi

# ── 7) push ─────────────────────────────────────────────────────────────
if [ "$PUSH" -eq 0 ]; then
  warn "Tryb --no-push: pomijam wypchnięcie. Wykonaj ręcznie: git push"
  exit 0
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
info "Wypycham na origin/$BRANCH ..."
if git push origin "$BRANCH"; then
  ok "Wypchnięto. CI 'Adam CI' powinno wystartować w zakładce Actions."
  echo
  echo "   Sprawdź: https://github.com/walerys1003/Adam-2027/actions"
else
  err "Push nie powiódł się."
  echo
  err "Najczęstsza przyczyna: brak uprawnienia 'workflow' na tokenie."
  err "Rozwiązanie — zaloguj się kontem z PAT (classic) mającym scope: repo + workflow."
  err "  1) GitHub → Settings → Developer settings → Personal access tokens (classic)"
  err "  2) Generate new token → zaznacz: [x] repo  [x] workflow"
  err "  3) git push  (login: walerys1003, hasło: wklej token)"
  echo
  err "Alternatywa (przeglądarka): Actions → New workflow → set up a workflow yourself,"
  err "wklej treść ci-templates/adam-ci.yml jako adam-ci.yml i Commit."
  exit 1
fi
