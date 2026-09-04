#!/usr/bin/env python3
"""Controlli statici sulla skill: nessuna chiamata di rete, nessuna dipendenza
esterna. Pensato per girare in CI a ogni push/PR.

Verifica:
- evals.json è JSON valido, id univoci, coppie prompt/expected_output presenti;
  riporta anche (informativo) quante eval hanno tool_input_must_not_include e
  quante sono TEMPLATE (manuali, mai eseguite in automatico)
- SKILL.md ha frontmatter YAML valido con i campi richiesti e la description
  entro il limite di 1024 caratteri
- ogni file in references/ nominato da SKILL.md esiste davvero (puntatori non
  rotti), e viceversa ogni file in references/ è nominato da SKILL.md (nessun
  orfano mai caricato), salvo allowlist esplicita
- ogni URL in references/*.md usa https (non solo fonti_normative.md)
- ogni tool lex_* citato per nome in SKILL.md esiste nel contratto
  schema/lex_tools_contract.json
- fonti_normative.md: ogni voce di catalogo ha 4 colonne, uno Stato che inizia
  con un valore riconosciuto e un permalink verso una fonte ufficiale nota, e se
  il permalink è su normattiva.it contiene il pattern uri-res/N2Ls
- tutte le tabelle markdown di references/*.md hanno un numero di colonne
  coerente riga per riga (errore strutturale, non semantico)
- ogni sezione numerata di fonti_per_materia.md porta un'etichetta di
  maturità riconosciuta ([copertura piena] / [copertura parziale] /
  [solo instradamento])
- schema/lex_tools_contract.json è JSON Schema valido (parsing strutturale)
- (informativo, non bloccante) crescita in byte di SKILL.md rispetto
  all'ultimo tag: un avviso oltre il 10% ricorda di valutare una
  compattazione prima del prossimo rilascio, senza bloccare la CI
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".claude" / "skills" / "ricerca-giuridica-it"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS_DIR = SKILL_DIR / "references"
EVALS = ROOT / "evals" / "evals.json"
CONTRACT = ROOT / "schema" / "lex_tools_contract.json"
FONTI_NORMATIVE = REFS_DIR / "fonti_normative.md"
FONTI_PER_MATERIA = REFS_DIR / "fonti_per_materia.md"

STATO_PREFISSI = ("Vigente", "Abrogato", "Abrogata", "Applicabile", "Abrogazione differita")
MATURITA_RICONOSCIUTE = ("copertura piena", "copertura parziale", "solo instradamento")
URL_PREFISSI = ("https://www.normattiva.it", "https://eur-lex.europa.eu", "https://www.cnel.it")
# file di lavoro temporanei ammessi in references/ senza puntatore in SKILL.md
ORFANI_AMMESSI: set[str] = set()
# nomi di tool lex_* citati in SKILL.md ma volutamente non per nome esplicito
# (coperti solo dal riferimento generico "lex_*"), da non segnalare come errore
TOOL_LEX_CITAZIONE_NON_RICHIESTA: set[str] = set()

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
    elif not all(isinstance(i, int) for i in ids):
        errori.append("evals.json: uno o più id non sono interi, impossibile verificare la sequenzialità 1..N")
    elif sorted(ids) != list(range(1, len(ids) + 1)):
        mancanti = sorted(set(range(1, len(ids) + 1)) - set(ids))
        errori.append(f"evals.json: id non sequenziali 1..N (mancanti: {mancanti})")
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
    template = sum(1 for e in items if str(e.get("prompt", "")).startswith("TEMPLATE"))
    minimizzazione = sum(1 for e in items if "tool_input_must_not_include" in e.get("checks", {}))
    print(f"evals.json: {len(items)} eval, {sum(1 for e in items if 'checks' in e)} con assertion strutturate")
    print(f"evals.json: {minimizzazione}/{len(items)} eval con tool_input_must_not_include (copertura minimizzazione); {template}/{len(items)} TEMPLATE (solo collaudo manuale)")


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
    orfani = esistenti - nominati - ORFANI_AMMESSI
    if orfani:
        errori.append(f"references/ presenti ma non citate in SKILL.md (mai caricate): {sorted(orfani)}")
    print(f"references/: {len(esistenti)} file, {len(nominati)} puntatori in SKILL.md, {len(mancanti)} rotti, {len(orfani)} orfani")


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
            elif url.startswith("https://www.normattiva.it") and "uri-res/N2Ls" not in url:
                problemi.append(f"riga {i}: URL Normattiva senza il formato permalink atteso (uri-res/N2Ls): {url[:80]}")
        else:
            in_tabella = False
    if problemi:
        errori.extend(f"fonti_normative.md: {p}" for p in problemi)
    print(f"fonti_normative.md: {voci} voci di catalogo verificate, {len(problemi)} problemi")


def check_tabelle_generiche() -> None:
    """Verifica strutturale (non semantica) delle tabelle markdown in tutti i
    file references/*.md: ogni riga dati di una tabella deve avere lo stesso
    numero di colonne della riga di intestazione che la apre. Non valida il
    contenuto (a differenza di check_catalogo_normativo, dedicata a
    fonti_normative.md): serve a evitare errori di battitura come una colonna
    in più o in meno, che altrimenti passerebbero inosservati fino a lettura.
    """
    problemi: list[str] = []
    tabelle = 0
    for path in sorted(REFS_DIR.glob("*.md")):
        if path == FONTI_NORMATIVE:
            continue  # già validata nel dettaglio da check_catalogo_normativo
        colonne_attese: int | None = None
        header_riga = 0
        for i, riga in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            r = riga.strip()
            if not r.startswith("|"):
                colonne_attese = None
                continue
            if set(r.replace("|", "").replace("-", "").replace(":", "").strip()) == set():
                continue  # riga separatrice |---|---|
            n = len(r.strip("|").split("|"))
            if colonne_attese is None:
                colonne_attese = n
                header_riga = i
                tabelle += 1
                continue
            if n != colonne_attese:
                problemi.append(
                    f"{path.name} riga {i}: {n} colonne, ne attendevo {colonne_attese} come l'intestazione a riga {header_riga}"
                )
    if problemi:
        errori.extend(f"tabelle references/: {p}" for p in problemi)
    print(f"tabelle references/*.md: {tabelle} tabelle esaminate, {len(problemi)} problemi di colonne")


def check_maturita_aree() -> None:
    """Ogni sezione numerata di fonti_per_materia.md deve portare, nel titolo,
    un'etichetta di maturità riconosciuta — rende la dichiarazione di
    copertura machine-checkable: un'area nuova senza etichetta rompe la CI
    invece di passare inosservata.
    """
    if not FONTI_PER_MATERIA.exists():
        errori.append("references/fonti_per_materia.md non trovato")
        return
    sezioni = 0
    numeri: list[int] = []
    problemi: list[str] = []
    conteggi: dict[str, int] = {m: 0 for m in MATURITA_RICONOSCIUTE}
    for i, riga in enumerate(FONTI_PER_MATERIA.read_text(encoding="utf-8").splitlines(), start=1):
        m = re.match(r"^## (\d+)\. (.+)$", riga)
        if not m:
            continue
        sezioni += 1
        numero = int(m.group(1))
        numeri.append(numero)
        titolo = m.group(2)
        etichetta = next((e for e in MATURITA_RICONOSCIUTE if f"[{e}]" in titolo), None)
        if etichetta is None:
            problemi.append(f"riga {i}: '{titolo[:60]}' priva di un'etichetta di maturità riconosciuta {MATURITA_RICONOSCIUTE}")
        else:
            conteggi[etichetta] += 1
    attesi = set(range(1, sezioni + 1))
    trovati = set(numeri)
    if trovati != attesi:
        mancanti = sorted(attesi - trovati)
        duplicati = sorted({n for n in numeri if numeri.count(n) > 1})
        problemi.append(f"numerazione sezioni non 1..{sezioni}: mancanti {mancanti}, duplicati {duplicati}")
    if problemi:
        errori.extend(f"fonti_per_materia.md: {p}" for p in problemi)
    riepilogo = ", ".join(f"{k}: {v}" for k, v in conteggi.items())
    print(f"fonti_per_materia.md: {sezioni} sezioni, maturità — {riepilogo}")


def check_url_references() -> None:
    """Ogni URL http(s) in references/*.md deve usare https — un check leggero
    (solo il protocollo, non il dominio) su tutti i file, a differenza di
    check_catalogo_normativo che valida anche il dominio ma solo per
    fonti_normative.md. Trovato un caso reale in schemi_atti.md durante
    l'audit del 2026-08-21 (link http:// a una fonte strutturale verificata),
    corretto insieme all'aggiunta di questo controllo.
    """
    problemi: list[str] = []
    for path in sorted(REFS_DIR.glob("*.md")):
        for i, riga in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for url in re.findall(r"https?://[^\s)>\]]+", riga):
                if not url.startswith("https://"):
                    problemi.append(f"{path.name} riga {i}: URL non-https: {url}")
    if problemi:
        errori.extend(f"references/: {p}" for p in problemi)
    print(f"references/*.md: URL non-https trovati: {len(problemi)}")


def check_coerenza_tool_lex() -> None:
    """Ogni nome di tool lex_* citato esplicitamente in SKILL.md deve esistere
    come chiave in schema/lex_tools_contract.json — stesso principio di
    check_reference_pointers applicato ai tool invece che ai file references/.
    """
    if not CONTRACT.exists():
        return
    try:
        contratto = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return  # già segnalato da check_contract_schema
    tool_contratto = set(contratto.get("tools", {}).keys())
    src = SKILL_MD.read_text(encoding="utf-8")
    citati = set(re.findall(r"lex_[a-z_]+", src))
    orfani = citati - tool_contratto - TOOL_LEX_CITAZIONE_NON_RICHIESTA
    if orfani:
        errori.append(f"SKILL.md cita tool lex_* assenti dal contratto: {sorted(orfani)}")
    non_citati = tool_contratto - citati
    if non_citati:
        print(f"AVVISO (non bloccante): tool nel contratto mai citati per nome esplicito in SKILL.md: {sorted(non_citati)}")
    print(f"coerenza tool lex_*: {len(citati)} nomi citati in SKILL.md, {len(tool_contratto)} nel contratto, {len(orfani)} orfani")


def check_crescita_skill() -> None:
    """Confronta la dimensione in byte di SKILL.md con quella all'ultimo tag
    git: solo informativo, non aggiunge mai a `errori` (non deve bloccare la
    CI). Serve a rendere visibile una crescita rapida prima che diventi un
    problema di consumo di token, dato che la cronologia del progetto mostra
    che senza un promemoria esplicito la compattazione non emerge da sola.
    """
    try:
        tag = subprocess.run(
            ["git", "-C", str(ROOT), "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True, timeout=5,
        )
        if tag.returncode != 0 or not tag.stdout.strip():
            print("crescita SKILL.md: nessun tag trovato, controllo saltato")
            return
        ultimo_tag = tag.stdout.strip()
        rel_path = str(SKILL_MD.relative_to(ROOT))
        precedente = subprocess.run(
            ["git", "-C", str(ROOT), "show", f"{ultimo_tag}:{rel_path}"],
            capture_output=True, timeout=5,
        )
        if precedente.returncode != 0:
            print(f"crescita SKILL.md: SKILL.md non trovato al tag {ultimo_tag}, controllo saltato")
            return
        dim_precedente = len(precedente.stdout)
        dim_attuale = SKILL_MD.stat().st_size
        if dim_precedente == 0:
            return
        crescita = (dim_attuale - dim_precedente) / dim_precedente * 100
        print(f"SKILL.md: {dim_attuale} byte (era {dim_precedente} byte a {ultimo_tag}, {crescita:+.1f}%)")
        if crescita > 10:
            print(f"AVVISO (non bloccante): SKILL.md cresciuto di oltre il 10% dall'ultimo tag ({ultimo_tag}) — valuta una compattazione prima del prossimo rilascio.")
    except (subprocess.SubprocessError, OSError, ValueError) as e:
        print(f"crescita SKILL.md: controllo saltato ({e})")


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
    check_tabelle_generiche()
    check_maturita_aree()
    check_url_references()
    check_coerenza_tool_lex()
    check_crescita_skill()
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
