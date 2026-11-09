#!/usr/bin/env python3
"""Privacy gate: backstop tecnico alla minimizzazione delle query (hook PreToolUse di Claude Code).

La skill chiede al modello di formulare le query verso il web e il corpus con soli concetti giuridici
astratti (SKILL.md, "Riservatezza e minimizzazione delle query"). Questo script e' il controllo
indipendente dal modello: legge dallo standard input il payload JSON dell'hook, scandisce gli input del
tool con regole deterministiche e, se trova dati identificativi, nega la chiamata (o chiede conferma,
per i rilevatori ambigui) prima che la query lasci la macchina.

Due livelli di rilevatori:
- BLOCCA: identificativi che in una query giuridica non sono mai un concetto astratto (codice fiscale,
  partita IVA, IBAN, targa, telefono, email/PEC, numero di ruolo generale, documento d'identita',
  ragione sociale, nome di file allegato, numero di polizza/sinistro). Decisione: deny.
- CHIEDI: pattern ambigui, che in una query possono essere legittimi (importi in euro, che sono anche
  soglie di legge; indirizzi; date di nascita; nome e cognome, riconosciuto dal solo nome proprio).
  Decisione: ask (in esecuzione headless equivale a deny).

Non copre: localita', patologie e altre categorie particolari, dettagli identificanti per combinazione.
Per quelli resta la regola comportamentale della skill.

Uso come hook (in ~/.claude/settings.json o .claude/settings.json):
  {"hooks": {"PreToolUse": [{"matcher": "^(WebSearch|WebFetch|mcp__.*__lex_.*)$",
    "hooks": [{"type": "command", "command": "python3 /percorso/scripts/privacy_gate.py", "timeout": 10}]}]}}
Variabile PRIVACY_GATE_MODE=redigi: invece di negare, sostituisce gli span rilevati con [OMISSIS:tipo]
(updatedInput) e lascia passare la query redatta.

Uso come banco di misura (nessun hook, nessuna rete):
  python3 scripts/privacy_gate.py --misura
Misura richiamo sulle stringhe vietate delle eval di minimizzazione e falsi positivi sul resto del
repository (eval legittime, cataloghi references/, GUIDA.md).
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
SKILL_DIR = RADICE / ".claude" / "skills" / "ricerca-giuridica-it"

BLOCCA = "blocca"
CHIEDI = "chiedi"


@dataclass(frozen=True)
class Rilevamento:
    tipo: str
    livello: str
    inizio: int
    fine: int
    testo: str


@dataclass
class Regola:
    tipo: str
    livello: str
    pattern: re.Pattern
    valida: object = None  # callable(match) -> bool, opzionale


# --- validatori di checksum: riducono i falsi positivi dei pattern numerici ---------------------

_CF_DISPARI = {
    "0": 1, "1": 0, "2": 5, "3": 7, "4": 9, "5": 13, "6": 15, "7": 17, "8": 19, "9": 21,
    "A": 1, "B": 0, "C": 5, "D": 7, "E": 9, "F": 13, "G": 15, "H": 17, "I": 19, "J": 21,
    "K": 2, "L": 4, "M": 18, "N": 20, "O": 11, "P": 3, "Q": 6, "R": 8, "S": 12, "T": 14,
    "U": 16, "V": 10, "W": 22, "X": 25, "Y": 24, "Z": 23,
}


def codice_fiscale_valido(cf: str) -> bool:
    cf = cf.upper()
    if len(cf) != 16:
        return False
    somma = 0
    for i, ch in enumerate(cf[:15]):
        if i % 2 == 0:  # posizioni dispari (1-based)
            somma += _CF_DISPARI[ch]
        else:
            somma += int(ch) if ch.isdigit() else ord(ch) - ord("A")
    return chr(ord("A") + somma % 26) == cf[15]


def partita_iva_valida(piva: str) -> bool:
    if len(piva) != 11 or not piva.isdigit():
        return False
    somma = 0
    for i, ch in enumerate(piva[:10]):
        n = int(ch)
        if i % 2 == 0:
            somma += n
        else:
            n *= 2
            somma += n - 9 if n > 9 else n
    return (10 - somma % 10) % 10 == int(piva[10])


def iban_valido(iban: str) -> bool:
    iban = iban.replace(" ", "").upper()
    if not (15 <= len(iban) <= 34):
        return False
    ruotato = iban[4:] + iban[:4]
    numerico = "".join(str(ord(c) - 55) if c.isalpha() else c for c in ruotato)
    return int(numerico) % 97 == 1


# --- nomi propri: lista di orientamento (livello CHIEDI, serve solo a riconoscere "Nome Cognome") ---

NOMI_PROPRI = set("""
Alessandro Alessandra Alessia Alberto Alice Andrea Angela Angelo Anna Antonio Antonella Arianna Aurora
Barbara Beatrice Benedetta Bruno Camilla Carla Carlo Carmela Carmine Caterina Chiara Christian Claudia
Claudio Cristina Cristian Daniela Daniele Dario Davide Debora Diego Domenico Donatella Edoardo Elena
Eleonora Elisa Elisabetta Emanuele Emanuela Emma Enrico Enzo Erika Fabio Fabrizio Federica Federico Filippo
Flavio Francesca Francesco Franco Gabriele Gabriella Gaia Gennaro Giacomo Giada Giancarlo Gianluca Gianni
Gioia Giorgia Giorgio Giovanna Giovanni Giulia Giuliano Giulio Giuseppe Giuseppina Greta Ilaria Irene
Jacopo Laura Leonardo Letizia Lorenzo Luca Lucia Luciano Luigi Luisa Manuel Manuela Marco Margherita Maria
Mariangela Marina Mario Marta Martina Massimiliano Massimo Matteo Mattia Maurizio Mauro Michela Michele
Mirko Monica Nicola Nicolo Nicolò Noemi Paola Paolo Pasquale Patrizia Pietro Raffaele Raffaella Riccardo
Roberta Roberto Rosa Rosaria Rosario Salvatore Samuele Sara Sergio Silvia Simona Simone Sofia Sonia
Stefania Stefano Teresa Tiziana Tommaso Umberto Valentina Valeria Valerio Veronica Vincenzo Vittoria Vittorio
Tizio Caio Sempronio Mevio
""".split())

_NOMI_ALT = "|".join(sorted(NOMI_PROPRI, key=len, reverse=True))
_SUFFISSI_SOCIETA = (
    r"s\.?\s?r\.?\s?l\.?(?:\s?s\.?)?|s\.?\s?p\.?\s?a\.?|s\.?\s?n\.?\s?c\.?|s\.?\s?a\.?\s?s\.?|s\.?\s?c\.?\s?a\s?r\.?\s?l\.?"
    r"|s\.?\s?s\.?|soc\.\s?coop\.?|cooperativa|GmbH|AG|Ltd\.?|LLC|Inc\.?|S\.?A\.?|SARL|SAS|BV|NV|PLC"
)
_TOPONIMO = r"(?:via|viale|v\.le|piazza|p\.zza|piazzale|corso|c\.so|largo|vicolo|vico|contrada|c\.da|strada|lungomare)"
_NON_STRADE = r"(?!(?:PEC|e-?mail|mail|posta|raccomandata|fax|telematica|telematico|web|internet|SMS|WhatsApp|giudiziale|stragiudiziale|amministrativa|ordinaria|breve|preliminare|incidentale|cautelare|di|del|della|dei|delle|interpretativa|analogica|generale|principale|subordinata|esclusiva|definitiva|provvisoria|transitoria|eccezionale|equitativa)\b)"

REGOLE: tuple[Regola, ...] = (
    Regola("codice_fiscale", BLOCCA,
           re.compile(r"(?<![A-Z0-9])[A-Z]{6}\d{2}[A-EHLMPRST]\d{2}[A-Z]\d{3}[A-Z](?![A-Z0-9])", re.I)),
    Regola("iban", BLOCCA,
           re.compile(r"(?<![A-Z0-9])[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{4}){2,7}(?:\s?[A-Z0-9]{1,4})?(?![A-Z0-9])"),
           lambda m: iban_valido(m.group(0))),
    Regola("partita_iva", BLOCCA,
           re.compile(r"(?:(?:P\.?\s?IVA|partita\s+IVA|C\.?\s?F\.?|codice\s+fiscale|VAT)\s*(?:n\.?\s*)?[:.]?\s*(?:IT\s?)?)?(?<!\d)(?<!\d[.,/-])\d{11}(?!\d)(?![.,/-]\d)", re.I),
           lambda m: partita_iva_valida(m.group(0)[-11:]) or not m.group(0)[0].isdigit()),
    Regola("email", BLOCCA,
           re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    Regola("telefono", BLOCCA,
           re.compile(r"(?<![\d/.-])(?:\+39[\s.]?)?(?:0\d{1,3}[\s.\-/]\d{5,8}|3\d{2}[\s.\-]?\d{6,7}|0\d{8,9})(?![\d/])")),
    Regola("targa", BLOCCA,
           re.compile(r"(?<![A-Z0-9])[A-Z]{2}\s?\d{3}\s?[A-Z]{2}(?![A-Z0-9])")),
    Regola("ruolo_generale", BLOCCA,
           re.compile(r"(?:\bR\.?\s?G\.?|ruolo\s+generale|\bN\.?\s?R\.?\s?G\.?)\s*(?:n\.?\s*)?\d{1,7}\s*/\s*(?:19|20)?\d{2}\b", re.I)),
    Regola("documento_identita", BLOCCA,
           re.compile(r"(?<![A-Z0-9])(?:[A-Z]{2}\d{7}|C[A-Z]\d{5}[A-Z]{2})(?![A-Z0-9])")),
    Regola("polizza_sinistro", BLOCCA,
           re.compile(r"\b(?:polizza|sinistro|pratica|contratto)\s+(?:RCA\s+)?n(?:\.|umero|°)?\s*[A-Z0-9][A-Z0-9\-/]{3,}", re.I)),
    Regola("file_allegato", BLOCCA,
           re.compile(r"(?<![/\w.-])[\w\-]+(?:\.[\w\-]+)*\.(?:pdf|docx?|odt|rtf|p7m|eml|msg|xlsx?|zip|jpe?g|png)\b", re.I)),
    Regola("ragione_sociale", BLOCCA,
           re.compile(r"\b(?:[A-Z][\w&'’.-]*\s+){1,4}(?i:" + _SUFFISSI_SOCIETA + r")(?![\w])")),
    Regola("nome_cognome", CHIEDI,
           re.compile(r"(?<!\bSan )(?<!\bSanta )(?<!\bSant')\b(?:" + _NOMI_ALT + r")\s+(?:[Dd][aeio]\s+|[Dd]e[gl]l[ai']\s?|[Dd]al\s+)?[A-Z][a-zà-ù'’]{2,}(?:\s+[A-Z][a-zà-ù'’]{2,})?")),
    Regola("indirizzo", CHIEDI,
           re.compile(r"\b" + _TOPONIMO + r"\s+" + _NON_STRADE + r"(?:[A-Z][\w'’.-]*\s*){1,4},?\s*(?:n\.?\s*)?\d{1,4}(?:/?[A-Za-z])?\b", re.I)),
    Regola("data_nascita", CHIEDI,
           re.compile(r"\b(?:nat[oa]\s+(?:a\s+[A-Z][\w'’ -]+?\s+)?il|data\s+di\s+nascita[: ]+)\s*\d{1,2}[\s./-](?:\d{1,2}|[a-z]+)[\s./-]\d{2,4}\b", re.I)),
    # frase intera tra virgolette (> 12 parole): e' il frammento di un documento del caso incollato nella
    # query, vietato dalla regola "solo locuzioni tecniche brevi tra virgolette"
    Regola("citazione_lunga", CHIEDI,
           re.compile(r"(?<![\w)])(?:[\"“«](?:[^\s\"”»]+[ \t]+){12,}[^\s\"”»]+[\"”»]"
                      r"|(?<![\w)\]])'(?:(?:[^\s']|'(?=\w))+[ \t]+){12,}(?:[^\s']|'(?=\w))+'(?!\w))")),
    Regola("importo", CHIEDI,
           re.compile(r"(?:€\s?\d[\d.]*(?:,\d{1,2})?|\b\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?\s?(?:€|euro)\b|\b\d+(?:,\d{1,2})?\s?(?:€|euro)\b)", re.I)),
)

_SPIEGAZIONE = {
    "codice_fiscale": "codice fiscale", "iban": "IBAN", "partita_iva": "partita IVA", "email": "indirizzo email/PEC",
    "telefono": "numero di telefono", "targa": "targa", "ruolo_generale": "numero di ruolo generale",
    "documento_identita": "numero di documento d'identità", "polizza_sinistro": "numero di polizza/sinistro/pratica",
    "file_allegato": "nome di file allegato", "ragione_sociale": "ragione sociale",
    "nome_cognome": "possibile nome e cognome", "indirizzo": "possibile indirizzo", "data_nascita": "data di nascita",
    "importo": "importo in euro (può essere una soglia di legge: conferma se è astratto)",
    "citazione_lunga": "frase intera tra virgolette (frammento di documento del caso?)",
}

# Nomi di eccezione per la regola ragione_sociale: sigle che precedono comunemente "S.p.A."/"s.r.l." in
# testi normativi astratti e non identificano una parte.
_SOCIETA_ASTRATTE = re.compile(r"^(?:Società|Societa|Le|La|Una|Delle|Nelle|Della|Tra|Per|Ogni|Nella|Alla|Dalla|Con|Di|Da|In|Su|Tipo|Forma|Modello|Statuto|Trasformazione|Fusione|Scissione|Costituzione|Amministratore|Amministratori|Socio|Soci|Liquidazione|Fallimento|Responsabilità|Responsabilita|Capitale|Quote|Azioni|Assemblea|Bilancio|Recesso|Esclusione|Cessione|Trasferimento|Governance|Organi|Controllo|Collegio|Sindaci|Revisore|Partecipazione|Start-up|Startup|PMI|Srl|Spa|S\.r\.l\.|S\.p\.A\.|Le\s|Il\s|Lo\s)", re.I)


def _norm(span: str) -> str:
    return span.strip()


def rileva(testo: str) -> list[Rilevamento]:
    """Restituisce gli span sospetti nel testo, ordinati per posizione, senza sovrapposizioni."""
    trovati: list[Rilevamento] = []
    for regola in REGOLE:
        for m in regola.pattern.finditer(testo):
            if regola.valida is not None and not regola.valida(m):
                continue
            span = m.group(0)
            if regola.tipo == "ragione_sociale":
                prima = span.rsplit(None, 1)[0] if " " in span else span
                if _SOCIETA_ASTRATTE.match(prima):
                    continue
            trovati.append(Rilevamento(regola.tipo, regola.livello, m.start(), m.end(), _norm(span)))
    # rimuovi sovrapposizioni: prima gli span BLOCCA (il piu' esteso vince), poi i CHIEDI che non si
    # sovrappongono a nessuno span gia' tenuto — un identificativo dentro una citazione lunga resta BLOCCA
    esito: list[Rilevamento] = []
    for livello in (BLOCCA, CHIEDI):
        for r in sorted((x for x in trovati if x.livello == livello), key=lambda r: (r.inizio, -(r.fine - r.inizio))):
            if any(r.inizio < k.fine and k.inizio < r.fine for k in esito):
                continue
            esito.append(r)
    esito.sort(key=lambda r: r.inizio)
    return esito


def livello_complessivo(rilevamenti: list[Rilevamento]) -> str | None:
    if any(r.livello == BLOCCA for r in rilevamenti):
        return BLOCCA
    if rilevamenti:
        return CHIEDI
    return None


def redigi(testo: str, rilevamenti: list[Rilevamento]) -> str:
    out = []
    pos = 0
    for r in rilevamenti:
        out.append(testo[pos:r.inizio])
        out.append(f"[OMISSIS:{r.tipo}]")
        pos = r.fine
    out.append(testo[pos:])
    return "".join(out)


# --- payload dell'hook -----------------------------------------------------------------------------

def stringhe_in(valore, percorso: str = "") -> list[tuple[str, str]]:
    """Coppie (percorso, stringa) per ogni stringa nel tool_input, a qualunque profondita'."""
    if isinstance(valore, str):
        return [(percorso, valore)]
    if isinstance(valore, dict):
        acc = []
        for k, v in valore.items():
            acc.extend(stringhe_in(v, f"{percorso}.{k}" if percorso else str(k)))
        return acc
    if isinstance(valore, list):
        acc = []
        for i, v in enumerate(valore):
            acc.extend(stringhe_in(v, f"{percorso}[{i}]"))
        return acc
    return []


def _senza_url(testo: str) -> str:
    """Gli URL verso le fonti ufficiali restano fuori dalla scansione: il percorso di un permalink
    Normattiva o un PDF della Gazzetta non e' un dato personale. Il resto del testo si scandisce."""
    return re.sub(r"https?://\S+", " ", testo)


@dataclass
class Decisione:
    livello: str | None
    rilevamenti: list[tuple[str, Rilevamento]] = field(default_factory=list)  # (campo, rilevamento)

    def motivo(self) -> str:
        tipi = sorted({_SPIEGAZIONE.get(r.tipo, r.tipo) for _, r in self.rilevamenti})
        campi = sorted({campo for campo, _ in self.rilevamenti})
        testa = ("Privacy gate: la query contiene dati identificativi" if self.livello == BLOCCA
                 else "Privacy gate: la query contiene dati che potrebbero identificare il caso")
        return (f"{testa} ({', '.join(tipi)}) nel campo {', '.join(campi)}. "
                "Le query verso web e corpus devono contenere solo concetti giuridici astratti "
                "(SKILL.md, Riservatezza e minimizzazione delle query): riformula senza nomi di parti, "
                "identificativi, estremi di procedimenti o documenti del caso.")


def valuta(tool_input) -> Decisione:
    coppie = []
    for campo, testo in stringhe_in(tool_input):
        for r in rileva(_senza_url(testo)):
            coppie.append((campo, r))
    return Decisione(livello_complessivo([r for _, r in coppie]), coppie)


def redigi_input(tool_input):
    """Copia del tool_input con gli span rilevati sostituiti da [OMISSIS:tipo]."""
    if isinstance(tool_input, str):
        return redigi(tool_input, rileva(_senza_url(tool_input))) if "http" not in tool_input else tool_input
    if isinstance(tool_input, dict):
        return {k: redigi_input(v) for k, v in tool_input.items()}
    if isinstance(tool_input, list):
        return [redigi_input(v) for v in tool_input]
    return tool_input


def esito_hook(payload: dict, modo: str = "nega") -> dict | None:
    """Output JSON per Claude Code, o None se la chiamata passa senza osservazioni."""
    decisione = valuta(payload.get("tool_input", {}))
    if decisione.livello is None:
        return None
    if modo == "redigi" and decisione.livello == BLOCCA:
        esito = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "updatedInput": redigi_input(payload.get("tool_input", {})),
            },
        }
        esito["hookSpecificOutput"]["additionalContext"] = (
            decisione.motivo() + " La query è stata redatta automaticamente: gli span sostituiti da "
            "[OMISSIS:...] non hanno lasciato la macchina.")
        return esito
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny" if decisione.livello == BLOCCA else "ask",
            "permissionDecisionReason": decisione.motivo(),
        },
    }


# --- banco di misura -------------------------------------------------------------------------------

def misura(evals_path: Path, refs_dir: Path, extra: list[Path]) -> dict:
    dati = json.loads(evals_path.read_text(encoding="utf-8"))
    evals = dati["evals"] if isinstance(dati, dict) else dati

    # richiamo: le stringhe vietate devono cadere dentro uno span rilevato nel prompt
    richiamo = []
    for e in evals:
        vietate = (e.get("checks") or {}).get("tool_input_must_not_include") or []
        if not vietate:
            continue
        prompt = e["prompt"]
        spans = rileva(_senza_url(prompt))
        for s in vietate:
            pos = prompt.find(s)
            colpita = None
            if pos >= 0:
                for r in spans:
                    if r.inizio <= pos and pos + len(s) <= r.fine or (r.inizio < pos + len(s) and pos < r.fine):
                        colpita = r
                        break
            richiamo.append({"eval": e["id"], "stringa": s, "presente_nel_prompt": pos >= 0,
                             "rilevata": colpita is not None,
                             "tipo": colpita.tipo if colpita else None,
                             "livello": colpita.livello if colpita else None})

    # falsi positivi: testo legittimo. Non i prompt (sono testo dell'utente, che puo' contenere i dati del
    # caso: l'hook non li vede), ma gli expected_output delle eval senza vincolo di minimizzazione, i
    # cataloghi references/ e gli altri file passati — tutto testo che in una query sarebbe lecito.
    legittimi: list[tuple[str, str]] = []
    for e in evals:
        if (e.get("checks") or {}).get("tool_input_must_not_include"):
            continue
        legittimi.append((f"eval {e['id']} expected_output", e.get("expected_output", "")))
    for p in sorted(refs_dir.glob("*.md")) + extra:
        for i, riga in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
            legittimi.append((f"{p.name}:{i}", riga))
    falsi = []
    for origine, testo in legittimi:
        for r in rileva(_senza_url(testo)):
            falsi.append({"origine": origine, "tipo": r.tipo, "livello": r.livello, "testo": r.testo})

    rilevate = [x for x in richiamo if x["rilevata"]]
    return {
        "richiamo": {"stringhe": len(richiamo), "rilevate": len(rilevate),
                     "blocca": sum(1 for x in rilevate if x["livello"] == BLOCCA),
                     "chiedi": sum(1 for x in rilevate if x["livello"] == CHIEDI),
                     "dettaglio": richiamo},
        "falsi_positivi": {"testi_legittimi": len(legittimi), "segnalazioni": len(falsi),
                           "blocca": sum(1 for x in falsi if x["livello"] == BLOCCA),
                           "chiedi": sum(1 for x in falsi if x["livello"] == CHIEDI),
                           "dettaglio": falsi},
    }


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "--misura":
        extra = [RADICE / "GUIDA.md", SKILL_DIR / "SKILL.md"]
        esito = misura(RADICE / "evals" / "evals.json", SKILL_DIR / "references", [p for p in extra if p.exists()])
        r, f = esito["richiamo"], esito["falsi_positivi"]
        print(f"Richiamo: {r['rilevate']}/{r['stringhe']} stringhe vietate rilevate "
              f"({r['blocca']} blocca, {r['chiedi']} chiedi)")
        for x in r["dettaglio"]:
            stato = f"OK  {x['livello']:6} {x['tipo']}" if x["rilevata"] else "--  non coperta"
            print(f"  eval {x['eval']:>3}  {stato:34} {x['stringa']!r}")
        print(f"Falsi positivi: {f['segnalazioni']} su {f['testi_legittimi']} testi legittimi "
              f"({f['blocca']} blocca, {f['chiedi']} chiedi)")
        for x in f["dettaglio"]:
            print(f"  {x['livello']:6} {x['tipo']:18} {x['origine']:40} {x['testo']!r}")
        out = RADICE / "evals" / "risultati" / "privacy_gate_misura.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(esito, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Nota: SKILL.md e cartella_di_lavoro.md contengono esempi deliberati di query da evitare; "
              "una segnalazione su quelle righe è una rilevazione corretta, non un falso positivo.")
        print(f"Dettaglio in {out}")
        return 0
    if argv and argv[0] == "--testo":
        testo = " ".join(argv[1:]) or sys.stdin.read()
        for r in rileva(_senza_url(testo)):
            print(f"{r.livello:6} {r.tipo:18} {r.testo!r}")
        return 0
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0  # payload illeggibile: non bloccare per un difetto del gate
    modo = "redigi" if os.environ.get("PRIVACY_GATE_MODE", "").lower() == "redigi" else "nega"
    esito = esito_hook(payload, modo)
    if esito is not None:
        print(json.dumps(esito, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
