#!/usr/bin/env bash
set -euo pipefail

#Change to project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

#Check if on local mongo
if [[ "${CLOUD_MONGO:-0}" != "0" ]]; then
    echo "Local import requires CLOUD_MONGO=0." >&2
    exit 1
fi

#Check python executable
if [[ -n "${PYTHON:-}" ]]; then
    PYTHON_BIN="$PYTHON"
elif [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
    PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
else
    PYTHON_BIN=python3
fi

#Ping DB
"$PYTHON_BIN" -c 'from data.db_connect import connect_db; connect_db().admin.command("ping")'

#Run load.py script 
exec "$PYTHON_BIN" -m data.places.load
