#!/usr/bin/env python3
"""Audit meccanico dei permalink normativi nei cataloghi della skill.

Due livelli, entrambi ripetibili:

- offline (nessuna rete): in fonti_normative.md l'URN del permalink Normattiva
  di ogni voce deve corrispondere agli estremi dichiarati nella riga (tipo di
  atto, data, numero) — un copia-incolla sbagliato del link passerebbe
  inosservato a check_catalogo_normativo, che valida solo il formato;
- online (rete, opt-in): ogni permalink Normattiva unico in references/*.md
  (incluse le voci ad articolo `~artN` di percorsi_processuali.md e
  computo_termini.md) deve risolvere a una pagina il cui <title> riporta lo
  stesso atto dell'URN; ogni CELEX citato deve essere servito da
  publications.europa.eu (EUR-Lex diretto risponde con captcha ai fetch).

Un fetch al secondo, User-Agent da browser, nessun contenuto salvato: è un
controllo di coerenza dei link, non un'acquisizione. Dipende da rete e anti-bot:
come verifica_fonti.sh non è un gate di CI, si lancia a mano prima di un
rilascio o dopo aver toccato un catalogo. Le funzioni di parsing e confronto sono
pure e testate in tests/test_verifica_permalink.py.

Uso:  scripts/verifica_permalink.py            # offline + online
      scripts/verifica_permalink.py --offline  # solo coerenza URN/estremi, senza rete
"""

from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
REFS_DIR = ROOT / ".claude" / "skills" / "ricerca-giuridica-it" / "references"

MESI = ("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
        "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre")
# tipo di atto nell'URN Normattiva -> come Normattiva lo scrive nel <title>
TIPO_URN = {
    "regio.decreto": "REGIO DECRETO",
    "legge": "LEGGE",
    "decreto.legislativo": "DECRETO LEGISLATIVO",
    "decreto.legge": "DECRETO-LEGGE",
    "decreto.del.presidente.della.repubblica": "DECRETO DEL PRESIDENTE DELLA REPUBBLICA",
}
# abbreviazione usata nella colonna Estremi -> tipo di atto nell'URN
TIPO_ABBR = {"R.D.": "regio.decreto", "L.": "legge", "D.lgs.": "decreto.legislativo",
             "D.L.": "decreto.legge", "D.P.R.": "decreto.del.presidente.della.repubblica"}
RE_URN = re.compile(r"urn:nir:stato:([a-z.]+):(\d{4})-(\d{2})-(\d{2});(\d+)")
RE_ESTREMI = re.compile(r"^(D\.lgs\.|R\.D\.|L\.|D\.P\.R\.|D\.L\.)\s+(\d{1,2}\s+\w+\s+\d{4}),\s*n\.\s*(\d+)")
RE_URL_NORMATTIVA = re.compile(r"https://www\.normattiva\.it/uri-res/N2Ls\?[^\s)|>\]]+")
RE_CELEX = re.compile(r"CELEX:(\d{5}[A-Z]\d{4})")
RE_ELI_REG = re.compile(r"eur-lex\.europa\.eu/eli/reg/(\d{4})/(\d+)/oj")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"

Fetch = Callable[..., tuple[int, str]]


def urn_atteso(url: str) -> tuple[str, str | None, str | None] | None:
    """(tipo, 'g mese aaaa', numero) dall'URN del permalink; ('costituzione', None, None)
    per la Costituzione; None se l'URL non è un permalink Normattiva riconosciuto."""
    m = RE_URN.search(url)
    if m:
        tipo, a, me, g, n = m.groups()
        return tipo, f"{int(g)} {MESI[int(me) - 1]} {a}", n
    if "urn:nir:stato:costituzione" in url:
        return "costituzione", None, None
    return None


def estremi_parsati(estremi: str) -> tuple[str, str, str] | None:
    """(tipo URN, 'g mese aaaa', numero) dalla colonna Estremi; None se non è un atto statale datato."""
    m = RE_ESTREMI.match(estremi)
    if not m:
        return None
    abbr, data, num = m.groups()
    giorno, mese, anno = data.split()
    return TIPO_ABBR[abbr], f"{int(giorno)} {mese.lower()} {anno}", num


def titolo_coerente(titolo: str, atteso: tuple[str, str | None, str | None] | None) -> bool | None:
    """True se il <title> Normattiva descrive l'atto atteso; None se non c'è un atteso confrontabile."""
    if atteso is None:
        return None
    tipo, data, num = atteso
    if tipo == "costituzione":
        return "costituzione" in titolo.lower()
    if tipo not in TIPO_URN:
        return None
    return titolo.upper().startswith(f"{TIPO_URN[tipo]} {data}, n. {num}".upper())


def voci_fonti_normative(path: Path) -> list[tuple[int, str, str, str]]:
    voci = []
    for i, r in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not r.startswith("| ") or r.startswith("| Fonte |"):
            continue
        col = [c.strip() for c in r.strip().strip("|").split("|")]
        if len(col) == 4:
            voci.append((i, col[0], col[1], col[3]))
    return voci


def url_normattiva(refs_dir: Path) -> dict[str, set[str]]:
    urls: dict[str, set[str]] = {}
    for f in sorted(refs_dir.glob("*.md")):
        for u in RE_URL_NORMATTIVA.findall(f.read_text(encoding="utf-8")):
            urls.setdefault(u, set()).add(f.name)
    return urls


def celex_nei_cataloghi(refs_dir: Path) -> set[str]:
    celex: set[str] = set()
    for f in sorted(refs_dir.glob("*.md")):
        txt = f.read_text(encoding="utf-8")
        celex |= set(RE_CELEX.findall(txt))
        for anno, num in RE_ELI_REG.findall(txt):
            celex.add(f"3{anno}R{int(num):04d}")
    return celex


def verifica_offline(refs_dir: Path) -> list[dict]:
    esiti = []
    for riga, fonte, estremi, url in voci_fonti_normative(refs_dir / "fonti_normative.md"):
        if "normattiva.it" not in url:
            continue
        att = urn_atteso(url)
        dich = estremi_parsati(estremi)
        if att and att[0] == "costituzione":
            ok: bool | None = "Costituzione" in estremi
        elif dich is None:
            ok = None  # estremi non parsabili (voce da leggere a mano)
        else:
            ok = att == dich
        esiti.append({"riga": riga, "fonte": fonte, "estremi": estremi, "urn": att, "ok": ok})
    return esiti


def fetch_http(url: str, headers: dict[str, str] | None = None) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.status, r.read(400_000).decode("utf-8", "replace")


def _titolo(body: str) -> str:
    m = re.search(r"<title>([^<]*)</title>", body)
    return html.unescape(m.group(1)).strip() if m else ""


def verifica_online(urls: dict[str, set[str]], fetch: Fetch = fetch_http, pausa: float = 1.0,
                    log: Callable[[str], None] = print) -> list[dict]:
    esiti = []
    for k, (u, files) in enumerate(sorted(urls.items()), start=1):
        att = urn_atteso(u)
        esito: dict = {"url": u, "file": sorted(files), "atteso": att}
        try:
            st, body = fetch(u)
            esito["status"] = st
            esito["titolo"] = _titolo(body)
            esito["ok"] = titolo_coerente(esito["titolo"], att)
        except Exception as ex:  # rete, timeout, HTTP error: si registra e si prosegue
            esito.update(status="ERR", errore=str(ex)[:120], ok=False)
        esiti.append(esito)
        log(f"[{k}/{len(urls)}] {'OK' if esito['ok'] else 'KO'} {esito.get('titolo') or esito.get('errore', '')}"[:110])
        if k < len(urls):
            time.sleep(pausa)
    return esiti


def verifica_eurlex(celex: set[str], fetch: Fetch = fetch_http, pausa: float = 1.0,
                    log: Callable[[str], None] = print) -> list[dict]:
    """EUR-Lex diretto risponde 202/captcha ai fetch automatici; l'Ufficio delle
    pubblicazioni serve lo stesso atto con Accept xhtml e Accept-Language ita."""
    esiti = []
    for k, c in enumerate(sorted(celex), start=1):
        anno, num = c[1:5], str(int(c[6:]))
        e: dict = {"celex": c}
        try:
            st, body = fetch(f"https://publications.europa.eu/resource/celex/{c}",
                             {"Accept": "application/xhtml+xml", "Accept-Language": "ita"})
            e["status"] = st
            e["ok"] = f"{num}/{anno}" in body or f"{anno}/{num}" in body
        except Exception as ex:
            e.update(status="ERR", errore=str(ex)[:120], ok=False)
        esiti.append(e)
        log(f"CELEX {c}: {'OK' if e['ok'] else 'KO'} {e.get('errore', '')}")
        if k < len(celex):
            time.sleep(pausa)
    return esiti


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    solo_offline = "--offline" in args
    offline = verifica_offline(REFS_DIR)
    ko_off = [x for x in offline if x["ok"] is False]
    non_conf = [x for x in offline if x["ok"] is None]
    print(f"offline: {len(offline)} voci Normattiva in fonti_normative.md, {len(ko_off)} incoerenti, {len(non_conf)} non confrontabili")
    for x in ko_off:
        print(f"  KO riga {x['riga']}: {x['fonte']} — estremi '{x['estremi']}' vs URN {x['urn']}")
    for x in non_conf:
        print(f"  (a mano) riga {x['riga']}: {x['fonte']} — '{x['estremi']}'")
    ko_on: list[dict] = []
    ko_eu: list[dict] = []
    if not solo_offline:
        urls = url_normattiva(REFS_DIR)
        print(f"online: {len(urls)} permalink Normattiva unici in references/*.md")
        online = verifica_online(urls)
        ko_on = [x for x in online if not x["ok"]]
        celex = celex_nei_cataloghi(REFS_DIR)
        eurlex = verifica_eurlex(celex)
        ko_eu = [x for x in eurlex if not x["ok"]]
        print(f"online: {len(online)} permalink, {len(ko_on)} KO | EUR-Lex: {len(eurlex)} CELEX, {len(ko_eu)} KO")
        for x in ko_on:
            print(f"  KO {x['url']} ({', '.join(x['file'])}): {x.get('titolo') or x.get('errore')}")
        for x in ko_eu:
            print(f"  KO CELEX {x['celex']}: {x.get('errore', 'atto non riconosciuto nel testo servito')}")
        (ROOT / "evals" / "risultati").mkdir(parents=True, exist_ok=True)
        rapporto = ROOT / "evals" / "risultati" / "verifica_permalink.json"
        rapporto.write_text(json.dumps({"offline": offline, "online": online, "eurlex": eurlex}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"rapporto: {rapporto.relative_to(ROOT)}")
    if ko_off or ko_on or ko_eu:
        print("\nFALLITO: permalink incoerenti o non raggiungibili.")
        return 1
    print("\nOK: permalink coerenti" + ("" if solo_offline else " e pagine reali corrispondenti agli atti attesi."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
