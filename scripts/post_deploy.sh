#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3.11}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if command -v systemctl >/dev/null 2>&1; then
  SERVICE_NAME="${SERVICE_NAME:-binancebot}"
  SYSTEMD_MODE="${SYSTEMD_MODE:-system}"
  if [ "$SYSTEMD_MODE" = "user" ]; then
    systemctl --user restart "$SERVICE_NAME"
  else
    if command -v sudo >/dev/null 2>&1; then
      sudo systemctl restart "$SERVICE_NAME"
    else
      systemctl restart "$SERVICE_NAME"
    fi
  fi
fi
