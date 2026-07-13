#!/usr/bin/env python3
"""Controlli statici sulla skill: nessuna chiamata di rete, nessuna dipendenza
esterna. Pensato per girare in CI a ogni push/PR.

Verifica:
- evals.json è JSON valido, id univoci, coppie prompt/expected_output presenti
- SKILL.md ha frontmatter YAML valido con i campi richiesti e la description
  entro il limite di 1024 caratteri
- ogni file in references/ nominato da SKILL.md esiste davvero (puntatori non rotti)
- fonti_normative.md: ogni voce di catalogo ha 4 colonne, uno Stato che inizia
  con un valore riconosciuto e un permalink verso una fonte ufficiale nota
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
FONTI_NORMATIVE = REFS_DIR / "fonti_normative.md"

STATO_PREFISSI = ("Vigente", "Abrogato", "Abrogata", "Applicabile", "Abrogazione differita")
URL_PREFISSI = ("https://www.normattiva.it", "https://eur-lex.europa.eu", "https://www.cnel.it")

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
            if "tool_input_must_not_include" in c and not isinstance(c["tool_input_must_not_include"], list):
                errori.append(f"evals.json: eval {e.get('id')} — checks.tool_input_must_not_include non è una lista")
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


def check_catalogo_normativo() -> None:
    """Valida senza rete lo schema tabellare (Fonte | Estremi | Stato | Testo
    ufficiale) di fonti_normative.md: colonne complete, Stato che inizia con
    un valore riconosciuto, permalink che punta a una fonte ufficiale nota.
    """
    if not FONTI_NORMATIVE.exists():
        errori.append("references/fonti_normative.md non trovato")
        return
    voci = 0
    problemi: list[str] = []
    in_tabella = False
    for i, riga in enumerate(FONTI_NORMATIVE.read_text(encoding="utf-8").splitlines(), start=1):
        if riga.startswith("| Fonte |"):
            in_tabella = True
            continue
        if riga.startswith("|---"):
            continue
        if not in_tabella:
            continue
        if riga.strip().startswith("|") and riga.strip() != "":
            colonne = [c.strip() for c in riga.strip().strip("|").split("|")]
            if len(colonne) != 4:
                problemi.append(f"riga {i}: {len(colonne)} colonne invece di 4")
                continue
            _fonte, _estremi, stato, url = colonne
            voci += 1
            if not stato:
                problemi.append(f"riga {i}: colonna Stato vuota")
            elif not stato.startswith(STATO_PREFISSI):
                problemi.append(f"riga {i}: Stato '{stato[:40]}' non inizia con un valore riconosciuto {STATO_PREFISSI}")
            if not url:
                problemi.append(f"riga {i}: colonna Testo ufficiale vuota")
            elif not url.startswith(URL_PREFISSI):
                problemi.append(f"riga {i}: URL non punta a una fonte ufficiale riconosciuta: {url[:60]}")
        else:
            in_tabella = False
    if problemi:
        errori.extend(f"fonti_normative.md: {p}" for p in problemi)
    print(f"fonti_normative.md: {voci} voci di catalogo verificate, {len(problemi)} problemi")


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
    check_catalogo_normativo()
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
