#!/bin/bash
# Wrapper di compatibilità: il runner delle eval è scripts/esegui_evals.py
# (stessi argomenti, stessa variabile EVAL_WEB, stessi file di risultato in
# evals/risultati/). Resta qui perché documentazione e abitudini lo chiamano.
set -euo pipefail
exec python3 "$(dirname "$0")/esegui_evals.py" "$@"
