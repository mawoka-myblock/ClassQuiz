#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0
#
# Stops a stack left running by `KEEP_UP=1 bash e2e/run.sh`. Finds each service by the
# port it listens on, so it works from any shell, not just the one that started it.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for port in 6380 7701 8010 3000; do
  for pid in $(netstat -ano | awk -v p=":$port" '$2 ~ p"$" && $4 == "LISTENING" {print $5}' | sort -u); do
    taskkill //F //T //PID "$pid" >/dev/null 2>&1 && echo "stopped :$port (pid $pid)"
  done
done
PG_BIN="$(dirname "$(command -v pg_ctl 2>/dev/null || ls -d /c/Program\ Files/PostgreSQL/*/bin/pg_ctl.exe 2>/dev/null | tail -1)")"
DATA="${E2E_DATA:-$ROOT/e2e/.data}"
case "$DATA" in /*|?:*) ;; *) DATA="$ROOT/$DATA" ;; esac
"$PG_BIN/pg_ctl" -D "$DATA/pg" -m fast stop >/dev/null 2>&1 && echo "stopped Postgres"
exit 0
