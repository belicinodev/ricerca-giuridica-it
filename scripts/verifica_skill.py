#!/usr/bin/env python3
"""Controlli statici sulla skill: nessuna chiamata di rete, nessuna dipendenza
esterna. Pensato per girare in CI a ogni push/PR.

Verifica:
- evals.json è JSON valido, id univoci, coppie prompt/expected_output presenti
- SKILL.md ha frontmatter YAML valido con i campi richiesti e la description
  entro il limite di 1024 caratteri
- ogni file in references/ nominato da SKILL.md esiste davvero (puntatori non rotti)
- schema/lex_tools_contract.json è JSON Schema valido (parsing strutturale)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".claude" / "skills" / "ricerca-giuridica-it"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS_DIR = SKILL_DIR / "references"
EVALS = ROOT / "evals" / "evals.json"
CONTRACT = ROOT / "schema" / "lex_tools_contract.json"

errori: list[str] = []


def check_evals() -> None:
    try:
        d = json.loads(EVALS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errori.append(f"evals.json non è JSON valido: {e}")
        return
    items = d.get("evals")
    if not isinstance(items, list) or not items:
        errori.append("evals.json: campo 'evals' assente o vuoto")
        return
    ids = [e.get("id") for e in items]
    if len(ids) != len(set(ids)):
        dup = [i for i in ids if ids.count(i) > 1]
        errori.append(f"evals.json: id duplicati: {sorted(set(dup))}")
    for e in items:
        for campo in ("id", "prompt", "expected_output"):
            if campo not in e:
                errori.append(f"evals.json: eval {e.get('id', '?')} priva del campo '{campo}'")
        if "checks" in e:
            c = e["checks"]
            for campo in ("must_include", "must_not_include"):
                if campo not in c or not isinstance(c[campo], list):
                    errori.append(f"evals.json: eval {e.get('id')} — checks.{campo} mancante o non è una lista")
    print(f"evals.json: {len(items)} eval, {sum(1 for e in items if 'checks' in e)} con assertion strutturate")


def check_frontmatter() -> None:
    src = SKILL_MD.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", src, re.S)
    if not m:
        errori.append("SKILL.md: frontmatter YAML non trovato o malformato (delimitatori --- mancanti)")
        return
    fm = m.group(1)
    for campo in ("name:", "description:"):
        if campo not in fm:
            errori.append(f"SKILL.md: frontmatter privo del campo '{campo}'")
    dm = re.search(r"description:\s*>\s*\n((?:  .*\n?)+?)(?=\n?\w[\w-]*:|\Z)", fm)
    if dm:
        desc = " ".join(l.strip() for l in dm.group(1).splitlines())
        if len(desc) > 1024:
            errori.append(f"SKILL.md: description lunga {len(desc)} caratteri, oltre il limite di 1024")
        else:
            print(f"SKILL.md: description {len(desc)} caratteri (limite 1024)")
    else:
        errori.append("SKILL.md: description non estraibile dal frontmatter (formato inatteso)")


def check_reference_pointers() -> None:
    src = SKILL_MD.read_text(encoding="utf-8")
    nominati = set(re.findall(r"references/([a-zA-Z0-9_\-]+\.md)", src))
    esistenti = {p.name for p in REFS_DIR.glob("*.md")} if REFS_DIR.exists() else set()
    mancanti = nominati - esistenti
    if mancanti:
        errori.append(f"SKILL.md nomina file in references/ inesistenti: {sorted(mancanti)}")
    orfani = esistenti - nominati
    if orfani:
        print(f"AVVISO (non bloccante): reference presenti ma non nominate in SKILL.md: {sorted(orfani)}")
    print(f"references/: {len(esistenti)} file, {len(nominati)} puntatori in SKILL.md, {len(mancanti)} rotti")


def check_contract_schema() -> None:
    try:
        d = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errori.append(f"schema/lex_tools_contract.json non è JSON valido: {e}")
        return
    if "tools" not in d:
        errori.append("schema/lex_tools_contract.json: campo 'tools' assente")
        return
    print(f"schema/lex_tools_contract.json: {len(d['tools'])} tool descritti")


def main() -> int:
    check_evals()
    check_frontmatter()
    check_reference_pointers()
    check_contract_schema()
    if errori:
        print("\nERRORI:")
        for e in errori:
            print(f"  - {e}")
        return 1
    print("\nTutti i controlli statici superati.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
