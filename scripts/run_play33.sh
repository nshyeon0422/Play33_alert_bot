#!/usr/bin/env bash
set -e
# Run from repo root. Activate venv at .venv and start the app.
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

exec python -m play33_alert_bot.main
