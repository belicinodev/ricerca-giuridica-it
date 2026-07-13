#!/bin/bash
# Esegue le eval del repo contro Claude Code in modalità headless e produce un
# rapporto con tre livelli di verifica per ciascuna: (1) assertion
# deterministiche must_include/must_not_include sulla risposta finale (grep,
# nessun giudizio linguistico coinvolto); (2) quando l'eval definisce
# checks.tool_input_must_not_include, verifica che quelle stringhe non
# compaiano negli input passati ai tool durante la conversazione — non solo
# nella risposta finale: livello mirato alla minimizzazione delle query; (3)
# giudice LLM come ultimo livello, per la qualità comportamentale che una
# stringa non cattura. Un FAIL su un livello deterministico non arriva al
# giudice: è già un fatto, non un'opinione.
#
# Va lanciato da un terminale normale (NON dentro una sessione Claude Code:
# la sessione annidata è bloccata). Le eval TEMPLATE, che descrivono un
# comportamento senza un prompt concreto, vengono saltate e vanno collaudate
# manualmente in sessione interattiva: sottoponi il prompt alla skill e
# confronta la risposta con expected_output.
#
# Nota tecnica sul livello 2: usa --output-format stream-json per poter
# ispezionare anche gli input dei tool_use, non solo la risposta finale. Il
# formato NDJSON esatto non ha uno schema pubblico stabile documentato: se il
# parsing non riconosce nulla (CLI aggiornato, formato cambiato), lo script
# non si blocca — perde solo il livello 2 per quella eval e lo segnala con un
# AVVISO, ricostruendo comunque la risposta testuale dal campo "result" del
# messaggio finale quando presente, o dal contenuto grezzo come extrema
# ratio. Se al primo utilizzo dopo un aggiornamento del CLI vedi solo AVVISI,
# ispeziona un file *.stream.jsonl in evals/risultati/ per adattare il parser.
#
# Uso:  scripts/esegui_evals.sh [id ...]     # senza argomenti: tutte
set -euo pipefail
cd "$(dirname "$0")/.."

command -v claude >/dev/null || { echo "claude CLI non trovato"; exit 1; }
command -v python3 >/dev/null || { echo "python3 non trovato"; exit 1; }
[ -z "${CLAUDECODE:-}" ] || { echo "Non lanciare da dentro Claude Code: apri un terminale normale."; exit 1; }

STAMP=$(date +%Y%m%d_%H%M)
OUT="evals/risultati/$STAMP"
mkdir -p "$OUT"
TOOLS="Skill,mcp__lex-corpus,mcp__lex-corpus__lex_stato_corpus,mcp__lex-corpus__lex_cerca_norma,mcp__lex-corpus__lex_leggi_articolo,mcp__lex-corpus__lex_cerca_giurisprudenza,mcp__lex-corpus__lex_cerca_prassi,mcp__lex-corpus__lex_verifica_citazione"

python3 - "$@" <<'PYEOF' > "$OUT/_lista.tsv"
import json, sys
evals = json.load(open('evals/evals.json'))['evals']
ids = {int(x) for x in sys.argv[1:]} if len(sys.argv) > 1 else None
for e in evals:
    if ids and e['id'] not in ids:
        continue
    if e['prompt'].startswith('TEMPLATE'):
        print(f"{e['id']}\tSKIP_TEMPLATE\t")
        continue
    dati = {'p': e['prompt'], 'a': e['expected_output'], 'checks': e.get('checks', {})}
    print(f"{e['id']}\tRUN\t{json.dumps(dati, ensure_ascii=False)}")
PYEOF

PASS=0; FAIL=0; SKIP=0
while IFS=$'\t' read -r ID AZIONE DATI; do
  if [ "$AZIONE" = "SKIP_TEMPLATE" ]; then
    SKIP=$((SKIP+1)); echo "eval $ID: TEMPLATE (richiede collaudo manuale interattivo)"; continue
  fi
  PROMPT=$(printf '%s' "$DATI" | python3 -c "import json,sys; print(json.load(sys.stdin)['p'])")
  ATTESO=$(printf '%s' "$DATI" | python3 -c "import json,sys; print(json.load(sys.stdin)['a'])")
  echo "eval $ID: esecuzione..."
  claude -p "$PROMPT" --allowedTools "$TOOLS" --output-format stream-json --verbose > "$OUT/$ID.stream.jsonl" 2>"$OUT/$ID.err" || true

  # Ricostruisce la risposta finale e gli input dei tool_use dallo stream NDJSON
  python3 - "$OUT/$ID.stream.jsonl" "$OUT/$ID.risposta.md" "$OUT/$ID.tool_input.txt" <<'PYEOF2'
import json, sys
stream_path, risposta_path, tool_input_path = sys.argv[1:4]
result_text = None
raw_lines = []
tool_inputs = []
try:
    with open(stream_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            raw_lines.append(line)
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = ev.get('type')
            if t == 'result':
                result_text = ev.get('result', '')
            elif t == 'assistant':
                content = (ev.get('message') or {}).get('content') or []
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'tool_use':
                        tool_inputs.append(json.dumps(block.get('input', {}), ensure_ascii=False))
except FileNotFoundError:
    pass

with open(risposta_path, 'w', encoding='utf-8') as f:
    if result_text is not None:
        f.write(result_text)
    else:
        # Degrado: nessun evento "result" riconosciuto, usa il grezzo come extrema ratio
        f.write('\n'.join(raw_lines))

with open(tool_input_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(tool_inputs))
PYEOF2

  # Livello 1: assertion deterministiche sulla risposta finale (fatto, non opinione)
  ESITO_CHECK=$(printf '%s' "$DATI" | python3 -c "
import json, sys
d = json.load(sys.stdin)
checks = d.get('checks') or {}
risposta = open('$OUT/$ID.risposta.md', encoding='utf-8').read()
mancanti = [s for s in checks.get('must_include', []) if s.lower() not in risposta.lower()]
vietati = [s for s in checks.get('must_not_include', []) if s.lower() in risposta.lower()]
if mancanti or vietati:
    dett = []
    if mancanti: dett.append('mancanti: ' + '; '.join(mancanti))
    if vietati: dett.append('presenti e vietati: ' + '; '.join(vietati))
    print('FAIL_ASSERTION\t' + ' | '.join(dett))
else:
    print('OK\t' + ('nessuna assertion definita' if not checks.get('must_include') and not checks.get('must_not_include') else 'assertion soddisfatte'))
")
  IFS=$'\t' read -r STATO_CHECK DETT_CHECK <<< "$ESITO_CHECK"

  if [ "$STATO_CHECK" = "FAIL_ASSERTION" ]; then
    echo "FAIL: assertion deterministica — $DETT_CHECK" > "$OUT/$ID.giudizio.txt"
    FAIL=$((FAIL+1))
    echo "  -> FAIL (assertion deterministica: $DETT_CHECK)"
    continue
  fi

  # Livello 2: minimizzazione delle query — verifica sugli input dei tool_use, non sulla risposta
  ESITO_MINIM=$(printf '%s' "$DATI" | python3 -c "
import json, sys
d = json.load(sys.stdin)
checks = d.get('checks') or {}
vietati_tool = checks.get('tool_input_must_not_include') or []
if not vietati_tool:
    print('OK\tnessun controllo di minimizzazione definito')
else:
    tool_input = open('$OUT/$ID.tool_input.txt', encoding='utf-8').read()
    if not tool_input.strip():
        print('AVVISO\tnessun tool_use rilevato nello stream (formato non riconosciuto o nessun tool chiamato): controllo saltato')
    else:
        presenti = [s for s in vietati_tool if s.lower() in tool_input.lower()]
        if presenti:
            print('FAIL_MINIMIZZAZIONE\tdati identificativi presenti negli input dei tool: ' + '; '.join(presenti))
        else:
            print('OK\tnessun dato identificativo negli input dei tool')
")
  IFS=$'\t' read -r STATO_MINIM DETT_MINIM <<< "$ESITO_MINIM"

  if [ "$STATO_MINIM" = "FAIL_MINIMIZZAZIONE" ]; then
    echo "FAIL: minimizzazione — $DETT_MINIM" > "$OUT/$ID.giudizio.txt"
    FAIL=$((FAIL+1))
    echo "  -> FAIL (minimizzazione: $DETT_MINIM)"
    continue
  fi
  if [ "$STATO_MINIM" = "AVVISO" ]; then
    echo "  (nota: $DETT_MINIM)"
  fi

  # Livello 3: giudice LLM, per la qualità comportamentale
  GIUDIZIO=$(claude -p "Sei il giudice di una eval. RISPOSTA DA VALUTARE: <<<$(cat "$OUT/$ID.risposta.md")>>> COMPORTAMENTO ATTESO: <<<$ATTESO>>> Rispondi con una sola riga: PASS oppure FAIL, due punti, motivo in una frase. Sii severo sugli estremi normativi: un estremo diverso dall'atteso è FAIL." --output-format text 2>/dev/null || echo "FAIL: giudice non eseguito")
  echo "$GIUDIZIO" > "$OUT/$ID.giudizio.txt"
  case "$GIUDIZIO" in PASS*) PASS=$((PASS+1));; *) FAIL=$((FAIL+1));; esac
  echo "  -> $GIUDIZIO ($DETT_CHECK)"
done < "$OUT/_lista.tsv"

echo ""
echo "Esito: PASS=$PASS FAIL=$FAIL TEMPLATE_SALTATE=$SKIP — dettagli in $OUT/"
[ "$FAIL" -eq 0 ]
