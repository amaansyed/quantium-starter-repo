#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
TMP_DIR="$ROOT_DIR/.tmp"

if [ ! -d "$VENV_DIR" ]; then
  echo "Virtual environment not found at $VENV_DIR" >&2
  exit 1
fi

mkdir -p "$TMP_DIR"
export TMPDIR="$TMP_DIR"

source "$VENV_DIR/bin/activate"

cd "$ROOT_DIR"
if ! python -m pytest -q; then
  exit 1
fi
