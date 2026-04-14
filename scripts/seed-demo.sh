#!/bin/bash

# SEN TRAFIC AI - Demo data seeding
# Safe, schema-compatible seed helper.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "[seed-demo] Checking backend container..."
if ! docker compose ps backend-api >/dev/null 2>&1; then
  echo "[seed-demo] backend-api service not found. Start stack first with: docker compose up -d"
  exit 1
fi

BACKEND_STATE="$(docker compose ps --format json backend-api 2>/dev/null | grep -Eo '"State":"[^"]+"' | head -1 | cut -d':' -f2 | tr -d '\"')"
if [ "$BACKEND_STATE" != "running" ]; then
  echo "[seed-demo] backend-api is not running yet. Start stack first with: docker compose up -d"
  exit 1
fi

echo "[seed-demo] Running backend seed module..."
docker compose exec -T backend-api python -m app.db.seed

echo "[seed-demo] Done."
echo "[seed-demo] Dashboard: http://localhost:3001"
echo "[seed-demo] API docs:  http://localhost:8000/docs"
