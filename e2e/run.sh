#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0
#
# End-to-end run on Windows (Git Bash) with nothing but what the repo already needs:
#
#   Postgres     - a throwaway cluster from the installed Postgres binaries, port 5433,
#                  trust auth, recreated every run. Never touches your real server.
#   Redis        - fakeredis in server mode (pip, inside the project venv).
#   Meilisearch  - the official single-file Windows binary, fetched into e2e/.tools.
#   API          - uvicorn from the pipenv venv, port 8010 (8000 is in a Windows
#                  reserved port range on the machines this was built on).
#   Frontend     - vite dev on 3000, proxied to the API.
#   Browser      - Playwright driving the installed Edge; no browser download.
#
# Usage:  bash e2e/run.sh [playwright args...]
#         bash e2e/run.sh e2e/anon-game.e2e.ts        # one spec
#         KEEP_UP=1 bash e2e/run.sh --list            # leave the stack running after
#
# Everything it creates lives in e2e/.data (gitignored) and is wiped on the next run.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# E2E_DATA and PG_PORT can be overridden so a second stack can run beside one another
# session left up: `E2E_DATA=e2e/.data2 PG_PORT=5434 bash e2e/run.sh`. The other ports
# stay fixed because the frontend and specs assume them, so stop that stack's API and
# Vite first (`bash e2e/stop.sh`); it is only its Postgres that can be left alone.
DATA="${E2E_DATA:-$ROOT/e2e/.data}"
case "$DATA" in /*|?:*) ;; *) DATA="$ROOT/$DATA" ;; esac
TOOLS="$ROOT/e2e/.tools"
PG_PORT="${PG_PORT:-5433}"
REDIS_PORT=6380
MEILI_PORT=7701
API_PORT=8010
WEB_PORT=3000

log() { printf '\033[1;32m[e2e]\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m[e2e]\033[0m %s\n' "$*" >&2; exit 1; }

# ---- toolchain discovery ---------------------------------------------------------
PG_BIN="$(dirname "$(command -v pg_ctl 2>/dev/null || ls -d /c/Program\ Files/PostgreSQL/*/bin/pg_ctl.exe 2>/dev/null | tail -1)")"
[ -x "$PG_BIN/pg_ctl" ] || [ -x "$PG_BIN/pg_ctl.exe" ] || die "Postgres binaries not found (install Postgres, or put its bin/ on PATH)"
VENV_RAW="$(cd "$ROOT" && python -m pipenv --venv 2>/dev/null)" || die "no pipenv venv; run 'python -m pipenv sync --dev' first"
VENV="$(cygpath -u "$VENV_RAW" 2>/dev/null || printf '%s' "$VENV_RAW")"
PY="$VENV/Scripts/python.exe"; [ -x "$PY" ] || PY="$VENV/bin/python"
PNPM="$(command -v pnpm || echo "$APPDATA/npm/pnpm")"

# ---- teardown --------------------------------------------------------------------
PIDS=()
cleanup() {
  [ "${KEEP_UP:-}" = 1 ] && { log "KEEP_UP=1: leaving the stack running"; return; }
  log "stopping services"
  for pid in "${PIDS[@]:-}"; do
    [ -n "$pid" ] || continue
    # Git Bash's kill does not reach native grandchildren (pnpm -> node -> vite);
    # taskkill /T takes the whole tree.
    winpid="$(cat "/proc/$pid/winpid" 2>/dev/null || true)"
    if [ -n "$winpid" ]; then taskkill //F //T //PID "$winpid" >/dev/null 2>&1 || true; else kill "$pid" 2>/dev/null || true; fi
  done
  "$PG_BIN/pg_ctl" -D "$DATA/pg" -m fast stop >/dev/null 2>&1 || true
}
trap cleanup EXIT

port_busy() { (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null; }
wait_http() { # url, name
  for _ in $(seq 1 90); do curl -fs -o /dev/null "$1" && return 0; sleep 1; done
  die "$2 did not come up; see $DATA/$2.log"
}

for p in $PG_PORT $REDIS_PORT $MEILI_PORT $API_PORT $WEB_PORT; do
  port_busy "$p" && die "port $p is already in use (a previous run with KEEP_UP=1?)"
done

# ---- fresh state -----------------------------------------------------------------
log "resetting $DATA"
"$PG_BIN/pg_ctl" -D "$DATA/pg" -m fast stop >/dev/null 2>&1 || true
rm -rf "$DATA"
mkdir -p "$DATA/storage" "$DATA/meili" "$TOOLS"

# ---- dependencies that live outside the lockfile ---------------------------------
if [ ! -x "$TOOLS/meilisearch.exe" ]; then
  log "fetching Meilisearch (one-off, ~350 MB)"
  curl -fL --retry 3 -o "$TOOLS/meilisearch.exe" \
    https://github.com/meilisearch/meilisearch/releases/latest/download/meilisearch-windows-amd64.exe
fi
"$PY" -c "import fakeredis" 2>/dev/null || { log "installing fakeredis into the venv"; "$PY" -m pip install -q "fakeredis[lua]"; }

# ---- Postgres --------------------------------------------------------------------
log "starting Postgres on $PG_PORT"
"$PG_BIN/initdb" -D "$DATA/pg" -U postgres --auth=trust -E UTF8 --no-locale >"$DATA/initdb.log" 2>&1
# pg_ctl leaves the server holding its stdout; without the redirect this hangs.
"$PG_BIN/pg_ctl" -D "$DATA/pg" -o "-p $PG_PORT -c listen_addresses=127.0.0.1" -l "$DATA/pg.log" -w start >/dev/null 2>&1 </dev/null
"$PG_BIN/psql" -h 127.0.0.1 -p $PG_PORT -U postgres -qc "create database frogquiz;"

# ---- Redis, Meilisearch ----------------------------------------------------------
log "starting fakeredis on $REDIS_PORT and Meilisearch on $MEILI_PORT"
"$PY" "$ROOT/e2e/redis_server.py" $REDIS_PORT >"$DATA/redis.log" 2>&1 & PIDS+=($!)
"$TOOLS/meilisearch.exe" --http-addr 127.0.0.1:$MEILI_PORT --db-path "$DATA/meili/data.ms" \
  --no-analytics --env development >"$DATA/meili.log" 2>&1 & PIDS+=($!)
wait_http "http://127.0.0.1:$MEILI_PORT/health" meili

# ---- API -------------------------------------------------------------------------
set -a; . "$ROOT/e2e/e2e.env"; set +a
export DB_URL="postgresql://postgres@127.0.0.1:$PG_PORT/frogquiz"
export STORAGE_PATH="$DATA/storage"
# Stand-in for python-magic, whose Windows DLL crashes on import. See e2e/shims/magic.py.
export PYTHONPATH="$ROOT/e2e/shims${PYTHONPATH:+:$PYTHONPATH}"
cd "$ROOT"
log "migrating"
"$PY" -m alembic upgrade head >"$DATA/alembic.log" 2>&1 || die "migrations failed; see $DATA/alembic.log"
log "starting API on $API_PORT"
"$PY" -m uvicorn frogquiz:app --host 127.0.0.1 --port $API_PORT >"$DATA/api.log" 2>&1 & PIDS+=($!)
wait_http "http://127.0.0.1:$API_PORT/api/docs" api

# ---- frontend --------------------------------------------------------------------
log "starting frontend on $WEB_PORT"
cd "$ROOT/frontend"
# API_URL is for server-side loaders (Docker sets it; without it /view/[id] 500s).
API_URL="http://127.0.0.1:$API_PORT" API_PROXY_TARGET="http://127.0.0.1:$API_PORT" \
  "$PNPM" exec vite dev --port $WEB_PORT --strictPort >"$DATA/web.log" 2>&1 & PIDS+=($!)
wait_http "http://localhost:$WEB_PORT/" web

# ---- tests -----------------------------------------------------------------------
log "running Playwright"
set +e
"$PNPM" exec playwright test "$@"
status=$?
set -e
log "report: frontend/../e2e/.data/report/index.html   logs: $DATA/*.log"
exit $status
