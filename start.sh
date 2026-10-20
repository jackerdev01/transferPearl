#!/bin/sh
# macOS / Linux: start the oyster wallet (if needed), wait for sync, then open the menu.
cd "$(dirname "$0")" || exit 1
export PYTHONIOENCODING=utf-8
PY=$(command -v python3 || command -v python)
if [ -z "$PY" ]; then
  echo "Python 3 is required: https://www.python.org/downloads/" >&2
  exit 1
fi
"$PY" main.py 11
"$PY" main.py
