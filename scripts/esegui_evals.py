#!/usr/bin/env python3
"""Esegue le eval del repo contro Claude Code in modalità headless e produce
un rapporto con tre livelli di verifica per ciascuna:

1. assertion deterministiche must_include / must_not_include sulla risposta
   finale (confronto di stringhe, nessun giudizio linguistico coinvolto);
2. controlli sugli input passati ai tool durante la conversazione — non sulla
   risposta: checks.tool_input_must_not_include (dati identificativi che non
   devono uscire: minimizzazione delle query) e checks.tool_input_must_include
   (letture o chiamate che devono avvenire, es. il file di modalità in
   references/ da leggere prima di rispondere);
3. giudice LLM come ultimo livello, per la qualità comportamentale che una
   stringa non cattura.

Un FAIL su un livello deterministico non arriva al giudice: è già un fatto,
non un'opinione.

Va lanciato da un terminale normale (NON dentro una sessione Claude Code: la
sessione annidata è rifiutata). Le eval TEMPLATE, che descrivono un
comportamento senza un prompt concreto, vengono saltate e vanno collaudate a
mano in sessione interattiva: sottoponi il prompt alla skill e confronta la
risposta con expected_output.

Nota sul livello 2: usa --output-format stream-json per ispezionare anche gli
input dei tool_use. Il formato NDJSON non ha uno schema pubblico stabile: se il
parsing non riconosce nulla (CLI aggiornato, formato cambiato), lo script non si
blocca — perde il livello 2 per quella eval e lo segnala, ricostruendo la
risposta dal campo "result" del messaggio finale quando c'è, o dal grezzo come
extrema ratio. Se dopo un aggiornamento del CLI vedi solo AVVISI, ispeziona un
file *.stream.jsonl in evals/risultati/ e adatta `analizza_stream`.

Il parsing dello stream e i livelli 1-2 sono funzioni pure, testate in
tests/test_esegui_evals.py; l'invocazione di `claude` è iniettabile (`run`).

Uso:  scripts/esegui_evals.py [id ...]     # senza argomenti: tutte
      EVAL_WEB=1 scripts/esegui_evals.py   # aggiunge WebSearch e WebFetch, per le eval in Fallback web
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
EVALS_DEFAULT = ROOT / "evals" / "evals.json"
RISULTATI_DEFAULT = ROOT / "evals" / "risultati"

TOOLS_BASE = (
    "Skill",
    "mcp__lex-corpus",
    "mcp__lex-corpus__lex_stato_corpus",
    "mcp__lex-corpus__lex_cerca_norma",
    "mcp__lex-corpus__lex_leggi_articolo",
    "mcp__lex-corpus__lex_cerca_giurisprudenza",
    "mcp__lex-corpus__lex_cerca_prassi",
    "mcp__lex-corpus__lex_verifica_citazione",
)
# EVAL_WEB=1 aggiunge ricerca e fetch web: serve alle eval che esercitano il
# Fallback web (senza corpus, o su temi che il corpus non copre). Dipende dalla
# rete e dagli anti-bot dei siti, quindi resta opt-in e non è mai un gate.
TOOLS_WEB = ("WebSearch", "WebFetch")

PROMPT_GIUDICE = (
    "Sei il giudice di una eval. RISPOSTA DA VALUTARE: <<<{risposta}>>> "
    "COMPORTAMENTO ATTESO: <<<{atteso}>>> Rispondi con una sola riga: PASS oppure FAIL, "
    "due punti, motivo in una frase. Sii severo sugli estremi normativi: un estremo "
    "diverso dall'atteso è FAIL."
)
GIUDICE_NON_ESEGUITO = "FAIL: giudice non eseguito"

# Firma di subprocess.run: (cmd, **kwargs) -> CompletedProcess. Iniettabile nei test.
Esecutore = Callable[..., "subprocess.CompletedProcess[str]"]


@dataclass
class Stream:
    """Quanto si ricava dallo stream NDJSON di `claude -p --output-format stream-json`."""

    risposta: str
    tool_inputs: list[str]
    result_trovato: bool

    @property
    def tool_input_testo(self) -> str:
        return "\n".join(self.tool_inputs)


def analizza_stream(testo: str) -> Stream:
    """Ricostruisce la risposta finale (campo `result` dell'evento finale) e la
    lista degli input dei tool_use (eventi `assistant`). Righe non JSON o eventi
    sconosciuti vengono ignorati; senza evento `result` la risposta è il grezzo
    concatenato, extrema ratio, e `result_trovato` è False."""
    result_text: str | None = None
    grezze: list[str] = []
    tool_inputs: list[str] = []
    for riga in testo.splitlines():
        riga = riga.strip()
        if not riga:
            continue
        grezze.append(riga)
        try:
            ev = json.loads(riga)
        except json.JSONDecodeError:
            continue
        if not isinstance(ev, dict):
            continue
        tipo = ev.get("type")
        if tipo == "result":
            result_text = str(ev.get("result", ""))
        elif tipo == "assistant":
            contenuto = (ev.get("message") or {}).get("content") or []
            for blocco in contenuto:
                if isinstance(blocco, dict) and blocco.get("type") == "tool_use":
                    tool_inputs.append(json.dumps(blocco.get("input", {}), ensure_ascii=False))
    if result_text is not None:
        return Stream(result_text, tool_inputs, True)
    return Stream("\n".join(grezze), tool_inputs, False)


def strumenti(eval_web: bool) -> str:
    return ",".join(TOOLS_BASE + (TOOLS_WEB if eval_web else ()))


def seleziona_eval(evals: list[dict], ids: set[int] | None) -> list[dict]:
    return [e for e in evals if ids is None or e.get("id") in ids]


def livello_assertion(checks: dict, risposta: str) -> tuple[str, str]:
    """Livello 1: stringhe sulla risposta finale (confronto senza maiuscole)."""
    r = risposta.lower()
    mancanti = [s for s in checks.get("must_include") or [] if s.lower() not in r]
    vietati = [s for s in checks.get("must_not_include") or [] if s.lower() in r]
    if mancanti or vietati:
        dett = []
        if mancanti:
            dett.append("mancanti: " + "; ".join(mancanti))
        if vietati:
            dett.append("presenti e vietati: " + "; ".join(vietati))
        return "FAIL", " | ".join(dett)
    if not checks.get("must_include") and not checks.get("must_not_include"):
        return "OK", "nessuna assertion definita"
    return "OK", "assertion soddisfatte"


def livello_tool_input(checks: dict, tool_input: str) -> tuple[str, str]:
    """Livello 2: stringhe sugli input dei tool_use. Senza tool_use nello stream
    il controllo di minimizzazione si salta con AVVISO (non si può dire nulla),
    ma una lettura richiesta non avvenuta è un FAIL: fatto, non opinione."""
    vietati = checks.get("tool_input_must_not_include") or []
    richiesti = checks.get("tool_input_must_include") or []
    if not vietati and not richiesti:
        return "OK", "nessun controllo sugli input dei tool definito"
    if not tool_input.strip():
        if richiesti:
            return "FAIL", "nessun tool_use rilevato nello stream, ma l'eval richiede: " + "; ".join(richiesti)
        return "AVVISO", "nessun tool_use rilevato nello stream (formato non riconosciuto o nessun tool chiamato): controllo saltato"
    t = tool_input.lower()
    presenti = [s for s in vietati if s.lower() in t]
    mancanti = [s for s in richiesti if s.lower() not in t]
    if presenti or mancanti:
        dett = []
        if presenti:
            dett.append("dati identificativi presenti negli input dei tool: " + "; ".join(presenti))
        if mancanti:
            dett.append("letture o chiamate richieste non avvenute: " + "; ".join(mancanti))
        return "FAIL", " | ".join(dett)
    return "OK", "input dei tool conformi (nessun dato identificativo; letture richieste avvenute)"


def esito_giudice(testo: str) -> bool:
    return testo.strip().startswith("PASS")


@dataclass
class Riepilogo:
    superate: int = 0
    fallite: int = 0
    template: int = 0
    per_eval: dict[str, dict] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {"pass": self.superate, "fail": self.fallite, "template_saltate": self.template, "per_eval": self.per_eval}


def esegui(
    evals: list[dict],
    out: Path,
    eval_web: bool = False,
    run: Esecutore = subprocess.run,
    log: Callable[[str], None] = print,
) -> Riepilogo:
    """Esegue le eval date scrivendo in `out` gli stessi file del runner storico:
    <id>.stream.jsonl, <id>.err, <id>.risposta.md, <id>.tool_input.txt,
    <id>.giudizio.txt, più _riepilogo.json con l'esito per eval."""
    out.mkdir(parents=True, exist_ok=True)
    tools = strumenti(eval_web)
    r = Riepilogo()
    for e in evals:
        ident = str(e.get("id"))
        prompt = str(e.get("prompt", ""))
        checks = e.get("checks") or {}
        if prompt.startswith("TEMPLATE"):
            r.template += 1
            r.per_eval[ident] = {"stato": "TEMPLATE"}
            log(f"eval {ident}: TEMPLATE (richiede collaudo manuale interattivo)")
            continue
        log(f"eval {ident}: esecuzione...")
        stream_path = out / f"{ident}.stream.jsonl"
        err_path = out / f"{ident}.err"
        with stream_path.open("w", encoding="utf-8") as f_out, err_path.open("w", encoding="utf-8") as f_err:
            run(
                ["claude", "-p", prompt, "--allowedTools", tools, "--output-format", "stream-json", "--verbose"],
                stdout=f_out, stderr=f_err, text=True, check=False,
            )
        st = analizza_stream(stream_path.read_text(encoding="utf-8"))
        (out / f"{ident}.risposta.md").write_text(st.risposta, encoding="utf-8")
        (out / f"{ident}.tool_input.txt").write_text(st.tool_input_testo, encoding="utf-8")
        giudizio_path = out / f"{ident}.giudizio.txt"

        stato1, dett1 = livello_assertion(checks, st.risposta)
        if stato1 == "FAIL":
            giudizio_path.write_text(f"FAIL: assertion deterministica — {dett1}\n", encoding="utf-8")
            r.fallite += 1
            r.per_eval[ident] = {"stato": "FAIL", "livello": 1, "dettaglio": dett1}
            log(f"  -> FAIL (assertion deterministica: {dett1})")
            continue

        stato2, dett2 = livello_tool_input(checks, st.tool_input_testo)
        if stato2 == "FAIL":
            giudizio_path.write_text(f"FAIL: input dei tool — {dett2}\n", encoding="utf-8")
            r.fallite += 1
            r.per_eval[ident] = {"stato": "FAIL", "livello": 2, "dettaglio": dett2}
            log(f"  -> FAIL (input dei tool: {dett2})")
            continue
        if stato2 == "AVVISO":
            log(f"  (nota: {dett2})")

        prompt_giudice = PROMPT_GIUDICE.format(risposta=st.risposta, atteso=str(e.get("expected_output", "")))
        esito = run(["claude", "-p", prompt_giudice, "--output-format", "text"], capture_output=True, text=True, check=False)
        giudizio = (esito.stdout or "").strip() if esito.returncode == 0 else ""
        if not giudizio:
            giudizio = GIUDICE_NON_ESEGUITO
        giudizio_path.write_text(giudizio + "\n", encoding="utf-8")
        if esito_giudice(giudizio):
            r.superate += 1
            stato = "PASS"
        else:
            r.fallite += 1
            stato = "FAIL"
        r.per_eval[ident] = {"stato": stato, "livello": 3, "dettaglio": giudizio, "assertion": dett1, "tool_input": dett2}
        log(f"  -> {giudizio} ({dett1})")

    (out / "_riepilogo.json").write_text(json.dumps(r.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    log("")
    log(f"Esito: PASS={r.superate} FAIL={r.fallite} TEMPLATE_SALTATE={r.template} — dettagli in {out}/")
    return r


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if os.environ.get("CLAUDECODE"):
        print("Non lanciare da dentro Claude Code: apri un terminale normale.", file=sys.stderr)
        return 1
    if not shutil.which("claude"):
        print("claude CLI non trovato", file=sys.stderr)
        return 1
    try:
        ids: set[int] | None = {int(a) for a in args} or None
    except ValueError:
        print("gli id delle eval devono essere interi", file=sys.stderr)
        return 2
    evals = json.loads(EVALS_DEFAULT.read_text(encoding="utf-8"))["evals"]
    out = RISULTATI_DEFAULT / datetime.now().strftime("%Y%m%d_%H%M")
    riepilogo = esegui(seleziona_eval(evals, ids), out, eval_web=os.environ.get("EVAL_WEB", "0") == "1")
    return 0 if riepilogo.fallite == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
