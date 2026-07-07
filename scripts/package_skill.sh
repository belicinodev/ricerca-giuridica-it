#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dist
VERSION="${1:-$(date +%Y%m%d)}"
OUT="dist/ricerca-giuridica-it_${VERSION}.zip"
rm -f "$OUT"
(cd .claude/skills && zip -rq "../../$OUT" ricerca-giuridica-it -x "*.DS_Store")
echo "Pacchetto creato: $OUT"
unzip -l "$OUT"
