#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0
#
# End-to-end run with nothing but what the repo already needs — no Docker, no WSL.
# Works on Windows (Git Bash), Linux and macOS:
#
#   Postgres     - a throwaway cluster from the installed Postgres binaries, port 5433,
#                  trust auth, recreated every run. Never touches your real server.
#   Redis        - the real redis-server where there is one, otherwise fakeredis (pip,
#                  inside the project venv).
#   Meilisearch  - the official single-file binary for this platform, fetched into
#                  e2e/.tools.
#   API          - uvicorn from the project venv, port 8010 (8000 is in a Windows
#                  reserved port range on the machines this was built on).
#   Frontend     - vite dev on 3000, proxied to the API.
#   Browser      - Playwright driving an already-installed browser: Edge on Windows,
#                  Chromium elsewhere. Override with E2E_BROWSER=chrome|msedge|chromium,
#                  or point E2E_CHROME at an executable.
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

# ---- platform --------------------------------------------------------------------
case "$(uname -s)" in
  MINGW* | MSYS* | CYGWIN*) OS=windows ;;
  Darwin) OS=macos ;;
  *) OS=linux ;;
esac
log "platform: $OS"

# ---- toolchain discovery ---------------------------------------------------------
# Postgres ships its binaries somewhere different on every platform and none of them is
# reliably on PATH: Windows puts them under Program Files, Debian hides them in
# /usr/lib/postgresql/<major>/bin so several majors can coexist, Homebrew keeps them in
# its own prefix.
find_pg_bin() {
  if command -v pg_ctl >/dev/null 2>&1; then dirname "$(command -v pg_ctl)"; return; fi
  local candidate
  for candidate in \
    /c/Program\ Files/PostgreSQL/*/bin \
    /usr/lib/postgresql/*/bin \
    /usr/local/opt/postgresql*/bin \
    /opt/homebrew/opt/postgresql*/bin \
    /usr/pgsql-*/bin; do
    [ -x "$candidate/pg_ctl" ] && { printf '%s' "$candidate"; return; }
  done
}
PG_BIN="$(find_pg_bin || true)"
[ -n "$PG_BIN" ] && { [ -x "$PG_BIN/pg_ctl" ] || [ -x "$PG_BIN/pg_ctl.exe" ]; } \
  || die "Postgres binaries not found (install Postgres, or put its bin/ on PATH)"

VENV_RAW="$(cd "$ROOT" && python -m pipenv --venv 2>/dev/null || python3 -m pipenv --venv 2>/dev/null)" \
  || die "no pipenv venv; run 'python -m pipenv sync --dev' first"
VENV="$(cygpath -u "$VENV_RAW" 2>/dev/null || printf '%s' "$VENV_RAW")"
PY="$VENV/Scripts/python.exe"; [ -x "$PY" ] || PY="$VENV/bin/python"
[ -x "$PY" ] || die "no python in $VENV"
PNPM="$(command -v pnpm || echo "${APPDATA:-}/npm/pnpm")"
[ -x "$PNPM" ] || command -v "$PNPM" >/dev/null 2>&1 || die "pnpm not found on PATH"

# initdb refuses to run as root, which is how this runs inside a container. Fall back to
# the `postgres` system user, whose home is somewhere it can actually traverse -- a data
# directory under the repo is unreadable to it, and initdb fails with "permission denied"
# on the parent rather than on the directory it just made.
PG_AS=""
PGDATA="$DATA/pg"
if [ "$OS" != "windows" ] && [ "$(id -u)" = "0" ]; then
  id postgres >/dev/null 2>&1 || die "running as root and there is no postgres user to drop to"
  PG_AS="postgres"
  PGDATA="${E2E_PGDATA:-/var/lib/postgresql/frogquiz-e2e}"
  log "running as root: Postgres will run as the postgres user, with its cluster in $PGDATA"
fi
# Runs a Postgres binary, as the postgres user when we had to drop privileges.
pg() {
  local bin="$1"; shift
  if [ -n "$PG_AS" ]; then
    su "$PG_AS" -c "$(printf '%q ' "$PG_BIN/$bin" "$@")"
  else
    "$PG_BIN/$bin" "$@"
  fi
}

# ---- teardown --------------------------------------------------------------------
PIDS=()
cleanup() {
  [ "${KEEP_UP:-}" = 1 ] && { log "KEEP_UP=1: leaving the stack running"; return; }
  log "stopping services"
  for pid in "${PIDS[@]:-}"; do
    [ -n "$pid" ] || continue
    # Git Bash's kill does not reach native grandchildren (pnpm -> node -> vite);
    # taskkill /T takes the whole tree. Elsewhere, kill the process group.
    if [ "$OS" = "windows" ]; then
      winpid="$(cat "/proc/$pid/winpid" 2>/dev/null || true)"
      if [ -n "$winpid" ]; then taskkill //F //T //PID "$winpid" >/dev/null 2>&1 || true
      else kill "$pid" 2>/dev/null || true; fi
    else
      kill -- "-$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
    fi
  done
  pg pg_ctl -D "$PGDATA" -m fast stop >/dev/null 2>&1 || true
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
pg pg_ctl -D "$PGDATA" -m fast stop >/dev/null 2>&1 || true
rm -rf "$DATA"
mkdir -p "$DATA/storage" "$DATA/meili" "$TOOLS"
if [ -n "$PG_AS" ]; then
  rm -rf "$PGDATA"
  mkdir -p "$(dirname "$PGDATA")"
  chown "$PG_AS" "$(dirname "$PGDATA")"
fi

# ---- dependencies that live outside the lockfile ---------------------------------
case "$OS" in
  windows) MEILI_BIN="$TOOLS/meilisearch.exe"; MEILI_ASSET=meilisearch-windows-amd64.exe ;;
  macos)   MEILI_BIN="$TOOLS/meilisearch"
           case "$(uname -m)" in arm64) MEILI_ASSET=meilisearch-macos-apple-silicon ;; *) MEILI_ASSET=meilisearch-macos-amd64 ;; esac ;;
  *)       MEILI_BIN="$TOOLS/meilisearch"
           case "$(uname -m)" in aarch64|arm64) MEILI_ASSET=meilisearch-linux-aarch64 ;; *) MEILI_ASSET=meilisearch-linux-amd64 ;; esac ;;
esac
if [ ! -x "$MEILI_BIN" ]; then
  log "fetching Meilisearch ($MEILI_ASSET, one-off, ~350 MB)"
  curl -fL --retry 3 -o "$MEILI_BIN" \
    "https://github.com/meilisearch/meilisearch/releases/latest/download/$MEILI_ASSET"
  chmod +x "$MEILI_BIN"
fi

# ---- Postgres --------------------------------------------------------------------
log "starting Postgres on $PG_PORT"
pg initdb -D "$PGDATA" -U postgres --auth=trust -E UTF8 --no-locale >"$DATA/initdb.log" 2>&1
# pg_ctl leaves the server holding its stdout; without the redirect this hangs.
pg pg_ctl -D "$PGDATA" -o "-p $PG_PORT -c listen_addresses=127.0.0.1" -l "$PGDATA/pg.log" -w start >/dev/null 2>&1 </dev/null
"$PG_BIN/psql" -h 127.0.0.1 -p $PG_PORT -U postgres -qc "create database frogquiz;"

# ---- Redis, Meilisearch ----------------------------------------------------------
# A real redis-server where there is one (Linux and macOS usually have it, and it
# behaves exactly like production); fakeredis is the stand-in that needs no install.
if command -v redis-server >/dev/null 2>&1; then
  log "starting redis-server on $REDIS_PORT and Meilisearch on $MEILI_PORT"
  redis-server --port $REDIS_PORT --save '' --appendonly no --dir "$DATA" \
    >"$DATA/redis.log" 2>&1 & PIDS+=($!)
else
  log "starting fakeredis on $REDIS_PORT and Meilisearch on $MEILI_PORT"
  "$PY" -c "import fakeredis" 2>/dev/null || { log "installing fakeredis into the venv"; "$PY" -m pip install -q "fakeredis[lua]"; }
  "$PY" "$ROOT/e2e/redis_server.py" $REDIS_PORT >"$DATA/redis.log" 2>&1 & PIDS+=($!)
fi
"$MEILI_BIN" --http-addr 127.0.0.1:$MEILI_PORT --db-path "$DATA/meili/data.ms" \
  --no-analytics --env development >"$DATA/meili.log" 2>&1 & PIDS+=($!)
wait_http "http://127.0.0.1:$MEILI_PORT/health" meili

# ---- API -------------------------------------------------------------------------
set -a; . "$ROOT/e2e/e2e.env"; set +a
export DB_URL="postgresql://postgres@127.0.0.1:$PG_PORT/frogquiz"
export STORAGE_PATH="$DATA/storage"
# Stand-in for python-magic, whose Windows DLL crashes on import. See e2e/shims/magic.py.
# Everywhere else the real libmagic works, and the shim would only hide a difference.
[ "$OS" = "windows" ] && export PYTHONPATH="$ROOT/e2e/shims${PYTHONPATH:+:$PYTHONPATH}"
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
# Edge is the browser that is already there on the machines this was written for; on
# Linux and macOS, Playwright's own Chromium is. playwright.config.ts reads both.
if [ -z "${E2E_BROWSER:-}" ]; then
  case "$OS" in windows) export E2E_BROWSER=msedge ;; *) export E2E_BROWSER=chromium ;; esac
fi
log "running Playwright ($E2E_BROWSER)"
set +e
"$PNPM" exec playwright test "$@"
status=$?
set -e
log "report: frontend/../e2e/.data/report/index.html   logs: $DATA/*.log"
exit $status
