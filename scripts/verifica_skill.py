#!/usr/bin/env python3
"""Controlli statici sulla skill: nessuna chiamata di rete, nessuna dipendenza
esterna. Pensato per girare in CI a ogni push/PR e per essere testato in
isolamento (tests/test_verifica_skill.py): ogni controllo riceve i percorsi del
repo (`Percorsi`) e restituisce un `Esito` — errori bloccanti più note
informative — senza stato globale, così un controllo si può esercitare da solo
su una fixture minimale.

Verifica:
- evals.json è JSON valido, id interi univoci e sequenziali 1..N, coppie
  prompt/expected_output presenti, `checks` ben formati (liste di stringhe non
  vuote); riporta anche (informativo) quante eval hanno
  tool_input_must_not_include e quante sono TEMPLATE (manuali, mai eseguite in
  automatico)
- SKILL.md ha frontmatter YAML con soli campi ammessi dalla specifica Agent
  Skills (fuori da Claude Code un campo estraneo come `argument-hint` fa fallire
  il caricamento), `name` conforme (minuscole, cifre e trattini singoli, max 64
  caratteri, uguale al nome della cartella), `description` non vuota entro 1024
  caratteri, `metadata.version` presente nel formato X.Y.Z
- il corpo di SKILL.md resta sotto le 500 righe (errore) e, come avviso, sotto
  i ~5.000 token che Claude Code ri-attacca dopo una compattazione
- nessuna eval non-TEMPLATE ha stringhe di must_not_include già presenti nel
  proprio expected_output (eval insuperabile dalla risposta attesa);
  `tool_input_must_include` (letture o chiamate che devono avvenire) ha la
  stessa forma di `tool_input_must_not_include`
- CHANGELOG.md: intestazioni "## vX.Y.Z - AAAA-MM-GG" ben formate, senza
  versioni duplicate, in ordine decrescente; la versione in testa coincide con
  `metadata.version` di SKILL.md (il workflow di release pretende che il tag
  coincida a sua volta, così un tag non può puntare a una versione dichiarata
  stantia)
- ogni file in references/ nominato da SKILL.md esiste davvero (puntatori non
  rotti), e viceversa ogni file in references/ è nominato da SKILL.md (nessun
  orfano mai caricato), salvo allowlist esplicita
- ogni URL in references/*.md usa https
- ogni tool lex_* citato per nome in SKILL.md o in references/ esiste nel
  contratto schema/lex_tools_contract.json
- fonti_normative.md: ogni voce di catalogo ha 4 colonne, uno Stato che inizia
  con un valore riconosciuto e un permalink verso una fonte ufficiale nota, e se
  il permalink è su normattiva.it contiene il pattern uri-res/N2Ls
- tutte le tabelle markdown di references/*.md hanno un numero di colonne
  coerente riga per riga (errore strutturale, non semantico)
- ogni sezione numerata di fonti_per_materia.md porta un'etichetta di
  maturità riconosciuta e la numerazione è 1..N senza buchi né doppioni
- schema/lex_tools_contract.json è JSON valido con il campo `tools`
- (informativo, non bloccante) crescita in byte di SKILL.md rispetto
  all'ultimo tag git: un avviso oltre il 10% ricorda di valutare una
  compattazione prima del prossimo rilascio, senza bloccare la CI

Uso:
  python3 scripts/verifica_skill.py [radice_repo]   # default: il repo che contiene lo script
  python3 scripts/verifica_skill.py --versione      # stampa solo metadata.version di SKILL.md
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

NOME_SKILL = "ricerca-giuridica-it"
ROOT_DEFAULT = Path(__file__).resolve().parents[1]

STATO_PREFISSI = ("Vigente", "Abrogato", "Abrogata", "Applicabile", "Abrogazione differita")
MATURITA_RICONOSCIUTE = ("copertura piena", "copertura parziale", "solo instradamento")
URL_PREFISSI = ("https://www.normattiva.it", "https://eur-lex.europa.eu", "https://www.cnel.it")
# file di lavoro temporanei ammessi in references/ senza puntatore in SKILL.md
ORFANI_AMMESSI: frozenset[str] = frozenset()
# nomi di tool lex_* citati in SKILL.md ma volutamente non per nome esplicito
# (coperti solo dal riferimento generico "lex_*"), da non segnalare come errore
TOOL_LEX_CITAZIONE_NON_RICHIESTA: frozenset[str] = frozenset()

LIMITE_NAME = 64
LIMITE_DESCRIPTION = 1024
# Campi di frontmatter ammessi dalla specifica Agent Skills (agentskills.io).
# Fuori da Claude Code — upload dello ZIP su claude.ai, Skills API,
# package_skill.py — qualunque altro campo fa fallire il caricamento con
# errore, non viene ignorato (code.claude.com/docs/en/skills, confermato con
# `agentskills validate` il 2026-09-14: `argument-hint` bloccava tutte le
# release da v0.4.10 a v0.6.4).
CAMPI_FRONTMATTER_SPEC = frozenset({"name", "description", "license", "compatibility", "metadata", "allowed-tools"})
# Limite di righe del corpo raccomandato dalla specifica Agent Skills.
LIMITE_RIGHE_SKILL = 500
# Claude Code, dopo l'auto-compattazione della conversazione, ri-attacca di
# ogni skill invocata solo i primi 5.000 token (25.000 complessivi fra tutte):
# oltre quella soglia la coda di SKILL.md sparisce dal contesto senza avviso.
TOKEN_BUDGET_RIATTACCO = 5000
# Soglia di avviso: sotto il budget reale, per lasciare margine a piccole modifiche
# future prima che la stima (calibrata, non un conteggio diretto) superi 5.000 in
# silenzio — trovato con margine di 8 token su ricerca-giuridica-it il 2026-09-14.
SOGLIA_AVVISO_TOKEN = 4500
# Byte per token per prosa italiana con markdown: misurati con tiktoken o200k
# sui due SKILL.md del progetto il 2026-09-14 (3,66 e 3,78), arrotondati.
BYTE_PER_TOKEN_STIMA = 3.7
# specifica Agent Skills: minuscole, cifre, trattini singoli, né in testa né in
# coda (qui ristretta ad ASCII: i nomi di questo repo lo sono)
RE_NOME_SKILL = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RE_VERSIONE = re.compile(r"^\d+\.\d+\.\d+$")
RE_CHANGELOG_VOCE = re.compile(r"^## v(\d+)\.(\d+)\.(\d+) - (\d{4}-\d{2}-\d{2})\s*$")


@dataclass(frozen=True)
class Percorsi:
    """Tutti i percorsi che i controlli leggono, derivati dalla radice del repo."""

    root: Path
    nome_skill: str = NOME_SKILL

    @property
    def skill_dir(self) -> Path:
        return self.root / ".claude" / "skills" / self.nome_skill

    @property
    def skill_md(self) -> Path:
        return self.skill_dir / "SKILL.md"

    @property
    def refs_dir(self) -> Path:
        return self.skill_dir / "references"

    @property
    def evals(self) -> Path:
        return self.root / "evals" / "evals.json"

    @property
    def contract(self) -> Path:
        return self.root / "schema" / "lex_tools_contract.json"

    @property
    def changelog(self) -> Path:
        return self.root / "CHANGELOG.md"

    @property
    def fonti_normative(self) -> Path:
        return self.refs_dir / "fonti_normative.md"

    @property
    def fonti_per_materia(self) -> Path:
        return self.refs_dir / "fonti_per_materia.md"


@dataclass
class Esito:
    """Risultato di un controllo: `errori` bloccano la CI, `note` sono solo
    informative (conteggi, avvisi non bloccanti)."""

    errori: list[str] = field(default_factory=list)
    note: list[str] = field(default_factory=list)

    def errore(self, messaggio: str) -> None:
        self.errori.append(messaggio)

    def nota(self, messaggio: str) -> None:
        self.note.append(messaggio)

    def estendi(self, altro: "Esito") -> None:
        self.errori.extend(altro.errori)
        self.note.extend(altro.note)

    @property
    def ok(self) -> bool:
        return not self.errori


# ---------------------------------------------------------------------------
# Frontmatter (sottoinsieme YAML sufficiente a SKILL.md, senza dipendenze)
# ---------------------------------------------------------------------------

def leggi_frontmatter(src: str) -> dict[str, object] | None:
    """Estrae il frontmatter YAML di SKILL.md in un dizionario. Supporta il
    sottoinsieme usato dal repo: `chiave: valore`, blocchi ripiegati (`>`) o
    letterali (`|`) indentati, e una mappa annidata di un livello (`metadata:`).
    Restituisce None se i delimitatori --- mancano.
    """
    m = re.match(r"---\n(.*?)\n---\n", src, re.S)
    if not m:
        return None
    campi: dict[str, object] = {}
    righe = m.group(1).splitlines()
    i = 0
    while i < len(righe):
        km = re.match(r"^([\w-]+):\s*(.*)$", righe[i])
        if not km:
            i += 1
            continue
        chiave, valore = km.group(1), km.group(2).strip()
        if valore in (">", ">-", "|", "|-"):
            blocco: list[str] = []
            i += 1
            while i < len(righe) and (righe[i].startswith("  ") or not righe[i].strip()):
                blocco.append(righe[i].strip())
                i += 1
            righe_utili = [r for r in blocco if r]
            campi[chiave] = " ".join(righe_utili) if valore.startswith(">") else "\n".join(righe_utili)
            continue
        if valore == "":
            sotto: dict[str, str] = {}
            i += 1
            while i < len(righe) and righe[i].startswith("  "):
                sm = re.match(r"^\s+([\w-]+):\s*(.*)$", righe[i])
                if sm:
                    sotto[sm.group(1)] = _senza_virgolette(sm.group(2))
                i += 1
            campi[chiave] = sotto
            continue
        campi[chiave] = _senza_virgolette(valore)
        i += 1
    return campi


def _senza_virgolette(valore: str) -> str:
    v = valore.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return v


def versione_dichiarata(p: Percorsi) -> str | None:
    """`metadata.version` del frontmatter di SKILL.md, o None se assente."""
    if not p.skill_md.exists():
        return None
    fm = leggi_frontmatter(p.skill_md.read_text(encoding="utf-8"))
    if not fm:
        return None
    meta = fm.get("metadata")
    if not isinstance(meta, dict):
        return None
    versione = meta.get("version")
    return versione if isinstance(versione, str) and versione else None


# ---------------------------------------------------------------------------
# Controlli
# ---------------------------------------------------------------------------

def check_evals(p: Percorsi) -> Esito:
    e = Esito()
    if not p.evals.exists():
        e.errore("evals/evals.json non trovato")
        return e
    try:
        d = json.loads(p.evals.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        e.errore(f"evals.json non è JSON valido: {exc}")
        return e
    items = d.get("evals") if isinstance(d, dict) else None
    if not isinstance(items, list) or not items:
        e.errore("evals.json: campo 'evals' assente o vuoto")
        return e
    ids = [x.get("id") if isinstance(x, dict) else None for x in items]
    if len(ids) != len(set(ids)):
        dup = [i for i in ids if ids.count(i) > 1]
        e.errore(f"evals.json: id duplicati: {sorted(set(dup), key=str)}")
    elif not all(isinstance(i, int) for i in ids):
        e.errore("evals.json: uno o più id non sono interi, impossibile verificare la sequenzialità 1..N")
    elif sorted(ids) != list(range(1, len(ids) + 1)):
        mancanti = sorted(set(range(1, len(ids) + 1)) - set(ids))
        e.errore(f"evals.json: id non sequenziali 1..N (mancanti: {mancanti})")
    for x in items:
        if not isinstance(x, dict):
            e.errore("evals.json: una voce di 'evals' non è un oggetto")
            continue
        ident = x.get("id", "?")
        for campo in ("id", "prompt", "expected_output"):
            if campo not in x:
                e.errore(f"evals.json: eval {ident} priva del campo '{campo}'")
        if "files" in x and not isinstance(x["files"], list):
            e.errore(f"evals.json: eval {ident} — 'files' non è una lista")
        if "checks" in x:
            c = x["checks"]
            if not isinstance(c, dict):
                e.errore(f"evals.json: eval {ident} — 'checks' non è un oggetto")
                continue
            for campo in ("must_include", "must_not_include"):
                if campo not in c or not isinstance(c[campo], list):
                    e.errore(f"evals.json: eval {ident} — checks.{campo} mancante o non è una lista")
                elif not _lista_di_stringhe_non_vuote(c[campo]):
                    e.errore(f"evals.json: eval {ident} — checks.{campo} contiene voci vuote o non stringhe")
            for campo in ("tool_input_must_not_include", "tool_input_must_include"):
                if campo in c:
                    if not isinstance(c[campo], list):
                        e.errore(f"evals.json: eval {ident} — checks.{campo} non è una lista")
                    elif not _lista_di_stringhe_non_vuote(c[campo]):
                        e.errore(f"evals.json: eval {ident} — checks.{campo} contiene voci vuote o non stringhe")
            # Una stringa vietata che compare nell'expected_output stesso rende
            # l'eval insuperabile dalla risposta che la ricalca (caso reale nella
            # skill gemella: "non l'affidamento diretto" nell'atteso, "affidamento
            # diretto" vietato). Nelle TEMPLATE l'atteso è narrativo e può
            # nominare la frase proibita per escluderla: lì è solo una nota.
            atteso = str(x.get("expected_output", "")).lower()
            vietati = c.get("must_not_include") if isinstance(c.get("must_not_include"), list) else []
            nell_atteso = [s for s in vietati if isinstance(s, str) and s and s.lower() in atteso]
            if nell_atteso:
                msg = (f"evals.json: eval {ident} — stringhe di must_not_include già presenti nell'expected_output "
                       f"{nell_atteso}: una risposta che ricalca l'atteso fallirebbe la propria assertion")
                if str(x.get("prompt", "")).startswith("TEMPLATE"):
                    e.nota(f"AVVISO (non bloccante): {msg} (TEMPLATE: atteso narrativo, tollerato)")
                else:
                    e.errore(msg)
    validi = [x for x in items if isinstance(x, dict)]
    template = sum(1 for x in validi if str(x.get("prompt", "")).startswith("TEMPLATE"))
    minimizzazione = sum(1 for x in validi if "tool_input_must_not_include" in (x.get("checks") or {}))
    con_checks = sum(1 for x in validi if "checks" in x)
    e.nota(f"evals.json: {len(items)} eval, {con_checks} con assertion strutturate")
    e.nota(f"evals.json: {minimizzazione}/{len(items)} eval con tool_input_must_not_include (copertura minimizzazione); {template}/{len(items)} TEMPLATE (solo collaudo manuale)")
    return e


def _lista_di_stringhe_non_vuote(valori: list) -> bool:
    return all(isinstance(v, str) and v.strip() for v in valori)


def check_frontmatter(p: Percorsi) -> Esito:
    e = Esito()
    if not p.skill_md.exists():
        e.errore("SKILL.md non trovato")
        return e
    fm = leggi_frontmatter(p.skill_md.read_text(encoding="utf-8"))
    if fm is None:
        e.errore("SKILL.md: frontmatter YAML non trovato o malformato (delimitatori --- mancanti)")
        return e
    fuori_spec = sorted(k for k in fm if k not in CAMPI_FRONTMATTER_SPEC)
    if fuori_spec:
        e.errore(
            f"SKILL.md: campi di frontmatter fuori dalla specifica Agent Skills: {fuori_spec} — "
            f"fuori da Claude Code il caricamento fallisce con errore; ammessi solo {sorted(CAMPI_FRONTMATTER_SPEC)}"
        )
    name = fm.get("name")
    if not isinstance(name, str) or not name:
        e.errore("SKILL.md: frontmatter privo del campo 'name:'")
    else:
        if len(name) > LIMITE_NAME:
            e.errore(f"SKILL.md: name lungo {len(name)} caratteri, oltre il limite di {LIMITE_NAME}")
        if not RE_NOME_SKILL.match(name):
            e.errore(f"SKILL.md: name '{name}' non conforme alla specifica Agent Skills (solo minuscole, cifre e trattini singoli, non in testa né in coda)")
        if name != p.skill_dir.name:
            e.errore(f"SKILL.md: name '{name}' diverso dal nome della cartella della skill '{p.skill_dir.name}'")
    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        e.errore("SKILL.md: frontmatter privo del campo 'description:' (o vuoto)")
    elif len(desc) > LIMITE_DESCRIPTION:
        e.errore(f"SKILL.md: description lunga {len(desc)} caratteri, oltre il limite di {LIMITE_DESCRIPTION}")
    else:
        e.nota(f"SKILL.md: description {len(desc)} caratteri (limite {LIMITE_DESCRIPTION})")
    versione = versione_dichiarata(p)
    if not versione:
        e.errore("SKILL.md: frontmatter privo di metadata.version (versione dichiarata della skill, deve coincidere con CHANGELOG.md e con il tag di release)")
    elif not RE_VERSIONE.match(versione):
        e.errore(f"SKILL.md: metadata.version '{versione}' non nel formato X.Y.Z")
    else:
        e.nota(f"SKILL.md: versione dichiarata {versione}")
    return e


def check_dimensione_skill(p: Percorsi) -> Esito:
    """Dimensione del corpo di SKILL.md, caricato per intero a ogni attivazione.
    Le righe sono un limite documentato della specifica (errore oltre 500); i
    token sono una stima (byte / BYTE_PER_TOKEN_STIMA) confrontata con il
    budget di ri-attacco post-compattazione di Claude Code: oltre, solo un
    avviso, ma un avviso che spiega cosa si perde (la coda del file).
    """
    e = Esito()
    if not p.skill_md.exists():
        return e  # già segnalato da check_frontmatter
    src = p.skill_md.read_text(encoding="utf-8")
    m = re.match(r"---\n.*?\n---\n", src, re.S)
    corpo = src[m.end():] if m else src
    righe = corpo.count("\n")
    byte = len(corpo.encode("utf-8"))
    token_stimati = int(byte / BYTE_PER_TOKEN_STIMA)
    e.nota(f"SKILL.md: corpo di {righe} righe, {byte} byte, ~{token_stimati} token stimati (budget di ri-attacco dopo compattazione: {TOKEN_BUDGET_RIATTACCO})")
    if righe > LIMITE_RIGHE_SKILL:
        e.errore(f"SKILL.md: corpo di {righe} righe, oltre le {LIMITE_RIGHE_SKILL} raccomandate dalla specifica Agent Skills")
    if token_stimati > SOGLIA_AVVISO_TOKEN:
        e.nota(
            f"AVVISO (non bloccante): SKILL.md supera il budget di ri-attacco post-compattazione di Claude Code "
            f"(~{token_stimati} > {TOKEN_BUDGET_RIATTACCO} token): le regole oltre i primi {TOKEN_BUDGET_RIATTACCO} token non "
            "sopravvivono a una compattazione. Tieni gli invarianti in testa e le procedure lunghe in references/ (rileggibili)."
        )
    return e


def check_changelog(p: Percorsi) -> Esito:
    e = Esito()
    if not p.changelog.exists():
        e.errore("CHANGELOG.md non trovato")
        return e
    voci: list[tuple[tuple[int, int, int], str, int]] = []
    for i, riga in enumerate(p.changelog.read_text(encoding="utf-8").splitlines(), start=1):
        if not riga.startswith("## "):
            continue
        m = RE_CHANGELOG_VOCE.match(riga)
        if not m:
            e.errore(f"CHANGELOG.md riga {i}: intestazione non nel formato '## vX.Y.Z - AAAA-MM-GG': {riga[:60]}")
            continue
        voci.append(((int(m.group(1)), int(m.group(2)), int(m.group(3))), m.group(4), i))
    if not voci:
        e.errore("CHANGELOG.md: nessuna voce di versione '## vX.Y.Z - AAAA-MM-GG' trovata")
        return e
    versioni = [v for v, _, _ in voci]
    duplicate = sorted({v for v in versioni if versioni.count(v) > 1})
    if duplicate:
        e.errore(f"CHANGELOG.md: versioni duplicate: {[_v(v) for v in duplicate]}")
    for (prec, _, _), (succ, _, riga_succ) in zip(voci, voci[1:]):
        if succ > prec:
            e.errore(f"CHANGELOG.md riga {riga_succ}: {_v(succ)} compare dopo {_v(prec)} — le voci devono essere in ordine decrescente")
    in_testa, data_testa, _ = voci[0]
    dichiarata = versione_dichiarata(p)
    if dichiarata and dichiarata != _v(in_testa)[1:]:
        e.errore(f"versione dichiarata in SKILL.md (metadata.version {dichiarata}) diversa dalla voce in testa a CHANGELOG.md ({_v(in_testa)})")
    e.nota(f"CHANGELOG.md: {len(voci)} versioni, in testa {_v(in_testa)} ({data_testa})")
    return e


def _v(versione: tuple[int, int, int]) -> str:
    return "v" + ".".join(str(n) for n in versione)


def check_reference_pointers(p: Percorsi) -> Esito:
    e = Esito()
    if not p.skill_md.exists():
        e.errore("SKILL.md non trovato")
        return e
    src = p.skill_md.read_text(encoding="utf-8")
    nominati = set(re.findall(r"references/([a-zA-Z0-9_\-]+\.md)", src))
    esistenti = {f.name for f in p.refs_dir.glob("*.md")} if p.refs_dir.exists() else set()
    mancanti = nominati - esistenti
    if mancanti:
        e.errore(f"SKILL.md nomina file in references/ inesistenti: {sorted(mancanti)}")
    orfani = esistenti - nominati - ORFANI_AMMESSI
    if orfani:
        e.errore(f"references/ presenti ma non citate in SKILL.md (mai caricate): {sorted(orfani)}")
    e.nota(f"references/: {len(esistenti)} file, {len(nominati)} puntatori in SKILL.md, {len(mancanti)} rotti, {len(orfani)} orfani")
    return e


def check_catalogo_normativo(p: Percorsi) -> Esito:
    """Valida senza rete lo schema tabellare (Fonte | Estremi | Stato | Testo
    ufficiale) di fonti_normative.md: colonne complete, Stato che inizia con
    un valore riconosciuto, permalink che punta a una fonte ufficiale nota.
    """
    e = Esito()
    if not p.fonti_normative.exists():
        e.errore("references/fonti_normative.md non trovato")
        return e
    voci = 0
    problemi: list[str] = []
    in_tabella = False
    for i, riga in enumerate(p.fonti_normative.read_text(encoding="utf-8").splitlines(), start=1):
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
    for pr in problemi:
        e.errore(f"fonti_normative.md: {pr}")
    e.nota(f"fonti_normative.md: {voci} voci di catalogo verificate, {len(problemi)} problemi")
    return e


def check_tabelle_generiche(p: Percorsi) -> Esito:
    """Verifica strutturale (non semantica) delle tabelle markdown in tutti i
    file references/*.md: ogni riga dati di una tabella deve avere lo stesso
    numero di colonne della riga di intestazione che la apre. Non valida il
    contenuto (a differenza di check_catalogo_normativo, dedicata a
    fonti_normative.md): serve a evitare errori di battitura come una colonna
    in più o in meno, che altrimenti passerebbero inosservati fino a lettura.
    """
    e = Esito()
    problemi: list[str] = []
    tabelle = 0
    for path in sorted(p.refs_dir.glob("*.md")) if p.refs_dir.exists() else []:
        if path == p.fonti_normative:
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
    for pr in problemi:
        e.errore(f"tabelle references/: {pr}")
    e.nota(f"tabelle references/*.md: {tabelle} tabelle esaminate, {len(problemi)} problemi di colonne")
    return e


def check_maturita_aree(p: Percorsi) -> Esito:
    """Ogni sezione numerata di fonti_per_materia.md deve portare, nel titolo,
    un'etichetta di maturità riconosciuta — rende la dichiarazione di
    copertura machine-checkable: un'area nuova senza etichetta rompe la CI
    invece di passare inosservata.
    """
    e = Esito()
    if not p.fonti_per_materia.exists():
        e.errore("references/fonti_per_materia.md non trovato")
        return e
    sezioni = 0
    numeri: list[int] = []
    problemi: list[str] = []
    conteggi: dict[str, int] = {m: 0 for m in MATURITA_RICONOSCIUTE}
    for i, riga in enumerate(p.fonti_per_materia.read_text(encoding="utf-8").splitlines(), start=1):
        m = re.match(r"^## (\d+)\. (.+)$", riga)
        if not m:
            continue
        sezioni += 1
        numeri.append(int(m.group(1)))
        titolo = m.group(2)
        etichetta = next((et for et in MATURITA_RICONOSCIUTE if f"[{et}]" in titolo), None)
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
    for pr in problemi:
        e.errore(f"fonti_per_materia.md: {pr}")
    riepilogo = ", ".join(f"{k}: {v}" for k, v in conteggi.items())
    e.nota(f"fonti_per_materia.md: {sezioni} sezioni, maturità — {riepilogo}")
    return e


def check_url_references(p: Percorsi) -> Esito:
    """Ogni URL http(s) in references/*.md deve usare https — un check leggero
    (solo il protocollo, non il dominio) su tutti i file, a differenza di
    check_catalogo_normativo che valida anche il dominio ma solo per
    fonti_normative.md. Trovato un caso reale in schemi_atti.md durante
    l'audit del 2026-08-21 (link http:// a una fonte strutturale verificata),
    corretto insieme all'aggiunta di questo controllo.
    """
    e = Esito()
    problemi: list[str] = []
    for path in sorted(p.refs_dir.glob("*.md")) if p.refs_dir.exists() else []:
        for i, riga in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for url in re.findall(r"https?://[^\s)>\]]+", riga):
                if not url.startswith("https://"):
                    problemi.append(f"{path.name} riga {i}: URL non-https: {url}")
    for pr in problemi:
        e.errore(f"references/: {pr}")
    e.nota(f"references/*.md: URL non-https trovati: {len(problemi)}")
    return e


def check_coerenza_tool_lex(p: Percorsi) -> Esito:
    """Ogni nome di tool lex_* citato esplicitamente in SKILL.md deve esistere
    come chiave in schema/lex_tools_contract.json — stesso principio di
    check_reference_pointers applicato ai tool invece che ai file references/.
    """
    e = Esito()
    if not p.contract.exists() or not p.skill_md.exists():
        return e  # l'assenza è già segnalata dagli altri controlli
    try:
        contratto = json.loads(p.contract.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return e  # già segnalato da check_contract_schema
    tools = contratto.get("tools") if isinstance(contratto, dict) else None
    tool_contratto = set(tools.keys()) if isinstance(tools, dict) else set()
    # l'uso dei singoli tool sta in references/corpus_lex.md (caricato a
    # richiesta quando i tool ci sono): il controllo copre SKILL.md e references/
    testi = [p.skill_md.read_text(encoding="utf-8")]
    if p.refs_dir.exists():
        testi += [f.read_text(encoding="utf-8") for f in sorted(p.refs_dir.glob("*.md"))]
    citati = set(re.findall(r"lex_[a-z_]+", "\n".join(testi)))
    orfani = citati - tool_contratto - TOOL_LEX_CITAZIONE_NON_RICHIESTA
    if orfani:
        e.errore(f"SKILL.md o references/ citano tool lex_* assenti dal contratto: {sorted(orfani)}")
    non_citati = tool_contratto - citati
    if non_citati:
        e.nota(f"AVVISO (non bloccante): tool nel contratto mai citati per nome esplicito in SKILL.md o references/: {sorted(non_citati)}")
    e.nota(f"coerenza tool lex_*: {len(citati)} nomi citati in SKILL.md e references/, {len(tool_contratto)} nel contratto, {len(orfani)} orfani")
    return e


def check_crescita_skill(p: Percorsi) -> Esito:
    """Confronta la dimensione in byte di SKILL.md con quella all'ultimo tag
    git: solo informativo, non aggiunge mai errori (non deve bloccare la CI).
    Serve a rendere visibile una crescita rapida prima che diventi un problema
    di consumo di token, dato che la cronologia del progetto mostra che senza
    un promemoria esplicito la compattazione non emerge da sola.
    """
    e = Esito()
    if not p.skill_md.exists():
        return e
    try:
        tag = subprocess.run(
            ["git", "-C", str(p.root), "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True, timeout=5,
        )
        if tag.returncode != 0 or not tag.stdout.strip():
            e.nota("crescita SKILL.md: nessun tag trovato, controllo saltato")
            return e
        ultimo_tag = tag.stdout.strip()
        rel_path = p.skill_md.relative_to(p.root).as_posix()
        precedente = subprocess.run(
            ["git", "-C", str(p.root), "show", f"{ultimo_tag}:{rel_path}"],
            capture_output=True, timeout=5,
        )
        if precedente.returncode != 0:
            e.nota(f"crescita SKILL.md: SKILL.md non trovato al tag {ultimo_tag}, controllo saltato")
            return e
        dim_precedente = len(precedente.stdout)
        dim_attuale = p.skill_md.stat().st_size
        if dim_precedente == 0:
            return e
        crescita = (dim_attuale - dim_precedente) / dim_precedente * 100
        e.nota(f"SKILL.md: {dim_attuale} byte (era {dim_precedente} byte a {ultimo_tag}, {crescita:+.1f}%)")
        if crescita > 10:
            e.nota(f"AVVISO (non bloccante): SKILL.md cresciuto di oltre il 10% dall'ultimo tag ({ultimo_tag}) — valuta una compattazione prima del prossimo rilascio.")
    except (subprocess.SubprocessError, OSError, ValueError) as exc:
        e.nota(f"crescita SKILL.md: controllo saltato ({exc})")
    return e


def check_contract_schema(p: Percorsi) -> Esito:
    e = Esito()
    if not p.contract.exists():
        e.errore("schema/lex_tools_contract.json non trovato")
        return e
    try:
        d = json.loads(p.contract.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        e.errore(f"schema/lex_tools_contract.json non è JSON valido: {exc}")
        return e
    if not isinstance(d, dict) or "tools" not in d or not isinstance(d["tools"], dict):
        e.errore("schema/lex_tools_contract.json: campo 'tools' assente o non è un oggetto")
        return e
    e.nota(f"schema/lex_tools_contract.json: {len(d['tools'])} tool descritti")
    return e


CONTROLLI: tuple[Callable[[Percorsi], Esito], ...] = (
    check_evals,
    check_frontmatter,
    check_dimensione_skill,
    check_changelog,
    check_reference_pointers,
    check_catalogo_normativo,
    check_tabelle_generiche,
    check_maturita_aree,
    check_url_references,
    check_coerenza_tool_lex,
    check_crescita_skill,
    check_contract_schema,
)


def esegui_tutti(p: Percorsi) -> Esito:
    totale = Esito()
    for controllo in CONTROLLI:
        totale.estendi(controllo(p))
    return totale


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    solo_versione = "--versione" in args
    if solo_versione:
        args.remove("--versione")
    root = Path(args[0]).resolve() if args else ROOT_DEFAULT
    p = Percorsi(root)
    if solo_versione:
        versione = versione_dichiarata(p)
        if not versione:
            print("metadata.version assente nel frontmatter di SKILL.md", file=sys.stderr)
            return 1
        print(versione)
        return 0
    esito = esegui_tutti(p)
    for nota in esito.note:
        print(nota)
    if esito.errori:
        print("\nERRORI:")
        for err in esito.errori:
            print(f"  - {err}")
        return 1
    print("\nTutti i controlli statici superati.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
