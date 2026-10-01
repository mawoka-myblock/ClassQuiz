#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0
#
# Stops a stack left running by `KEEP_UP=1 bash e2e/run.sh`. Finds each service by the
# port it listens on, so it works from any shell, not just the one that started it.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
case "$(uname -s)" in MINGW* | MSYS* | CYGWIN*) OS=windows ;; *) OS=unix ;; esac

for port in 6380 7701 8010 3000; do
  if [ "$OS" = windows ]; then
    for pid in $(netstat -ano | awk -v p=":$port" '$2 ~ p"$" && $4 == "LISTENING" {print $5}' | sort -u); do
      taskkill //F //T //PID "$pid" >/dev/null 2>&1 && echo "stopped :$port (pid $pid)"
    done
  else
    # lsof is not everywhere; fuser comes with psmisc and ss with iproute2.
    pids="$(lsof -ti tcp:"$port" 2>/dev/null || fuser "$port"/tcp 2>/dev/null || true)"
    for pid in $pids; do kill "$pid" 2>/dev/null && echo "stopped :$port (pid $pid)"; done
  fi
done

find_pg_bin() {
  if command -v pg_ctl >/dev/null 2>&1; then dirname "$(command -v pg_ctl)"; return; fi
  local c
  for c in /c/Program\ Files/PostgreSQL/*/bin /usr/lib/postgresql/*/bin \
           /usr/local/opt/postgresql*/bin /opt/homebrew/opt/postgresql*/bin /usr/pgsql-*/bin; do
    [ -x "$c/pg_ctl" ] && { printf '%s' "$c"; return; }
  done
}
PG_BIN="$(find_pg_bin || true)"
DATA="${E2E_DATA:-$ROOT/e2e/.data}"
case "$DATA" in /*|?:*) ;; *) DATA="$ROOT/$DATA" ;; esac
# run.sh puts the cluster in the postgres user's home when it had to drop from root.
PGDATA="$DATA/pg"
[ -d "$PGDATA" ] || PGDATA="${E2E_PGDATA:-/var/lib/postgresql/frogquiz-e2e}"
if [ "$OS" != windows ] && [ "$(id -u)" = 0 ] && id postgres >/dev/null 2>&1; then
  su postgres -c "$PG_BIN/pg_ctl -D $PGDATA -m fast stop" >/dev/null 2>&1 && echo "stopped Postgres"
else
  "$PG_BIN/pg_ctl" -D "$PGDATA" -m fast stop >/dev/null 2>&1 && echo "stopped Postgres"
fi
exit 0
