#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
API_PID=""
WEB_PID=""

cleanup() {
    echo ""
    echo "Shutting down..."
    [[ -n "$WEB_PID" ]] && kill "$WEB_PID" 2>/dev/null
    [[ -n "$API_PID" ]] && kill "$API_PID" 2>/dev/null
    wait 2>/dev/null
    echo "Done."
}
trap cleanup EXIT INT TERM

# -- Install dependencies if needed --

if [[ ! -d "$ROOT/api/.venv" ]]; then
    echo "Installing API dependencies..."
    (cd "$ROOT/api" && uv sync)
fi

if [[ ! -d "$ROOT/web/node_modules" ]]; then
    echo "Installing web dependencies..."
    (cd "$ROOT/web" && npm install)
fi

# -- Start API --

echo "Starting API on :8000..."
(cd "$ROOT/api" && uv run uvicorn api.main:app --port 8000) &
API_PID=$!

# -- Start web --

echo "Starting web on :5173..."
(cd "$ROOT/web" && npm run dev -- --open) &
WEB_PID=$!

echo ""
echo "  API:  http://localhost:8000"
echo "  Web:  http://localhost:5173"
echo "  Press Ctrl+C to stop"
echo ""

wait
